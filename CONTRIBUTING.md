# Contributing to Agent Load Balancer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)
7. [Feature Requests](#feature-requests)
8. [Bug Reports](#bug-reports)

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could be considered inappropriate

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (optional)
- Git

### Setup Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/solvers.git
   cd solvers
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔄 Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Adding tests

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add agent priority levels

fix(ui): resolve mobile responsiveness issue

docs(readme): update installation instructions

refactor(backend): simplify load balancing algorithm
```

## 📝 Coding Standards

### Python (Backend)

Follow [PEP 8](https://pep8.org/) style guide:

```python
# Good
def find_most_available_agent() -> Optional[Agent]:
    """Find the agent with the most available capacity."""
    available_agents = [
        agent for agent in agents_db.values() 
        if agent.is_available
    ]
    return max(available_agents, key=lambda a: a.available_capacity)

# Use type hints
def create_agent(name: str, max_requests: int = 2) -> Agent:
    pass

# Document functions
def complex_function(param: str) -> dict:
    """
    Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

**Tools:**
- Linting: `pylint`, `flake8`
- Formatting: `black`
- Type checking: `mypy`

### TypeScript (Frontend)

Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript):

```typescript
// Good - Use meaningful names
const handleCreateAgent = async (e: React.FormEvent) => {
  // Implementation
};

// Use interfaces for props
interface AgentCardProps {
  agent: Agent;
  onDelete: (id: string) => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onDelete }) => {
  // Implementation
};

// Async/await over promises
const loadData = async () => {
  try {
    const response = await agentApi.getAgents();
    setAgents(response.data);
  } catch (error) {
    console.error(error);
  }
};
```

**Tools:**
- Linting: ESLint
- Formatting: Prettier (if configured)
- Type checking: TypeScript compiler

### General Guidelines

1. **Keep it simple**: Write clear, readable code
2. **DRY**: Don't repeat yourself
3. **Single responsibility**: Each function/class should do one thing
4. **Meaningful names**: Use descriptive variable and function names
5. **Comments**: Explain why, not what
6. **Error handling**: Always handle errors gracefully
7. **Security**: Validate input, sanitize output

## 🧪 Testing

### Backend Testing

Create tests in `backend/tests/`:

```python
# test_agents.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_agent():
    response = client.post(
        "/agents",
        json={"name": "Test Agent", "max_requests": 2}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Agent"

def test_load_balancing():
    # Create agents
    agent1 = client.post("/agents", json={"name": "Agent 1", "max_requests": 2})
    agent2 = client.post("/agents", json={"name": "Agent 2", "max_requests": 3})
    
    # Create request
    request = client.post(
        "/requests",
        json={"customer_name": "John", "description": "Help"}
    )
    
    # Should assign to agent with higher capacity
    assert request.json()["assigned_agent_id"] == agent2.json()["id"]
```

Run tests:
```bash
pytest backend/tests/
```

### Frontend Testing

Create tests in `frontend/src/__tests__/`:

```typescript
// App.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

test('renders agent form', () => {
  render(<App />);
  expect(screen.getByText(/Create Agent/i)).toBeInTheDocument();
});

test('creates agent successfully', async () => {
  render(<App />);
  
  const nameInput = screen.getByLabelText(/Agent Name/i);
  const submitButton = screen.getByText(/Add Agent/i);
  
  fireEvent.change(nameInput, { target: { value: 'Test Agent' } });
  fireEvent.click(submitButton);
  
  // Assert success message or new agent appears
});
```

Run tests:
```bash
npm test
```

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Test your changes**
   - Run all tests
   - Test manually in browser
   - Check for console errors
   - Verify Docker build works

3. **Update documentation**
   - Update README.md if needed
   - Add/update code comments
   - Update ARCHITECTURE.md for design changes

4. **Lint your code**
   ```bash
   # Backend
   cd backend
   flake8 .
   
   # Frontend
   cd frontend
   npm run lint
   ```

### Submitting PR

1. **Push your changes**
   ```bash
   git push origin your-branch
   ```

2. **Create Pull Request**
   - Go to GitHub and create PR
   - Use descriptive title
   - Fill out PR template
   - Link related issues

3. **PR Title Format**
   ```
   feat: Add agent priority system
   fix: Resolve memory leak in load balancer
   docs: Update API documentation
   ```

4. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Backend tests pass
   - [ ] Frontend tests pass
   - [ ] Manual testing completed
   - [ ] Docker build successful
   
   ## Screenshots (if applicable)
   
   ## Related Issues
   Fixes #123
   ```

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, maintainer will merge

### After Merge

1. Delete your branch
2. Pull latest main
3. Thank you for contributing! 🎉

## 💡 Feature Requests

### Before Requesting

1. Check existing issues/PRs
2. Ensure it aligns with project goals
3. Consider if it's generally useful

### Creating Feature Request

Use this template:

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Screenshots, mockups, examples, etc.
```

## 🐛 Bug Reports

### Before Reporting

1. Check if already reported
2. Verify it's actually a bug
3. Test with latest version
4. Try to reproduce consistently

### Creating Bug Report

Use this template:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Python version: [e.g., 3.11.5]
- Node version: [e.g., 20.10.0]

## Screenshots
If applicable

## Additional Context
Logs, error messages, etc.
```

## 📚 Resources

### Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Docker**: https://docs.docker.com/

### Project Documentation

- [README.md](README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Deployment guide

## 🎯 Areas for Contribution

Looking for ideas? Here are areas that need help:

### High Priority
- [ ] Add database integration (PostgreSQL/MongoDB)
- [ ] Implement authentication system
- [ ] Add comprehensive test suite
- [ ] Add rate limiting
- [ ] Implement WebSocket for real-time updates

### Medium Priority
- [ ] Agent priority levels
- [ ] Request categorization
- [ ] Analytics dashboard
- [ ] Export functionality (CSV/JSON)
- [ ] Email notifications

### Low Priority
- [ ] Dark/light theme toggle
- [ ] Multi-language support
- [ ] Advanced filtering and search
- [ ] Agent performance metrics
- [ ] Request history timeline

### Documentation
- [ ] API usage examples in multiple languages
- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] Performance benchmarks
- [ ] Deployment guides for AWS/GCP/Azure

## 🏆 Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Questions?

- Open a Discussion on GitHub
- Ask in Pull Request comments
- Check existing documentation

---

Thank you for contributing to Agent Load Balancer! 🙏
