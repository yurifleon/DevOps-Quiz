# AGENTS.md - DevOps Quiz Project

## Project Overview

A static, single-page DevOps quiz app with no build step and no framework:
- `index.html` — the entire UI: markup, inline `<style>`, and a `<script>` block with all app logic
- `devops_questions.json` — the single source of truth for quiz content (698 questions across 17 categories); hand-edited directly, not generated
- `generate_devops_bank_split.py` — standalone script that defines its own question set and writes it as per-category files into an output directory; it does not read or write `devops_questions.json` and isn't part of the normal question-editing workflow

---

## Commands

### Running the Quiz Interface

```bash
# Python HTTP server (recommended)
python -m http.server 8000
# Open: http://localhost:8000/index.html

# Or using Node.js
npm start   # runs: npx serve -s . -l $PORT
```

### Running the Question Generator

```bash
# Generate questions to default output directory (devops_bank/)
python generate_devops_bank_split.py

# Custom output directory and seed
python generate_devops_bank_split.py -d output_folder --seed 123
```

### Linting & Type Checking (Python)

```bash
ruff check .
ruff format .
mypy .
```

There is no test framework in this repo.

---

## Code Style Guidelines

### Python (`generate_devops_bank_split.py`)

#### Imports
- Standard library first, then third-party, then local
- Group: `from __future__ import annotations` → stdlib → third-party → local

```python
from __future__ import annotations

import argparse
import json
import os
import random
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
```

#### Formatting
- Line length: 100 characters max
- 4 spaces for indentation (no tabs)
- Trailing commas in multi-line collections

#### Types
- Type hints on all function signatures and variables
- Prefer `List[T]`, `Dict[K, V]` over `list[T]`, `dict[K,V]` (Python 3.9 compat)
- Use `Optional[X]` instead of `X | None`

#### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: prefix with `_`

#### Error Handling
- Use specific exceptions with descriptive messages, e.g. `_mcq()` raises `ValueError` if `answer` isn't one of `options`
- Fail fast with clear error messages rather than silently coercing bad data

### HTML/CSS/JavaScript (`index.html`)

- Vanilla ES6+, no external libraries/frameworks
- Prefer `const` over `let`, avoid `var`
- Inline CSS in the single `<style>` block; no CSS-in-JS or separate stylesheets

---

## Question Data Schema

```json
{
  "id": 1,
  "category": "DevOps Fundamentals",
  "difficulty": "easy|medium|hard",
  "type": "mcq|true_false|multi_select",
  "question": "Question text",
  "options": ["A", "B", "C", "D"] | null,
  "answer": "Correct answer text" | ["Correct", "Answers"],
  "explanation": "Explanation text",
  "tags": ["tag1", "tag2"]
}
```

### Validation Rules
- `id`: unique integer across the whole file
- `difficulty`: one of `easy`, `medium`, `hard`
- `type`: one of `mcq`, `true_false`, `multi_select` — the frontend supports `multi_select` (checkbox-style, `answer` as an array, exact-set match) but no such questions exist in `devops_questions.json` yet
- `options`: required for `mcq`/`multi_select`, `null`/absent for `true_false`
- `answer`: for `mcq`/`true_false` must exactly match one entry in `options` (case-insensitive at runtime); for `multi_select` an array of such strings
- `tags`: optional — only present on a subset of questions

---

## JSON File Editing Conventions

When editing any JSON dataset files in this repo (especially `devops_questions.json`):

- Keep files valid JSON: double-quoted keys/strings, no comments, and no trailing commas.
- Preserve the existing indentation and array/object structure where possible to keep diffs readable.
- Maintain the documented question schema exactly; do not invent fields or change `type`/`answer` semantics without updating the frontend logic.
- Before finishing a JSON edit, validate it with:

```bash
python -m json.tool devops_questions.json > /dev/null
```

- For large or repetitive updates, prefer scripted edits over manual patching to avoid accidental formatting errors or duplicate `id` values.

## Common Tasks

### Add a New Question to `devops_questions.json`
1. Add a new object with a unique `id`
2. Use a valid `category`, `difficulty`, `type`
3. For `mcq`: include 4 options, with `answer` matching one of them exactly
4. Include an `explanation`

### Generate a Standalone Question Bank
```bash
python generate_devops_bank_split.py -d devops_bank --seed 42
```
This writes to a new `devops_bank/` directory using the generator's own hardcoded question set — it does not touch `devops_questions.json`.
