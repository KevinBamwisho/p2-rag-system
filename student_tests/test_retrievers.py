"""Checks for my dense and hybrid retrievers on a three-document corpus: uv run pytest student_tests"""

from pathlib import Path

import pytest

from p2 import config, corpus, retrievers

DOCS = {
    "a-dust": "# 1.1 Rock dust.\n\nIncombustible rock dust shall be applied to the roof, ribs and floor.",
    "b-alarm": "# 1.2 Backup alarms.\n\nMobile equipment shall have an automatic reverse-activated signal alarm.",
    "c-radon": "# 1.3 Annual exposure limits.\n\nNo person shall receive an exposure in excess of 4 WLM in any calendar year.",
}
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def setup(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    for docid, text in DOCS.items():
        (docs / f"{docid}.md").write_text(text + "\n", encoding="utf-8", newline="\n")
    retrievers._built.clear()
    return corpus.load_dir(docs, "tiny"), config.load(ROOT).replace(root=tmp_path)


def test_dense_ranks_by_meaning_not_shared_words(setup):
    c, cfg = setup
    dense = retrievers.build("dense", c, cfg)
    hits = dense.search("Do trucks beep when they back up?", 3)
    assert hits[0][0] == "b-alarm"
    assert all(-1.0 <= s <= 1.0 for _, s in hits)  # cosine similarity of unit vectors
    assert dense.search_chunks("yearly cap on radioactive gas", 1)[0][0] == "c-radon#0"


def test_hybrid_scores_are_rrf_with_k_60(setup):
    c, cfg = setup
    # "rock dust": bm25 matches only a-dust; dense ranks a-dust first, the other two after it
    got = retrievers.build("hybrid", c, cfg).search("rock dust", 3)
    assert got[0] == ("a-dust", pytest.approx(2 / 61))  # rank 1 in both lists
    assert [s for _, s in got[1:]] == pytest.approx([1 / 62, 1 / 63])  # dense only, ranks 2 and 3


def test_hybrid_ignores_bm25_zero_score_padding(setup):
    c, cfg = setup
    dense, hybrid = (retrievers.build(n, c, cfg) for n in ("dense", "hybrid"))
    q = "zzz qqq"  # shares no word with any document, so bm25 scores all three 0
    expected = {d: 1 / (60 + r) for r, (d, _) in enumerate(dense.search(q, 3), 1)}
    assert dict(hybrid.search(q, 3)) == pytest.approx(expected)


def test_hybrid_fuses_chunks_for_p2_answer(setup):
    c, cfg = setup
    hits = retrievers.build("hybrid", c, cfg).search_chunks("rock dust", 2)
    assert hits[0][0] == "a-dust#0"
    assert len(hits) == 2
