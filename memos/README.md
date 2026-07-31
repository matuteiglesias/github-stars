# Memos

Memos are durable stage-closure records.

They exist to prevent conclusions from being trapped in notebook state or terminal output.

Each stage memo must contain:

- stage;
- status;
- objective;
- evidence produced;
- findings;
- integrity checks;
- unresolved issues;
- decision;
- next-stage gate;
- author or agent;
- timestamp or run identifier.

Generated stage memos belong under:

```text
artifacts/generated/memos/
```

`T00_closure_memo.md` is versioned here because it encodes the initial analytical contract before raw-data execution.
