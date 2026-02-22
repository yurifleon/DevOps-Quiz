# AGENTS.md - DevOps Quiz Project

## Project Overview

This is a DevOps quiz application with:
- `quiz.html` - Single-page quiz interface (HTML/CSS/JS)
- `devops_questions.json` - Question data file
- `generate_devops_bank_split.py` - Python script to generate 200-question quiz banks

---

## Commands

### Running the Quiz Interface

```bash
# Python HTTP server (recommended)
python -m http.server 8000
# Open: http://localhost:8000/quiz.html

# Or using Node.js
npx serve .
```

### Running the Question Generator

```bash
# Generate 200 questions to default output directory (devops_bank/)
python generate_devops_bank_split.py

# Custom output directory and seed
python generate_devops_bank_split.py -d output_folder --seed 123
```

### Linting & Type Checking (Python)

```bash
# Install dependencies
pip install ruff mypy

# Run ruff (linting + formatting)
ruff check .
ruff format .

# Run mypy (type checking)
mypy .

# Run a single test file
ruff check generate_devops_bank_split.py

# Run specific lint rule
ruff check --select E501 .  # Line length only
```

### Single Test Execution

No formal test framework is set up. To add tests:

```bash
# Install pytest
pip install pytest

# Run a specific test
pytest tests/test_quiz_generator.py::test_mcq_validation

# Run tests matching a pattern
pytest -k "test_mcq"
```

---

## Code Style Guidelines

### Python (`generate_devops_bank_split.py`)

#### Imports
- Standard library first, then third-party, then local
- Use explicit relative imports for local modules
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
- Use 4 spaces for indentation (no tabs)
- Use trailing commas in multi-line collections
- One blank line between top-level definitions

#### Types
- Use type hints for all function signatures and variables
- Prefer `List[T]`, `Dict[K, V]` over `list[T]`, `dict[K,V]` (compatible with Python 3.9)
- Use `Optional[X]` instead of `X | None`

```python
def process_questions(questions: List[Dict[str, Any]], seed: int) -> List[Question]:
    ...
```

#### Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: prefix with `_`

#### Error Handling
- Use specific exceptions with descriptive messages
- Validate inputs at function boundaries
- Fail fast with clear error messages

```python
def _mcq(category: str, difficulty: str, prompt: str, options: List[str], answer: str,
         explanation: str, tags: List[str]) -> Dict[str, Any]:
    if answer not in options:
        raise ValueError(f"MCQ answer must be one of the options. Got {answer!r}")
```

#### Dataclasses
- Use `@dataclass` for simple data containers
- Use `frozen=True` for immutable data
- Use `field()` with `default_factory` for mutable defaults

---

### HTML/CSS/JavaScript (`quiz.html`)

#### General
- Use semantic HTML5 elements
- Keep JavaScript vanilla (no frameworks)
- Inline CSS in `<style>` for single-file simplicity

#### JavaScript
- Use ES6+ features (const/let, arrow functions, template literals)
- Prefer `const` over `let`, avoid `var`
- Use meaningful variable names
- Add JSDoc comments for functions

```javascript
/**
 * Loads questions from the JSON file
 * @returns {Promise<Array>} Array of question objects
 */
async function loadQuestions() {
    const response = await fetch('devops_questions.json');
    return await response.json();
}
```

#### CSS
- Use CSS custom properties for theming
- Group related styles together
- Use BEM-like naming for complex components
- Keep specificity low

---

## Question Data Schema

Each question must follow this structure:

```json
{
  "id": 1,
  "category": "DevOps Fundamentals",
  "difficulty": "easy|medium|hard",
  "type": "mcq|true_false|short_answer",
  "question": "Question text",
  "options": ["A", "B", "C", "D"] | null,
  "answer": "Correct answer text",
  "explanation": "Explanation text",
  "tags": ["tag1", "tag2"]
}
```

### Validation Rules
- `id`: Unique integer across all categories
- `difficulty`: Must be one of: easy, medium, hard
- `type`: Must be one of: mcq, true_false, short_answer
- `options`: Required for mcq, null for true_false/short_answer
- `answer`: Must exist in `options` for mcq type

---

## Project Structure

```
AI-quiz/
├── quiz.html                    # Main quiz interface
├── devops_questions.json        # Question data
├── generate_devops_bank_split.py # Question generator
├── AGENTS.md                    # This file
└── devops_bank/                 # Generated output (after running script)
    ├── index.json
    ├── DevOps_Fundamentals.json
    └── ...
```

---

## Common Tasks

### Add New Question to `devops_questions.json`
1. Add new object with unique `id`
2. Ensure valid `category`, `difficulty`, `type`
3. For MCQ: include 4 options, answer in options
4. Include explanation

### Generate New Question Bank
```bash
python generate_devops_bank_split.py -d devops_bank --seed 42
```

### Test Quiz Interface
1. Start HTTP server: `python -m http.server 8000`
2. Open `http://localhost:8000/quiz.html`
3. Test filters, quiz flow, and results

---

## Notes for Agents

- This is a simple project - no build system required
- The quiz loads questions dynamically from JSON via fetch
- For production, consider adding error handling for failed JSON loads
- The Python script uses deterministic output with `--seed` flag
