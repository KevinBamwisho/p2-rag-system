"""dense with potion-retrieval-32M instead of bge-small: the embedding-model ablation.

potion is a static model (model2vec): a token's vector is a table lookup and a text's vector is
their mean, with no network at query time, so it is much faster and blind to word order and context.
Everything else (chunks, cosine, max-pooling to documents) is dense's.
"""

from __future__ import annotations

from p2 import embed
from p2.retrievers.dense import Dense

NEEDS_CLAUDE = False
BASE = "dense"


class DensePotion(Dense):
    model = embed.POTION


def build(corpus, cfg):
    return DensePotion(corpus, cfg)
