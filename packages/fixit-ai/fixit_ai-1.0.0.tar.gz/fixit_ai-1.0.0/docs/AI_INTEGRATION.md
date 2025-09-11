# 🤖 AI Integration Guide

This guide covers how to integrate Fixit.AI with local Large Language Models (LLMs) for intelligent API testing, failure analysis, and code suggestions.

## 🎯 Why Local LLMs?

- **🔒 Privacy**: Your code and API data never leaves your machine
- **⚡ Speed**: No network latency for AI analysis
- **💰 Cost**: No API usage fees or rate limits
- **🛠️ Customizable**: Use models optimized for code analysis

---

## 🏆 Recommended Models

For **AI-powered API testing**, we recommend **GPT-OSS compatible models**:

### 🥇 Top Recommendations

| Model | Size | Performance | Setup Time | Best For |
|-------|------|-------------|------------|----------|
| **GPT-OSS 20B** | **Model Selection**

**For Best Analysis:**
- **GPT-OSS 20B**: Highest quality analysis and code suggestions
- **Gemma2-14B**: Excellent balanced performance
- **DeepSeek Coder 14B**: Best for code-specific analysis

**For Quick Development:**
- **Gemma2-7B**: Good balance of speed and quality
- **DeepSeek Coder 7B**: Fast code analysis
- **Phi-3-mini**: Fastest setup and executionanding | < 15 min | Production Analysis |
| **Gemma2-7B** | 7B | Excellent | < 10 min | Balanced Performance |
| **Gemma2-14B** | 14B | Outstanding | < 15 min | High-Quality Analysis |
| **DeepSeek Coder 7B** | 7B | Excellent | < 10 min | Code-Focused Tasks |
| **DeepSeek Coder 14B** | 14B | Outstanding | < 15 min | Advanced Code Analysis |
| **Phi-3-mini** | 3.8B | Good | < 5 min | Quick Setup |

### 🎯 Quick Setup Recommendations

**For Best Results (Recommended):**
```bash
# Download GPT-OSS 20B model via LM Studio
# Search for: "gpt-oss-20b" or similar in LM Studio model library
```

**For Fast Development:**
```bash
# Ollama setup with recommended models
ollama pull gemma2:7b
ollama pull deepseek-coder:7b
```

---

## 🖥️ LM Studio Setup (Recommended)

### Step 1: Download and Install

