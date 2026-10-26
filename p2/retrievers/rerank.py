"""Listwise reranker: Claude reorders hybrid's top 20, one claude -p call per query.

Ported from rerank_one() in the 13 lab's pipeline.py. The top 20 go to Claude as numbered passages,
the schema forces the reply into {"order": [20 different numbers, each 1 to 20]}, and a reply that is
still not each number exactly once (or a failed call) keeps hybrid's order, with a warning. Candidates
below the 20 keep their order underneath, and scores are 1 / rank, as in the lab.

Changes from the lab:
- the schema bounds every item to 1..20 and sets uniqueItems, so claude -p rejects a number that
  names no passage, or a repeated one, before the reply comes back;
- a document's passage is its best chunk in hybrid's chunk ranking (the title goes in front when that
  is not the first chunk), cut to 2,000 characters, because a long CFR section can hold its matching
  rule well past the opening the lab's 600-character cut would show (sections: median 437, 90th
  percentile 2,366 characters);
- an invalid reply's saved copy is deleted, so the next run asks again instead of reusing it.
search_chunks reranks hybrid's top 20 chunks the same way, for `p2 answer --system rerank`.
"""

from __future__ import annotations

import sys

from p2 import claude, retrievers
from p2.corpus import docid_of

NEEDS_CLAUDE = True
CANDIDATES = 20
PASSAGE_CHARS = 2000
PROMPT = """Below are {n} passages, numbered 1 to {n}, and a search query.
Order the passages from the most useful for answering the query to the least useful.
Reply with all {n} passage numbers, each exactly once, best first.

Query: {query}

{passages}"""


def schema(n: int) -> dict:
    items = {"type": "integer", "minimum": 1, "maximum": n}
    order = {"type": "array", "items": items, "minItems": n, "maxItems": n, "uniqueItems": True}
    return {"type": "object", "properties": {"order": order}, "required": ["order"]}


class Rerank:
    def __init__(self, corpus, cfg):
        self.first = retrievers.build("hybrid", corpus, cfg)
        self.cfg = cfg
        self.model = cfg.model
        self.titles = {d: doc.title for d, doc in corpus.docs.items()}
        self.chunks = corpus.chunk_texts(cfg.chunk_words, cfg.chunk_overlap)

    def passage(self, chunk_id: str) -> str:
        text = self.chunks[chunk_id]
        if not chunk_id.endswith("#0"):
            text = f"# {self.titles[docid_of(chunk_id)]}\n\n... {text}"
        return text[:PASSAGE_CHARS]

    def rerank(self, query: str, hits, chunk_of):
        """hits: the first stage's (id, score) list; chunk_of: an id to the chunk shown for it."""
        top, rest = [d for d, _ in hits[:CANDIDATES]], [d for d, _ in hits[CANDIDATES:]]
        passages = "\n\n".join(f"[{i}] {self.passage(chunk_of(d))}" for i, d in enumerate(top, 1))
        prompt, shape = PROMPT.format(n=len(top), query=query, passages=passages), schema(len(top))
        reply = claude.call(prompt, shape, model=self.model, cache_dir=claude.cache_folder(self.cfg))
        order = (reply.output or {}).get("order")
        valid = isinstance(order, list) and all(type(i) is int for i in order) and sorted(order) == list(range(1, len(top) + 1))
        if valid:
            top = [top[i - 1] for i in order]
        else:
            print(f"  WARNING: {reply.error or f'reply was not each of 1 to {len(top)} once: {order}'}; kept hybrid's order", file=sys.stderr)
            if (folder := claude.cache_folder(self.cfg)) is not None:
                (folder / f"{claude.cache_key(prompt, shape, self.model, None)}.json").unlink(missing_ok=True)
        return [(d, 1 / rank) for rank, d in enumerate(top + rest, 1)]

    def search(self, text: str, k: int):
        best: dict[str, str] = {}
        for chunk_id, _ in self.first.search_chunks(text, len(self.chunks)):
            best.setdefault(docid_of(chunk_id), chunk_id)
        return self.rerank(text, self.first.search(text, max(k, CANDIDATES)), best.__getitem__)[:k]

    def search_chunks(self, text: str, k: int):
        return self.rerank(text, self.first.search_chunks(text, max(k, CANDIDATES)), lambda c: c)[:k]


def build(corpus, cfg):
    return Rerank(corpus, cfg)
