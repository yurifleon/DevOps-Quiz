# GitHub Copilot Instructions

This repository is a static DevOps quiz app.

## Key guidance

- Work from the `AI-quiz/` directory for all code and content changes.
- `AI-quiz/index.html` is the full frontend application; it contains the UI, inline CSS, and JavaScript logic.
- `AI-quiz/devops_questions.json` is the single source of truth for quiz questions.
- `AI-quiz/generate_devops_bank_split.py` is a standalone generator script; it does not modify `devops_questions.json`.

## Recommended commands

```bash
cd AI-quiz
python -m http.server 8000
npm start
```

## Important rules

- Preserve valid JSON when editing `AI-quiz/devops_questions.json`.
- Maintain unique `id` values across questions.
- For `mcq`, include exactly 4 options and ensure `answer` matches one option.
- For `true_false`, use `options: null` or omit `options`.
- Validate JSON with `python -m json.tool AI-quiz/devops_questions.json > /dev/null`.

## More details

See `AI-quiz/AGENTS.md` for full project conventions, commands, and schema rules.