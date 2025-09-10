const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 3000;

// BUG #1: Permissive CORS (security issue)
app.use(cors({
    origin: '*',  // BUG: wildcard allows any origin
    credentials: true
}));

app.use(express.json());

// In-memory "database"
const users = [];
let userIdCounter = 1;

const JWT_SECRET = 'weak-secret'; // BUG #2: weak secret

// BUG #3: No input validation + unhandled error (500 instead of 409)
app.post('/api/users', (req, res) => {
    const { email, password, name } = req.body;
    
    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
        // Fixed: Return proper 409 Conflict instead of throwing error
        return res.status(409).json({ error: 'User already exists' });
    }
    
    const user = {
        id: userIdCounter++,
        email,
        password, // BUG #4: storing plaintext password
        name
    };
    
    users.push(user);
    res.status(201).json(user);
});

app.post('/api/auth/login', (req, res) => {
    const { email, password } = req.body;
    
    const user = users.find(u => u.email === email && u.password === password);
    if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token, user });
});

// Authentication middleware
const auth = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'No token' });
    
    try {
        req.user = jwt.verify(token, JWT_SECRET);
        next();
    } catch {
        res.status(403).json({ error: 'Invalid token' });
    }
};

// BUG #5: IDOR - any authenticated user can view any user
app.get('/api/users/:id', auth, (req, res) => {
    const userId = parseInt(req.params.id);
    
    // BUG: No ownership check - user A can read user B's data
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user); // BUG #6: Returns password in response
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});

module.exports = app;