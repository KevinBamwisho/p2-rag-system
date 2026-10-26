"""Dense retrieval with bge-small-en-v1.5: embed every chunk once, embed the query, rank chunks by cosine similarity.

Ported from the embedding arm of the 12 lab's retrieve.py (dense_rankings). embed.doc_vectors caches
the chunk vectors in .cache/vectors/, and every vector has length 1, so one matrix-vector product
gives the cosine similarity of the query with every chunk. ChunkScorer lifts chunks to documents
(a document scores its best chunk) for search, and ranks chunks directly for search_chunks.

The query goes in without bge's optional retrieval instruction, as in the lab's main bge arm.
A variant with another embedder subclasses Dense and sets `model` (see dense_potion.py).
"""

from __future__ import annotations

from p2 import embed
from p2.retrievers import ChunkScorer

NEEDS_CLAUDE = False


class Dense(ChunkScorer):
    model = embed.BGE

    def __init__(self, corpus, cfg):
        super().__init__(corpus, cfg)
        self.embedder = embed.load(self.model)
        self.vectors = embed.doc_vectors(self.embedder, [c.text for c in self.chunks], cfg.root)

    def score_chunks(self, text: str):
        return self.vectors @ self.embedder.encode([text])[0]


def build(corpus, cfg):
    return Dense(corpus, cfg)
