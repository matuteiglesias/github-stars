# Tests

The initial tests enforce repository and output contracts.

They are intentionally small.

Required categories:

1. bundle structure;
2. metric correctness;
3. raw-schema validation;
4. submission schema and value checks;
5. no negative predictions;
6. preservation of prediction row count and order;
7. fixed age-reference behavior;
8. duplicate and identity checks;
9. pipeline clean-run smoke test.

The coding agent should extend tests only when a discovered failure mode would otherwise propagate silently.

Do not build a large testing framework during the case.
