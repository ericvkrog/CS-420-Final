# ChromaCode 🎨

> A programming language where **color is syntax**, not decoration.

ChromaCode is a dual-channel programming language: every line carries meaning through both its **text keyword** and its **color tag**. The color defines what kind of operation the line performs — enforced at parse time by the interpreter.

---

## Color Roles

| Tag | Color | Role | Valid Constructs |
|-----|-------|------|-----------------|
| `BLUE` | 🔵 Variables / Data | Assignment | `BLUE x = 42` |
| `GREEN` | 🟢 Functions / Output | print, func, return | `GREEN print("hi")` |
| `YELLOW` | 🟡 Conditions | if, elif, else | `YELLOW if x > 0` |
| `PURPLE` | 🟣 Loops / Repetition | for, while | `PURPLE for i in 1..10` |
| `RED` | 🔴 End / Stop | Closes loops and functions | `RED end` |

A **ColorTypeError** is thrown at parse time if a tag is misused (e.g., using YELLOW on a non-boolean expression).

---

## Quick Start

```bash
python3 chromacode.py programs/hello_world.chroma
```

### Requirements
- Python 3.10+
- No external dependencies

---

## Example Programs

### Hello World (`hello_world.chroma`)
```
BLUE name = "World"
YELLOW if name != ""
GREEN print("Hello, " + name + "!")
GREEN print("Welcome to ChromaCode.")
```

### FizzBuzz (`fizzbuzz.chroma`)
```
GREEN print("--- FizzBuzz 1 to 30 ---")
PURPLE for i in 1..30
YELLOW if i % 15 == 0
GREEN print("FizzBuzz")
YELLOW elif i % 3 == 0
GREEN print("Fizz")
YELLOW elif i % 5 == 0
GREEN print("Buzz")
YELLOW else
GREEN print(str(i))
RED end
```

### Function Definition (`temp_converter.chroma`)
```
GREEN func celsius_to_fahrenheit(c)
BLUE result = c * 9 / 5 + 32
GREEN return result
RED end

BLUE boiling_c = 100
BLUE boiling_f = celsius_to_fahrenheit(boiling_c)
GREEN print("Boiling: " + str(boiling_f) + "F")
```

---

## Language Specification

### Syntax Rules
- Each line begins with a **color tag** (BLUE, GREEN, YELLOW, PURPLE, RED)
- Tags are case-insensitive (`blue`, `BLUE`, `Blue` all valid)
- Comments use `//` — inline or standalone
- Block scope is ended with `RED end`
- `if/elif/else` chains do **not** require `RED end` — they self-terminate
- Indentation is optional (visual aid only, not structural)

### Scoping
ChromaCode uses **lexical scoping**. Functions capture their definition environment (closure).

### Type System
Types are **inferred** at runtime. Supported types:
- `int`, `float`, `str`, `bool`, `None`

### Block Semantics
```
PURPLE for i in 1..10   ← opens a loop block
  ...body...
RED end                 ← closes the loop

GREEN func foo(x)       ← opens a function block
  ...body...
RED end                 ← closes the function

YELLOW if x > 0         ← opens an if branch (no RED needed)
  ...body...
YELLOW elif x == 0      ← continues the chain
  ...body...
YELLOW else             ← final branch
  ...body...
                        ← chain ends when next non-YELLOW line appears
```

---

## Running the Interpreter

```bash
# Run a .chroma file
python3 interpreter/chromacode.py programs/fizzbuzz.chroma

# Run from Python
from interpreter.chromacode import interpret_source
interpret_source("""
BLUE x = 10
GREEN print(str(x))
""")
```

---

## Project Structure

```
chromacode/
├── interpreter/
│   └── chromacode.py      # Full lexer + parser + interpreter
├── programs/
│   ├── hello_world.chroma    # Simple Program 1
│   ├── temp_converter.chroma # Simple Program 2
│   ├── countdown.chroma      # Simple Program 3
│   ├── fizzbuzz.chroma       # FizzBuzz
│   └── stats_calculator.chroma # Complex program
└── website/
    └── index.html            # Live browser IDE
```

---

## Design Philosophy

ChromaCode's color system is inspired by the way visual thinkers process information:

- **Blue** — calm, stable data. Variables are the foundation.
- **Green** — growth, output. Functions create and produce.
- **Yellow** — caution, decision. Every branch is a choice point.
- **Purple** — cycles, rhythm. Loops repeat and persist.
- **Red** — stop. Clear, unmistakable block termination.

The goal: make a program's structure **visible at a glance** — useful for beginners, educators, and anyone who thinks visually.

---

## Error Types

| Error | When | Example |
|-------|------|---------|
| `SyntaxError` | Unknown color tag | `ORANGE x = 5` |
| `ColorTypeError` | Tag used for wrong construct | `YELLOW x = 5` (assignment isn't a condition) |
| `RuntimeError` | Expression evaluation fails | `BLUE x = undefined_var + 1` |

---

## CS 420 — Final Project
**Language:** ChromaCode v1.0  
**Interpreter:** Python 3.10+, ~430 lines  
**Programs:** 5 (3 simple + 1 FizzBuzz + 1 complex)  
**Website:** Live browser IDE with JS-ported interpreter

*Honor Code: I have neither given nor received unauthorized aid in completing this work, nor have I presented someone else's work as my own.*
