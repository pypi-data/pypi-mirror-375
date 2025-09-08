# PEX Demo - Stepan Matula

A Flask web application demonstrating Jenkins CI/CD pipeline with PyPI publishing.

## Features

- RESTful API endpoints (`/`, `/health`, `/info`)
- Health check endpoint for monitoring
- Application info with build metadata
- Complete Jenkins CI/CD Pipeline (6 stages)
- Docker containerization support
- Automated PyPI publishing

## Installation

```bash
pip install pex-demo-stepanmatula
```

## Usage

### As a console command:
```bash
pex-demo
```

### As a Python module:
```python
from app import app
app.run()
```

## API Endpoints

- `GET /` - Main application endpoint
- `GET /health` - Health check endpoint  
- `GET /info` - Application information

## Development

This package was built using Jenkins CI/CD pipeline with the following stages:
1. Build & Setup
2. Test & Quality Assurance  
3. Manual Approval
4. Deploy & Archive
5. Package Preparation
6. PyPI Publication

## License

MIT License
