# Blank Line Enforcement Script Design

## Overview

A standalone script that enforces the blank line rules defined in CLAUDE.md, similar to `black` or `ruff`. The script processes Python files in-place, applying complex blank line rules while preserving existing multiline formatting.

## Architecture

### Core Components

1. **MultilineParser**: Handles line-by-line reading with bracket tracking for multiline statements
2. **StatementClassifier**: Identifies statement types and maintains block classification
3. **BlankLineRuleEngine**: Applies configurable blank line rules based on block transitions
4. **FileAnalyzer**: Manages parsing and analysis of file structure
5. **BlankLineConfig**: Configuration system for customizable blank line rules
6. **CLI Interface**: Command-line tool with file/directory processing and configuration support
7. **FileProcessor**: Handles file I/O and change detection

### Architecture Overview

Prism uses a two-pass architecture with configurable rules:

```
Configuration Layer:
├── BlankLineConfig (TOML parsing, CLI overrides)
├── Validation (0-3 range, valid block types)
└── Default + Override system

Processing Pipeline:
├── Pass 1: FileAnalyzer
│   ├── MultilineParser (bracket tracking, statement completion)
│   └── StatementClassifier (block type identification)
├── Pass 2: BlankLineRuleEngine
│   ├── Configuration-driven rule application
│   ├── Scope-aware processing (nested indentation)
│   └── Special rule handling (consecutive Control/Definition)
└── Pass 3: FileProcessor
    ├── File reconstruction with correct spacing
    └── Change detection and conditional writing
```

## Key Design Decisions

### 1. Configuration System Architecture
- **Default + Override Pattern**: Simple default for common cases, fine-grained overrides for specific needs
- **TOML Configuration**: Standard format with validation (0-3 blank lines)
- **CLI Precedence**: Command-line flags override config file settings
- **Backward Compatibility**: No configuration = current behavior (1 blank line)

### 2. Multiline Statement Handling
- **Buffer physical lines** until complete logical statement is formed
- **Preserve original formatting** - do not alter line breaks within multiline statements
- **Classify entire statement** once complete (e.g., `x = func(\n  arg\n)` is Assignment)

### 3. Block Classification Priority
```python
# Classification precedence (highest to lowest):
1. Assignment block (x = foo(), comprehensions, lambdas)
2. Import block (import statements)
3. Definition block (def/class complete structures)
4. Control block (if/for/while/try/with complete structures)
5. Declaration block (global/nonlocal)
6. Call block (foo(), del, assert, pass, raise, yield, return)
7. Comment block (consecutive comment lines)
```

### 4. Configuration Structure
```toml
# prism.toml
[blank_lines]
default_between_different = 1  # Default spacing
consecutive_control = 1        # Special consecutive rules
consecutive_definition = 1

# Fine-grained overrides (optional)
assignment_to_call = 2
import_to_assignment = 0
```

### 5. Nested Control Structure Tracking
- **Independent rule application** at each indentation level
- **Secondary clause handling**: No blank lines before `elif`/`else`/`except`/`finally`
- **Complete structure detection**: Track when control blocks end with/without optional clauses
- **Scope boundary enforcement**: Always 0 blank lines at start/end of scopes (non-configurable)

### 6. Comment Block Behavior
- **Comment blocks** are first-class block types in the system
- **Configuration-driven spacing**: Comments follow same rules as other block types
- **Preserve existing spacing**: "Leave as-is" rule for existing blank lines after comments
- **Break behavior**: Comments cause block type transitions like any other block

## Implementation Architecture

### Configuration System
```python
@dataclass
class BlankLineConfig:
    defaultBetweenDifferent: int = 1
    transitions: dict[tuple[BlockType, BlockType], int]
    consecutiveControl: int = 1
    consecutiveDefinition: int = 1
    
    @classmethod
    def fromToml(cls, path: Path) -> 'BlankLineConfig'
    def getBlankLines(self, fromBlock: BlockType, toBlock: BlockType) -> int
```

### Rule Engine with Configuration
```python
class BlankLineRuleEngine:
    def __init__(self, config: BlankLineConfig):
        self.config = config
        
    def applyRules(self, statements: list[Statement]) -> list[int]:
        # Returns list of blank line counts (not just boolean)
        pass
        
    def _needsBlankLineBetween(self, prevType: BlockType, currentType: BlockType) -> int:
        return self.config.getBlankLines(prevType, currentType)
```

### CLI with Configuration Support
```python
def loadConfiguration(args) -> BlankLineConfig:
    # Load from TOML file (./prism.toml by default)
    # Apply CLI overrides
    # Validate all values (0-3 range)
    pass
```

## Critical Edge Cases

1. **Nested control with secondary clauses**:
```python
if condition:
    if nested:
        pass
    # NO blank line here
    else:
        pass
# NO blank line here  
else:
    pass
```

2. **Comment breaks with preserved spacing**:
```python
x = 1

# Comment causes break
y = 2  # This starts new Assignment block
```

3. **Multiline classification**:
```python
result = complexFunction(
    arg1,
    arg2
)  # Entire construct is Assignment block
```

4. **Mixed statement classification**:
```python
x = someCall()  # Assignment block (precedence rule)
```

## Testing Strategy

1. **Unit tests** for each component (LineParser, BlockClassifier, BlankLineEngine)
2. **Integration tests** with complex nested scenarios
3. **Edge case validation** for all rule combinations
4. **Performance tests** on large Python files
5. **Regression tests** to ensure no unintended modifications

## CLI Interface Design

```bash
# Basic usage (same as before)
prism file.py
prism src/
prism --check file.py

# Configuration options
prism --config custom.toml file.py
prism --no-config file.py
prism --blank-lines-default=2 file.py
prism --blank-lines assignment_to_call=0 file.py
prism --blank-lines-consecutive-control=2 file.py

# Multiple overrides
prism --blank-lines assignment_to_call=0 --blank-lines import_to_control=2 file.py
```

### Configuration File Format
```toml
# prism.toml - Complete example
[blank_lines]
# Default spacing between different block types
default_between_different = 1

# Special consecutive block rules
consecutive_control = 1
consecutive_definition = 1

# Fine-grained transition overrides
assignment_to_call = 2
call_to_assignment = 2
import_to_assignment = 0
assignment_to_import = 0
control_to_definition = 2
```

## Performance Considerations

- **Two-pass processing** (analyze, then apply rules)
- **Configuration loaded once** per execution, not per file
- **Fast bracket tracking** with simple character scanning
- **Efficient indentation detection** without full AST parsing
- **Change detection** to avoid unnecessary file writes
- **TOML parsing** only when configuration file exists and is newer