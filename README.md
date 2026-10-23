# Could Redbelly connect to Quant Overledger? (TASK-29)

Live site: https://overledger.vercel.app

A feasibility report on whether Redbelly Network could connect to Quant's Overledger, what that would take, and what it could offer institutions. It uses public sources only. Redbelly and Quant have no announced partnership or talks, and the report does not suggest otherwise.

## Short answer

| Question | Answer | Status |
|---|---|---|
| Could the Overledger Gateway reach Redbelly, for reading data and sending signed transactions? | Possibly, but unconfirmed: Redbelly fits the technical self-serve tests, but Overledger describes self-serve as for public permissionless networks, and writing to Redbelly needs a credential. Untested | Analysis |
| Can Redbelly join the Fusion Rollup (deposits, unified balances, cross-chain messages)? | Not possible yet, as far as public sources show | Analysis |
| Do Receptor credentials and Tokeniser rules travel with an asset to another chain? | No, not by themselves | Analysis |
| Is there any agreement between Redbelly and Quant? | None announced | Confirmed |

## Deliverables

| Deliverable | Where |
|---|---|
| The report, as PDF and Word | `public/downloads/redbelly-overledger-feasibility-report.pdf` and `.docx`, linked from every page of the site |
| The report as a website: the short answer and key findings on the home page, then 11 chapters with 7 diagrams | https://overledger.vercel.app |
| Community summary: a few paragraphs and a 6 post X thread | `COMMUNITY-SUMMARY.md`, the last chapter of the report, and https://overledger.vercel.app/chapters/community-summary (with copy buttons) |
| Source list, with a link and the exact quoted words for every factual claim | `SOURCES.md`, the end of the PDF and Word file, and https://overledger.vercel.app/sources |

## How the submission meets the brief

The scoring rubric and the failure criteria of TASK-29, and where each one is answered.

| Rubric item | Where it is met |
|---|---|
| 1. Deliverable completeness | All three deliverables above, each in more than one format |
| 2. Quality benchmarks | See the four benchmarks below |
| 3. Technical accuracy | Facts about Overledger and Redbelly are quoted word for word from their own documentation. We ran the JSON-RPC and Overledger API calls ourselves (logs in `evidence/tests/`). Checks 11 and 12 confirm that the chain IDs and test dates in the report match those logs |
| 4. Documentation quality | This file, and a description at the top of every script in `scripts/` |
| 5. Test coverage and verification | `scripts/check.py` runs 12 checks, also on GitHub Actions for every push. Every source page is saved with its SHA-256, and every quote is matched against that saved copy |
| 6. Failure criteria | See the failure criteria below |
| 7. Overall standard | The PDF, the Word file and the website are built from the same content files, so the three always say the same thing |

| Quality benchmark | How |
|---|---|
| Every factual claim has a working source link | Every claim cites a fact, and every fact quotes its source. `check.py --online` asks every link whether it answers today. `scripts/archive_sources.py` adds an Internet Archive copy next to each link |
| Clear separation of confirmed, analysis and unknown | Every finding paragraph carries one of four labels (below). Chapter 9 gathers everything that is not possible yet or unknown |
| A non technical reader can follow the main findings | The short answer comes first, then "Plain words" (10 technical terms in one or two lines each), short chapters with a reading time, and diagrams with captions |
| Neutral tone | Checks 3 and 4 fail the quality gate on partnership wording, price talk, hype words and investment language |

| Failure criterion | How it is avoided |
|---|---|
| Wording that suggests a partnership, talks or plans between Redbelly and Quant | Check 3 reads every sentence we wrote, including the words inside the diagrams. The footer of the home page, every chapter and the source list repeats that there is no announced partnership |
| A factual claim without a source, or with a source that does not support it | Check 2: every labelled paragraph cites a fact. Check 1: every quote is found word for word in the saved copy of its page |
| Wrong technical claims about Redbelly or Overledger | Claims are quoted from the projects' own documentation, our tests are logged in full, and checks 11 and 12 compare the report with those logs |
| Price talk, investment advice or promises of returns | Check 4 |
| AI generated text without checking, made up facts or sources | Every one of the 107 facts is a verbatim quote found in a saved copy of a real page (check 1), and every one of the 38 sources is cited (check 2) |
| Personal credit inside the deliverable | Check 5 scans every file for the names and links in two private, git-ignored lists, and checks that the Word file properties name no tool or person |

## Check any claim in two minutes

