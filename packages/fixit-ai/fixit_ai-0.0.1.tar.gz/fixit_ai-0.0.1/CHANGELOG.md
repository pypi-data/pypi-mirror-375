# Changelog

All notable changes to Fixit.AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2025-09-07

### Added
- 🚀 **Zero-Config FastAPI Integration**: Automatic OpenAPI spec discovery and test generation
- 🟢 **Express.js Support**: Full integration with OpenAPI-documented Express.js applications
- 🤖 **AI-Powered Analysis**: Local LLM integration for intelligent failure analysis and code suggestions
- 🛡️ **Security Scanning**: Built-in OWASP API Security Top 10 vulnerability detection
- 📊 **Rich HTML Reports**: Beautiful, interactive test result dashboards
- ⚡ **Parallel Test Execution**: Multi-threaded testing for faster feedback
- 🔧 **Code Patches**: AI-generated code fixes for common API issues
- 🎯 **Framework Support**: Native support for FastAPI, Express.js, and universal OpenAPI compatibility

### Features
- **CLI Commands**:
  - `fixit init` - Initialize workspace with zero-config onboarding
  - `fixit gen` - Generate comprehensive test suites from OpenAPI specs
  - `fixit test` - Run tests with AI-powered failure analysis
  - `fixit sec` - Security vulnerability scanning
  - `fixit fix` - AI-powered code suggestions

- **AI Integration**:
  - LM Studio support for local LLM inference
  - Ollama integration for CLI-based model management
  - llama.cpp direct integration for resource-constrained environments
  - Recommended ChatGPT OSS models for hackathon compliance

- **Security Features**:
  - OWASP API Security Top 10 coverage
  - Authentication/Authorization flaw detection
  - Input validation vulnerability scanning
  - Data exposure prevention checks
  - Rate limiting validation

- **Framework Support**:
  - ✅ FastAPI: Zero-config, auto-discovery, code patches
  - ✅ Express.js: OpenAPI-based integration with full feature support
  - ⚡ Django REST: Via OpenAPI spec with drf-spectacular
  - ⚡ Flask: Via OpenAPI spec with flask-restx
  - ⚡ Spring Boot: Via OpenAPI spec with springdoc-openapi

### Technical Implementation
- **Core Package**: Modular architecture with separate CLI, core, spec, gen, run, sec, and AI modules
- **Testing Engine**: Built on pytest with custom runners and reporters
- **Spec Processing**: Advanced OpenAPI 3.0+ parsing with validation and enhancement
- **AI Backend**: Flexible adapter pattern supporting multiple LLM providers
- **Report Generation**: HTML and JSON output with rich formatting

### Dependencies
- **Core**: typer, rich, httpx, requests, pytest, jinja2, pydantic, prance, schemathesis
- **AI Integration**: openai (for LM Studio), ollama, llama-cpp-python
- **Development**: black, ruff, mypy, pytest-cov, pre-commit, deptry

### Documentation
- 📚 Comprehensive README with quick start guides
- 🛠️ Framework integration guide for all supported platforms
- 🤖 AI integration guide with local LLM setup instructions
- 🔧 CLI reference documentation
- 📦 PyPI package with proper metadata and classifiers

### Package Information
- **Name**: fixit-ai
- **License**: MIT License
- **Python Support**: 3.11, 3.12, 3.13
- **Package Size**: ~68KB wheel, ~57KB source distribution
- **Dependencies**: 13 core + 61 transitive dependencies
- **Entry Points**: `fixit` console script for CLI access

---

## Development History

### Pre-Release Development
- Initial FastAPI integration and zero-config onboarding
- LLM integration with LM Studio and Ollama
- Security scanning implementation with OWASP coverage
- Express.js support with OpenAPI documentation requirements
- Comprehensive test suite with unit, integration, and e2e tests
- AI-powered failure analysis and code suggestion features
- Rich CLI with progress indicators and colored output
- HTML report generation with interactive dashboards

### Testing & Validation
- ✅ Clean-room installation testing in isolated environments
- ✅ Full dependency resolution validation (74 packages)
- ✅ CLI functionality verification across all commands
- ✅ Import validation for all package modules
- ✅ Package building and distribution testing
- ✅ Cross-platform compatibility (Windows, Linux, macOS)

---

## Contributors

- **[@Ashiiish-88](https://github.com/Ashiiish-88)**
- **[@Gauri727](https://github.com/Gauri727)**
- **[@khushali2502](https://github.com/khushali2502)**
- **[@ommo007](https://github.com/ommo007)**

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*For the complete list of changes and detailed technical information, visit our [GitHub repository](https://github.com/Fixit-Local-AI-Agent/Fixit.AI).*
