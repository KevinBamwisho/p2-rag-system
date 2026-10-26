# The own corpus: Meta Stack Exchange questions

This folder holds 998 questions from Meta Stack Exchange (https://meta.stackexchange.com), the site where Stack Exchange users report bugs, ask for features and discuss how the network works.
Each file in `docs/` is one question, named by its post id. `manifest.tsv` gives each one's source URL, its license and its author.

## License

The text is licensed under CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
It stays under that license here, and anything shared from it has to stay under it too.

- The archive.org copy of the data dump says: "All user content contributed to the Stack Exchange network is cc-by-sa 4.0 licensed, intended to be shared and remixed." (https://archive.org/details/stackexchange)
- Stack Exchange's licensing page says: "Content contributed on or after 2018-05-02 (UTC) is distributed under the terms of CC BY-SA 4.0" (https://meta.stackexchange.com/help/licensing). Every question here was posted on or after that date, and the dump records CC BY-SA 4.0 on each one.

## Attribution

Every question comes from Meta Stack Exchange. In `manifest.tsv`, the `source` column links the original question, and the `notes` column gives the author's display name and a link to their profile.
The authors don't endorse this project.

## Where the text comes from

It comes from `meta.stackexchange.com.7z` in the archive.org item `stackexchange`, dated 2024-04-06 (https://archive.org/download/stackexchange).
The questions are tagged bug, feature-request, support or discussion, were posted between 2018-05-02 and 2024-03-28, and were sampled from the dump. EVAL.md section 3 explains how.

## What was changed

The text was modified from the original posts:

- Each post's HTML was converted to plain text. Code is kept as text.
- Images were dropped (492 posts had at least one).
- Link targets were dropped and only the link text kept (807 posts). This includes links that credited sources the authors quoted.
- Ordered list numbers, bullet marks and strikethrough were lost (72 posts had numbered lists, 13 had strikethrough).
- Tables were flattened to plain rows (3 posts had HTML tables). Runs of spaces were squeezed to one, so tables typed inside code blocks lost their column alignment, as in 337458.
- Superscripts and subscripts were flattened onto the line, so a footnote number sticks to the word before it, as in "reply-able1" (40 posts).
- Tags, answers, comments, votes and edit history were left out. Only the title and the question body are here.
- Some posts quote short passages from other sources, such as news sites, the Stack Overflow blog and Stack Exchange's help center. Those quotes were left as the authors posted them.
