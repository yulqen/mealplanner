# General Code Style Guide

These principles apply to all languages.

## Clarity
- Write code for humans first, computers second
- Use descriptive names that reveal intent
- Keep functions small and focused on one thing
- Avoid clever tricks that obscure meaning

## Consistency
- Follow existing patterns in the codebase
- Use consistent naming conventions
- Format code consistently (use automated formatters)

## Comments
- Write comments that explain "why", not "what"
- Keep comments up to date with code changes
- Use doc comments for public APIs
- Delete commented-out code

## Structure
- Keep files focused on a single responsibility
- Group related functionality together
- Order code logically (public before private, important before trivial)
- Limit nesting depth (max 3-4 levels)

## Error Handling
- Handle errors explicitly
- Provide useful error messages
- Fail fast on invalid input
- Log errors with context

## Testing
- Write tests for public interfaces
- Test edge cases and error conditions
- Keep tests readable and maintainable
- One assertion per test when practical

## Dependencies
- Minimize external dependencies
- Pin dependency versions
- Keep dependencies up to date
- Prefer standard library when sufficient
