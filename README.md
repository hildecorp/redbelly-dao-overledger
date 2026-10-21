# Could Redbelly connect to Quant Overledger? (TASK-29)

Live site: https://overledger.vercel.app

A feasibility report on whether Redbelly Network could connect to Quant's Overledger, what that would take, and what it could offer institutions. It uses public sources only. Redbelly and Quant have no announced partnership or talks, and the report does not suggest otherwise.

## Deliverables

| Deliverable | Where |
|---|---|
| The report, as PDF and Word | `public/downloads/redbelly-overledger-feasibility-report.pdf` and `.docx`, also linked from every page of the site |
| The report as a website: key findings on the home page, then 11 chapters with 7 diagrams | https://overledger.vercel.app, built into `public/` |
| Short community summary: a few paragraphs and a 6 post X thread | `COMMUNITY-SUMMARY.md`, the last chapter of the report, and https://overledger.vercel.app/chapters/community-summary (with copy buttons) |
| Source list, with a link and the exact quoted words for every factual claim | `SOURCES.md`, the end of the PDF and Word file, and https://overledger.vercel.app/sources |

## Short answer

| Question | Answer | Status |
|---|---|---|
| Could the Overledger Gateway reach Redbelly, for reading data and sending signed transactions? | Possibly, but unconfirmed: Redbelly fits the technical self-serve tests, but Overledger describes self-serve as for public permissionless networks, and writing to Redbelly needs a credential. Untested | Analysis |
| Can Redbelly join the Fusion Rollup (deposits, unified balances, cross-chain messages)? | Not possible yet, as far as public sources show | Analysis |
| Do Receptor credentials and Tokeniser rules travel with an asset to another chain? | No, not by themselves | Analysis |
| Is there any agreement between Redbelly and Quant? | None announced | Confirmed |

## How the report keeps facts, analysis and unknowns apart

Every finding paragraph carries one label (chapter intros and figure captions summarise the cited facts around them):

- **Confirmed**: stated in a public source, which is linked and quoted.
- **Tested**: we ran the call ourselves on 15 October 2026. The log is in `evidence/tests/`.
- **Analysis**: our reasoning from the confirmed facts it cites.
- **Unknown**: not answered by any public source we found.

Chapter 9 lists everything that is not possible yet or unknown. A short "Plain words" list on the home page, and near the start of the PDF and Word file, explains the technical terms in one or two lines each.

## The website

| Address | Page |
|---|---|
| `/` | The short answer, the four key findings, how to read the labels, plain words for the technical terms, and the list of chapters with reading times |
| `/chapters/why-now` to `/chapters/community-summary` | One page per chapter, 11 in all. Each shows "Chapter 3 of 11" with a progress bar, and Previous and Next at the end |
| `/sources` | Every source in groups, the exact words relied on, where each is used, and a filter |
| `/evidence/` | The saved copy of every source page, `manifest.json` with the SHA-256 of each, and the logs of our own tests |

- Every chapter is a real page with its own address, so it can be linked, shared and read without JavaScript. Addresses have no `.html`.
- Under the header of each chapter, a slider shows the position ("Chapter 3 of 11"); drag or tap it to open any chapter.
- The side menu has two entries, Key findings and Chapters. Chapters opens a list of all 11 chapters, with the open chapter boxed in red.
- The bar at the bottom of the screen gives the chapter list, Previous and Next, the source list and back to top. On a chapter page the left and right arrow keys also go to the previous and next chapter.
- A citation such as S5 opens the source list at S5 and marks it with a red box. Hovering a citation shows the quoted words first.
- Status labels follow the Task Board brand kit: a small dot plus a monospace label, on the site and inside the diagrams.
- Diagrams are drawn in SVG, a wide version for desktop and a narrow one for phones, and each can open full screen.
- The tab icon is the Task Board icon, and the header carries the DAO logo, both from the brand kit.

## One source for everything

