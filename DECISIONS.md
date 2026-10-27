# Decision log

Your methods section, in your own words.
About one to two pages in total.

Answer these as you go, not the night before it is due.
Each answer is easier to write while the decision is still fresh, and prompt 1 only works if you write it before you see your own-corpus numbers.
Specifics beat polish: a short, honest answer with a number in it is worth more than a long vague one.

Each prompt ends with a marker line.
Replace that line with your answer.
`uv run p2 check` reports a marker as unfinished work, and `uv run p2 check --final` fails while any marker is left, so a finished log is part of being done.

Please do not let the agent write these for you.
These answers are about what you chose and what you knew, and the agent cannot know that.
Prompt 3 in particular only works in your own words.

---

## 1. Why this corpus, and what you expected

Why did you pick the corpus you used in stage 2, and why does it belong to a field or a question you care about?
Then say what you expected before you measured anything: which of `bm25`, `dense`, `hybrid` and `rerank` do you think will win on it, and which will do worst, and why?

Commit this answer before your first `uv run p2 score` on the own corpus.
Git history then shows that the expectation came first, which is what lets it be wrong in a way that teaches you something.
If you were surprised later, say so in prompt 4 or in EVAL.md; do not come back and rewrite this one.

### Answer

I’m using about 1,000 posts from Meta Stack Exchange, which are users’ feature requests, bug reports and complaints about the platform. I first planned arXiv abstracts on customer-feedback NLP, but switched before running anything, since these are actual feedback and not papers about it. That fits the role I’m aiming at, which is voice-of-customer and NLP on feedback text. The posts are CC BY-SA 4.0, so I can republish them with attribution under the same license. The median post is about 95 words, so judging relevance is quick.

I expect rerank to win again. On the CFR it put the right section first every time it was in hybrid’s top 20. The catch is the same as before: it can’t fix anything hybrid didn’t find.

I expect bm25 to do worst overall. A named query (a feature or site name) should work like a CFR identifier, but on the CFR bm25 scored 0 when the wording didn’t match, and plain-language queries will do that. Dense should do better here than on the CFR, since this is prose.

I expect hybrid to land close behind rerank, because bm25 and dense should agree more often on prose, so RRF should bury less.

What I’m least sure about is that about a third of the corpus is duplicate clusters, the same complaint in different words, and 188 posts are under 50 words. That makes picking the one right post harder for every system, so the gaps between them might shrink.

---

## 2. A fork in the road

Name one real design choice where you could have gone two ways: the chunk size, the embedding model, how the two systems are fused, how many documents the reranker sees, a sentence in `prompts/answer.txt`, how you cleaned the corpus.

Say which you picked, what the alternative was, and what you gave up by not taking it.
If you measured both, give both numbers.
If you rejected the alternative without measuring it, say why that was a fair call, and what it cost you in time, tokens or complexity.

"There was no alternative" is not an answer.
Find the fork.

### Answer

I went with bge-small-en-v1.5 for `dense`.
The other option was potion-retrieval-32M, a static model: a word's vector is a table lookup and a text's vector is pretty much the average of its words, so it never sees word order or context.
I ran both on the 20 shared practice queries.

- MRR@10: bge 0.562, potion 0.475. The difference is -0.088 [-0.335, +0.153], so not distinguishable, and the MDD for that pair is 0.349.
- Recall@10: bge 0.558, potion 0.533. nDCG@10: bge 0.480, potion 0.432.
- Encoding the corpus: bge took 115 seconds, potion 0.4 seconds. Per query (median): bge 9.9 ms, potion 2.2 ms.

What I gave up is speed.
At this size that barely matters: the 115 seconds happens once because the vectors get cached, and 10 ms a query is nothing next to a Claude call.
On a much bigger corpus, or one that changes all the time, it would matter a lot more.

Why bge when the gold set can't tell them apart: it comes down to the job dense does inside hybrid.
bm25 already finds every identifier query (recall@10 1.000) and none of the paraphrase ones (0.000).
Potion's edge was on identifiers (MRR@10 0.571 vs bge's 0.333), which bm25 already covers.
bge's edge was on paraphrases (0.714 vs 0.300), which is exactly the gap dense is there to fill.
That's 7 queries per class with no interval, so it's a reason, not proof.

I'll test it again in the ablation on my own corpus.
I've already seen these numbers, so that prediction isn't blind, and it'll say so.

---

## 3. Where you overruled the agent

One time Claude suggested, wrote or claimed something and you did not take it.
It might be a relevance judgment you disagreed with, a retriever it called finished when a run file showed otherwise, a number it summarized wrongly, or a license it said was fine.

What did it do?
How did you notice?
What did you do instead?

If it genuinely never happened, say so plainly, and then say what you would have had to check in order to notice.
Being honest here costs you far less than a story you cannot defend when you record your video.

### Answer

It was my own query h18, “weekly Sunday refresh stalled for Unix and Linux on SEDE”. To build the pool, Claude guessed from titles which post each of my hand queries was about. For h18 it guessed 347083, “No new data on data.stackexchange.com”. I read it, and it’s about Stack Overflow data, not Unix and Linux. 347039, “SEDE appears to be partially-refreshed”, was also in the pool, and it’s the one that names U&L. I marked 347039 relevant and 347083 not. I only caught it because I read the bodies and not the titles. The guess only decided what went into the pool, so it changed no score, but if I’d trusted it, h18 would have scored about 0.11 on dense instead of 1.0. EVAL section 3 says the guess was wrong.

---

## 4. A number you do not trust

Pick one number in `EVAL.md` that you do not fully trust, and say why.
It could be a mean over a small query class, a difference whose interval includes zero, a verified share of 100%, a score on a gold set you wrote yourself, or a result you got only once.

What would have to be true for you to trust it?
Did you do anything to test it, and what did that show?

### Answer

Rerank’s 0.963 MRR@10 on my corpus. It’s nearly the max, and p2 warns that 0.95 or higher may mean the queries are too easy. Every query was written with one post in mind, and Claude’s share 0.75 of their words with that post, against 0.51 for mine. Real users haven’t seen the post they’re looking for. I split by origin: on my 20 hand queries rerank gets 0.925, and the gap to Claude’s 1.000 isn’t distinguishable (-0.075 [-0.200, +0.000]). So mine are easy too. To trust it I’d want queries written without seeing the target, like titles of posts closed as duplicates, taken from the raw dump.

---

## 5. What is still wrong

One thing in your system, your corpus or your gold set that is not right, not finished, or that you do not fully understand.

What would you do next, and how would you find out whether it matters?
Name the file, the query or the document where someone could look.

### Answer

The pool is incomplete. Hybrid, rerank and potion were never pooled, and unjudged counts as not relevant. Potion has 179 unjudged posts in its top 10, which hits the ablation hardest: its drop is -0.238 [-0.363, -0.114], but if every unjudged post were relevant it would get 0.791 against dense’s 0.819. So I can’t say how much of the drop is the model. Next I’d judge the unjudged posts potion ranked above its first relevant one, from its run file in runs/own/ablation/, then rescore. It matters if potion’s interval stops excluding zero.