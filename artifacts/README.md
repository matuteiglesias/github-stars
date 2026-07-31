# Artifacts

This directory contains the artifact registry and, after execution, generated evidence.

Generated outputs belong under:

```text
artifacts/generated/
```

Recommended generated subdirectories:

```text
artifacts/generated/
  data/
  eda/
  figures/
  modeling/
  policy/
  submission/
  handoff/
  memos/
```

Do not commit raw data by default.

Do not create empty generated files merely to satisfy a path. A planned artifact remains listed as `planned` in the registry until real evidence exists.

Every generated artifact must be:

- reproducible;
- named according to `plans/artifact_contract.md`;
- traceable to a stage;
- referenced by a closure memo;
- removed or superseded deliberately when obsolete.
