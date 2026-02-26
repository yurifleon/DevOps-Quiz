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

This is a static single-page app with no build step and no framework.

**`index.html`** — The entire quiz UI: HTML structure, inline `<style>` block, and a `<script>` block with all application logic. Key JS flow:
1. `loadQuestions()` fetches `./devops_questions.json` on page load
2. Start screen lets users filter by category/difficulty; "AI Quiz" button shortcuts to the "AI in DevOps" category
3. `filterQuestions()` picks up to `QUESTIONS_PER_SESSION` (20) random questions from the filtered pool
4. `showQuestion()` → `selectOption()` → `submitAnswer()` → `nextQuestion()` → `showResults()`

**Question data files:**
- `devops_questions.json` — primary question bank (DevOps, CI/CD, containers, Kubernetes, etc.)
- `ai_questions.json` — AI in DevOps questions (loaded alongside devops questions in future iterations)

**`generate_devops_bank_split.py`** — standalone Python script that programmatically generates question JSON. Questions are defined as function calls to `_mcq()` and `_tf()` helpers, then serialized. Uses `--seed` for deterministic output.

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

- `options` is `null` for `true_false` type; the UI renders True/False buttons automatically
- `answer` must exactly match one of `options` (case-insensitive comparison at runtime)
- `id` must be unique across all questions

## Code style

**Python** (`generate_devops_bank_split.py`): line length 100, type hints on all signatures using `List[T]`/`Dict[K,V]`/`Optional[X]` (Python 3.9 compat), `snake_case` functions, `PascalCase` classes, `UPPER_SNAKE_CASE` constants.

**JavaScript** (`index.html`): vanilla ES6+, `const` over `let`, no `var`, no external libraries.
