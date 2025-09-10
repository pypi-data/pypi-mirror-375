# 🚀 Framework Integration Guide

This guide covers how to integrate Fixit.AI with various API frameworks and provides detailed setup instructions for each supported platform.

## 🎯 Quick Framework Selection

| Framework | Best For | Setup Time | AI Support | Code Patches |
|-----------|----------|------------|------------|--------------|
| **FastAPI** | Python APIs | < 30 seconds | ✅ Full | ✅ Full |
| **Express.js** | Node.js APIs | < 2 minutes | ✅ Full | ✅ Full |

---

## 🐍 FastAPI Integration (Recommended)

### Zero-Config Setup

**Fixit.AI offers the smoothest experience with FastAPI** through automatic OpenAPI spec extraction:

```python
# main.py - Your FastAPI application
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="User Management API",
    description="A simple user management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int
    active: bool = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

# Sample database
users_db = []

@app.post("/users/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user in the system."""
    new_user = User(id=len(users_db) + 1, **user.dict())
    users_db.append(new_user)
    return new_user

@app.get("/users/", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100):
    """Retrieve a list of users with pagination."""
    return users_db[skip: skip + limit]

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserCreate):
    """Update an existing user."""
    for i, user in enumerate(users_db):
        if user.id == user_id:
            updated_user = User(id=user_id, **user_update.dict())
            users_db[i] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user from the system."""
    for i, user in enumerate(users_db):
        if user.id == user_id:
            del users_db[i]
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Start your API and test with Fixit.AI:**

```bash
# Terminal 1: Start your FastAPI application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Install and run Fixit.AI
pip install fixit-ai

# Zero-config initialization - Fixit.AI auto-discovers everything!
fixit init --fastapi main:app --base http://localhost:8000
fixit gen
fixit test
fixit sec
```

### What Fixit.AI Discovers Automatically

- ✅ **OpenAPI Schema**: Complete API specification with all endpoints
- ✅ **Data Models**: Pydantic models and validation rules
- ✅ **Response Formats**: Expected response schemas and status codes
- ✅ **Authentication**: Security schemes if configured
- ✅ **Validation Rules**: Field constraints and data types

### Advanced FastAPI Configuration

```python
# Advanced FastAPI setup with authentication
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Secure API",
    description="API with authentication and advanced features",
    version="2.0.0",
    openapi_tags=[
        {"name": "users", "description": "User management operations"},
        {"name": "auth", "description": "Authentication operations"},
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials

@app.post("/users/", response_model=User, tags=["users"])
async def create_user(
    user: UserCreate, 
    token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    # Implementation here
    pass
```

**Test with authentication:**

```bash
fixit init --fastapi main:app --base http://localhost:8000
# Fixit.AI will automatically detect auth requirements and include in tests
fixit gen
fixit test --auth-header "Authorization: Bearer valid-token"
```

---

## 🟢 Express.js Integration

### Setup Express.js with OpenAPI

Express.js requires OpenAPI documentation setup. Here's the complete guide:

#### Step 1: Install Dependencies

```bash
npm init -y
npm install express swagger-jsdoc swagger-ui-express
npm install --save-dev @types/node
```

#### Step 2: Create Express App with OpenAPI

```javascript
// app.js
const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');

const app = express();
app.use(express.json());

// Swagger/OpenAPI configuration
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Express API with OpenAPI',
      version: '1.0.0',
      description: 'A sample Express.js API with comprehensive OpenAPI documentation',
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server',
      },
    ],
    components: {
      schemas: {
        User: {
          type: 'object',
          required: ['name', 'email'],
          properties: {
            id: { type: 'integer', description: 'User ID' },
            name: { type: 'string', description: 'User name' },
            email: { type: 'string', format: 'email', description: 'User email' },
            age: { type: 'integer', minimum: 0, maximum: 120 },
            active: { type: 'boolean', default: true }
          }
        },
        UserInput: {
          type: 'object',
          required: ['name', 'email'],
          properties: {
            name: { type: 'string', minLength: 1, maxLength: 100 },
            email: { type: 'string', format: 'email' },
            age: { type: 'integer', minimum: 0, maximum: 120 }
          }
        },
        Error: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' }
          }
        }
      },
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      }
    }
  },
  apis: ['./app.js'], // Path to the API docs
};

// Generate OpenAPI spec
const specs = swaggerJsdoc(swaggerOptions);

// Serve Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

// Export OpenAPI spec for Fixit.AI
fs.writeFileSync('./openapi.json', JSON.stringify(specs, null, 2));

// Sample data store
let users = [
  { id: 1, name: 'John Doe', email: 'john@example.com', age: 30, active: true }
];
let nextId = 2;

/**
 * @swagger
 * /health:
 *   get:
 *     summary: Health check endpoint
 *     tags: [Health]
 *     responses:
 *       200:
 *         description: Service is healthy
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status: { type: string, example: "healthy" }
 *                 timestamp: { type: string, format: date-time }
 */
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString() 
  });
});

/**
 * @swagger
 * /users:
 *   get:
 *     summary: Get all users
 *     tags: [Users]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema: { type: integer, minimum: 1, default: 1 }
 *         description: Page number
 *       - in: query
 *         name: limit
 *         schema: { type: integer, minimum: 1, maximum: 100, default: 10 }
 *         description: Number of items per page
 *     responses:
 *       200:
 *         description: List of users
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 users: { type: array, items: { $ref: '#/components/schemas/User' } }
 *                 total: { type: integer }
 *                 page: { type: integer }
 *                 limit: { type: integer }
 */
app.get('/users', (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  
  const paginatedUsers = users.slice(startIndex, endIndex);
  
  res.json({
    users: paginatedUsers,
    total: users.length,
    page,
    limit
  });
});

