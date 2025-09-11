## ModelAudit — August 2025 Investor Update

### Overview
- **Four releases shipped** in August: `0.2.1` (Aug 15), `0.2.2` (Aug 21), `0.2.3` (Aug 21), `0.2.4` (Aug 28)
- **Broadened coverage and depth**: new scanners and CVE coverage across pickle/joblib, TensorFlow, Jinja2, and PyTorch
- **Enterprise readiness**: SARIF output, typed JSON schemas, robust auth and cache management, CLI simplification
- **Scale and reliability**: production-scale scans to 1TB+, streaming analysis, longer timeouts, graceful degradation

### Product & Security Coverage
- **New scanners and detections**
  - Keras ZIP `.keras` scanner; enhanced TensorFlow SavedModel (Lambda layers) and detection of dangerous TensorFlow ops
  - Jinja2 template injection scanner (config and prompt template hardening)
  - Comprehensive metadata security scanner with enhanced HuggingFace support
  - Expanded CVE coverage: pickle/joblib vulnerabilities and targeted coverage for CVE-2025-32434
  - Pickle hardening: `STACK_GLOBAL` + memo tracking, broadened builtin/operator and `compile()/eval()` variants detection
  - OS module alias detection (`nt`, `posix`) to block indirect command execution
  - PyTorch ZIP scanner refactor for maintainability and deeper analysis
  - 7‑Zip archive scanning support (post-0.2.4 in August window)

### Enterprise & Integrations
- **SARIF output** for CI/SAST/SIEM pipelines
- **Typed JSON schemas** (deep Pydantic integration) for stable programmatic consumption
- **Authentication system** with promptfoo-style delegation; CLI cache management commands for operational workflows
- **Asset/SBOM pipeline improvements** and file-type validation for safer ingestion paths

### Scale, Performance, and UX
- **Scale**: support for scanning models up to 1TB+; per-entry size raised to 100GB
- **Performance**: streaming, scanner-driven analysis; cache performance (fewer filesystem calls); weight distribution optimizations
- **Reliability**: graceful degradation, robust error handling, circular import resolution, improved interrupt behavior (Ctrl-C)
- **UX**: CLI consolidated from 25→12 flags with smart detection; progress tracking for large scans; clearer logging
- **Throughput**: timeout increased to 1 hour for long-running enterprise scans

### Releases Shipped
- **0.2.1 (Aug 15)**: Keras ZIP scanner, TF SavedModel Lambda detection, broader dangerous-op coverage, network/JIT/secrets detection, progressive timeout config; numerous false-positive fixes
- **0.2.2 (Aug 21)**: 1TB+ model support, 100GB entry limit, 1h timeout, progress tracking, streaming analysis, auth delegation; large-file handling and stability fixes
- **0.2.3 (Aug 21)**: Performance and CI improvements; import/format hygiene; additional test coverage and reliability fixes
- **0.2.4 (Aug 28)**: SARIF output; improved CVE-2025-32434 detection; cache performance; graceful degradation; metadata scanner; CLI/UX audit; PyTorch ZIP refactor

### Community & Operations
- **Contributors**: external contributions included SARIF support (Ian Webster) and improved interrupt handling (Faizan Minhas)
- **CI**: faster feedback loops, clearer developer guidance, and resilience improvements in Docker/CI pipelines

### Why This Matters (Investor Lens)
- **Coverage leadership**: breadth (15+ scanners) and depth (CVE-focused and ML‑context‑aware analysis) differentiate the product for security and MLOps buyers
- **Enterprise integration**: SARIF, typed schemas, and CLI/CI ergonomics reduce time-to-adoption in regulated environments
- **Production readiness at LLM scale**: 1TB+ support, streaming, and long timeouts align with real-world model sizes and workflows
- **Operational reliability**: graceful degradation and UX simplifications lower support burden and expand self-serve paths

### Looking Ahead
- Harden newly added archive support (7‑Zip) and continue CLI simplification roll-out
- Expand SBOM/export pathways and tighten CVE coverage across emerging model formats
- Continue performance work on caching and extreme-size streaming scenarios
