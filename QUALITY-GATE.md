# Quality gate

Result of `python3 scripts/check.py` on 23 Oct 2026, 18:49 UTC: **PASS**, 12 of 12 checks passed.

Each check is described at the top of `scripts/check.py`. GitHub Actions runs the same script on every push (`.github/workflows/check.yml`), without the private name lists, so that run skips the name scan in check 5.

| # | Check | Result | What was checked |
|---|---|---|---|
| 1 | Quotes are word for word in their saved snapshots | PASS | 107 quotes, 38 evidence files |
| 2 | Every claim cites a known fact and every source is cited | PASS | 106 facts cited from 38 sources |
| 3 | No wording that suggests a Redbelly and Quant link | PASS | 151 passages |
| 4 | No price talk, hype words, dashes or emoji | PASS | 151 passages, 107 quotes |
| 5 | No personal credit in any deliverable | PASS | name scan skipped (no .credit-names here), Word properties checked |
| 6 | Every X post fits in 280 characters | PASS | 6 posts, longest 256 |
| 7 | PDF, Word file and website carry the current text | PASS | 137 paragraphs in 3 outputs |
| 8 | Diagrams follow the SVG rules and their approved wording | PASS | 7 diagrams, 14 SVG files |
| 9 | Website loads nothing from outside and runs no inline script | PASS | 17 files |
| 10 | Links inside the website resolve at clean addresses | PASS | 1224 links on 15 pages |
| 11 | Chain IDs agree: our RPC test, Redbelly's docs and the report | PASS | 3 RPC answers, 10 statements in the report |
| 12 | Each test log was run on the date the report gives | PASS | 2 test logs |

Notes:

- fact fw-permissioned is not cited (kept in the fact list only)
- personal credit scan skipped, .credit-names not present