/**
 * @swagger
 * /users/{id}:
 *   get:
 *     summary: Get user by ID
 *     tags: [Users]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema: { type: integer }
 *         description: User ID
 *     responses:
 *       200:
 *         description: User details
 *         content:
 *           application/json:
 *             schema: { $ref: '#/components/schemas/User' }
 *       404:
 *         description: User not found
 *         content:
 *           application/json:
 *             schema: { $ref: '#/components/schemas/Error' }
 */
app.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) {
    return res.status(404).json({ error: 'Not Found', message: 'User not found' });
  }
  res.json(user);
});

/**
 * @swagger
 * /users:
 *   post:
 *     summary: Create a new user
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema: { $ref: '#/components/schemas/UserInput' }
 *     responses:
 *       201:
 *         description: User created successfully
 *         content:
 *           application/json:
 *             schema: { $ref: '#/components/schemas/User' }
 *       400:
 *         description: Invalid input
 *         content:
 *           application/json:
 *             schema: { $ref: '#/components/schemas/Error' }
 *       401:
 *         description: Unauthorized
 */
app.post('/users', (req, res) => {
  const { name, email, age } = req.body;
  
  // Basic validation
  if (!name || !email) {
    return res.status(400).json({ 
      error: 'Bad Request', 
      message: 'Name and email are required' 
    });
  }
  
  // Check for duplicate email
  if (users.find(u => u.email === email)) {
    return res.status(400).json({ 
      error: 'Bad Request', 
      message: 'Email already exists' 
    });
  }
  
  const newUser = {
    id: nextId++,
    name,
    email,
    age: age || null,
    active: true
  };
  
  users.push(newUser);
  res.status(201).json(newUser);
});

/**
 * @swagger
 * /users/{id}:
 *   put:
 *     summary: Update user by ID
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema: { type: integer }
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema: { $ref: '#/components/schemas/UserInput' }
 *     responses:
 *       200:
 *         description: User updated successfully
 *       404:
 *         description: User not found
 *       400:
 *         description: Invalid input
 */
app.put('/users/:id', (req, res) => {
  const userIndex = users.findIndex(u => u.id === parseInt(req.params.id));
  if (userIndex === -1) {
    return res.status(404).json({ error: 'Not Found', message: 'User not found' });
  }
  
  const { name, email, age } = req.body;
  if (!name || !email) {
    return res.status(400).json({ 
      error: 'Bad Request', 
      message: 'Name and email are required' 
    });
  }
  
  users[userIndex] = { ...users[userIndex], name, email, age };
  res.json(users[userIndex]);
});

/**
 * @swagger
 * /users/{id}:
 *   delete:
 *     summary: Delete user by ID
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema: { type: integer }
 *     responses:
 *       204:
 *         description: User deleted successfully
 *       404:
 *         description: User not found
 */
app.delete('/users/:id', (req, res) => {
  const userIndex = users.findIndex(u => u.id === parseInt(req.params.id));
  if (userIndex === -1) {
    return res.status(404).json({ error: 'Not Found', message: 'User not found' });
  }
  
  users.splice(userIndex, 1);
  res.status(204).send();
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API docs available at http://localhost:${PORT}/api-docs`);
  console.log(`OpenAPI spec exported to ./openapi.json`);
});
```

#### Step 3: Test with Fixit.AI

```bash
# Terminal 1: Start Express server
node app.js

# Terminal 2: Test with Fixit.AI
pip install fixit-ai

# Initialize with Express project
fixit init --express . --base http://localhost:3000
fixit gen
fixit test
fixit sec

# View generated OpenAPI spec
cat openapi.json
```

### Express.js Advanced Features

#### Authentication Testing

```javascript
// Add authentication middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access denied. No token provided.' });
  }
  
  // In real app, verify JWT token
  if (token !== 'valid-token') {
    return res.status(403).json({ error: 'Invalid token.' });
  }
  
  next();
}

// Apply to protected routes
app.post('/users', authenticateToken, (req, res) => {
  // User creation logic
});
```

**Test authentication with Fixit.AI:**

```bash
fixit test --auth-header "Authorization: Bearer valid-token"
```

#### Error Handling

```javascript
// Global error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Internal Server Error', 
    message: 'Something went wrong!' 
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Not Found', 
    message: 'Endpoint not found' 
  });
});
```

---

## 🛠️ Framework Comparison & Best Practices

### Performance Comparison

| Framework | Startup Time | Spec Generation | Test Coverage | AI Analysis |
|-----------|--------------|-----------------|---------------|-------------|
| FastAPI | < 10s | Instant | 95%+ | Excellent |
| Express.js | < 30s | Manual Setup | 90%+ | Good |


### Best Practices by Framework

#### FastAPI Best Practices
- Use Pydantic models for all request/response schemas
- Add comprehensive docstrings to endpoints
- Use proper HTTP status codes
- Implement dependency injection for shared logic
- Add tags for better organization

#### Express.js Best Practices
- Use comprehensive JSDoc comments for all endpoints
- Define schemas in OpenAPI components
- Implement proper error handling middleware
- Use validation middleware (e.g., express-validator)
- Export OpenAPI spec to file for Fixit.AI

---

## 🚀 Next Steps

After setting up your framework integration:

1. **Run Comprehensive Tests**: `fixit test --coverage 95`
2. **Security Scanning**: `fixit sec --owasp-top-10`
3. **AI Analysis**: Setup local LLM for intelligent insights
4. **CI/CD Integration**: Add Fixit.AI to your deployment pipeline
5. **Performance Testing**: Use load testing mode for bottleneck detection

**Questions or issues?** Check our [main documentation](../README.md) or [open an issue](https://github.com/Fixit-Local-AI-Agent/Fixit.AI/issues).
