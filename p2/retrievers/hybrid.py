"""Hybrid retrieval: reciprocal rank fusion (k = 60) of bm25 and dense.

Ported from rrf() in the 13 lab's pipeline.py: each document scores the sum of 1 / (60 + rank) over
the rankings it appears in. RRF uses ranks, not scores, because bm25's scores (0 to ~35) and cosine
similarities (about 0.3 to 0.9) are on scales that do not add up.

Both systems rank everything (full rankings, not top 10), so a document 11th in both lists can still
reach the fused top 10. One change from the lab: bm25's zero-score tail is left out. Those documents
share no word with the query and come in docid order, so their "ranks" would be alphabetical noise.
search_chunks fuses the chunk rankings the same way, for `p2 answer`.
"""

from __future__ import annotations

from p2 import retrievers
from p2.runfile import order

NEEDS_CLAUDE = False
K = 60


def rrf(*rankings):
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, (item, _) in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0.0) + 1 / (K + rank)
    return order(scores.items())


class Hybrid:
    def __init__(self, corpus, cfg):
        self.bm25 = retrievers.build("bm25", corpus, cfg)
        self.dense = retrievers.build("dense", corpus, cfg)
        self.n_docs = len(corpus.docs)
        self.n_chunks = len(self.dense.chunks)

    def search(self, text: str, k: int):
        keyword = [p for p in self.bm25.search(text, self.n_docs) if p[1] > 0]
        return rrf(keyword, self.dense.search(text, self.n_docs))[:k]

    def search_chunks(self, text: str, k: int):
        keyword = [p for p in self.bm25.search_chunks(text, self.n_chunks) if p[1] > 0]
        return rrf(keyword, self.dense.search_chunks(text, self.n_chunks))[:k]


def build(corpus, cfg):
    return Hybrid(corpus, cfg)