1. **Download LM Studio**: Visit [lmstudio.ai](https://lmstudio.ai/)
2. **Install**: Follow platform-specific installation
3. **Launch**: Open LM Studio application

### Step 2: Download a Model

**Recommended Models:**
```
Search and download one of these models:
📦 GPT-OSS-20B (Recommended for best analysis)
📦 google/gemma-2-7b-it-gguf
📦 deepseek-ai/deepseek-coder-7b-instruct-gguf
📦 microsoft/Phi-3-mini-4k-instruct-gguf (Fast setup)
```

**For Advanced Analysis:**
```
📦 GPT-OSS-20B (Best quality)
📦 google/gemma-2-14b-it-gguf
📦 deepseek-ai/deepseek-coder-14b-instruct-gguf
```

### Step 3: Configure LM Studio Settings

1. **Load Model**: Click on your downloaded model
2. **Set Preset**: Use these optimal settings for Fixit.AI:
   
   **Temperature**: `0.20`
   
   **System Prompt**: 
   ```
   Return ONLY a valid JSON object that matches the requested structure. No markdown, no code fences, no comments, no extra fields. Keep JSON short and end with '}'
   ```
   
   **Structured Output**: Enable JSON mode with this schema:
   ```json
   {
     "type": "json",
     "jsonSchema": {
       "type": "object",
       "required": [
         "test_id",
         "failure_type", 
         "root_cause",
         "fix_suggestions",
         "confidence_score",
         "timestamp"
       ],
       "properties": {
         "test_id": {
           "type": "string"
         },
         "failure_type": {
           "type": "string",
           "enum": [
             "assertion_error",
             "type_error", 
             "value_error",
             "http_error",
             "connection_error",
             "timeout",
             "permission_error",
             "unknown"
           ]
         },
         "root_cause": {
           "type": "object",
           "required": [
             "summary",
             "details"
           ],
           "properties": {
             "summary": {
               "type": "string"
             },
             "details": {
               "type": "string"
             }
           }
         },
         "fix_suggestions": {
           "type": "array",
           "minItems": 1,
           "maxItems": 1,
           "items": {
             "type": "object",
             "required": [
               "description",
               "code_changes",
               "priority"
             ],
             "properties": {
               "description": {
                 "type": "string"
               },
               "code_changes": {
                 "type": "array",
                 "minItems": 1,
                 "maxItems": 1,
                 "items": {
                   "type": "object",
                   "required": [
                     "file",
                     "change_type"
                   ],
                   "properties": {
                     "file": {
                       "type": "string"
                     },
                     "change_type": {
                       "type": "string",
                       "enum": [
                         "add",
                         "modify",
                         "delete"
                       ]
                     }
                   }
                 }
               },
               "priority": {
                 "type": "string",
                 "enum": [
                   "high",
                   "medium",
                   "low"
                 ]
               }
             }
           }
         },
         "confidence_score": {
           "type": "number",
           "minimum": 0,
           "maximum": 1
         },
         "timestamp": {
           "type": "string",
           "format": "date-time"
         }
       }
     }
   }
   ```

3. **Start Server**: Click "Start Server" 
4. **Verify**: Server runs on `http://localhost:1234`

### Step 4: Configure Fixit.AI

```bash
# Initialize your project
fixit init --fastapi main:app --base http://localhost:8000

# Edit .fixit/config.yaml to add LLM configuration
```

Add to `.fixit/config.yaml`:
```yaml
# .fixit/config.yaml
spec:
  path: "auto-discovered"
  base_url: "http://localhost:8000"

llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "gpt-oss-20b"  # Use the actual model name loaded in LM Studio
  temperature: 0.20     # Optimized for structured output
  max_tokens: 2048
  
  # AI analysis features
  features:
    failure_analysis: true
    code_suggestions: true
    security_insights: true

testing:
  parallel_workers: 4
  timeout_seconds: 30
  retry_attempts: 3
```

### Step 5: Test AI Integration

```bash
# Run tests with AI analysis
fixit test --verbose

# Generate AI-powered test cases
fixit gen

# Get AI code improvement suggestions
fixit fix
```

**Expected Output with AI:**
```
🤖 AI Analysis Enabled (GPT-OSS via LM Studio)

🧪 Running tests...
❌ POST /users/ failed (400 Bad Request)

🤖 AI Analysis:
The endpoint is rejecting the request due to email validation. 
The API expects a valid email format but received 'test@'. 
Suggestion: Update email validation in UserCreate model to be more permissive 
for testing or fix test data generation.

💡 Code Suggestion:
# In your FastAPI model
class UserCreate(BaseModel):
    email: EmailStr = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    
# Or in test data generation
test_email = fake.email()  # Use faker for valid emails
```

---

## 🐋 Ollama Setup (CLI Alternative)

### Step 1: Install Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
```powershell
# Download from https://ollama.ai/download/windows
# Or use winget
winget install Ollama.Ollama
```

### Step 2: Download Models

**Quick Start:**
```bash
# Fast, efficient model
ollama pull gemma2:7b

# Code-focused model  
ollama pull deepseek-coder:7b

# High quality analysis
ollama pull gemma2:14b
```

**Model Comparison:**
```bash
# List available models
ollama list

# Model sizes and capabilities:
gemma2:7b           - 4.3GB - Balanced performance
deepseek-coder:7b   - 3.8GB - Best for code analysis  
gemma2:14b          - 8.2GB - High quality analysis
gpt-oss             - Varies - OpenAI-compatible models
```

### Step 3: Start Ollama Service

```bash
# Start Ollama service
ollama serve

# Verify it's running
curl http://localhost:11434/api/version
```

### Step 4: Configure Fixit.AI

Add to `.fixit/config.yaml`:
```yaml
llm:
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "gemma2:7b"  # or deepseek-coder:7b, gemma2:14b
  temperature: 0.20   # Optimized for accurate analysis
  max_tokens: 2048

  # Model-specific optimizations
  options:
    num_ctx: 4096      # Context window
    num_predict: 512   # Max response length
    temperature: 0.7   # Creativity vs accuracy
    top_k: 40         # Token selection diversity
    top_p: 0.9        # Nucleus sampling
```

### Step 5: Test Integration

```bash
# Test Ollama connection
ollama run gemma2:7b "Explain this API error: 422 Unprocessable Entity"

# Run Fixit.AI with AI analysis
fixit test --verbose
```

---

## 🛠️ llama.cpp Setup (Advanced)

For **resource-constrained environments** or **custom model optimization**:

### Step 1: Install llama.cpp

```bash
# Clone and build
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Or install pre-built binaries
pip install llama-cpp-python[server]
```

### Step 2: Download GGUF Models

```bash
# Download models in GGUF format
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_k_m.gguf

# Or download GPT-OSS compatible models
wget https://huggingface.co/google/gemma-2-7b-it-gguf/resolve/main/gemma-2-7b-it-q4_k_m.gguf
```

### Step 3: Start Server

```bash
# Start llama.cpp server with GPT-OSS compatible model
python -m llama_cpp.server \
  --model gemma-2-7b-it-q4_k_m.gguf \
  --host localhost \
  --port 8080 \
  --n_ctx 4096

# Or with Phi-3 for faster setup
python -m llama_cpp.server \
  --model Phi-3-mini-4k-instruct-q4_k_m.gguf \
  --host localhost \
  --port 8080 \
  --n_ctx 4096
```

### Step 4: Configure Fixit.AI

```yaml
# .fixit/config.yaml
llm:
  provider: "llama_cpp"
  base_url: "http://localhost:8080"
  model: "gemma-2-7b"  # or "phi-3-mini"
  temperature: 0.20    # Optimized for structured analysis
  max_tokens: 1024
```

---

## 🎯 AI Features in Fixit.AI

### 🔍 Failure Analysis

**What it does:**
- Analyzes failed test cases
- Identifies root causes
- Suggests specific fixes
- Provides code examples

**Example Analysis:**
```bash
fixit test --ai-analysis

# Output:
🤖 AI Analysis: Authentication Failure
❌ POST /users/ -> 401 Unauthorized

🔍 Root Cause Analysis:
The endpoint requires Bearer token authentication but the test is not 
providing credentials. The API expects 'Authorization: Bearer <token>' header.

💡 Suggested Fix:
1. Add authentication setup in test:
   headers = {"Authorization": "Bearer test-token"}
   
2. Or configure test authentication in .fixit/config.yaml:
   testing:
     auth_header: "Authorization: Bearer test-token"
     
3. Check if endpoint should be public and remove security requirement.
```

### 🛡️ Security Insights

**Enhanced vulnerability detection:**
```bash
fixit sec

# Output:
🤖 AI Security Analysis  
🔍 Scanning for OWASP API Security Top 10...

⚠️  API1:2023 - Broken Object Level Authorization
Location: GET /users/{user_id}
Issue: No access control validation for user resource access
AI Insight: Any authenticated user can access any user's data by changing 
the user_id parameter. This violates the principle of least privilege.

💡 Recommended Fix:
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Access denied")
    return get_user_by_id(user_id)
```

### 🔧 Code Suggestions

**Intelligent code improvements:**
```bash
fixit fix

# Output:
🤖 AI Code Analysis
📁 Analyzing: main.py

💡 Suggestion 1: Add Input Validation
Location: POST /users/ endpoint
Current Code:
  def create_user(user: UserCreate):
      return User(**user.dict())

Improved Code:
  from pydantic import validator
  
  class UserCreate(BaseModel):
      name: str = Field(..., min_length=1, max_length=100)
      email: EmailStr
      age: int = Field(..., ge=0, le=120)
      
      @validator('name')
      def name_must_not_be_empty(cls, v):
          if not v.strip():
              raise ValueError('Name cannot be empty')
          return v.strip()

💡 Suggestion 2: Add Error Handling
Location: GET /users/{user_id}
Add try-catch for database errors and return appropriate HTTP status codes.
```

### 📊 Performance Analysis

**AI-powered testing insights:**
```bash
fixit test --verbose

# Output:
🤖 AI Performance Analysis
⏱️  Response Time Analysis:

🐌 Slow Endpoint Detected: GET /users/
Average: 2.3s (Target: <200ms)
P95: 4.1s

🔍 AI Analysis:
The endpoint is likely performing N+1 queries or missing database indexes.
The response time increases linearly with user count, suggesting inefficient 
data loading.

💡 Optimization Suggestions:
1. Add database index: CREATE INDEX idx_users_active ON users(active);
2. Use select_related() for foreign key relationships
3. Implement pagination: ?page=1&limit=20
4. Add caching for frequently accessed data
```

---

## ⚙️ Advanced Configuration

### Model-Specific Optimizations

**For Code Analysis (DeepSeek Coder):**
```yaml
llm:
  provider: "ollama"
  model: "deepseek-coder:7b"
  temperature: 0.20  # Lower for more precise code analysis
  max_tokens: 2048
  
  prompts:
    code_analysis: |
      You are an expert API developer. Analyze this code for:
      1. Security vulnerabilities
      2. Performance issues  
      3. Best practices violations
      4. Potential bugs
      
      Provide specific, actionable suggestions with code examples.
```

**For Security Analysis (Specialized prompt):**
```yaml
llm:
  model: "gemma2:7b"
  temperature: 0.10  # Very low for security analysis
  
  prompts:
    security_analysis: |
      You are a cybersecurity expert specializing in API security.
      Analyze this API for OWASP API Security Top 10 vulnerabilities:
      
      Focus on:
      - Authentication and authorization flaws
      - Input validation issues
      - Data exposure risks
      - Rate limiting problems
      
      Provide specific remediation steps.
```

### Performance Tuning

**GPU Acceleration (if available):**
```yaml
llm:
  provider: "ollama"
  model: "gemma2:14b"
  
  # GPU settings
  options:
    num_gpu: 1          # Use GPU layers
    num_ctx: 8192       # Larger context with GPU
    num_predict: 1024   # More detailed responses
```

**CPU Optimization:**
```yaml
llm:
  provider: "ollama"
  model: "gemma2:7b"
  
  # CPU-optimized settings
  options:
    num_ctx: 2048       # Smaller context for speed
    num_predict: 512    # Shorter responses
    num_thread: 8       # Match CPU cores
```

### Custom Prompts

**Create custom analysis prompts:**
```yaml
llm:
  prompts:
    custom_failure_analysis: |
      You are analyzing API test failures for a {framework} application.
      
      Test Details:
      - Endpoint: {endpoint}
      - Method: {method}
      - Status: {status_code}
      - Error: {error_message}
      - Request: {request_data}
      - Response: {response_data}
      
      Please provide:
      1. Root cause analysis
      2. Specific fix suggestions
      3. Prevention strategies
      4. Code examples if applicable
      
      Keep suggestions practical and framework-specific.
```

---

## 🚀 Integration Examples

### FastAPI + AI Analysis

```python
# main.py with intentional issues for AI to catch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str  # AI will suggest EmailStr
    password: str  # AI will flag security issue

users = []

@app.post("/users/")
async def create_user(user: User):
    # AI will flag: no input validation, password in response
    users.append(user)
    return user  # Returns password - security issue!

@app.get("/users/{user_id}")
async def get_user(user_id: str):  # AI will suggest int type
    # AI will flag: no error handling, type mismatch
    return users[int(user_id)]
```

**Run AI analysis:**
```bash
fixit init --fastapi main:app --base http://localhost:8000
fixit test --verbose
fixit fix
```

**Expected AI Feedback:**
```
🤖 Security Issues Detected:
1. Password returned in response (data exposure)
2. No input validation on user_id parameter
3. Plain text password storage

🤖 Code Quality Issues:
1. user_id should be int type, not str
2. Missing error handling for invalid user_id
3. Missing email validation

💡 AI Suggestions Applied:
- Use EmailStr for email validation
- Add response model without password
- Add proper error handling
- Implement password hashing
```

### Express.js + AI Analysis

```javascript
// app.js with issues for AI to analyze
const express = require('express');
const app = express();

app.use(express.json());

let users = [];

app.post('/users', (req, res) => {
    // AI will flag: no validation, no error handling
    const user = req.body;
    user.id = Date.now(); // AI will suggest better ID generation
    users.push(user);
    res.json(user);
});

app.get('/users/:id', (req, res) => {
    // AI will flag: no error handling, type coercion issues
    const user = users.find(u => u.id == req.params.id);
    res.json(user); // Can return undefined
});

app.listen(3000);
```

**AI Analysis Output:**
```
🤖 Issues Found:
1. No input validation on POST /users
2. Weak ID generation using timestamp
3. No error handling for missing users
4. Type coercion vulnerability (== vs ===)

💡 Suggested Improvements:
1. Add express-validator middleware
2. Use uuid for ID generation
3. Add 404 handling for missing resources
4. Use strict equality comparisons
```

---

## 🔧 Troubleshooting

### Common Issues

**1. LLM Server Not Responding**
```bash
# Check if service is running
curl http://localhost:1234/v1/models  # LM Studio
curl http://localhost:11434/api/version  # Ollama

# Restart service if needed
# LM Studio: Click "Stop Server" then "Start Server"
# Ollama: pkill ollama && ollama serve
```

**2. Model Loading Errors**
```bash
# Check available models
ollama list
lm-studio list  # If available

# Ensure model is downloaded
ollama pull phi3:mini

# Check system resources
htop  # Ensure enough RAM available
```

**3. Poor AI Analysis Quality**
```yaml
# Adjust model parameters
llm:
  temperature: 0.3    # Lower = more focused
  max_tokens: 1024    # Increase for detailed analysis
  top_p: 0.8         # Adjust token selection
```

### Performance Optimization

**Speed up analysis:**
```yaml
llm:
  options:
    num_predict: 256   # Shorter responses
    num_ctx: 2048      # Smaller context window
    
testing:
  verbose_ai: false    # Less detailed output for speed
```

**Improve quality:**
```yaml
llm:
  model: "gpt-oss-20b"   # Larger model
  temperature: 0.10      # More precise
  max_tokens: 2048       # Detailed responses
```

---

## 🏆 Best Practices

### Model Selection

**For Hackathons:**
- **Phi-3-mini**: Fast, good quality, small size
- **TinyLlama**: Ultra-fast for quick feedback
- **Qwen2.5-3B**: Balanced performance

**For Production:**
- **CodeLlama-7B**: Best code understanding
- **Gemma-7B**: General purpose excellence
- **Phi-3-medium**: High quality analysis

### Prompt Engineering

**Effective prompts include:**
- Specific context about the framework
- Clear instructions for analysis type
- Expected output format
- Relevant code examples

**Example effective prompt:**
```yaml
prompts:
  fastapi_analysis: |
    Analyze this FastAPI endpoint for issues:
    
    Framework: FastAPI
    Endpoint: {method} {path}
    Error: {error}
    
    Check for:
    1. Pydantic model issues
    2. HTTP status code problems
    3. FastAPI best practices
    4. Security vulnerabilities
    
    Provide specific FastAPI code fixes.
```

### Resource Management

**Monitor resource usage:**
```bash
# Check GPU memory (if using GPU)
nvidia-smi

# Check system resources
htop
df -h  # Disk space for models
```

**Optimize for your hardware:**
- **16GB+ RAM**: Use 14B+ models (GPT-OSS 20B, Gemma2-14B)
- **8GB RAM**: Use 7B models (Gemma2-7B, DeepSeek Coder 7B)
- **4GB RAM**: Use smaller models (Phi-3-mini)

---

## 🎯 Next Steps

1. **Choose your model** based on hardware and use case
2. **Install and configure** your preferred LLM backend
3. **Update Fixit.AI configuration** with LLM settings
4. **Run tests with AI analysis** to see immediate benefits
5. **Fine-tune prompts** for your specific use cases
6. **Integrate into CI/CD** for automated AI-powered testing

**Ready to get started?** Pick your setup:
- 🚀 **Quick Start**: [LM Studio + GPT-OSS](#lm-studio-setup-recommended)
- 🐋 **CLI Focused**: [Ollama + Gemma2](#ollama-setup-cli-alternative)  
- 🔧 **Advanced**: [llama.cpp custom setup](#llamacpp-setup-advanced)

**Questions?** Check our [main documentation](../README.md) or [open an issue](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/issues).
