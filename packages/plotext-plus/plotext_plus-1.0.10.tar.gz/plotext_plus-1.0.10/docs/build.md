# 🛠️ Development & Build System

Plotext+ includes a comprehensive build system with modern tooling for development, testing, and deployment.

## Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/ccmitchellusa/plotext_plus.git
cd plotext_plus

# Development environment setup  
make dev          # Install all dependencies + format + test
make setup        # Alternative: setup development environment
```

## Build Commands

### **🌱 Environment & Installation**
```bash
make install      # Install basic dependencies
make install-dev  # Install with development tools
make install-mcp  # Install with MCP server support  
make install-all  # Install with all optional dependencies
make update       # Update all dependencies
```

### **🧪 Testing & Quality**
```bash
make test         # Run tests with coverage
make test-fast    # Run tests without coverage
make test-mcp     # Test MCP server functionality
make coverage     # Generate coverage reports

# Code quality
make lint         # Run full linting suite (ruff + black + isort + mypy)
make lint-check   # Check linting without fixing
make format       # Format code (black + isort)
make ruff         # Ruff linting and formatting
make black        # Black code formatting
make isort        # Import sorting
make mypy         # Type checking
make bandit       # Security analysis
```

### **📦 Building & Publishing**
```bash
make build        # Build Python package
make publish      # Build and publish to PyPI (with twine)
make publish-test # Publish to TestPyPI
make clean        # Clean build artifacts

# Version management
make bump-patch   # Bump patch version (1.0.0 → 1.0.1)
make bump-minor   # Bump minor version (1.0.0 → 1.1.0)  
make bump-major   # Bump major version (1.0.0 → 2.0.0)

# Combined release workflow
make release-patch # Bump patch + publish
make release-minor # Bump minor + publish  
make release-major # Bump major + publish
```

### **🐋 Container Operations**
```bash
# Docker
make docker-build    # Build Docker image
make docker-up       # Start with Docker Compose
make docker-down     # Stop Docker Compose
make docker-logs     # View container logs
make docker-clean    # Clean containers and images

# Podman
make podman-build    # Build with Podman
make podman-run-mcp  # Run MCP server container
make podman-test     # Test container health
make podman-logs     # Follow container logs
make podman-stats    # Show resource usage
make podman-shell    # Interactive shell access
```

### **☁️ Cloud Deployment**
```bash
# IBM Cloud Code Engine
make ce-push-image   # Push to IBM Container Registry
make ce-deploy       # Deploy to Code Engine
make ce-update       # Update existing deployment
make ce-status       # Check deployment status
make ce-logs         # View application logs
make ce-full-deploy  # Complete deployment workflow
```

### **🎯 Quick Workflows**
```bash
make dev       # Development setup (install-all + format + test-fast)
make check     # Quick validation (lint-check + test-fast)
make all       # Full pipeline (format + lint + test + build)
```

### **▶️ Running & Demo**
```bash
make run-mcp     # Start MCP server
make run-demos   # Run interactive examples
```

### **🔧 Utilities**
```bash
make version     # Show version information
make info        # Show project information  
make deps        # Show dependency tree
make help        # Show all available targets
```

## Project Structure

```
plotext_plus/
├── src/plotext_plus/          # 🎯 Main source code
│   ├── plotting.py           # Core plotting functions  
│   ├── charts.py             # Chart classes
│   ├── themes.py             # Theme system
│   ├── utilities.py          # Helper functions
│   ├── mcp_server.py         # MCP server (optional)
│   └── _*.py                 # 🔒 Private modules
├── examples/                 # Interactive demos
├── tests/                    # Test suites  
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD automation
├── docker/                   # Container files
└── Makefile                  # Build system
```

## Development Workflow

1. **Setup**: `make dev` 
2. **Code**: Write your changes
3. **Quality**: `make check` (lint + test)
4. **Comprehensive**: `make all` (full pipeline)
5. **Deploy**: `make release-patch` (version + publish)

## CI/CD Integration

The project includes comprehensive GitHub Actions workflows:

- **🔄 CI**: Automated testing, linting, security scanning
- **🚀 Release**: Automated publishing to PyPI + container registry
- **🔒 Security**: Daily security scans, dependency updates  
- **📦 Dependencies**: Weekly automated dependency updates

All workflows use modern tooling (uv, ruff, mypy, pytest) for fast, reliable builds.

## Quality Standards

- **Code Quality**: Ruff + Black + isort for consistent formatting
- **Type Safety**: MyPy for static type checking
- **Security**: Bandit for security analysis  
- **Testing**: Pytest with coverage reporting
- **Documentation**: Comprehensive docs with examples

Use `make help` to see all available commands with descriptions.