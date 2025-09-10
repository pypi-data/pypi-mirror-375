# 🔧 Fixit.AI

[![PyPI version](https://badge.fury.io/py/fixit-ai.svg)](https://badge.fury.io/py/fixit-ai)
[![Python Support](https://img.shields.io/pypi/pyversions/fixit-ai.svg)](https://pypi.org/project/fixit-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Fixit-Local-AI-Agent/Fixit.AI.svg)](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Fixit-Local-AI-Agent/Fixit.AI.svg)](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/issues)

> **AI-Powered API Testing Agent with Zero-Config Onboarding for OpenAPI-First Development**

**Fixit.AI** is an offline-first API testing platform that automatically generates comprehensive test suites, detects security vulnerabilities, and provides AI-powered failure analysis. Built for modern API development with native support for **FastAPI** and **Express.js**.

## 🌟 Key Features

- **🚀 Zero-Config Onboarding** - Start testing in seconds with automatic spec discovery
- **🤖 AI-Powered Analysis** - Intelligent failure detection and code suggestions  
- **🔒 Security-First** - Built-in vulnerability scanning and OWASP compliance
- **📊 Rich Reporting** - Beautiful HTML reports with detailed analytics
- **⚡ Offline-First** - Works entirely on your machine with local LLMs
- **🛠️ Smart Patching** - Automated code fixes for common API issues

## 🎯 Perfect For

**API Developers** • **QA Engineers** • **DevOps Teams** • **Startups**

---

## ⚡ Quick Start

### Installation
```bash
pip install fixit-ai

or 

# Clean installation (recommended)
pip install fixit-ai --quiet
```

### FastAPI (Zero-Config)
```bash
# Start your FastAPI app
uvicorn main:app --reload

# Test with zero configuration
fixit init --fastapi main:app --base http://localhost:8000
fixit gen && fixit test && fixit fix && fixit sec
```

### Express.js
```bash
# Start your Express.js app with OpenAPI
node app.js

# Test your Express.js API
fixit init --express . --base http://localhost:3000
fixit gen && fixit test && fixit fix && fixit sec
```

### Universal (Any OpenAPI Framework)
```bash
fixit init --spec openapi.yaml --base http://localhost:8000
fixit gen && fixit test && fixit fix && fixit sec
```

## 🎯 What Fixit.AI Does

| Step | Command | What Happens |
|------|---------|--------------|
| **Initialize** | `fixit init` | 🔍 Auto-extracts OpenAPI spec, creates `fixit.toml` with LLM defaults |
| **Generate** | `fixit gen` | 📝 Creates comprehensive test suite covering all endpoints |
| **Test** | `fixit test` | 🧪 Runs tests with real-time AI analysis of failures |
| **Fix** | `fixit fix` | 🛠️ Shows AI-generated code patches (suggestions-only by default) |
| **Secure** | `fixit sec` | 🔒 Scans for OWASP API Security Top 10 vulnerabilities |

## 🤖 AI Integration

Fixit.AI works with **local LLMs** for private, offline analysis:

### Quick Setup (LM Studio)
1. **Download** [LM Studio](https://lmstudio.ai/)
2. **Install model**: `GPT-OSS 20B`
3. **Start server** on `localhost:1234`
4. **Run**: `fixit test` (auto-detects LM Studio)

### Alternative (Ollama)
```bash
# Install and setup
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3:mini

# Configure (optional - auto-detected)
fixit init --llm-provider ollama --llm-model phi3:mini
```

## 📋 Framework Support

| Framework | Language | Zero-Config | Code Patches | Security Scan |
|-----------|----------|-------------|--------------|---------------|
| **FastAPI** | Python | ✅ | ✅ | ✅ |
| **Express.js** | Node.js | ✅ | ✅ | ✅ |
| **Any OpenAPI 3.0+** | Any | ✅ | ✅ | ✅ |

## ⚙️ Configuration

**Auto-Generated `fixit.toml`** (created on first run):
```toml
llm_active = "llm"
openapi = "openapi.yaml"

[llm]
provider = "lmstudio"
# base_url = "http://localhost:11434/v1" # Ollama
base_url = "http://localhost:1234/v1"    # LM Studio
model = "gpt-oss20B"
temperature = 0.0
max_tokens = 2048
timeout_seconds = 180
offline = true
api_key_env = "FIXIT_API_KEY"

[llm.demo]
provider = "llama.cpp-stub"

[test]
include = []
exclude = []
max_tests = 0
concurrency = 8
```

**Override during init**:
```bash
fixit init --fastapi main:app --base http://localhost:8000 \
  --llm-provider ollama --llm-model phi3:mini
```

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `fixit init --fastapi main:app` | Initialize FastAPI project (zero-config) |
| `fixit init --express .` | Initialize Express.js project |
| `fixit init --spec openapi.yaml` | Initialize with existing OpenAPI spec |
| `fixit gen` | Generate comprehensive test suite |
| `fixit test` | Run tests with AI analysis |
| `fixit fix` | Show AI code suggestions |
| `fixit sec` | Security vulnerability scan |

## 🚀 Getting Started Checklist

- [ ] **Install**: `pip install fixit-ai`
- [ ] **Choose framework**: FastAPI (zero-config) or Express.js  
- [ ] **Initialize**: `fixit init --fastapi main:app --base http://localhost:8000`
- [ ] **Generate tests**: `fixit gen`
- [ ] **Run tests**: `fixit test`
- [ ] **Review suggestions**: `fixit fix`
- [ ] **Security scan**: `fixit sec`
- [ ] **View report**: Open `.fixit/reports/index.html`

## 🔍 Example Output

**Real-time AI Analysis:**
```bash
$ fixit test
🧪 Running 7 tests...
❌ 3 failures detected

🤖 AI Analysis:
[1/3] Analyzing post_/users_validation_error... 🆕 (fresh)
[2/3] Analyzing get_/users/{id}_not_found... 💾 (cached)
[3/3] Analyzing post_/auth/login_unauthorized... 🆕 (fresh)

$ fixit fix
💡 3 AI-generated suggestions:
✨ Fix email validation in UserCreate model
✨ Add proper 404 error handling
✨ Implement JWT token validation
```

## 🔗 Resources

- **📚 [Full Documentation](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/wiki)** - Comprehensive guides and tutorials
- **🐛 [Issues](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/issues)** - Bug reports and feature requests  
- **💬 [Discussions](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/discussions)** - Community support and Q&A
- **⭐ [GitHub](https://github.com/Fixit-Local-AI-Agent/Fixit.AI)** - Source code and examples

## 📄 License

MIT License - see [LICENSE](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/blob/main/LICENSE) for details.

---

<div align="center">

**Made with ❤️ by the Fixit.AI team**

⭐ **Star us on GitHub** • 🐛 **Report Issues** • 💬 **Join Discussions**

[GitHub](https://github.com/Fixit-Local-AI-Agent/Fixit.AI) • [PyPI](https://pypi.org/project/fixit-ai/) • [Documentation](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/wiki)

</div>