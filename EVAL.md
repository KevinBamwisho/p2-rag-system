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

`rerank` sends hybrid's top 20 to Claude (Sonnet) as numbered passages and asks for all 20 back, best first.
It's one listwise call per query, like `rerank_one()` in the 13 lab.
If a reply isn't each number once, the query keeps hybrid's order.
None of the 20 practice replies needed that.

The main change from the lab is what Claude sees.
The lab cut each article to its first 600 characters.
I send each document's best chunk instead, with the title in front, cut at 2,000 characters.
CFR sections run longer than help center articles (median 437 characters, 90th percentile 2,366), and the rule that matched can sit past the opening.

The 20 practice calls read 881,875 input tokens and cost $1.86.
That's about 44,000 tokens a call, more than three times the brief's 12,000.

### Practice queries (20)

Scores per system.

<!-- p2:begin shared-practice -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.625 | 0.507 | 0.518 |
| dense | 0.558 | 0.562 | 0.480 |
| hybrid | 0.617 | 0.471 | 0.457 |
| rerank | 0.725 | 0.750 | 0.731 |
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
| rerank | Recall@10 | 0.714 | 0.500 | 1.000 |
| rerank | MRR@10 | 0.714 | 0.571 | 1.000 |
| rerank | nDCG@10 | 0.714 | 0.516 | 1.000 |
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
| rerank minus bm25 | Recall@10 | +0.100 | [-0.125, +0.325] | 0.331 | not distinguishable |
| rerank minus bm25 | MRR@10 | +0.243 | [+0.010, +0.476] | 0.339 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.212 | [-0.008, +0.426] | 0.316 | not distinguishable |
| rerank minus dense | Recall@10 | +0.167 | [-0.025, +0.350] | 0.271 | not distinguishable |
| rerank minus dense | MRR@10 | +0.188 | [-0.017, +0.392] | 0.294 | not distinguishable |
| rerank minus dense | nDCG@10 | +0.251 | [+0.062, +0.431] | 0.268 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.108 | [+0.025, +0.209] | 0.141 | rerank higher |
| rerank minus hybrid | MRR@10 | +0.279 | [+0.128, +0.441] | 0.229 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.274 | [+0.159, +0.396] | 0.171 | rerank higher |
| dense_potion minus bm25 | Recall@10 | -0.092 | [-0.308, +0.125] | 0.313 | not distinguishable |
| dense_potion minus bm25 | MRR@10 | -0.033 | [-0.228, +0.177] | 0.296 | not distinguishable |
| dense_potion minus bm25 | nDCG@10 | -0.086 | [-0.268, +0.106] | 0.270 | not distinguishable |
| dense_potion minus dense | Recall@10 | -0.025 | [-0.233, +0.167] | 0.286 | not distinguishable |
| dense_potion minus dense | MRR@10 | -0.088 | [-0.335, +0.153] | 0.349 | not distinguishable |
| dense_potion minus dense | nDCG@10 | -0.047 | [-0.260, +0.159] | 0.299 | not distinguishable |
| dense_potion minus hybrid | Recall@10 | -0.083 | [-0.258, +0.067] | 0.236 | not distinguishable |
| dense_potion minus hybrid | MRR@10 | +0.003 | [-0.161, +0.175] | 0.248 | not distinguishable |
| dense_potion minus hybrid | nDCG@10 | -0.025 | [-0.161, +0.108] | 0.195 | not distinguishable |
| dense_potion minus rerank | Recall@10 | -0.192 | [-0.350, -0.050] | 0.220 | rerank higher |
| dense_potion minus rerank | MRR@10 | -0.275 | [-0.463, -0.108] | 0.261 | rerank higher |
| dense_potion minus rerank | nDCG@10 | -0.298 | [-0.453, -0.159] | 0.216 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end shared-practice-pairs -->

The 40 test queries have no answer key in this repo.
Your test run files are scored by the course and the score comes back to you as feedback, so nothing goes here for them.

### What the intervals let you claim

Which differences are distinguishable from zero and which are not?
What is the minimum detectable difference at 20 queries, and what does that say about any gap smaller than it?
Which claim from lecture 12 or 13 did your numbers support, and which did they leave open?

Among bm25, dense, hybrid and dense_potion, no two are distinguishable on the 20 practice queries: every paired interval between them includes zero, on all three metrics.
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

rerank is the one system that separates.
Against hybrid, its own first stage, it wins on all three metrics.
MRR@10 goes up by +0.279 [+0.128, +0.441], which is also bigger than that pair's MDD of 0.229.
nDCG@10 goes up by +0.274 [+0.159, +0.396] and recall@10 by +0.108 [+0.025, +0.209].
It also beats bm25 on MRR@10, but only barely: +0.243 [+0.010, +0.476].
It beats dense on nDCG@10, +0.251 [+0.062, +0.431].
Every other comparison with those two includes zero.

Per query it's pretty simple.
On all 15 queries where hybrid had a relevant section in its top 20, rerank put one at rank 1.
The 5 it misses (p03, p06, p08, p10, p14) are exactly the ones where hybrid had none in its top 20.
So 0.750 = 15/20 is the most this reranker could get from hybrid's candidates.
What holds it back now is the first stage's recall, not the reordering.
That's the two stage idea from the 13 lab: cheap recall first, expensive ordering second.
It also makes the RRF problem above cost more, since p08 sat at 22 in hybrid, two places from getting rescued.

These intervals only cover which queries got sampled.
They don't cover the variance between repeated runs of the reranker.
Claude doesn't give the same order every time: p02 got three different orders from three calls, with the same top two each time.
Those were on earlier versions of the prompt, and it's one example, not a measurement.
This run is one draw.
I haven't measured how much MRR@10 moves between repeats.

---

## 2. Stage 1 - cited answers on the 12 shared questions

<!-- p2:begin answers -->
| Label | System | Verified (in) | 95% interval | not_found (in) | Declined (out) | 95% interval | Quotes found |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | hybrid | 7 of 8 (88%) | [0.529, 0.978] | 0 of 8 (0%) | 4 of 4 (100%) | [0.510, 1.000] | 13 of 14 |
| rerank | rerank | 8 of 8 (100%) | [0.676, 1.000] | 0 of 8 (0%) | 4 of 4 (100%) | [0.510, 1.000] | 11 of 11 |
<!-- p2:end answers -->

Which system answered, and why that one?
What did you change in `prompts/answer.txt`, if anything, and did the verified share or the declined share move?

