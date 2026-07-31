# Source Code Boundary

Production logic belongs under `src/case_bundle/`.

The notebook should import from this package rather than reimplement:

- loading;
- schema validation;
- metric computation;
- feature engineering;
- split construction;
- model training;
- evaluation;
- artifact writing;
- submission validation.

The initial scaffold only implements stable contracts and RMSLE.

Codex should add the smallest modules required by the current stage. Avoid speculative architecture.
