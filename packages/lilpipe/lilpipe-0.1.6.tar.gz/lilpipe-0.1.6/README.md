# lilpipe

A tiny, typed, sequential pipeline engine for Python.

[![PyPI](https://img.shields.io/pypi/v/lilpipe.svg)](https://pypi.org/project/lilpipe/)
[![Python Version](https://img.shields.io/pypi/pyversions/lilpipe.svg)](https://pypi.org/project/lilpipe/)
[![CI](https://github.com/andrewruba/lilpipe/actions/workflows/ci.yaml/badge.svg)](https://github.com/andrewruba/lilpipe/actions)
[![Coverage](https://codecov.io/gh/andrewruba/lilpipe/branch/main/graph/badge.svg)](https://codecov.io/gh/andrewruba/lilpipe)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/andrewruba/lilpipe/blob/main/LICENSE)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/andrewruba/lilpipe/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples%2Fexample.ipynb)

**lilpipe** is a lightweight, Pydantic-powered library for building and running sequential workflows in Python. It’s ideal for data processing, scientific workflows, and any task that benefits from a clear, linear sequence of steps. With built-in caching and simple control signals, lilpipe is small, typed, and practical.

## Features

- **Sequential workflows** — run steps in a fixed order.
- **Type-safe context** — Pydantic-based `PipelineContext`.
- **Smart caching** — `fingerprint_keys` to skip unchanged work.
- **Flow control** — `ctx.abort_pass()` and `ctx.abort_pipeline()`.
- **Composable steps** — nest via `Step(name, children=[...])`.
- **Tiny surface area** — minimal API and dependencies.

## Why not a DAG?

**lilpipe is intentionally *not* a DAG/orchestrator.** It’s a tiny, in-process, sequential runner for code you’d otherwise write as a script.

**Use lilpipe when…**
- The whole workflow runs **top-to-bottom in one process** and finishes in **seconds/minutes**.
- You don’t want extra infra: **no server, no scheduler UI, no metadata DB**.
- You want a **typed, validated shared state** (Pydantic `PipelineContext`) flowing step-to-step with helpful errors.
- You want **incremental reruns**: fingerprint caching to **skip unchanged steps** across runs.
- You need simple **retry/abort** semantics without standing up an orchestrator.
- You like **small, testable units**: steps you can unit-test and compose (`Step("name", children=[...])`).

*Examples:*  
- **Data science:** CSV → clean → feature engineer → fit/evaluate → export plots.
- **Lab/assay:** load plate → calibrate → QC/validate → generate PDF report.
- **Data eng script:** pull S3 JSON → normalize → write Parquet → send Slack notification.
- **Dev tooling:** codegen → format → validate → publish artifact.

## Installation

```bash
pip install lilpipe
````

> See `pyproject.toml` for supported Python versions.

## Example Notebook

Run the full demo notebook live on Binder:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/andrewruba/lilpipe/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples%2Fexample.ipynb)

(If you’d rather just view it, the raw notebook is at `examples/example.ipynb` in the repo.)

## License

Licensed under the [Apache 2.0 License](LICENSE).

## Links

* Issues: [https://github.com/andrewruba/lilpipe/issues](https://github.com/andrewruba/lilpipe/issues)
* PyPI: [https://pypi.org/project/lilpipe/](https://pypi.org/project/lilpipe/)
