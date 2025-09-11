# Prism

A Python code formatter that enforces blank line rules defined in CLAUDE.md.

## Features

- **Two-pass architecture**: Clean separation between code analysis and rule application
- **Multiline statement support**: Properly handles statements spanning multiple lines
- **Assignment precedence**: `x = func()` classified as Assignment (not Call)
- **Secondary clause handling**: No blank lines before `elif`/`else`/`except`/`finally`
- **Comment break rules**: Comments cause block breaks with specific blank line rules
- **Recursive indentation**: Independent rule application at each nesting level
- **Change detection**: Only modifies files that actually need changes

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Format files
prism file.py
prism src/

# Check if files need formatting
prism --check file.py

# Show help
prism --help
```

## CLAUDE.md Rules

Prism enforces the complex blank line rules defined in CLAUDE.md:

### Block Types (in precedence order)
1. **Assignment** - Variable assignments, comprehensions, lambdas
2. **Call** - Function calls, del, assert, pass, raise, yield, return
3. **Import** - Import statements  
4. **Control** - if/for/while/try/with structures
5. **Definition** - def/class structures
6. **Declaration** - global/nonlocal statements

### Key Rules
- Blank lines between different block types
- Consecutive Control/Definition blocks need separation
- No blank lines before secondary clauses (elif, else, except, finally)
- Comments cause block breaks and need preceding blank lines
- Rules applied independently at each indentation level

## Architecture

```
├── src/prism/
│   ├── __init__.py
│   ├── cli.py              # Command line interface
│   ├── analyzer.py         # Pass 1: File structure analysis
│   ├── rules.py            # Pass 2: Blank line rule engine
│   ├── parser.py           # Multiline statement parsing
│   ├── classifier.py       # Statement classification
│   └── processor.py        # File I/O and change detection
├── tests/
│   ├── test_analyzer.py
│   ├── test_rules.py
│   ├── test_parser.py
│   └── test_integration.py
└── docs/
    └── rules.md
```