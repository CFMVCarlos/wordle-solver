## 2026-10-10 - Wordle Grid UX State Mutation
**Learning:** In complex grid arrays (like a Wordle UI), standard HTML forms are anti-patterns. Use global key listeners mapped strictly to an immutable nested array state for snappy visual feedback without needing heavy form-validation wrappers (like react-hook-form) for micro-interactions. Zod should instead be leveraged for strict API response parsing.
**Action:** Use global event listeners mapped to immutable states for grid inputs rather than trying to coerce them into standard forms. Leverage Zod on the API boundary.
