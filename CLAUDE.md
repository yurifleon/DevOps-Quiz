# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

All project files live in `AI-quiz/`, which has its own more detailed `CLAUDE.md`. Run all commands from `AI-quiz/`, not the repo root.

This repository also includes root-level `AGENTS.md` and `.github/copilot-instructions.md` for agent guidance. Use `AI-quiz/AGENTS.md` as the primary project reference for code, schema, and content conventions.

## Commands

```bash
cd AI-quiz

# Run the quiz locally (static site, no build step)
python -m http.server 8000     # open http://localhost:8000/index.html
npm start                      # alternative: npx serve -s . -l $PORT

# Python linting/typechecking (applies only to generate_devops_bank_split.py)
ruff check .
ruff format .
mypy .

# Validate the question data after editing it
python -m json.tool devops_questions.json > /dev/null
```

There is no test framework in this repo.

## Architecture

A static single-page quiz app: no build step, no framework, no persistence between page loads.

- **`AI-quiz/index.html`** — the entire UI (markup, inline `<style>`, and one `<script>` block with all logic, vanilla ES6+). It fetches `./devops_questions.json` at load, builds category filters from the data, and runs sessions of up to 20 random questions (`QUESTIONS_PER_SESSION`). Skipped questions are revisited in a second review pass (`skippedIndices`/`reviewingSkipped`) before results are shown.
- **`AI-quiz/devops_questions.json`** — the single source of truth for quiz content (698 questions across 17 categories). Hand-edited directly; not generated.
- **`AI-quiz/generate_devops_bank_split.py`** — standalone script with its own hardcoded question set; writes per-category files plus `index.json` to an output directory (`-d`, default `devops_bank/`). It does **not** read or write `devops_questions.json` and is not part of the normal question-editing workflow.

## Question schema

```json
{
  "id": 1,
  "category": "DevOps Fundamentals",
  "difficulty": "easy|medium|hard",
  "type": "mcq|true_false",
  "question": "...",
  "options": ["A", "B", "C", "D"],
  "answer": "Correct option text",
  "explanation": "...",
  "tags": ["tag1"]
}
```

- `id` must be unique across the whole file
- `options` is `null`/absent for `true_false`; the UI renders True/False buttons automatically
- `answer` must exactly match one of `options` (compared case-insensitively at runtime)
- `tags` is optional (present on a subset of questions)
- The frontend also supports a `multi_select` type (`answer` as an array, exact-set match) but no such questions currently exist

When editing `devops_questions.json`, preserve existing indentation and key ordering to keep diffs readable, keep `id` values unique, and validate with `python -m json.tool` afterwards. Prefer scripted edits for large or repetitive changes.
