# ChromaCode

> A programming language where **color is syntax**, not decoration.

## Install VS Code Syntax Highlighting

Open VS Code, go to Extensions, click the `...` menu, choose **Install from VSIX...**, then select:

`chromacode-syntax/chromacode-syntax-1.0.0.vsix`

Restart VS Code and open any `.chroma` file.


## Run Sample Programs

```bash
python3 chromacode.py 'sample programs/hello_world.chroma'
python3 chromacode.py 'sample programs/temp_converter.chroma'
python3 chromacode.py 'sample programs/countdown.chroma'
python3 chromacode.py 'sample programs/fizzbuzz.chroma'
python3 chromacode.py 'sample programs/stats_calculator.chroma'
printf '1\n1\n4\n2\n5\n3\n' | python3 chromacode.py 'sample programs/ttt.chroma'
```

**Requirements:** Python 3.10+ · No external dependencies

For the image reader: `pip install Pillow`

---

ChromaCode is a dual-channel programming language: every line carries meaning through both its **text keyword** and its **color tag**. The color defines what kind of operation the line performs — enforced at parse time by the interpreter.

---

## Color Roles

| Tag | Role | Valid Constructs | Example |
|-----|------|-----------------|---------|
| `BLUE` | Variables / Data | Assignment | `BLUE x = 42` |
| `GREEN` | Functions / Output | print, func, return | `GREEN print("hi")` |
| `YELLOW` | Conditions | if, elif, else | `YELLOW if x > 0` |
| `PURPLE` | Loops / Repetition | for, while | `PURPLE for i in 1..10` |
| `RED` | End / Stop | Closes loops and functions | `RED end` |

A **ColorTypeError** is thrown at parse time if a tag is misused — e.g., using `YELLOW` on an assignment. The error card explains which color to use and why, with a "try this instead" fix.

---

## Quick Start

```bash
python3 chromacode.py 'sample programs/fizzbuzz.chroma'
```

---

## Example Programs

### Hello World
```
BLUE name = "World"
YELLOW if name != ""
GREEN print("Hello, " + name + "!")
GREEN print("Welcome to ChromaCode.")
```

### FizzBuzz
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

### Function Definition
```
GREEN func celsius_to_fahrenheit(c)
BLUE result = c * 9 / 5 + 32
GREEN return result
RED end

BLUE boiling_c = 100
BLUE boiling_f = celsius_to_fahrenheit(boiling_c)
GREEN print("Boiling: " + str(boiling_f) + "F")
```

### Tic-Tac-Toe (interactive)
```
// Full two-player game — runs in the browser IDE with a clickable board
GREEN func display(b)
GREEN print(" " + str(b[0]) + " | " + str(b[1]) + " | " + str(b[2]))
GREEN print("---+---+---")
// ...
RED end

BLUE board = ['1','2','3','4','5','6','7','8','9']
PURPLE while done == 0
GREEN display(board)
BLUE pos = int(input()) - 1
BLUE board = set_at(board, pos, mark)
// ...
RED end
```

---

## Language Specification

### Syntax Rules
- Each line begins with a **color tag** (`BLUE`, `GREEN`, `YELLOW`, `PURPLE`, `RED`)
- Tags are case-insensitive (`blue`, `BLUE`, `Blue` all work)
- Comments use `//` — inline or standalone
- Block scope is closed with `RED end`
- `if/elif/else` chains self-terminate — no `RED end` needed
- Indentation is optional (visual only, not structural)

### Block Semantics
```
PURPLE for i in 1..10    <- opens loop block
  ...body...
RED end                  <- closes it

GREEN func foo(x)        <- opens function block
  ...body...
RED end                  <- closes it

YELLOW if x > 0          <- opens if chain (no RED needed)
  ...body...
YELLOW elif x == 0
  ...body...
YELLOW else
  ...body...
                         <- chain ends at first non-YELLOW line
```

### Loop Syntax
```
PURPLE for i in 1..10        // range: 1 through 10 inclusive
PURPLE for i in range(5)     // 0 through 4
PURPLE while condition       // standard while loop
```

### Built-in Functions