Take the sentence "Mainnet is chain ID 151" in chapter 4, Redbelly facts that matter.

1. Its citation reads S16. Open it: https://overledger.vercel.app/sources#s16 shows the source (Vine, the Redbelly Network developer portal, "Redbelly Network environments") and the exact words relied on, which end in "Chain ID: 151".
2. "Saved copy" under the source opens the text of that page as it read on 15 October 2026: `evidence/snapshots/vine-redbelly-network-environments.txt`.
3. The copy has not changed since: `sha256sum evidence/snapshots/vine-redbelly-network-environments.txt` gives `31cf0f92a66c35a0ea7998915433f7e20055411ddaaf1db3c720d663a89bcbc4`, the value in `evidence/manifest.json`.
4. Our own test agrees: in `evidence/tests/rpc-check.txt` the mainnet RPC answered `eth_chainId` with `0x97`, which is 151.

## How the report keeps facts, analysis and unknowns apart

Every finding paragraph carries one label (chapter intros and figure captions summarise the cited facts around them):

- **Confirmed**: stated in a public source, which is linked and quoted.
- **Tested**: we ran the call ourselves on 15 October 2026. The log is in `evidence/tests/`.
- **Analysis**: our reasoning from the confirmed facts it cites.
- **Unknown**: not answered by any public source we found.

## The website

| Address | Page |
|---|---|
| `/` | The short answer, the four key findings, how to read the labels, plain words for the technical terms, and the list of chapters with reading times |
| `/chapters/why-now` to `/chapters/community-summary` | One page per chapter, 11 in all. Each shows "Chapter 3 of 11" with a progress bar, and Previous and Next at the end |
| `/sources` | Every source in groups, the exact words relied on, where each is used, and a filter |
| `/evidence` | The saved copy of every source page, `manifest.json` with the SHA-256 of each, and the logs of our own tests |

- Every chapter is a real page with its own address, so it can be linked, shared and read without JavaScript. Addresses have no `.html`.
- Under the header of each chapter, a slider shows the position; drag or tap it to open any chapter. On a chapter page the left and right arrow keys go to the previous and next chapter.
- A citation such as S5 opens the source list at S5 and marks it with a red box. Hovering a citation shows the quoted words first.
- Diagrams are drawn in SVG, a wide version for desktop and a narrow one for phones, and each can open full screen.
- The site loads nothing from another domain, and its Content-Security-Policy (in `vercel.json`) allows only its own files to run.
- Status labels, the tab icon and the DAO logo follow the Task Board brand kit.

## The repository

| Path | What it holds |
|---|---|
| `content/report.json` | Every word of the report and the community summary. Claims cite facts as `{fact-id}` |
| `content/facts.json` | 107 facts (106 cited in the report), each with its source and the exact words quoted from it |
| `content/sources.json` | 38 sources: publisher, title, link, snapshot file, and an Internet Archive copy once recorded |
| `content/diagrams.json` | The 7 diagrams: title, caption with citations, and the exact wording each one may show |
| `public/diagrams/` | The diagrams as hand-written SVG |
| `evidence/snapshots/` | A text copy of every source page as it read on 15 October 2026 |
| `evidence/tests/` | The full output of our JSON-RPC calls to Redbelly and our calls to the public Overledger API |
| `evidence/manifest.json` | Address, capture time (UTC) and SHA-256 of every evidence file. The build publishes `evidence/` on the site |
| `scripts/build.py` | Builds everything: the website, the PDF, the Word file, `SOURCES.md` and `COMMUNITY-SUMMARY.md` |
| `scripts/report_model.py` | Reads the content files and numbers the sources (S1, S2 ...) and figures in reading order |
| `scripts/pages.py` | The HTML of every page, and the print page the PDF is made from |
| `scripts/word_file.py` | The Word file |
| `scripts/site.css`, `scripts/site.js`, `scripts/print.css` | Website style and behaviour, and the print style of the PDF |
| `scripts/render_diagram.py` | Renders one diagram to PNG and measures it: smallest text size, overlapping text, text outside its box |
| `scripts/check.py` | The quality gate, below |
| `scripts/snap_sources.py` | Recaptures every source page and reports what changed, without touching `evidence/` unless asked |
| `scripts/archive_sources.py` | Records an Internet Archive copy of every source page |
| `scripts/serve.py` | Serves `public/` locally with the addresses and headers of `vercel.json` |
| `.github/workflows/check.yml` | Runs the quality gate on GitHub for every push |
| `vercel.json` | Vercel settings: `public/` is the web root, clean addresses, no build step, security and cache headers |

