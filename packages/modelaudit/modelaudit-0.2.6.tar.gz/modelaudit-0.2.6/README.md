# ModelAudit

**Secure your AI models before deployment.** Detects malicious code, backdoors, and security vulnerabilities in ML model files.

[![PyPI version](https://badge.fury.io/py/modelaudit.svg)](https://pypi.org/project/modelaudit/)
[![Python versions](https://img.shields.io/pypi/pyversions/modelaudit.svg)](https://pypi.org/project/modelaudit/)
[![Code Style: ruff](https://img.shields.io/badge/code%20style-ruff-005cd7.svg)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/promptfoo/promptfoo)](https://github.com/promptfoo/promptfoo/blob/main/LICENSE)

<img width="989" alt="image" src="https://www.promptfoo.dev/img/docs/modelaudit/modelaudit-result.png" />

📖 **[Full Documentation](https://www.promptfoo.dev/docs/model-audit/)** | 🎯 **[Usage Examples](https://www.promptfoo.dev/docs/model-audit/usage/)** | 🔍 **[Supported Formats](https://www.promptfoo.dev/docs/model-audit/scanners/)**

## 🚀 Quick Start

**Install and scan in 30 seconds:**

```bash
# Install ModelAudit with all ML framework support
pip install modelaudit[all]

# Scan a model file
modelaudit model.pkl

# Scan a directory
modelaudit ./models/

# Export results for CI/CD
modelaudit model.pkl --format json --output results.json
```

**Example output:**

```bash
$ modelaudit suspicious_model.pkl

✓ Scanning suspicious_model.pkl
Files scanned: 1 | Issues found: 2 critical, 1 warning

1. suspicious_model.pkl (pos 28): [CRITICAL] Malicious code execution attempt
   Why: Contains os.system() call that could run arbitrary commands

2. suspicious_model.pkl (pos 52): [WARNING] Dangerous pickle deserialization
   Why: Could execute code when the model loads

✗ Security issues found - DO NOT deploy this model
```

## 🛡️ What Problems It Solves

### **Prevents Code Execution Attacks**

Stops malicious models that run arbitrary commands when loaded (common in PyTorch .pt files)

### **Detects Model Backdoors**

Identifies trojaned models with hidden functionality or suspicious weight patterns

### **Ensures Supply Chain Security**

Validates model integrity and prevents tampering in your ML pipeline

### **Enforces License Compliance**

Checks for license violations that could expose your company to legal risk

### **Finds Embedded Secrets**

Detects API keys, tokens, and other credentials hidden in model weights or metadata

### **Flags Network Communication**

Identifies URLs, IPs, and socket usage that could enable data exfiltration or C2 channels

### **Detects Hidden JIT/Script Execution**

Scans TorchScript, ONNX, and other JIT-compiled code for dangerous operations

## 📊 Supported Model Formats

ModelAudit scans **all major ML model formats** with specialized security analysis for each:

| Format          | Extensions                            | Risk Level | Notes                                        |
| --------------- | ------------------------------------- | ---------- | -------------------------------------------- |
| **PyTorch**     | `.pt`, `.pth`, `.ckpt`, `.bin`        | 🔴 HIGH    | Contains pickle serialization - always scan  |
| **Pickle**      | `.pkl`, `.pickle`, `.dill`            | 🔴 HIGH    | Avoid in production - convert to SafeTensors |
| **Joblib**      | `.joblib`                             | 🔴 HIGH    | Can contain pickled objects                  |
| **Archives**    | `.zip`, `.tar`, `.gz`, `.7z`, `.bz2`  | 🔴 HIGH    | Can contain malicious payloads               |
| **SafeTensors** | `.safetensors`                        | 🟢 SAFE    | Preferred secure format                      |
| **GGUF/GGML**   | `.gguf`, `.ggml`                      | 🟢 SAFE    | LLM standard, binary format                  |
| **ONNX**        | `.onnx`                               | 🟢 SAFE    | Industry standard, good interoperability     |
| **TensorFlow**  | `.pb`, SavedModel                     | 🟠 MEDIUM  | Scan for dangerous operations                |
| **Keras**       | `.h5`, `.keras`, `.hdf5`              | 🟠 MEDIUM  | Check for executable layers                  |
| **JAX/Flax**    | `.msgpack`, `.flax`, `.orbax`, `.jax` | 🟡 LOW     | Validate transforms                          |

Plus 10+ additional formats including ExecuTorch, TensorFlow Lite, Core ML, and more.

[View complete format documentation →](https://www.promptfoo.dev/docs/model-audit/scanners/)

## 🎯 Common Use Cases

### **Pre-Deployment Security Checks**

```bash
modelaudit production_model.safetensors --format json --output security_report.json
```

### **CI/CD Pipeline Integration**

ModelAudit automatically detects CI environments and adjusts output accordingly:

```bash
# Recommended: Use JSON format for machine-readable output
modelaudit models/ --format json --output results.json

# Text output automatically adapts to CI (no spinners, plain text)
modelaudit models/ --timeout 300

# Disable colors explicitly with NO_COLOR environment variable
NO_COLOR=1 modelaudit models/
```

**CI-Friendly Features:**

- 🚫 Spinners automatically disabled when output is piped or in CI
- 🎨 Colors disabled when `NO_COLOR` environment variable is set
- 📊 JSON output recommended for parsing in CI pipelines
- 🔍 Exit codes: 0 (clean), 1 (issues found), 2 (errors)

### **Third-Party Model Validation**

```bash
# Scan models from HuggingFace, PyTorch Hub, MLflow, JFrog, or cloud storage
modelaudit https://huggingface.co/gpt2
modelaudit https://pytorch.org/hub/pytorch_vision_resnet/
modelaudit models:/MyModel/Production
modelaudit model.dvc
modelaudit s3://my-bucket/downloaded-model.pt

# JFrog Artifactory - now supports both files AND folders
# Auth: export JFROG_API_TOKEN=... (or JFROG_ACCESS_TOKEN)
modelaudit https://company.jfrog.io/artifactory/repo/model.pt
# Or with explicit flag:
modelaudit https://company.jfrog.io/artifactory/repo/model.pt --api-token "$JFROG_API_TOKEN"
modelaudit https://company.jfrog.io/artifactory/repo/models/  # Scan entire folder!
```

### **Compliance & Audit Reporting**

```bash
modelaudit model_package.zip --sbom compliance_report.json --strict --verbose
```

### 🧠 Smart Detection Examples

ModelAudit automatically adapts to your input - **no configuration needed for most cases:**

```bash
# Local file - fast scan, no progress bars
modelaudit model.pkl

# Cloud directory - auto enables caching + progress bars
modelaudit s3://my-bucket/models/

# HuggingFace model - selective download + caching
modelaudit hf://microsoft/DialoGPT-medium

# Large local file - enables progress + optimizations
modelaudit 15GB-model.bin

# CI environment - auto detects and uses JSON output
CI=true modelaudit model.pkl
```

**Override smart detection when needed:**

```bash
# Force strict mode for security-critical scans
modelaudit model.pkl --strict --format json --output report.json

# Override size limits for huge models
modelaudit huge-model.pt --max-size 50GB --timeout 7200

# Preview mode without downloading
modelaudit s3://bucket/model.pt --dry-run
```

[View advanced usage examples →](https://www.promptfoo.dev/docs/model-audit/usage/)

### ⚙️ Smart Detection & CLI Options

ModelAudit uses **smart detection** to automatically configure optimal settings based on your input:

**✨ Smart Detection Features:**

- **Input type** (local/cloud/registry) → optimal download & caching strategies
- **File size** (>1GB) → large model optimizations + progress bars
- **Terminal type** (TTY/CI) → appropriate UI (progress vs quiet mode)
- **Cloud operations** → automatic caching, size limits, timeouts

**🎛️ Override Controls (13 focused flags):**

- `--strict` – scan all file types, strict license validation, fail on warnings
- `--max-size SIZE` – unified size limit (e.g., `10GB`, `500MB`)
- `--timeout SECONDS` – override auto-detected timeout
- `--dry-run` – preview what would be scanned/downloaded
- `--progress` – force enable progress reporting
- `--no-cache` – disable caching (overrides smart detection)
- `--format json` / `--output file.json` – structured output for CI/CD
- `--sbom file.json` – generate CycloneDX v1.6 SBOM with enhanced ML-BOM support
- `--verbose` / `--quiet` – control output detail level
- `--blacklist PATTERN` – additional security patterns

**🔐 Authentication (via environment variables):**

- Set `JFROG_API_TOKEN` or `JFROG_ACCESS_TOKEN` for JFrog Artifactory
- Set `MLFLOW_TRACKING_URI` for MLflow registry access

### 🚀 Large Model Support (Up to 1 TB)

ModelAudit automatically optimizes scanning strategies for different model sizes:

- **< 100 GB**: Full in-memory analysis for comprehensive scanning
- **100 GB - 1 TB**: Chunked processing with 50 GB chunks for memory efficiency
- **1 TB - 5 TB**: Streaming analysis with intelligent sampling
- **> 5 TB**: Advanced distributed scanning techniques

Large models are supported with automatic timeout increases and memory-optimized processing.

### Static Scanning vs. Promptfoo Redteaming

ModelAudit performs **static** analysis only. It examines model files for risky patterns
without ever loading or executing them. Promptfoo's redteaming module is
**dynamic**—it loads the model (locally or via API) and sends crafted prompts to
probe runtime behavior. Use ModelAudit first to verify the model file itself,
then run redteaming if you need to test how the model responds when invoked.

## ⚙️ Installation Options

**Requirements:**

- Python 3.10 or higher
- Compatible with Python 3.10, 3.11, 3.12, and 3.13

**Basic installation (recommended for most users):**

### Quick Install Decision Guide

**🚀 Just want everything to work?**

```bash
pip install modelaudit[all]
```

**Basic installation:**

```bash
# Core functionality only (pickle, numpy, archives)
pip install modelaudit
```

**Specific frameworks:**

```bash
pip install modelaudit[tensorflow]  # TensorFlow (.pb)
pip install modelaudit[pytorch]     # PyTorch (.pt, .pth)
pip install modelaudit[h5]          # Keras (.h5, .keras)
pip install modelaudit[onnx]        # ONNX (.onnx)
pip install modelaudit[safetensors] # SafeTensors (.safetensors)

# Multiple frameworks
pip install modelaudit[tensorflow,pytorch,h5]
```

**Additional features:**

```bash
pip install modelaudit[cloud]       # S3, GCS, Azure storage
pip install modelaudit[coreml]      # Apple Core ML
pip install modelaudit[flax]        # JAX/Flax models
pip install modelaudit[mlflow]      # MLflow registry
pip install modelaudit[huggingface] # Hugging Face integration
```

**Compatibility:**

```bash
# NumPy 1.x compatibility (some frameworks require NumPy < 2.0)
pip install modelaudit[numpy1]

# For CI/CD environments (omits dependencies like TensorRT that may not be available)
pip install modelaudit[all-ci]
```

**Docker:**

```bash
docker pull ghcr.io/promptfoo/modelaudit:latest
# Linux/macOS
docker run --rm -v "$(pwd)":/app ghcr.io/promptfoo/modelaudit:latest model.pkl
# Windows
docker run --rm -v "%cd%":/app ghcr.io/promptfoo/modelaudit:latest model.pkl
```

## Security Checks

### Code Execution Detection

- Dangerous Python modules: `os`, `sys`, `subprocess`, `eval`, `exec`
- Pickle opcodes: `REDUCE`, `GLOBAL`, `INST`, `OBJ`, `NEWOBJ`, `STACK_GLOBAL`, `BUILD`, `NEWOBJ_EX`
- Embedded executable file detection

### Embedded Data Extraction

- API keys, tokens, and credentials in model weights/metadata
- URLs, IP addresses, and network endpoints
- Suspicious configuration properties

### Archive Security

- Path traversal attacks in ZIP/TAR archives
- Executable files within model packages
- Malicious filenames and directory structures

### ML Framework Analysis

- TensorFlow operations: `PyFunc`, `PyFuncStateless`
- Keras unsafe layers and custom objects
- Template injection in model configurations

### Context-Aware Analysis

- Intelligently distinguishes between legitimate ML framework patterns and genuine threats to reduce false positives in complex model files

## Supported Formats

ModelAudit includes 29 specialized scanners for ML model formats ([see complete list](https://www.promptfoo.dev/docs/model-audit/scanners/)):

| Format          | Extensions                                | Security Focus                                     |
| --------------- | ----------------------------------------- | -------------------------------------------------- |
| **Pickle**      | `.pkl`, `.pickle`, `.dill`, `.pt`, `.pth` | Code execution, malicious opcodes, deserialization |
| **Archives**    | `.zip`, `.tar`, `.gz`, `.7z`, `.bz2`      | Path traversal, embedded executables               |
| **TensorFlow**  | `.pb`, SavedModel directories             | Dangerous operations, custom ops                   |
| **Keras**       | `.h5`, `.keras`, `.hdf5`                  | Unsafe layers, custom objects                      |
| **ONNX**        | `.onnx`                                   | Custom operators, metadata                         |
| **SafeTensors** | `.safetensors`                            | Header validation, metadata                        |
| **GGUF/GGML**   | `.gguf`, `.ggml`                          | Header validation, metadata                        |
| **Joblib**      | `.joblib`                                 | Pickled objects, scikit-learn                      |
| **JAX/Flax**    | `.msgpack`, `.flax`, `.orbax`             | Serialized transforms                              |
| **NumPy**       | `.npy`, `.npz`                            | Array metadata, pickle objects                     |
| **Core ML**     | `.mlmodel`                                | Custom layers, metadata                            |
| **ExecuTorch**  | `.ptl`, `.pte`                            | Mobile model validation                            |

Plus scanners for TensorFlow Lite, TensorRT, PaddlePaddle, OpenVINO, text files, and configuration formats.

[Complete format documentation →](https://www.promptfoo.dev/docs/model-audit/scanners/)

## Usage Examples

### Basic Scanning

```bash
# Scan single file
modelaudit model.pkl

# Scan directory
modelaudit ./models/

# Strict mode (fail on warnings)
modelaudit model.pkl --strict
```

### CI/CD Integration

```bash
# JSON output for automation
modelaudit models/ --format json --output results.json

# Generate SBOM report
modelaudit model.pkl --sbom compliance_report.json

# Disable colors in CI
NO_COLOR=1 modelaudit models/
```

### Remote Sources

```bash
# Hugging Face models (via direct URL or hf:// scheme)
modelaudit https://huggingface.co/gpt2
modelaudit hf://microsoft/DialoGPT-medium

# Cloud storage
modelaudit s3://bucket/model.pt
modelaudit gs://bucket/models/
modelaudit https://account.blob.core.windows.net/container/model.pt

# MLflow registry
modelaudit models:/MyModel/Production

# JFrog Artifactory (files and folders)
modelaudit https://company.jfrog.io/artifactory/repo/model.pt      # Single file
modelaudit https://company.jfrog.io/artifactory/repo/models/       # Entire folder
```

### Command Options

- **`--format`** - Output format: text, json, sarif
- **`--output`** - Write results to file
- **`--verbose`** - Detailed output
- **`--quiet`** - Minimal output
- **`--strict`** - Fail on warnings, scan all files
- **`--timeout`** - Override scan timeout
- **`--max-size`** - Set size limits (e.g., 10 GB)
- **`--dry-run`** - Preview without scanning
- **`--progress`** - Force progress display
- **`--sbom`** - Generate CycloneDX SBOM
- **`--blacklist`** - Additional patterns to flag
- **`--no-cache`** - Disable result caching

[Advanced usage examples →](https://www.promptfoo.dev/docs/model-audit/usage/)

## Output Formats

### Text (default)

```text
$ modelaudit model.pkl

✓ Scanning model.pkl
Files scanned: 1 | Issues found: 1 critical

1. model.pkl (pos 28): [CRITICAL] Malicious code execution attempt
   Why: Contains os.system() call that could run arbitrary commands
```

### JSON (for automation)

```bash
modelaudit model.pkl --format json
```

```json
{
  "files_scanned": 1,
  "issues": [
    {
      "message": "Malicious code execution attempt",
      "severity": "critical",
      "location": "model.pkl (pos 28)"
    }
  ]
}
```

### SARIF (for security tools)

```bash
modelaudit model.pkl --format sarif --output results.sarif
```

## Troubleshooting

### Check scanner availability

```bash
modelaudit doctor --show-failed
```

### NumPy compatibility issues

```bash
# Use NumPy 1.x compatibility mode
pip install modelaudit[numpy1]
```

### Missing dependencies

```bash
# ModelAudit shows exactly what to install
modelaudit your-model.onnx
# Output: "Install with 'pip install modelaudit[onnx]'"
```

### Exit Codes

- `0` - No security issues found
- `1` - Security issues detected
- `2` - Scan errors occurred

### Authentication

ModelAudit uses environment variables for authenticating to remote services:

```bash
# JFrog Artifactory
export JFROG_API_TOKEN=your_token

# MLflow
export MLFLOW_TRACKING_URI=http://localhost:5000

# AWS, Google Cloud, and Azure
# Authentication is handled automatically by the respective client libraries
# (e.g., via IAM roles, `aws configure`, `gcloud auth login`, or environment variables).
# For specific env var setup, refer to the library's documentation.
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Hugging Face
export HF_TOKEN=your_token
```

## Documentation

- **Documentation**: [promptfoo.dev/docs/model-audit/](https://www.promptfoo.dev/docs/model-audit/)
- **Usage Examples**: [promptfoo.dev/docs/model-audit/usage/](https://www.promptfoo.dev/docs/model-audit/usage/)
- **Report Issues**: Contact support at [promptfoo.dev](https://www.promptfoo.dev/)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
