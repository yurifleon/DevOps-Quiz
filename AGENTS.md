# DevOps Quiz Agent Guidance

This repository’s actual application lives in `AI-quiz/`.
All commands, edits, and local runtime checks should be executed from that folder.

## Key project facts

- Main app: `AI-quiz/index.html` (single-page static app, no framework, inline CSS and JS).
- Question data: `AI-quiz/devops_questions.json` is the single source of truth for the quiz content.
- Generator script: `AI-quiz/generate_devops_bank_split.py` is standalone and does not read or write `AI-quiz/devops_questions.json`.
- No build step: use `python -m http.server 8000` or `npm start` from `AI-quiz/`.

## Recommended commands

```bash
cd AI-quiz
python -m http.server 8000
# open http://localhost:8000/index.html

npm start
# runs: npx serve -s . -l $PORT
```

## Validation and editing rules

- Preserve valid JSON formatting and the existing structure when editing `AI-quiz/devops_questions.json`.
- Keep `id` values unique across the whole file.
- For `mcq` questions, include 4 options and ensure `answer` matches one option exactly.
- For `true_false` questions, `options` should be `null` or omitted.
- Validate edits with:

```bash
python -m json.tool AI-quiz/devops_questions.json > /dev/null
```

## Notes for code changes

- The frontend is static and expects only vanilla ES6 in `AI-quiz/index.html`.
- The repo includes only one Node script entrypoint (`AI-quiz/package.json`), and the Node engine is `18.x`.
- There is no automated test framework in this repo.

## Reference

See `AI-quiz/AGENTS.md` for the full project overview, command list, schema rules, and coding conventions.