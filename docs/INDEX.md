# Documentation Index

Quick navigation for all guidance documents.

## 📌 Start Here

**New to the project?** Read [../AGENTS.md](../AGENTS.md) first (2 min read).

---

## 📚 Documentation

### For Daily Work
- **[QUICK_START.md](QUICK_START.md)** — Development commands, testing, database, CSS, deployment
  - *Example*: `uv run manage.py runserver`, `make css-watch`, running tests

### For Understanding the Code
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — App structure, data models, business logic
  - *Example*: How recipes flow to shopping lists, shuffle algorithm, store category ordering

### For Frontend Development
- **[FRONTEND.md](FRONTEND.md)** — Templates, HTMX patterns, styling, performance
  - *Example*: Recipe filter HTMX, shopping list checkbox polling, ingredient autocomplete

### Project Specification
- **[../mealplanner-spec.md](../mealplanner-spec.md)** — Complete requirements, tech stack, all data models
  - *Use when*: You need the source of truth on what features should do

---

## 🗂️ File Structure

```
mealplanner/
├── AGENTS.md                          ← Entry point for coding agents
├── mealplanner-spec.md                ← Complete specification
├── README.md                          ← Project overview
├── plan.md                            ← Implementation roadmap
├── TODO.md                            ← Current tasks
│
├── docs/
│   ├── INDEX.md                       ← You are here
│   ├── QUICK_START.md                 ← Commands & workflows
│   ├── ARCHITECTURE.md                ← Code structure & models
│   └── FRONTEND.md                    ← UI & templating
│
├── core/
│   ├── models.py                      ← All Django models
│   ├── views/                         ← Views by domain
│   ├── services/                      ← Business logic
│   └── templates/                     ← Templates & components
│
└── config/                            ← Django settings
```

---

## 🔗 Common Links

| Task | Document |
|------|----------|
| First-time setup | [QUICK_START.md](QUICK_START.md) → Development Server |
| Running tests | [QUICK_START.md](QUICK_START.md) → Testing |
| Adding a feature | [ARCHITECTURE.md](ARCHITECTURE.md) → Key Data Models |
| Building UI | [FRONTEND.md](FRONTEND.md) → Common HTMX Patterns |
| Deploying | [QUICK_START.md](QUICK_START.md) → Deployment |
| Feature requirements | [../mealplanner-spec.md](../mealplanner-spec.md) |

---

## 💡 Quick Tips

- **Running the dev server**: `uv run manage.py runserver`
- **Running tests**: `uv run manage.py test`
- **Building CSS**: `make css` or `make css-watch`
- **Database setup**: `uv run manage.py migrate && uv run manage.py seed_data`

See [QUICK_START.md](QUICK_START.md) for full command reference.