Then read three in-corpus answers that `uv run p2 verify` passed.
For each one, open the cited chunk and say whether the quote really supports the claim next to it.
The check proves a quote is a real piece of the chunk and cannot prove that it supports the claim, so this reading is the part only you can do.

I answered with `rerank`.
It beat hybrid on MRR@10 by +0.279, with an interval of [+0.128, +0.441].
The answer prompt only sees 5 chunks, so getting the right one near the top matters most.
It costs two calls per question instead of one: a rerank of hybrid's top 20 chunks, then the answer.
The 12 questions took 24 calls and $1.51.
One caveat: the gain was measured on ranking documents for the practice queries.
Nothing scores chunk reranking on these 12 questions, so I'm assuming it carries over.

I also answered with `hybrid` (12 calls, $0.33), mainly to get enough claims for the judge in section 8.
rerank's answers only had 11.
Both declined all 4 unanswerable questions and didn't answer from memory.
rerank verified 8 of 8 and hybrid 7 of 8.
The paired difference in passing share over all 12 questions is -0.083 [-0.250, +0.000] (the `stretch-cost` table), so I can't claim a difference.
hybrid's one failure, a04, isn't a made up quote.
The section has "shall—", then a paragraph break, then "(1) Be held", and Claude wrote "shall—(1)" with no space.
verify collapses whitespace but doesn't delete it, so it counts that as not word for word, which is fair.

I didn't change `prompts/answer.txt`.

For the audit I read rerank's a03, a05 and a07, 6 claims in all, against their cited chunks.
Four match their quotes and are supported.
Two are only partly supported.
a03-c2 lists the three approved device options but drops their conditions.
75.1714-1 requires MSHA and NIOSH approval under 42 CFR part 84, and option (c) also needs MSHA approval and use as prescribed.
So the claim reads like any breathing apparatus that lasts an hour counts.
a07-c3 says the same mid-axle rule applies under 57.9300, which the quote shows.
But it adds "for underground metal and nonmetal mines", which isn't in the quote or the section.

The bigger thing I found out is that the top level answers say more than their claims do.
a03's says "underground coal miner", but nothing it cites says coal.
It also says "provided" where the rule only says "make available", which is a weaker duty.
a05's says "underground miner" where the quote only says "new miner".
It also skips the paragraph (d) exception for recently trained miners.
That's not because Claude didn't see it: (d) was in `cfr30-48.5#3`, the second chunk it got, and it still left it out.
a07's calls 56.9300 surface and 57.9300 underground, with no claim behind either.
It also states the mid-axle rule like it applies everywhere.
Paragraph (a) limits it to roadways with a drop-off, and (d) exempts some elevated roadways that are rarely used.
verify only looks at claims, so none of this shows up in its numbers.
A PASS means the quotes are real, not that the answer a person reads is right.

---

## 3. Stage 2 - your corpus and your gold set

### The corpus

What is it, where did it come from, how many documents and how many megabytes, and what is the license basis for publishing it?
Name the one or two documents you were least sure about and what you decided.
Say which of the allowed sources in the brief it comes from.

The corpus is 998 questions from Meta Stack Exchange, where users report bugs, ask for features and argue about how the site works, so it’s real feedback on a real product. They’re tagged bug, feature-request, support or discussion, posted between 2018-05-02 and 2024-03-28, and come from the April 2024 dump on archive.org. It’s about 1.1 MB and 157,000 words, and posts are short: the median is 95 words and 188 are under 50. I kept only the title and the question. Tags would hand bm25 free keywords, and images are gone (492 posts lost at least one).

To pick them, I dropped posts with a negative score, posts by deleted users and posts under 20 words. Then I took whole groups of posts closed as duplicates of each other until they made up a third, and filled the rest at random, so 342 of the 998 link to another post in the corpus. That has two costs. Dropping downvoted posts leans toward feedback people agreed with, and the duplicate groups mean the same complaints show up more than they would in a random sample.

It’s CC BY-SA 4.0. The licensing page covers anything posted on or after 2018-05-02, and each post’s own license field says the same. The manifest links every question and every author’s profile, and NOTICE.md lists what I changed. CC BY-SA is share-alike, so the corpus stays CC BY-SA 4.0 here, not CC0. I removed two posts: 333531, whose pasted Safari version string has an Apple copyright notice, and 337461, which quotes about 290 words of a copyrighted blog post. The 9 short quotes from other sources I kept as the authors posted them.

### The gold set

How many queries, how many with origin `hand` and how many with origin `claude`, and which query classes did you use and why?
How did you decide that a document is relevant: write your relevance rule in two or three sentences, the way the brief does for the shared corpus.
How did you find candidates (the systems' top 10, a keyword search, reading), and did you read every document before you labeled it?
Your labels are binary (`rel` 1) unless you say otherwise: if you use graded labels, declare the scale here, for example 2 means the document answers the query fully and 1 means it helps.

There are 40 queries. I wrote 20 myself (`hand`) and Claude drafted 20 (`claude`). Both halves use the same three classes. Mine are 8 jargon, 6 plain and 6 named, and Claude’s are 7 jargon, 7 plain and 6 named, so 15, 13 and 12 overall. Jargon uses the site’s own words, like rep, close votes, review queues or the user card. Plain describes the same kind of problem the way a new user would, without those words. Named asks about a specific named feature, page, event, badge or policy, like SEDE, Winter Bash or the mandatory arbitration clause. A named query hangs on one rare, exact term, the way a CFR section number does on the shared corpus, so bm25 should be strong there. I picked these because people writing feedback either know the site’s words or they don’t, and that’s where bm25 and dense should split.

Every query was written with one post in mind. I wrote mine from a list of 40 random titles and 10 duplicate groups. Claude drafted its queries from a second random sample, reading each post first. So these are people looking for a specific complaint, and 34 of the 40 queries have only one relevant post. With one relevant post, recall@10 is all or nothing for that query, so per query scores jump around and the intervals will be wide.

A post is relevant if someone who typed the query would be happy to land on it, because it covers the same specific problem or request. A related topic isn’t enough. A duplicate counts only when it describes the same problem. Posts that lost a screenshot are judged on the text that’s left, and if that text doesn’t say what’s wrong, the post isn’t relevant. Labels are binary.

For candidates I pooled five sources per query: bm25’s top 10, dense’s top 10, a keyword search, the post each query was matched to, and that post’s duplicates. The keyword search took the 5 posts sharing the most content words with the query and kept those that share at least 2 and at least half of them, ties going to the lower post id. For Claude’s queries the matched post is the one it read. For mine it was a guess from the title, and the guess was wrong once (h18), which the pool still caught. That came to 705 candidates, 12 to 24 per query. Each list was shuffled with its sources hidden, so I couldn’t tell which system found what. I marked 51 relevant. I didn’t read every post in full. I rejected clearly off topic titles without opening them and skimmed the body of anything plausible. After judging, I checked the duplicates of every relevant post, and all of them were already in the pool.

The pool has a known gap. Hybrid, rerank and the dense_potion ablation weren’t in it, and a post nobody judged counts as not relevant. So if one of them finds a relevant post that bm25 and dense missed, it gets no credit, and those three can only look worse than they are on recall and MRR. It’s worst for dense_potion: 179 of its 400 top-10 posts were never judged, so the ablation compares a fully judged system with a half-judged one. Most queries have one relevant post that’s already in the qrels, so the effect may be small, but I can’t rule it out without judging those posts.

---

## 4. Stage 2 - results on your corpus

Scores per system on your gold set.

<!-- p2:begin own -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.786 | 0.779 | 0.758 |
| dense | 0.925 | 0.819 | 0.834 |
| hybrid | 0.894 | 0.835 | 0.835 |
| rerank | 0.931 | 0.963 | 0.936 |
| ablation/dense_potion | 0.869 | 0.581 | 0.643 |

40 judged queries; nDCG uses binary labels; a random ranking of the 998 documents would get recall@10 near 0.010.
<!-- p2:end own -->

The same scores per query class.

<!-- p2:begin own-classes -->
| System | Metric | plain (n=13) | jargon (n=15) | named (n=12) |
| --- | --- | ---: | ---: | ---: |
| bm25 | Recall@10 | 0.669 | 0.717 | 1.000 |
| bm25 | MRR@10 | 0.679 | 0.689 | 1.000 |
| bm25 | nDCG@10 | 0.621 | 0.684 | 1.000 |
| dense | Recall@10 | 0.923 | 0.867 | 1.000 |
| dense | MRR@10 | 0.754 | 0.732 | 1.000 |
| dense | nDCG@10 | 0.792 | 0.738 | 1.000 |
| hybrid | Recall@10 | 0.808 | 0.883 | 1.000 |
| hybrid | MRR@10 | 0.795 | 0.739 | 1.000 |
| hybrid | nDCG@10 | 0.769 | 0.760 | 1.000 |
| rerank | Recall@10 | 0.885 | 0.917 | 1.000 |
| rerank | MRR@10 | 0.923 | 0.967 | 1.000 |
| rerank | nDCG@10 | 0.893 | 0.922 | 1.000 |
| ablation/dense_potion | Recall@10 | 0.846 | 0.783 | 1.000 |
| ablation/dense_potion | MRR@10 | 0.427 | 0.542 | 0.799 |
| ablation/dense_potion | nDCG@10 | 0.541 | 0.565 | 0.849 |
<!-- p2:end own-classes -->

The same scores for the queries you wrote yourself (`hand`) and the ones a model drafted (`claude`), with the difference between the two groups and its interval.
Once both groups have queries, the table also says whether `bm25`'s lead over `dense` differs between them, and what share of each query's content words its best relevant document contains, which is stretch option 6.

<!-- p2:begin own-origins -->
| System | Metric | hand (n=20) | claude (n=20) | hand minus claude | 95% interval | Reading |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| bm25 | Recall@10 | 0.675 | 0.897 | -0.223 | [-0.450, +0.013] | not distinguishable |
| bm25 | MRR@10 | 0.700 | 0.858 | -0.158 | [-0.400, +0.075] | not distinguishable |
| bm25 | nDCG@10 | 0.681 | 0.836 | -0.155 | [-0.388, +0.076] | not distinguishable |
| dense | Recall@10 | 0.875 | 0.975 | -0.100 | [-0.250, +0.025] | not distinguishable |
| dense | MRR@10 | 0.704 | 0.935 | -0.231 | [-0.425, -0.038] | claude higher |
| dense | nDCG@10 | 0.739 | 0.930 | -0.191 | [-0.369, -0.020] | claude higher |
| hybrid | Recall@10 | 0.800 | 0.988 | -0.188 | [-0.362, -0.037] | claude higher |
| hybrid | MRR@10 | 0.704 | 0.967 | -0.263 | [-0.458, -0.079] | claude higher |
| hybrid | nDCG@10 | 0.712 | 0.958 | -0.246 | [-0.426, -0.078] | claude higher |
| rerank | Recall@10 | 0.875 | 0.988 | -0.113 | [-0.250, +0.000] | not distinguishable |
| rerank | MRR@10 | 0.925 | 1.000 | -0.075 | [-0.200, +0.000] | not distinguishable |
| rerank | nDCG@10 | 0.881 | 0.992 | -0.111 | [-0.242, -0.011] | claude higher |
| ablation/dense_potion | Recall@10 | 0.825 | 0.912 | -0.087 | [-0.287, +0.113] | not distinguishable |
| ablation/dense_potion | MRR@10 | 0.511 | 0.652 | -0.140 | [-0.380, +0.105] | not distinguishable |
| ablation/dense_potion | nDCG@10 | 0.584 | 0.701 | -0.118 | [-0.329, +0.093] | not distinguishable |

The hand and claude queries are different queries, so the interval of hand minus claude comes from resampling the queries within each group (10,000 times), not from pairing them.

Do model-written queries favor keyword search? bm25's lead over dense (bm25 minus dense, per query) on the claude queries and on the hand queries, and claude minus hand:

| Metric | Lead on claude | Lead on hand | Claude minus hand | 95% interval | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| Recall@10 | -0.077 | -0.200 | +0.122 | [-0.080, +0.325] | not distinguishable |
| MRR@10 | -0.077 | -0.004 | -0.073 | [-0.259, +0.113] | not distinguishable |
| nDCG@10 | -0.093 | -0.058 | -0.036 | [-0.218, +0.147] | not distinguishable |

Mean content-word overlap, the share of a query's content words found in its best relevant document: hand 0.51 (20 queries), claude 0.75 (20 queries).
<!-- p2:end own-origins -->

Differences between every pair of systems.

<!-- p2:begin own-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | +0.139 | [+0.044, +0.247] | 0.149 | dense higher |
| dense minus bm25 | MRR@10 | +0.040 | [-0.051, +0.135] | 0.135 | not distinguishable |
| dense minus bm25 | nDCG@10 | +0.076 | [-0.012, +0.168] | 0.131 | not distinguishable |
| hybrid minus bm25 | Recall@10 | +0.107 | [+0.025, +0.203] | 0.131 | hybrid higher |
| hybrid minus bm25 | MRR@10 | +0.056 | [-0.008, +0.123] | 0.094 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | +0.077 | [+0.015, +0.142] | 0.092 | hybrid higher |
| hybrid minus dense | Recall@10 | -0.031 | [-0.094, +0.013] | 0.080 | not distinguishable |
| hybrid minus dense | MRR@10 | +0.016 | [-0.046, +0.080] | 0.092 | not distinguishable |
| hybrid minus dense | nDCG@10 | +0.001 | [-0.053, +0.055] | 0.078 | not distinguishable |
| rerank minus bm25 | Recall@10 | +0.145 | [+0.050, +0.253] | 0.147 | rerank higher |
| rerank minus bm25 | MRR@10 | +0.183 | [+0.079, +0.300] | 0.159 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.178 | [+0.082, +0.285] | 0.148 | rerank higher |
| rerank minus dense | Recall@10 | +0.006 | [-0.031, +0.044] | 0.053 | not distinguishable |
| rerank minus dense | MRR@10 | +0.143 | [+0.063, +0.233] | 0.124 | rerank higher |
| rerank minus dense | nDCG@10 | +0.102 | [+0.036, +0.175] | 0.100 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.037 | [+0.000, +0.100] | 0.077 | not distinguishable |
| rerank minus hybrid | MRR@10 | +0.127 | [+0.048, +0.217] | 0.126 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.101 | [+0.038, +0.176] | 0.101 | rerank higher |
| ablation/dense_potion minus bm25 | Recall@10 | +0.083 | [-0.037, +0.205] | 0.175 | not distinguishable |
| ablation/dense_potion minus bm25 | MRR@10 | -0.198 | [-0.318, -0.086] | 0.168 | bm25 higher |
| ablation/dense_potion minus bm25 | nDCG@10 | -0.116 | [-0.224, -0.014] | 0.153 | bm25 higher |
| ablation/dense_potion minus dense | Recall@10 | -0.056 | [-0.138, +0.013] | 0.111 | not distinguishable |
| ablation/dense_potion minus dense | MRR@10 | -0.238 | [-0.363, -0.114] | 0.178 | dense higher |
| ablation/dense_potion minus dense | nDCG@10 | -0.192 | [-0.298, -0.090] | 0.148 | dense higher |
| ablation/dense_potion minus hybrid | Recall@10 | -0.025 | [-0.113, +0.062] | 0.122 | not distinguishable |
| ablation/dense_potion minus hybrid | MRR@10 | -0.254 | [-0.382, -0.132] | 0.181 | hybrid higher |
| ablation/dense_potion minus hybrid | nDCG@10 | -0.192 | [-0.295, -0.093] | 0.146 | hybrid higher |
| ablation/dense_potion minus rerank | Recall@10 | -0.062 | [-0.125, -0.013] | 0.090 | rerank higher |
| ablation/dense_potion minus rerank | MRR@10 | -0.381 | [-0.505, -0.262] | 0.174 | rerank higher |
| ablation/dense_potion minus rerank | nDCG@10 | -0.294 | [-0.389, -0.203] | 0.134 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-pairs -->

Which differences are distinguishable and which are not, at your gold-set size?
Do the `hand` queries and the `claude` queries tell the same story?
Did your prediction in `DECISIONS.md` prompt 1 hold?

Rerank is the only system that clearly beats the rest. On MRR@10 it beats bm25 by +0.183 [+0.079, +0.300], dense by +0.143 [+0.063, +0.233] and hybrid by +0.127 [+0.048, +0.217], and it beats all three on nDCG@10 too.

Between bm25, dense and hybrid, no MRR@10 difference is distinguishable. Their differences are 0.016 to 0.056, and 40 queries only detect 0.09 to 0.14. They do split on recall@10. Dense beats bm25 by +0.139 [+0.044, +0.247] and hybrid beats bm25 by +0.107 [+0.025, +0.203]. Hybrid also beats bm25 on nDCG@10, +0.077 [+0.015, +0.142]. So bm25 misses more relevant posts, but on MRR@10 I can't say the others put the first one any higher. On recall@10 rerank isn't distinguishable from dense, +0.006 [-0.031, +0.044], or from hybrid, +0.037 [+0.000, +0.100]. It can only pull posts up from hybrid's ranks 11 to 20, so there isn't much recall for it to add.

All four systems get 1.000 on the 12 named queries, so all of these differences come from the 28 plain and jargon ones.

The hand and claude queries mostly tell the same story, but Claude's are easier. Rerank is first on MRR@10 in both groups. On my hand queries bm25, dense and hybrid are pretty much tied, 0.700, 0.704 and 0.704. Claude's queries score higher on dense and hybrid, by -0.231 [-0.425, -0.038] and -0.263 [-0.458, -0.079] on MRR@10 (hand minus claude). On bm25, and on rerank's MRR@10, the gap isn't distinguishable. Claude's queries share 0.75 of their content words with the relevant post and mine share 0.51. bm25's lead over dense isn't distinguishably different between the two groups on any metric, so I can't say Claude's queries favor keyword search. p2 also warns that 0.963 may mean the queries are too easy. Rerank still gets 0.925 on my hand queries, so it isn't only Claude's queries (DECISIONS prompt 4).

My prediction mostly held. Rerank won. bm25 is the lowest of the four on every metric, but it's only distinguishably worse than rerank on everything, than dense and hybrid on recall, and than hybrid on nDCG. I was wrong that hybrid would land close behind rerank. Rerank beats it by 0.127, and hybrid doesn't beat dense. I said the duplicate clusters and the 188 posts under 50 words might shrink the gaps. The free systems are hard to tell apart, but nothing here shows either one is the reason.

These scores count only judged posts. Section 7 says how many unjudged posts sit in hybrid's and rerank's top 10.

---

## 5. The ablation

Change one thing and keep everything else the same.
Write your hypothesis here before you run it, in one sentence with a direction: "I expect X to raise MRR@10 on my corpus because Y."
The run file for it lives in `runs/own/ablation/`.

I expect swapping potion in for bge in dense to lower MRR@10 on my corpus. 13 of my 40 queries are plain, which should act like the shared paraphrases where bge beat potion 0.714 to 0.300, and potion’s edge on identifiers (0.571 to 0.333) should only help on the 12 named queries, which isn’t enough to make up for it. I expect the drop to be largest on plain and smallest, or reversed, on named, so the per-class table can check the mechanism and not just the headline number. The 15 jargon queries are the class I’m unsure about, since they share site words with the posts but aren’t exact ids. I already saw the shared result before writing this, so it isn’t a blind guess. The pool is also tilted against potion, since 179 of its 400 top-10 posts were never judged: that makes a potion drop weak evidence for this hypothesis, because the pool explains part of it, and a potion win strong evidence against it, because it won despite the bias.

<!-- p2:begin own-ablation -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| ablation/dense_potion minus bm25 | Recall@10 | +0.083 | [-0.037, +0.205] | 0.175 | not distinguishable |
| ablation/dense_potion minus bm25 | MRR@10 | -0.198 | [-0.318, -0.086] | 0.168 | bm25 higher |
| ablation/dense_potion minus bm25 | nDCG@10 | -0.116 | [-0.224, -0.014] | 0.153 | bm25 higher |
| ablation/dense_potion minus dense | Recall@10 | -0.056 | [-0.138, +0.013] | 0.111 | not distinguishable |
| ablation/dense_potion minus dense | MRR@10 | -0.238 | [-0.363, -0.114] | 0.178 | dense higher |
| ablation/dense_potion minus dense | nDCG@10 | -0.192 | [-0.298, -0.090] | 0.148 | dense higher |
| ablation/dense_potion minus hybrid | Recall@10 | -0.025 | [-0.113, +0.062] | 0.122 | not distinguishable |
| ablation/dense_potion minus hybrid | MRR@10 | -0.254 | [-0.382, -0.132] | 0.181 | hybrid higher |
| ablation/dense_potion minus hybrid | nDCG@10 | -0.192 | [-0.295, -0.093] | 0.146 | hybrid higher |
| ablation/dense_potion minus rerank | Recall@10 | -0.062 | [-0.125, -0.013] | 0.090 | rerank higher |
| ablation/dense_potion minus rerank | MRR@10 | -0.381 | [-0.505, -0.262] | 0.174 | rerank higher |
| ablation/dense_potion minus rerank | nDCG@10 | -0.294 | [-0.389, -0.203] | 0.134 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-ablation -->

The queries your ablation helped and hurt, against the system it varies, by reciprocal rank.
`p2 score` finds that system from a line such as `BASE = "bm25"` in your variant's file, or else from its name: `bm25_lab` varies `bm25`.

<!-- p2:begin own-ablation-queries -->
ablation/dense_potion against dense (BASE = "dense" in p2/retrievers/dense_potion.py): it helped 4 queries, hurt 18 and left 18 unchanged.

| Query | Class | Origin | dense RR | ablation/dense_potion RR | Change | Effect |
| --- | --- | --- | ---: | ---: | ---: | --- |
| h08 | jargon | hand | 0.143 | 1.000 | +0.857 | helped |
| c09 | plain | claude | 0.200 | 0.500 | +0.300 | helped |
| h11 | jargon | hand | 0.000 | 0.200 | +0.200 | helped |
| h04 | plain | hand | 0.100 | 0.200 | +0.100 | helped |
| c01 | jargon | claude | 1.000 | 0.000 | -1.000 | hurt |
| h05 | plain | hand | 1.000 | 0.000 | -1.000 | hurt |
| c13 | plain | claude | 1.000 | 0.100 | -0.900 | hurt |
| c11 | plain | claude | 1.000 | 0.167 | -0.833 | hurt |
| h09 | jargon | hand | 1.000 | 0.200 | -0.800 | hurt |
| h18 | named | hand | 1.000 | 0.250 | -0.750 | hurt |
| c04 | jargon | claude | 1.000 | 0.333 | -0.667 | hurt |
| c20 | named | claude | 1.000 | 0.333 | -0.667 | hurt |
| h02 | plain | hand | 1.000 | 0.333 | -0.667 | hurt |
| c08 | plain | claude | 1.000 | 0.500 | -0.500 | hurt |
| c14 | plain | claude | 1.000 | 0.500 | -0.500 | hurt |
| c18 | named | claude | 1.000 | 0.500 | -0.500 | hurt |
| h06 | jargon | hand | 0.500 | 0.000 | -0.500 | hurt |
| h20 | named | hand | 1.000 | 0.500 | -0.500 | hurt |
| c05 | jargon | claude | 0.500 | 0.100 | -0.400 | hurt |
| h14 | jargon | hand | 0.500 | 0.125 | -0.375 | hurt |
| h07 | plain | hand | 0.500 | 0.250 | -0.250 | hurt |
| h12 | jargon | hand | 0.333 | 0.167 | -0.167 | hurt |

RR is the reciprocal rank of the first relevant document in the top 10 (0 when none is there), the per-query value behind MRR@10; the queries at the top of each list are the ones to read.
<!-- p2:end own-ablation-queries -->

What did you change, what happened, and does the interval support the claim you want to make?
If the result is not distinguishable, say what size of effect your gold set could have seen.
Read the queries at the top of each list in the second table, and say whether your change explains them.

The one change is the embedding model in dense: potion-retrieval-32M instead of bge-small-en-v1.5. Chunks, cosine similarity and max pooling to posts stay the same.

The hypothesis held on the headline number. Potion lowered MRR@10 from 0.819 to 0.581. The difference is -0.238 [-0.363, -0.114], past the MDD of 0.178. Recall@10 dropped less, -0.056 [-0.138, +0.013], which isn't distinguishable. So potion still gets the right post into the top 10 most of the time. It just ranks it lower.

The pool could explain most of the drop, so like I said in the hypothesis, this is weak evidence. I checked the case that's worst for my hypothesis: count every one of the 179 unjudged posts in potion's top 10 as relevant. Potion would get 0.791, against dense's 0.819, and dense's top 10 was fully judged. That's a 0.028 gap with no interval, so it's not a claim either way. Per query, 11 of the 18 losses hold even in that case, and the other 7 could come from the pool. These numbers come from a side script over my local pool file, not from a p2 table.

The mechanism didn't hold up. As judged, the drop is largest on plain, 0.754 to 0.427, like I expected. But named didn't reverse. It fell from 1.000 to 0.799, a little more than jargon did (0.732 to 0.542). With 12 to 15 queries a class, plain's drop minus named's drop is -0.126 [-0.407, +0.157] (side script, unpaired bootstrap), so the order could be noise. The pool also flips it. If every unjudged post counted as relevant, potion would beat dense on plain, 0.787 to 0.754, and on jargon, 0.782 to 0.732, and only lose on named, 0.806 to 1.000. So the plain drop could be all pool, and the named drop is the part I'm surest is real.

Named couldn't reverse because dense was already at 1.000 there, so potion had no room to win. The named terms also aren't unique the way CFR section numbers are. Unicorn Meta Zoo, arbitration, Community Bulletin and SEDE each show up in 2 to 27 posts. So the term picks out a small group, and the model still has to find the one post that matches the rest of the query. Potion got the group right and the post wrong. On h20 it put "Unicorn Meta Zoo #6: Interview with Catija" above "Provide official podcast transcripts". On c18 it put "Can an anonymous user opt out of arbitration?" above the post about the promised electronic opt out.

The biggest win is h08, 0.143 to 1.000. Potion put "Don't invalidate spam or abuse flags upon review deletion" first, where dense had it at 7, under three review queue posts and three flag posts. I don't have a reason for that one. The biggest losses are c01 and h05, 1.000 to 0. On h05 potion's top 3 were about a lost answer draft, keyboard shortcuts and cookie popups on mobile, nothing about @ mentions. My guess is that averaging word vectors loses which words in the query matter. I didn't test that.

So the claim is that on my judged posts, potion in place of bge changes dense's MRR@10 by -0.238 [-0.363, -0.114]. How much of that is the pool I can't say without judging the 179 posts. The class pattern I predicted doesn't survive the pool, but the named drop does.

---

## 6. Failure analysis

Pick the queries where your best system on your own corpus failed: the relevant document is missing from the top 10, or sits far below the top.
Take at least five, and read what the system returned next to what was relevant.
Then sort the failures by cause, for example a vocabulary mismatch, near-duplicate documents, a chunk that cut the answer in half, a query that is ambiguous, or a label that was wrong, because sometimes the gold set is what failed.

The best system is rerank, at 0.963. It loses MRR on only 2 queries, h03 and h11. On 3 more (h05, h06, c07) the first relevant post is at rank 1 but a second relevant post is missing from the top 10. That's 5, and these are all of them. Hybrid rank is where the missed post sat in hybrid's ranking, and rerank only sees hybrid's top 20.

| qid | what the best system returned | what was relevant | cause | what you would try |
|---|---|---|---|---|
| h03 (plain) | 1: 371830 "Should the Disciplined and Peer Pressure badges be (partially) retired?", 2: 387025 "Why does deleting my own question tell me that I have flagged it...", 3: 312128 "My answer to my own question was deleted..." | 327788 "Let me edit my own self-deleted question", not in the top 10, hybrid rank 23 | Vocabulary. The query says removed and fixing mistakes, the post says deleted and edit. It fell just past the 20 candidates | Rerank hybrid's top 30. It worked if 327788 enters the top 10 and MRR doesn't drop on other queries |
| h05 (plain) | 1: 343178 "Are there plans to get the @ name completion working on the mobile website?" (relevant) | 335767 "Add a reply to comment button or @ autocompletion when using Chrome on Android", hybrid rank 41 | Fusion. Dense had it at 2, but bm25 found no matching word, so it got into RRF from dense alone and fell to 41. It's a duplicate of 343178 | Take bm25's top 20 and dense's top 20 as the candidates, not the fused top 20. It worked if 335767 enters the top 10 |
| h06 (jargon) | 1: 366329 "Profile images are pushed to next line if tags extend too far to the right" (relevant) | 366409 "Why are some user profile images showing up on the left side in the list of questions?", hybrid rank over 100 | Duplicate with a different symptom. It's linked as a duplicate of 366329, but its text never mentions tags or wrapping, and its screenshot is gone | Reread the label against my rule. If it holds, only the duplicate links could find it, and it worked if pulling in duplicates puts it in the top 10 |
| h11 (jargon) | 1: 388030 "Improving the copy in the close modal and post notices, 2023 edition", 2: 315724 (relevant) | 315724 "\"That solved my problem\" doesn't make sense if the target question is unanswered" and 328744 "How about an option to choose that your question is a duplicate even if it doesn't have an answer?", hybrid ranks 15 and 67 | A long post on the same topic. 388030 is a 1,955 word announcement about close wording that mentions duplicate targets needing answers. 328744 is a duplicate of 315724 that says duplicate and no answer where the query says dupe and zero answers | Reread the 388030 label. Expanding site slang like dupe for 328744, which worked if 328744 moves into hybrid's top 20 |
| c07 (jargon) | 1: 391952, 2: 392485, 3: 392313, all relevant | 392187 "Achievement link goes to wrong site", hybrid rank 21 | Duplicate group. Seven posts about one bug, four judged relevant, and this one says achievement drop down where the query says rep notification. It fell just past the 20 candidates | Rerank the top 30, or pull in the duplicates of whatever ranks first. It worked if 392187 enters the top 10 without pushing the other three out |

Rerank only got the order wrong once, on h11, and I haven't reread the label on 388030, so that one could be the gold set and not the reranker. All five posts it missed were outside hybrid's top 20, so the reranker never saw them. That's the same ceiling as on the shared corpus. Four of the five missed posts are the second post in a duplicate pair or group, where the system found one telling of the complaint but not the other. For a feedback search that's the mild kind of miss, because the complaint still shows up, but it undercounts how many people hit it. Two of them sat just outside, h03 at 23 and c07 at 21, so a bigger candidate list would probably catch them, at a higher cost per call.

---

## 7. Cross-corpus comparison

The two tables to compare are the shared-corpus scores in section 1 and your own-corpus scores in section 4, with their intervals.
If you want them side by side, copy the rows you need into a table here and say that you copied them.

Did the winner change between the shared corpus and yours?
Why, or why not: what is different about the two collections (document length, vocabulary, identifiers, near-duplicates, how the queries were written), and which of your explanations did you test and which are guesses?
Say what 20 queries on one side and your gold-set size on the other cannot support.

MRR@10, copied from the tables in sections 1 and 4:

| System | shared practice (20 queries) | own (40 queries) |
| --- | ---: | ---: |
| bm25 | 0.507 | 0.779 |
| dense | 0.562 | 0.819 |
| hybrid | 0.471 | 0.835 |
| rerank | 0.750 | 0.963 |
| dense_potion | 0.475 | 0.581 |

The winner didn't change. Rerank is first on both corpora, and it beats hybrid on both: +0.279 [+0.128, +0.441] on the shared corpus and +0.127 [+0.048, +0.217] on mine. What changed is the order under it. On the shared corpus hybrid was the lowest of the three free systems, and on mine it's the highest. But none of those three differ on MRR@10 on either corpus. On mine, dense and hybrid both beat bm25 on recall@10, +0.139 [+0.044, +0.247] and +0.107 [+0.025, +0.203], and hybrid beats bm25 on nDCG@10, +0.077 [+0.015, +0.142].

Tested: word overlap. I used p2 score's measure, the share of a query's content words found in its best relevant document, run on both corpora with a side script. The shared paraphrase queries share 0.11 of their words, and bm25 got 0 on them. My plain queries were meant to play that role, but they share 0.51, and bm25 gets 0.679. So my plain queries aren't real paraphrases. On the shared corpus each first stage system had a class it failed (dense 0.333 on identifiers, bm25 0 on paraphrases). My read is that RRF kept averaging a hit with a miss there, which I didn't test. On mine bm25 and dense both get every named query, and bm25 still misses about a third of plain queries (recall@10 0.669) but never a whole class, so fusing them costs nothing I can measure. Hybrid minus dense on recall@10 is -0.031 [-0.094, +0.013], though fusion did lose a post on h05 (section 6).

Compared, not tested: identifiers. My named class is the closest thing to CFR section numbers, but dense scores 1.000 on it, where it got 0.333 on identifiers. My guess is that named terms here are ordinary words like podcast or arbitration that the embedding model knows, and codes like 75.403 aren't. I didn't test that part.

Checked roughly: document length. The median document is 68 words on the shared corpus and 107 on mine, title included, and most of both fit in one 300 word chunk. They're not different enough for me to think length explains anything.

Counted on mine only: near duplicates. Four of the five posts rerank missed on my corpus are a second post in a duplicate group (section 6). I built my corpus to have duplicate groups and didn't count them on the shared corpus, so I can't say it's a failure only mine has.

Partly tested: how the queries were written. Every own query was written with one post in mind, and Claude read its post first. Claude's queries share 0.75 of their words with the relevant post and mine share 0.51, and dense scores higher on Claude's, a difference of -0.231 [-0.425, -0.038] (hand minus claude). p2 score also warns that rerank's 0.963 means the queries may be too easy. So my scores are probably higher than these systems would get on real searches. My guess is that's most of why everything scores higher on my corpus, more than anything about informal text.

What this can't support: no interval here compares the two corpora. They have different queries and different documents, so "rerank gains less on my corpus" isn't a claim. Hybrid is already near the top there, so there's less room. Between bm25, dense and hybrid, the 20 shared queries only detect MRR@10 differences of 0.19 to 0.41, and my 40 detect 0.09 to 0.14. Hybrid has 74 unjudged posts in its top 10 on my corpus and rerank has 131, none at rank 1 (side script over my local pool file). Unjudged counts as not relevant, so if their own unjudged posts got judged, their recall and MRR could only go up. nDCG could go either way, since a new relevant post also raises the best possible score.

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
| Answers file | Judged by Claude | supported | partly | not | Labeled by you | Labeled by both | Agree | 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 14 | 13 | 1 | 0 | 14 | 14 | 12 of 14 (86%) | [0.601, 0.960] |
| rerank | 11 | 9 | 2 | 0 | 11 | 11 | 9 of 11 (82%) | [0.523, 0.949] |
| all files |  |  |  |  |  | 25 | 21 of 25 (84%) | [0.653, 0.936] |

Claude's verdict (rows) against yours (columns), over the 25 claims you both labeled:

| Claude | you: supported | you: partly | you: not | Total |
| --- | ---: | ---: | ---: | ---: |
| supported | 19 | 3 | 0 | 22 |
| partly | 1 | 2 | 0 | 3 |
| not | 0 | 0 | 0 | 0 |
| total | 20 | 5 | 0 | 25 |

Agree is the share of the claims you both labeled where Claude's verdict is yours, with a Wilson 95% interval.
<!-- p2:end stretch-judge -->

1. Option 2, the claim level faithfulness check.

2. Before the judge ran, I labeled all 25 claims from both answers files myself.
I read each claim, its quote and the chunk it cites.
My labels are in `answers/shared/rerank.calibration.tsv` (11) and `answers/shared/hybrid.calibration.tsv` (14).
Then Claude judged every claim, one call each, with `prompts/judge.txt` unchanged.
Its verdicts are in `answers/shared/rerank.judged.json` and `answers/shared/hybrid.judged.json`, with traces in `traces/judge-rerank.jsonl` and `traces/judge-hybrid.jsonl`.

3. `stretch-judge`, above.

4. The table says the judge agrees with me on 21 of 25 claims (84%), with a Wilson interval of [0.653, 0.936].
But 3 of the 25 are the same claim counted twice.
a03-c1, a05-c1 and a08-c1 are identical in both answers files, same claim, quote and chunk.
On the 22 distinct claims it agrees on 18 (82%), with an interval of [0.615, 0.927].
That's not much better than a judge that does nothing.
I called 17 of the 22 supported, so always answering supported would already get 77%.
Cohen's kappa, which corrects for that, is about 0.40.
So "the judge is right 84% of the time" claims way more than this shows.

The disagreements say more than the headline.
On the 17 distinct claims I called supported, it agreed on 16.
On the 5 I called partly, it agreed on only 2 and called the other 3 supported.
That's the direction that matters for a faithfulness check, since it means partly supported claims get through.
But 5 claims is way too few to put a number on it.
One of those 3 is also a difference in evidence, not just a judge miss.
On rerank a03-c2 I went by conditions in the section's lead-in, and the judge only ever sees the quote.
Read against the quote alone, supported is a fair call.

Two of the disagreements, read closely.
hybrid a07-c1 and a07-c2 say the mid-axle rule applies to "surface" and "underground" metal and nonmetal mines.
The quote has the rule word for word but says nothing about surface or underground.
The judge called both supported.
For a07-c1 its reason was "the quote matches the claim's text verbatim regarding mid-axle height requirement".
So it checked the part that matched and skipped the part that got added.
It isn't consistent about it either.
It called rerank a07-c3 partly for the same kind of added scope, because the quote doesn't "specify that it applies to underground mines".
rerank a07-c1 goes the other way.
I called it supported, since it's identical to 56.9300(a).
The judge said partly because the quote "does not state any specific height requirement, which is what the question asks".
That's grading the claim against the question, not against the quote, and the prompt doesn't ask for that.

This says nothing about claims that aren't supported at all, since neither of us labeled any `not`.
It also says nothing about another corpus or another answer prompt.
And it's one person's labels, so it's agreement with me, not with the truth.
I also saw the cited chunk and the judge didn't, so we weren't always judging from the same evidence.

5. Next I'd tighten `prompts/judge.txt`.
The judge should check every part of the claim, scope words like surface or underground included, and compare the claim only to the quote, not to the question.
That would be tuning on my own labels, so I'd keep 21 of 25 as the before number and test on a fresh set of claims from new answers.
It worked if the judge catches more of my partly claims without starting to mark my supported ones partly.
The new set needs enough claims for the interval to actually move, and no repeats between files.
Matching how I read claims would also need the judge to see the cited chunk, and `p2 judge` only sends the question, claim and quote.

### Cost and latency (option 3)

The Claude calls, tokens and seconds in every trace you committed, and what a cheaper system or answers file saves against what it loses.

<!-- p2:begin stretch-cost -->
Every trace in traces/ that records a Claude call:

| Trace | System | Spans | Claude calls | Saved | Input tokens | Output tokens | Seconds | Input per span | Output per span | Seconds per span |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| traces/answers-hybrid.jsonl | hybrid | 12 | 12 | 2 | 331,299 | 5,076 | 80.6 | 27,608 | 423 | 6.7 |
| traces/answers-rerank.jsonl | rerank | 12 | 24 | 4 | 967,827 | 13,433 | 197.4 | 80,652 | 1,119 | 16.5 |
| traces/judge-hybrid.jsonl | judge | 14 | 14 | 3 | 387,384 | 2,257 | 64.0 | 27,670 | 161 | 4.6 |
| traces/judge-rerank.jsonl | judge | 11 | 11 | 2 | 342,382 | 1,589 | 48.2 | 31,126 | 144 | 4.4 |
| traces/own-own-rerank.jsonl | rerank | 40 | 40 | 2 | 640,073 | 11,799 | 396.3 | 16,002 | 295 | 9.9 |
| traces/shared-practice-rerank.jsonl | rerank | 20 | 20 | 0 | 881,875 | 13,240 | 190.8 | 44,094 | 662 | 9.5 |
| traces/shared-test-rerank.jsonl | rerank | 40 | 40 | 2 | 752,743 | 18,096 | 349.0 | 18,819 | 452 | 8.7 |

A span is one query of a run, one question of an answers file, or one claim of a judged file. A saved reply costs nothing now, so it counts the tokens and the seconds of the call that made it.

Every pair of systems on the same queries where at least one calls Claude, the one with fewer Claude input tokens per query first:

| Cheaper minus dearer | Queries | MRR@10 difference | 95% interval | Input tokens saved per query | Seconds saved per query | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| shared practice: bm25 minus rerank | 20 | -0.243 | [-0.476, -0.010] | 44,094 | 9.5 | rerank higher |
| shared practice: dense minus rerank | 20 | -0.188 | [-0.392, +0.017] | 44,094 | 9.5 | not distinguishable |
| shared practice: hybrid minus rerank | 20 | -0.279 | [-0.441, -0.128] | 44,094 | 9.5 | rerank higher |
| shared practice: dense_potion minus rerank | 20 | -0.275 | [-0.463, -0.108] | 44,094 | 9.5 | rerank higher |
| own: bm25 minus rerank | 40 | -0.183 | [-0.300, -0.079] | 16,002 | 9.9 | rerank higher |
| own: dense minus rerank | 40 | -0.143 | [-0.233, -0.063] | 16,002 | 9.9 | rerank higher |
| own: hybrid minus rerank | 40 | -0.127 | [-0.217, -0.048] | 16,002 | 9.9 | rerank higher |

The difference is the cheaper system's score minus the dearer one's, with its paired interval; the savings count Claude calls only, so a system that makes none saves all of the other's.

Every two answers files on the same questions, the one with fewer input tokens per question first:

| Cheaper minus dearer | Questions | Passing share difference | 95% interval | Input tokens saved per question | Seconds saved per question | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| shared: hybrid minus rerank | 12 | -0.083 | [-0.250, +0.000] | 53,044 | 9.7 | not distinguishable |

A question passes when its `p2 verify` line is a PASS: every quote is in a chunk that was retrieved, and the question is declined exactly when it should be.

Systems that do not call Claude, from traces/retrieval/ on the machine that last ran `p2 score` (git ignores that folder, so `p2 check` does not compare this part):

| Trace | System | Queries | Seconds | Milliseconds per query |
| --- | --- | ---: | ---: | ---: |
| traces/retrieval/own-own-ablation-dense_potion.jsonl | dense_potion | 40 | 0.04 | 0.9 |
| traces/retrieval/own-own-bm25.jsonl | bm25 | 40 | 0.05 | 1.3 |
| traces/retrieval/own-own-dense.jsonl | dense | 40 | 0.42 | 10.4 |
| traces/retrieval/own-own-hybrid.jsonl | hybrid | 40 | 0.35 | 8.7 |
| traces/retrieval/shared-practice-bm25.jsonl | bm25 | 20 | 0.04 | 1.9 |
| traces/retrieval/shared-practice-dense.jsonl | dense | 20 | 0.20 | 10.0 |
| traces/retrieval/shared-practice-dense_potion.jsonl | dense_potion | 20 | 0.05 | 2.5 |
| traces/retrieval/shared-practice-hybrid.jsonl | hybrid | 20 | 0.29 | 14.6 |
| traces/retrieval/shared-test-bm25.jsonl | bm25 | 40 | 0.10 | 2.5 |
| traces/retrieval/shared-test-dense.jsonl | dense | 40 | 0.36 | 9.0 |
| traces/retrieval/shared-test-hybrid.jsonl | hybrid | 40 | 0.55 | 13.8 |
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