## Quality gate

```
python3 scripts/check.py            # must end with RESULT: PASS
python3 scripts/check.py --online   # also asks every source link, and every archived copy, whether it answers today
python3 scripts/check.py --report   # also writes the table of results to QUALITY-GATE.md
```

It prints one line per check, and fails if:

1. a quote is not found word for word in its saved snapshot, or a snapshot changed after capture (SHA-256)
2. a labelled paragraph cites no source, a citation points to an unknown fact, or a source is never cited
3. any sentence about Redbelly or Quant suggests a partnership, talks, plans or an agreement
4. the text uses investment language or hype words, an en dash, an em dash or an emoji
5. any deliverable contains a personal name, handle or personal website listed in the local, git-ignored `.credit-names` and `.credit-links` files (this scan runs only where those private lists exist), or the Word file names a tool or a person in its properties
6. an X post is over 280 characters
7. the PDF, the Word file or the website does not carry the current text of every paragraph, or the source list misses a quote
8. a diagram breaks the SVG rules (brand palette only, prefixed ids, title and description, no styles, images, scripts or outside links), or draws a word that is not in its approved wording in `content/diagrams.json` (this catches typos)
9. the website loads anything from another domain, or has inline script that the Content-Security-Policy would block
10. a link inside the website opens nothing, points to a missing anchor, or uses an address ending in `.html`
11. the chain ID our RPC test received differs from the one Redbelly documents, or the report states a chain ID that is neither
12. a test log ran on a different day than the report says

GitHub Actions runs the same script on every push (see the Actions tab). That run has no private name lists, so it skips the name scan in check 5; run the check locally before each push.

To repeat the RPC test, call `eth_chainId` and `net_version` on `https://governors.mainnet.redbelly.network` (see `evidence/tests/rpc-check.txt`).

## Rebuild and preview

```
python3 -m venv .venv && . .venv/bin/activate     # once; .venv is git-ignored
pip install playwright python-docx pillow
python -m playwright install chromium
python scripts/build.py      # the site, the PDF, the Word file, SOURCES.md and COMMUNITY-SUMMARY.md
python scripts/check.py      # must end with RESULT: PASS
python scripts/serve.py      # then open http://127.0.0.1:8000
```

The check and the snapshot script read PDFs with `pdftotext` from poppler (`sudo apt install poppler-utils` on Ubuntu, `brew install poppler` on macOS). `scripts/serve.py` sends the same headers as Vercel, so a page that the Content-Security-Policy would break shows the problem locally first.

## Sources: recapture and archive

```
python3 scripts/snap_sources.py           # fresh copies into build/snapshots/, and a report of what changed
python3 scripts/snap_sources.py --write   # replace the copies that changed in evidence/, then run check.py
python3 scripts/archive_sources.py        # ask the Wayback Machine for a copy of every source page
```

The copies in `evidence/snapshots/` are what the report quotes, so `snap_sources.py` leaves them alone unless `--write` is given. With `--write` it replaces only the copies whose text changed, and every other copy keeps its original capture time in the manifest. Both scripts need network access; `archive_sources.py` records each copy in `content/sources.json`, and the next build shows it next to the original link.

## Deploy

The site is static and deploys on Vercel straight from this repository. `vercel.json` sets `public/` as the web root with no build or install step and turns on clean addresses, so `/sources` serves `public/sources.html`. It also sends a Content-Security-Policy, HSTS, a Permissions-Policy and cache headers. Nothing outside `public/` is served. Each push to the main branch redeploys the site.

## Licences and credits

- Fonts: Be Vietnam Pro and JetBrains Mono, SIL Open Font License 1.1 (`licenses/`), self-hosted from `public/fonts/`.
- Logo and icon: the Redbelly DAO logo and the Task Board icon, from the Task Board brand kit (taskboard.redbellydao.network/brand).
- Snapshots in `evidence/` are verbatim copies of third-party pages, kept only so every quote can be checked. They keep the source's own punctuation. The one exception: because the Task Board does not allow personal credit inside a deliverable, contributor names and links in two copies (the TASK-08 guide and the TASK-29 brief) were replaced with [name removed] and [link removed]. Each file's header and `evidence/manifest.json` say so.
- Diagrams are drawn for this report in SVG. No third-party images are used.
