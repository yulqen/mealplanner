# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth**: All work is tracked in plan.md
2. **Test-Driven Development**: Write tests before implementing
3. **High Code Coverage**: Aim for >80% coverage

## Task Workflow

### 1. Select Task
Choose the next `[ ]` task from plan.md in sequential order.

### 2. Mark In Progress
Change `[ ]` to `[~]` in plan.md before starting work.

### 3. Write Failing Tests (Red Phase)
- Create tests that define the expected behavior
- Run tests and confirm they fail
- Do not proceed until you have failing tests

### 4. Implement (Green Phase)
- Write the minimum code to make tests pass
- Run tests and confirm they pass

### 5. Refactor
- Clean up code with the safety of passing tests
- Remove duplication, improve clarity
- Re-run tests to ensure they still pass

### 6. Verify Coverage
Run coverage reports. Target >80% for new code.

### 7. Commit
Stage and commit with a descriptive message:
```
<type>(<scope>): <description>
```
Types: feat, fix, docs, refactor, test, chore

### 8. Mark Complete
Change `[~]` to `[x]` in plan.md.

## Phase Completion

When all tasks in a phase are complete:

1. **Run Full Test Suite**: Ensure all tests pass
2. **Manual Verification**: 
   - Present verification steps to user
   - Get explicit confirmation that phase works as expected
3. **Commit Checkpoint**: Create a checkpoint commit for the phase

## Quality Gates

Before marking a task complete, verify:

- [ ] All tests pass
- [ ] Code coverage ≥80%
- [ ] Code follows project style guidelines
- [ ] No linting errors
- [ ] Documentation updated if needed

## Commit Message Format

```
<type>(<scope>): <short description>

[optional body with more details]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that doesn't fix a bug or add a feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks