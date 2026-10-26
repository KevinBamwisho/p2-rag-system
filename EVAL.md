# Evaluation report

This is the report on what you built and what the numbers let you claim.
Two kinds of text live here.

The tables between a `p2:begin` comment line and its matching `p2:end` comment line are written by `uv run p2 score` from your committed run files and answers files.
Please do not edit anything between those two lines, because `uv run p2 check` recomputes them and fails when they differ.
A table that says no runs or answers exist yet is waiting for data; run `uv run p2 score` after you commit the files it needs.

Everything else is yours.
Each prompt ends with a marker line that you replace with your own writing; `uv run p2 check --final` fails while one is left.
Write what you measured, including what did not work.
What I read for is whether each claim matches its interval, not whether the result is good news.

Words used below: recall@10, MRR@10 and nDCG@10 are the three scores, each averaged over the queries of a set; step 7 of stage 1 in the README defines them, and lecture 14 goes deeper.
A paired interval is the 95% interval of the mean difference between two systems on the same queries, found by resampling the queries 10,000 times.
When an interval includes zero, the gold set cannot tell the two systems apart, and the right words are "not distinguishable on this gold set".
The minimum detectable difference is the smallest gap this many queries could reliably show, so a difference below it is invisible to this gold set, not absent.

---

## 1. Stage 1 - the shared corpus (30 CFR Chapter I)

### What you built

For each of `dense`, `hybrid` and `rerank`, one or two sentences: the embedding model, how documents were chunked, what was fused and how, how many candidates the reranker saw, and anything you changed from the 12 and 13 lab code.

All four systems search the same chunks: windows of 300 words that overlap by 50 (the `p2.toml` defaults), title line included.
That cuts the 2,484 sections into 3,132 chunks (3,127 distinct texts, since a few chunks repeat word for word), and most sections fit in one chunk.
A document gets the score of its best chunk.

`dense` embeds every chunk with bge-small-en-v1.5 (384 dimensions, through fastembed) and ranks chunks by cosine similarity with the query, same as the bge arm in the 12 lab, with no query instruction.
Encoding the corpus from scratch took 115 seconds on my laptop (timed around `embed.doc_vectors`), and after that the vectors come from the cache.
I also ran `dense_potion`, the same thing with potion-retrieval-32M, a static model.
It encoded the same chunks in 0.4 seconds and got MRR@10 0.475 to bge's 0.562, a difference of -0.088 [-0.335, +0.153], so it's not distinguishable on 20 queries.

