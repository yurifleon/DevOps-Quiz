# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the quiz locally

```bash
# Python (recommended)
python -m http.server 8000
# Open http://localhost:8000/index.html

# Node.js
npm start   # runs: npx serve -s . -l $PORT
```

### Python linting (generate script only)

```bash
ruff check .
ruff format .
mypy .
```

### Generate question banks

```bash
python generate_devops_bank_split.py -d devops_bank --seed 42
```

## Architecture

This is a static single-page app with no build step and no framework. All state lives in module-level JS variables in `index.html`; there is no persistence between page loads.

**`index.html`** — The entire quiz UI: HTML structure, inline `<style>` block, and a `<script>` block with all application logic. Key JS flow:
1. `loadQuestions()` fetches `./devops_questions.json` on page load and populates the category `<select>` and quick-pick buttons from the data (categories are not hardcoded in HTML)
2. Start screen lets users filter by category/difficulty; the "AI in DevOps" quick-pick button shortcuts to that category
3. `startQuiz()` → `filterQuestions()` picks up to `QUESTIONS_PER_SESSION` (20) random questions from the filtered pool
4. Per-question loop: `showQuestion()` → `selectOption()` (single-answer) or `toggleOption()` (multi-select) → `submitAnswer()` → `nextQuestion()`/`skipQuestion()` → `advanceQuestion()` → `showResults()`
5. **Skip/review pass**: `skipQuestion()` records the index in `skippedIndices` and calls `advanceQuestion()`. Once the main pass reaches the end, if any questions were skipped, `advanceQuestion()` switches into a second pass (`reviewingSkipped = true`) iterating `skippedIndices` before finally calling `showResults()`. The skip button is hidden during the review pass. `currentQ()` resolves the active question from either `filteredQuestions[currentQuestion]` or the review index depending on `reviewingSkipped`.

**`devops_questions.json`** — the single source of truth for quiz content (498 questions as of the last count). It is hand-edited directly (see recent commits fixing/improving individual question IDs) rather than regenerated from the Python script on every change.

**`generate_devops_bank_split.py`** — standalone script that *programmatically defines* a question set via `_mcq()`/`_tf()` helper calls and writes it as **split per-category files plus an `index.json`** into an output directory (`-d`, default `devops_bank/`). It does not read or write `devops_questions.json` and is not part of the normal edit workflow for existing questions — treat it as a reference/bootstrap generator, not a build step.

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

- `options` is `null`/absent for `true_false` type; the UI renders True/False buttons automatically
- `answer` must exactly match one of `options` (case-insensitive comparison at runtime)
- `id` must be unique across all questions
- `tags` is optional — only present on a subset of questions
- The frontend also supports a `multi_select` type (`answer` as an array of strings, checkbox-style `toggleOption()` UI, exact-set match required) but no questions of this type currently exist in `devops_questions.json`

## Working with JSON data files

Treat the JSON datasets as structured data, not freeform text:

- Keep them valid JSON with double quotes, no comments, and no trailing commas.
- Preserve existing indentation and object ordering when possible so diffs remain easy to review.
- When adding or editing quiz records, keep the schema consistent and ensure `id` values remain unique.
- Validate any edited file after changes with:

```bash
python -m json.tool devops_questions.json > /dev/null
```

## Code style

**Python** (`generate_devops_bank_split.py`): line length 100, type hints on all signatures using `List[T]`/`Dict[K,V]`/`Optional[X]` (Python 3.9 compat), `snake_case` functions, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.

**JavaScript** (`index.html`): vanilla ES6+, `const` over `let`, no `var`, no external libraries.
