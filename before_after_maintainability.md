# Before and After — Maintainability

| Question | Monolith | assistant_core |
|---|---|---|
| Places to change the credit rate | 1 constant in code | 1 variable in `.env` |
| Tests run offline and deterministically? | No | Yes |
| Missing `handbook.json` | Prints and continues silently | Raises `DataError` at startup |
| Secret printed or logged? | Yes | No |
| Module-level globals | 9 (3 mutable) | 0 |
| Bare `except:` | 3 | 0 |
| Longest function (lines) | Approximately 65 (`handle`) | Approximately 15 |
| Swap the LLM without touching the service? | No | Yes |

## Check yourself

**What got more complex?**

The new architecture has more files and introduces additional concepts, such as services, responders, configuration, and dependency injection. Understanding the flow may take more time initially.

**When is that trade-off worth it?**

This trade-off is worthwhile when multiple people maintain the code, when the project needs reliable automated tests, or when new features and integrations are expected. Separating responsibilities makes the code easier to test, debug, extend, and maintain.

For a very small, short-lived script maintained by one person, a monolithic design may be simpler. For a project that must be tested and extended over time, the more modular architecture is generally worth the extra complexity.