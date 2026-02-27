# Contributing to AI Design Tool

Thank you for your interest in contributing to AI Design Tool! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+
- Git

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/All-in-one-Design.git
   cd All-in-one-Design
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local with your API URL
   npm run dev
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 📝 How to Contribute

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Use the latest version
- Test with a clean environment

Include in your bug report:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, browser, versions)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
- Use a clear, descriptive title
- Provide detailed description of the proposed feature
- Explain why this enhancement would be useful
- List any alternatives you've considered

### Pull Requests

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make Your Changes**
   - Write clean, maintainable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm run test
   npm run lint
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes (formatting)
   - `refactor`: Code refactoring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 💻 Development Guidelines

### Python/Django Backend

- **Style Guide**: Follow PEP 8
- **Linting**: Use Ruff (`ruff check .`)
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Use Google-style docstrings
- **Testing**: Write tests for new features (pytest)

Example:
```python
def calculate_score(value: int, multiplier: float = 1.0) -> float:
    """Calculate score with multiplier.
    
    Args:
        value: The base value
        multiplier: Score multiplier
        
    Returns:
        The calculated score
        
    Raises:
        ValueError: If value is negative
    """
    if value < 0:
        raise ValueError("Value must be non-negative")
    return value * multiplier
```

### TypeScript/React Frontend

- **Style Guide**: Follow Airbnb style guide
- **Linting**: ESLint is configured
- **Components**: Use functional components with hooks
- **Types**: Always use TypeScript types, avoid `any`
- **Testing**: Write component tests (Jest/React Testing Library)

Example:
```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export function Button({ 
  label, 
  onClick, 
  variant = 'primary',
  disabled = false 
}: ButtonProps) {
  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {label}
    </button>
  );
}
```

### Database Migrations

- Always create migrations for model changes
- Test migrations both forward and backward
- Never edit existing migrations (create new ones)
- Write data migrations for complex changes

```bash
python manage.py makemigrations
python manage.py migrate
```

### API Design

- Follow RESTful conventions
- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Return appropriate status codes
- Include pagination for list endpoints
- Version your APIs (`/api/v1/`)

### Testing Requirements

- **Backend**: Minimum 70% code coverage
- **Frontend**: Test critical user flows
- **Integration**: Test API endpoints
- **E2E**: Test complete user journeys (optional but recommended)

## 🎨 Design Guidelines

- Follow existing UI/UX patterns
- Use Shadcn UI components
- Maintain accessibility (WCAG 2.1 AA)
- Test on multiple screen sizes
- Optimize for performance

## 📚 Documentation

- Update README.md for major changes
- Document new APIs in code
- Update relevant .md files in docs/
- Add inline code comments for complex logic
- Update CHANGELOG.md

## 🔍 Code Review Process

All submissions require review before merging:

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least one maintainer approval
3. **Testing**: All tests must pass
4. **Documentation**: Documentation must be updated

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in the community

## 📞 Getting Help

- **Discord**: [Join our community](#)
- **GitHub Discussions**: Ask questions
- **Email**: support@aidesigntool.com

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Questions?** Open an issue or reach out to maintainers.