`hybrid` is reciprocal rank fusion (k = 60) of `bm25` and `dense` over the full rankings, like `rrf()` in the 13 lab: each document scores the sum of 1 / (60 + rank) over the two lists.
One change from the lab: I drop documents with a bm25 score of 0 from bm25's list.
They share no word with the query, but the lab's version still ranks them in docid order, so the small bonus each one gets just depends on where its id falls in the alphabet.
On practice this leaves MRR@10 at 0.471, but it moves the first relevant section down on three queries, all outside the top 10: p08 from 18 to 22, p10 from 103 to 109, p14 from 56 to 63.
In those queries the relevant sections (all of p08's and p10's, two of p14's three) have no bm25 match, so the lab's version was lifting them by alphabet position, not by anything bm25 found.
I kept the change, but it does push p08 out of a top 20.
`search_chunks` fuses the two chunk rankings the same way, so `p2 answer` can use it.

TODO: describe `rerank` (Phase 2).

### Practice queries (20)

Scores per system.

<!-- p2:begin shared-practice -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.625 | 0.507 | 0.518 |
| dense | 0.558 | 0.562 | 0.480 |
| hybrid | 0.617 | 0.471 | 0.457 |
| dense_potion | 0.533 | 0.475 | 0.432 |

20 judged queries; nDCG uses binary labels; a random ranking of the 2,484 documents would get recall@10 near 0.004.
<!-- p2:end shared-practice -->

The same scores per query class.

<!-- p2:begin shared-practice-classes -->
| System | Metric | identifier (n=7) | paraphrase (n=7) | mixed (n=6) |
| --- | --- | ---: | ---: | ---: |
| bm25 | Recall@10 | 1.000 | 0.000 | 0.917 |
| bm25 | MRR@10 | 0.810 | 0.000 | 0.746 |
| bm25 | nDCG@10 | 0.857 | 0.000 | 0.728 |
| dense | Recall@10 | 0.214 | 0.595 | 0.917 |
| dense | MRR@10 | 0.333 | 0.714 | 0.653 |
| dense | nDCG@10 | 0.211 | 0.593 | 0.661 |
| hybrid | Recall@10 | 0.571 | 0.405 | 0.917 |
| hybrid | MRR@10 | 0.514 | 0.154 | 0.792 |
| hybrid | nDCG@10 | 0.435 | 0.203 | 0.779 |
| dense_potion | Recall@10 | 0.500 | 0.286 | 0.861 |
| dense_potion | MRR@10 | 0.571 | 0.300 | 0.565 |
| dense_potion | nDCG@10 | 0.470 | 0.254 | 0.595 |
<!-- p2:end shared-practice-classes -->

Differences between every pair of systems, each with its paired interval and the minimum detectable difference.

<!-- p2:begin shared-practice-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | -0.067 | [-0.350, +0.225] | 0.415 | not distinguishable |
| dense minus bm25 | MRR@10 | +0.055 | [-0.225, +0.343] | 0.412 | not distinguishable |
| dense minus bm25 | nDCG@10 | -0.039 | [-0.302, +0.231] | 0.385 | not distinguishable |
| hybrid minus bm25 | Recall@10 | -0.008 | [-0.225, +0.208] | 0.317 | not distinguishable |
| hybrid minus bm25 | MRR@10 | -0.036 | [-0.178, +0.084] | 0.193 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | -0.062 | [-0.218, +0.082] | 0.218 | not distinguishable |
| hybrid minus dense | Recall@10 | +0.058 | [-0.117, +0.242] | 0.261 | not distinguishable |
| hybrid minus dense | MRR@10 | -0.091 | [-0.305, +0.110] | 0.300 | not distinguishable |
| hybrid minus dense | nDCG@10 | -0.023 | [-0.191, +0.137] | 0.240 | not distinguishable |
| dense_potion minus bm25 | Recall@10 | -0.092 | [-0.308, +0.125] | 0.313 | not distinguishable |
| dense_potion minus bm25 | MRR@10 | -0.033 | [-0.228, +0.177] | 0.296 | not distinguishable |
| dense_potion minus bm25 | nDCG@10 | -0.086 | [-0.268, +0.106] | 0.270 | not distinguishable |
| dense_potion minus dense | Recall@10 | -0.025 | [-0.233, +0.167] | 0.286 | not distinguishable |
| dense_potion minus dense | MRR@10 | -0.088 | [-0.335, +0.153] | 0.349 | not distinguishable |
| dense_potion minus dense | nDCG@10 | -0.047 | [-0.260, +0.159] | 0.299 | not distinguishable |
| dense_potion minus hybrid | Recall@10 | -0.083 | [-0.258, +0.067] | 0.236 | not distinguishable |
| dense_potion minus hybrid | MRR@10 | +0.003 | [-0.161, +0.175] | 0.248 | not distinguishable |
| dense_potion minus hybrid | nDCG@10 | -0.025 | [-0.161, +0.108] | 0.195 | not distinguishable |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end shared-practice-pairs -->

The 40 test queries have no answer key in this repo.
Your test run files are scored by the course and the score comes back to you as feedback, so nothing goes here for them.

### What the intervals let you claim

Which differences are distinguishable from zero and which are not?
What is the minimum detectable difference at 20 queries, and what does that say about any gap smaller than it?
Which claim from lecture 12 or 13 did your numbers support, and which did they leave open?

No two systems are distinguishable on the 20 practice queries: every paired interval includes zero, on all three metrics.
The minimum detectable difference at 20 queries runs from 0.19 to 0.42, and every gap I saw is well under its own pair's MDD.
The biggest ones, -0.092 recall@10 for dense_potion minus bm25 and -0.091 MRR@10 for hybrid minus dense, sit against MDDs of 0.313 and 0.300.
The MDD is the gap this gold set would catch 80% of the time, so a real gap of 0.1 would get caught a lot less often than that.
"Not distinguishable" here means the gold set is too small to tell, not that the systems are the same.

The per class table shows the pattern from lecture 12, keyword search strong on identifiers and weak on paraphrases and dense the other way, but each class is only 7 queries with no interval of its own, so it describes this gold set and doesn't prove a rule.
bm25 has recall@10 1.000 on identifier queries and 0.000 on paraphrase queries, and dense has 0.214 and 0.595.
So dense is better on paraphrases than on identifiers, but even on paraphrases it only finds 0.595 of the relevant sections in its top 10 on average.
The two systems winning in opposite directions is probably why the overall dense minus bm25 interval is so wide, [-0.225, +0.343], since big per query differences of both signs make the resampled mean swing around; I haven't tested that.

The claim my numbers didn't support is that hybrid gets the best of both.
Inside the identifier and paraphrase classes hybrid lands between its two inputs (MRR@10 0.514 on identifiers vs bm25's 0.810, and 0.154 on paraphrases vs dense's 0.714), and it only beats both on mixed.
Overall its MRR@10 (0.471) and nDCG@10 (0.457) are the lowest of the three, though not distinguishably, and its recall@10 (0.617) is between bm25's and dense's.
What's going on is that RRF only counts ranks: with k = 60, a section only one system finds scores about 1/61 at best, while a section ranked around 50th by both scores 2/110 and passes it.
You can see it in the full rankings (rank of the first relevant section in bm25 / dense / hybrid, deeper than the top 10 the run files keep): p03 is 3 / 1736 / 35 and p06 is 1 / 664 / 32, and on p08 bm25 doesn't match any relevant section, dense ranks one first, and hybrid puts it 22nd.
p10 and p14 fail a different way: dense misses them too (first relevant at 33 and 19), so fusion had nothing good to work with.

---

## 2. Stage 1 - cited answers on the 12 shared questions

<!-- p2:begin answers -->
_No answers files yet: run `uv run p2 answer --corpus shared --system NAME`, then `uv run p2 score`._
<!-- p2:end answers -->

Which system answered, and why that one?
What did you change in `prompts/answer.txt`, if anything, and did the verified share or the declined share move?

Then read three in-corpus answers that `uv run p2 verify` passed.
For each one, open the cited chunk and say whether the quote really supports the claim next to it.
The check proves a quote is a real piece of the chunk and cannot prove that it supports the claim, so this reading is the part only you can do.

TODO: write your answer choices and your three-answer audit.

---

## 3. Stage 2 - your corpus and your gold set

### The corpus

What is it, where did it come from, how many documents and how many megabytes, and what is the license basis for publishing it?
Name the one or two documents you were least sure about and what you decided.
Say which of the allowed sources in the brief it comes from.

TODO: describe your corpus and its license basis.

### The gold set

How many queries, how many with origin `hand` and how many with origin `claude`, and which query classes did you use and why?
How did you decide that a document is relevant: write your relevance rule in two or three sentences, the way the brief does for the shared corpus.
How did you find candidates (the systems' top 10, a keyword search, reading), and did you read every document before you labeled it?
Your labels are binary (`rel` 1) unless you say otherwise: if you use graded labels, declare the scale here, for example 2 means the document answers the query fully and 1 means it helps.

TODO: describe your gold set and your relevance rule.

---

## 4. Stage 2 - results on your corpus

Scores per system on your gold set.

<!-- p2:begin own -->
_No scored runs here yet: run `uv run p2 run --corpus own --system bm25` (or `--all`), then `uv run p2 score`._
<!-- p2:end own -->

The same scores per query class.

<!-- p2:begin own-classes -->
_No scored runs here yet: run `uv run p2 run --corpus own --system bm25` (or `--all`), then `uv run p2 score`._
<!-- p2:end own-classes -->

The same scores for the queries you wrote yourself (`hand`) and the ones a model drafted (`claude`), with the difference between the two groups and its interval.
Once both groups have queries, the table also says whether `bm25`'s lead over `dense` differs between them, and what share of each query's content words its best relevant document contains, which is stretch option 6.

<!-- p2:begin own-origins -->
_No scored runs here yet: run `uv run p2 run --corpus own --system bm25` (or `--all`), then `uv run p2 score`._
<!-- p2:end own-origins -->

Differences between every pair of systems.

<!-- p2:begin own-pairs -->
_No scored runs here yet: run `uv run p2 run --corpus own --system bm25` (or `--all`), then `uv run p2 score`._
<!-- p2:end own-pairs -->

Which differences are distinguishable and which are not, at your gold-set size?
Do the `hand` queries and the `claude` queries tell the same story?
Did your prediction in `DECISIONS.md` prompt 1 hold?

TODO: write what your own-corpus intervals let you claim.

---

## 5. The ablation

Change one thing and keep everything else the same.
Write your hypothesis here before you run it, in one sentence with a direction: "I expect X to raise MRR@10 on my corpus because Y."
The run file for it lives in `runs/own/ablation/`.

<!-- p2:begin own-ablation -->
_No ablation runs yet: `uv run p2 run --corpus own --system NAME --ablation` writes one to runs/own/ablation/, then `uv run p2 score` fills this table._
<!-- p2:end own-ablation -->

The queries your ablation helped and hurt, against the system it varies, by reciprocal rank.
`p2 score` finds that system from a line such as `BASE = "bm25"` in your variant's file, or else from its name: `bm25_lab` varies `bm25`.

<!-- p2:begin own-ablation-queries -->
_No ablation runs yet: `uv run p2 run --corpus own --system NAME --ablation` writes one to runs/own/ablation/, then `uv run p2 score` fills this table._
<!-- p2:end own-ablation-queries -->

What did you change, what happened, and does the interval support the claim you want to make?
If the result is not distinguishable, say what size of effect your gold set could have seen.
Read the queries at the top of each list in the second table, and say whether your change explains them.

TODO: write the ablation: the one change, the hypothesis, the result and the claim.

---

## 6. Failure analysis

Pick the queries where your best system on your own corpus failed: the relevant document is missing from the top 10, or sits far below the top.
Take at least five, and read what the system returned next to what was relevant.
Then sort the failures by cause, for example a vocabulary mismatch, near-duplicate documents, a chunk that cut the answer in half, a query that is ambiguous, or a label that was wrong, because sometimes the gold set is what failed.

| qid | what the best system returned | what was relevant | cause | what you would try |
|---|---|---|---|---|

TODO: add one row for each failure you analyzed, and write two or three sentences on the pattern you see across them.

---

## 7. Cross-corpus comparison

The two tables to compare are the shared-corpus scores in section 1 and your own-corpus scores in section 4, with their intervals.
If you want them side by side, copy the rows you need into a table here and say that you copied them.

Did the winner change between the shared corpus and yours?
Why, or why not: what is different about the two collections (document length, vocabulary, identifiers, near-duplicates, how the queries were written), and which of your explanations did you test and which are guesses?
Say what 20 queries on one side and your gold-set size on the other cannot support.

TODO: write the cross-corpus comparison.

---

## 8. Stretch

498E: the stretch is one of the six options in the brief's "One stretch" section, and that section says what earns the 25 points for each.
It is optional, so `uv run p2 check --final` never waits on this section.
598E: the rider is your stretch, so write "rider" below and put its results in section 9; the other options add no points, because the project is capped at 150.

Whichever option you chose, write these five things:

1. The option's name.
2. What you did, and the files that hold it.
3. The table `p2 score` wrote for it, by name: one of the three below, `own-ablation` and `own-ablation-queries` in section 5 for a second ablation, `own-origins` in section 4 for the hand and claude queries, or `repeats` in section 9 for the rider.
4. What its interval lets you claim, and what it does not.
5. One thing you would do next, and what result would tell you it worked.

For a second ablation, write its hypothesis here before you run it, and commit it, so your history shows that it came first.
For the hand and claude queries, do the same with your prediction before you score.

### Claim-level faithfulness check (option 2)

Claude's verdicts from `p2 judge` against your own verdicts in the calibration file.

<!-- p2:begin stretch-judge -->
_No judged answers yet (stretch option 2): `uv run p2 judge answers/shared/LABEL.json` writes them, your own verdicts go in answers/shared/LABEL.calibration.tsv, and then `uv run p2 score` fills this table._
<!-- p2:end stretch-judge -->

### Cost and latency (option 3)

The Claude calls, tokens and seconds in every trace you committed, and what a cheaper system or answers file saves against what it loses.

<!-- p2:begin stretch-cost -->
_No Claude traces yet: a run of a system that calls Claude, `p2 answer` and `p2 judge` write them in traces/, and then `uv run p2 score` fills this table._

Systems that do not call Claude, from traces/retrieval/ on the machine that last ran `p2 score` (git ignores that folder, so `p2 check` does not compare this part):

| Trace | System | Queries | Seconds | Milliseconds per query |
| --- | --- | ---: | ---: | ---: |
| traces/retrieval/shared-practice-bm25.jsonl | bm25 | 20 | 0.03 | 1.7 |
| traces/retrieval/shared-practice-dense.jsonl | dense | 20 | 0.24 | 11.8 |
| traces/retrieval/shared-practice-dense_potion.jsonl | dense_potion | 20 | 0.05 | 2.3 |
| traces/retrieval/shared-practice-hybrid.jsonl | hybrid | 20 | 0.26 | 13.1 |
| traces/retrieval/shared-test-bm25.jsonl | bm25 | 40 | 0.13 | 3.2 |
| traces/retrieval/shared-test-dense.jsonl | dense | 40 | 0.32 | 8.1 |
| traces/retrieval/shared-test-hybrid.jsonl | hybrid | 40 | 0.48 | 12.0 |
<!-- p2:end stretch-cost -->

### The grep agent (option 5)

Your stretch run on some of your own queries against the four systems on the same queries.

<!-- p2:begin stretch-agent -->
_No stretch runs yet (stretch option 5): `uv run p2 run --corpus own --queries eval/own/agent.queries.tsv --system agent --stretch` writes one to runs/own/stretch/, then `uv run p2 score` fills this table._
<!-- p2:end stretch-agent -->

### Your stretch

Write the five things here.

---

## 9. 598E only - repeats and the pre-registered claim

498E students can leave this section as it is; nothing checks it.
598E students replace each line that starts with "598E: write", and `uv run p2 check --final` counts those lines as work still to do until they are gone.

### Repeats on the shared corpus

Three runs of the reranker on the practice queries, and three answers files, with their run-to-run spread and Wilson intervals.

<!-- p2:begin repeats -->
_No repeated runs or answers files yet (598E: `p2 run ... --repeat 3` and `p2 answer ... --repeat 3`)._
<!-- p2:end repeats -->

Does the reranker's gain over its first stage survive the run-to-run variation?
Write what the spread is, how it compares with the gain, and what the Wilson intervals on the verified share and the declined share say about 8 and 4 questions.

598E: write the repeats result here.

### The pre-registered claim

The claim, the smallest effect, the gold-set size and the test are in `PREREG.md`, committed before your own gold-set judgments.
Here, say whether you followed the plan, what the interval turned out to be, and what that means.
The outcome section of `PREREG.md` holds the short version.

598E: write the claim and its outcome here.