| Path | What it holds |
|---|---|
| `content/report.json` | Every word of the report and the community summary. Claims cite facts as `{fact-id}` |
| `content/facts.json` | 106 facts, each with its source and the exact words quoted from it |
| `content/sources.json` | 38 sources: publisher, title, link and snapshot file |
| `content/diagrams.json` | The 7 diagrams: title, caption with citations, and the exact wording each one may show |
| `public/diagrams/` | The diagrams as hand-written SVG |
| `evidence/snapshots/` | A text snapshot of every source page as it read on 15 October 2026 |
| `evidence/tests/` | Output of our own JSON-RPC calls to Redbelly and of the calls to the public Overledger API |
| `evidence/manifest.json` | Address, capture time (UTC) and SHA-256 of every evidence file. The build also publishes `evidence/` on the site |
| `scripts/build.py` | Builds the website, the PDF, the Word file, `SOURCES.md` and `COMMUNITY-SUMMARY.md` |
| `scripts/site.css`, `scripts/site.js`, `scripts/print.css` | Website style and behaviour, and the print style used for the PDF |
| `scripts/render_diagram.py` | Renders one diagram to PNG and measures it: smallest text size, overlapping text, text outside its box |
| `scripts/check.py` | The quality gate, below |
| `scripts/snap_sources.py` | Recaptures every source page and rewrites the manifest |
| `scripts/serve.py` | Serves `public/` locally with the same clean addresses as the live site |
| `vercel.json` | Vercel settings: `public/` is the web root, clean addresses, no build step |

## Check it

```
python3 scripts/check.py            # must end with RESULT: PASS
python3 scripts/check.py --online   # also confirms every source link answers today
```

`check.py` fails if:

- a quote is not found word for word in its snapshot, or a snapshot changed after capture (SHA-256)
- a labelled paragraph cites no source, a citation points to an unknown fact, or a source is never cited
- any sentence about Redbelly or Quant suggests a partnership, talks, plans or an agreement
- the text uses investment language or hype words, an en dash, an em dash or an emoji
- any deliverable contains a personal name, handle or personal website listed in the local, git-ignored `.credit-names` and `.credit-links` files (this scan runs only where those private lists exist; the "made by" and Word property checks always run), or the Word file names a tool or a person in its properties
- an X post is over 280 characters
- the PDF, the Word file or the website does not contain the current text of every paragraph, or the source list misses a quote
- a diagram breaks the SVG rules (brand palette only, prefixed ids, title and description, no styles, images or outside links), or its words break the wording rules above
- the website loads anything from another domain
- a word drawn in a diagram is not in that diagram's approved wording in `content/diagrams.json` (this catches typos)
- a link inside the website opens nothing, points to a missing anchor, or uses an address ending in `.html`

To repeat the RPC test, run `eth_chainId` and `net_version` against `https://governors.mainnet.redbelly.network` (see `evidence/tests/rpc-check.txt`).

## Rebuild and preview

```
pip install playwright python-docx pillow
python3 -m playwright install chromium
python3 scripts/build.py
python3 scripts/check.py
python3 scripts/serve.py            # then open http://localhost:8000
```

Playwright needs Chromium. `pdftotext` (poppler) is used by the check.

## Deploy

The site is static and deploys on Vercel straight from this repository. `vercel.json` sets `public/` as the web root with no build or install step, and turns on clean addresses, so `/sources` serves `public/sources.html`. Nothing outside `public/` is served. Each push to the main branch redeploys the site.

## Licences and credits

- Fonts: Be Vietnam Pro and JetBrains Mono, SIL Open Font License 1.1 (`licenses/`), self-hosted from `public/fonts/`.
- Logo and icon: the Redbelly DAO logo and the Task Board icon, from the Task Board brand kit (taskboard.redbellydao.network/brand).
- Snapshots in `evidence/` are verbatim copies of third-party pages, kept only so every quote can be checked. They keep the source's own punctuation. The one exception: because the Task Board does not allow personal credit inside a deliverable, contributor names and links in two copies (the TASK-08 guide and the TASK-29 brief) were replaced with [name removed] and [link removed]. Each file's header and `evidence/manifest.json` say so.
- Diagrams are drawn for this report in SVG. No third-party images are used.
