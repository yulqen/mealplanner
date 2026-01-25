# Python Style Guide

## Naming
- `snake_case`: functions, variables, modules
- `PascalCase`: classes
- `CONSTANT_CASE`: module-level constants
- `_single_leading_underscore`: internal use

## Formatting
- 4 spaces for indentation (no tabs)
- Maximum line length: 88-100 characters
- Two blank lines around top-level definitions
- One blank line around method definitions

## Imports
- One import per line
- Group: standard library, third-party, local
- Avoid wildcard imports (`from x import *`)
- Use absolute imports

## Type Hints
- Use type hints for function signatures
- Use `Optional[T]` for nullable types
- Use `list[T]`, `dict[K, V]` (Python 3.9+)

## Functions
- Use descriptive names
- Document with docstrings (Google or NumPy style)
- Prefer returning values over mutating arguments
- Use keyword arguments for clarity

## Code Style
- Use f-strings for string formatting
- Use context managers (`with`) for resources
- Prefer list/dict comprehensions for simple cases
- Use `is` for `None` comparisons