| Function | Description |
|----------|-------------|
| `print(expr)` | Print to output |
| `input()` | Read user input (browser: inline widget; CLI: stdin) |
| `str(v)`, `int(v)`, `float(v)` | Type conversion |
| `len(v)` | Length of string or list |
| `abs`, `max`, `min`, `round` | Math helpers |
| `set_at(arr, idx, val)` | Immutable array update — returns a new array |

### Scoping
ChromaCode uses **lexical scoping**. Functions capture their definition environment (closure).

### Type System
Types are inferred at runtime. Supported: `int`, `float`, `str`, `bool`, `None`, `list`.

---

## Error System

| Error | When | Example |
|-------|------|---------|
| `SyntaxError` | Unknown color tag | `ORANGE x = 5` |
| `ColorTypeError` | Tag used for wrong construct | `YELLOW x = 5` |
| `RuntimeError` | Expression evaluation fails | `BLUE x = undefined_var` |

`ColorTypeError` includes a learning card: it shows which color was used, what that color is actually for, which color should have been used, and a corrected example line.

---

## Website Features

The browser IDE (`index.html`) contains a full JavaScript port of the ChromaCode interpreter with additional tooling.

### Live Syntax Highlighting
Color tags are highlighted in their respective colors, matching the VS Code extension. Errors highlight the offending line in red.

### Learning Error Cards
When a `ColorTypeError` or runtime error occurs, the output panel shows an educational card explaining the mistake and demonstrating the correct usage.

### Step-Through Visualizer
Click **Step** to trace a program one statement at a time. Each step shows:
- The currently executing line (highlighted in blue)
- A description of the operation
- A live variable watch panel with current values
- All output produced so far

### Inline Input
When a program calls `input()`, execution pauses and an inline text field appears directly in the output panel. For tic-tac-toe, this automatically becomes a **clickable 3x3 board** — open squares are buttons, taken squares are disabled and colored by player (blue for X, purple for O).

### Image-to-ChromaCode
Upload a PNG color strip (horizontal blocks of ChromaCode colors) and the site reads the sequence, maps each block to the nearest ChromaCode color, and generates a skeleton program with `?placeholder` expressions to fill in.

### Sample Programs
Hello World · FizzBuzz · Prime Numbers · Factorial · Tic-Tac-Toe (click-to-play)

---

## Image Interpreter (`image_to_chroma.py`)

Reads a horizontal strip of colored squares and outputs a ChromaCode skeleton.

```bash
# Generate a sample FizzBuzz strip image
python3 image_to_chroma.py --sample

# Read a strip and print the skeleton
python3 image_to_chroma.py my_strip.png

# Read and immediately execute (no ?placeholders allowed)
python3 image_to_chroma.py --run my_strip.png
```

Color blocks map to: BLUE · GREEN · YELLOW · PURPLE · RED

---

## Running the Python Interpreter

```bash
# Run a .chroma file
python3 chromacode.py 'sample programs/fizzbuzz.chroma'

# Use as a module
from chromacode import interpret_source
interpret_source("""
BLUE x = 10
GREEN print(str(x))
""")
```

---

## Project Structure

```
CS-420-Final/
├── chromacode.py          # Python interpreter (lexer + parser + AST + evaluator)
├── image_to_chroma.py     # Image strip reader and skeleton generator
├── index.html             # Website with browser-based JS interpreter
├── sample programs/       # Example .chroma programs
│   ├── countdown.chroma
│   ├── fizzbuzz.chroma
│   ├── hello_world.chroma
│   ├── stats_calculator.chroma
│   ├── temp_converter.chroma
│   └── ttt.chroma
├── .vscode/
│   └── settings.json      # VS Code color overrides for .chroma files
└── README.md
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

## CS 420 — Final Project

**Language:** ChromaCode v1.0  
**Python Interpreter:** ~455 lines (lexer + parser + AST + evaluator)  
**JS Interpreter:** Full port embedded in `index.html`, async-capable with inline I/O  
**Sample Programs:** Hello World · FizzBuzz · Primes · Factorial · Tic-Tac-Toe  
**Extra Tools:** Image strip reader · Step-through visualizer · Learning error cards  

*Honor Code: I have neither given nor received unauthorized aid in completing this work, nor have I presented someone else's work as my own.*
