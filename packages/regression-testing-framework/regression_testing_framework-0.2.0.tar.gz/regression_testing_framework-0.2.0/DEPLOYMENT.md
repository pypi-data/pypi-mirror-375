# Reggie Deployment Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Core functionality
pip install -e .

# With web interface
pip install -e .[web]

# Development setup
pip install -e .[dev]

# Complete setup
pip install -e .[web,monitoring,dev]
```

### 2. Start Redis (Message Broker)

```bash
# Using Docker
docker run -d -p 6379:6379 redis

# Or using Docker Compose
docker-compose up -d redis
```

### 3. CLI Usage

```bash
# Start Celery workers
reggie worker

# Run tests (traditional multiprocessing)
reggie run config.yaml

# Run tests with Celery
reggie run config.yaml --celery

# Monitor workers
reggie status

# Start web interface
reggie web
```

### 4. Docker Deployment

#### Basic CLI-only deployment:
```bash
docker-compose up -d
```

#### Full web interface deployment:
```bash
docker-compose -f docker-compose.web.yml up -d
```

## 🏗️ Architecture

### Components

1. **CLI Interface** (`reggie` command)
   - Traditional multiprocessing mode
   - Celery-based distributed mode
   - Worker management
   - Status monitoring

2. **Celery Workers** (Optional)
   - Distributed task execution
   - Scalable test running
   - Redis-based message broker

3. **Web Interface** (Optional)
   - FastAPI + HTMX dashboard
   - Real-time job monitoring
   - Configuration management
   - Worker status

4. **Database** (SQLite)
   - Test result metadata
   - Job history
   - Configuration storage

### Execution Modes

1. **Multiprocessing Mode** (Default)
   - Direct process execution
   - Good for single-machine setups
   - No external dependencies

2. **Celery Mode** (Scalable)
   - Distributed task execution
   - Requires Redis broker
   - Supports multiple workers
   - Web interface integration

## 🐳 Docker Setup

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │────│  Celery Worker  │────│   Redis Broker  │
│   (FastAPI)     │    │   (Test Runner) │    │                 │
│   Port: 8000    │    │                 │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                           ┌─────────────────┐
                           │   Flower        │
                           │  (Monitoring)   │
                           │  Port: 5555     │
                           └─────────────────┘
```

### Services

- **reggie-app**: Main application container
- **reggie-worker**: Celery worker containers
- **redis**: Message broker
- **flower**: Celery monitoring (web mode only)

### Volumes

- `./test_runs`: Test output directory
- `./configs`: Configuration files
- `redis_data`: Redis persistence

## 🔧 Configuration

### Environment Variables

```bash
# Redis connection
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Web interface
WEB_HOST=0.0.0.0
WEB_PORT=8000

# Worker settings
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_LOGLEVEL=info
```

### pyproject.toml Extras

```toml
[project.optional-dependencies]
# Core Celery support
celery = ["celery[redis]>=5.3.0", "redis>=4.5.0"]

# Web interface
web = ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0", "jinja2>=3.1.0", "psutil>=5.9.0"]

# Monitoring tools
monitoring = ["flower>=2.0.0", "prometheus-client>=0.17.0"]

# Development tools
dev = ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black>=23.0.0", "ruff>=0.1.0"]
```

## 📊 Monitoring

### Web Dashboard
- Real-time job status
- Worker monitoring
- System resource usage
- Configuration management

### Flower (Celery Monitoring)
- Worker health and performance
- Task queue statistics
- Task history and results
- Worker pool management

### CLI Monitoring
```bash
# Worker status
reggie status

# Show active jobs
reggie jobs

# Worker management
reggie worker --help
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install dependencies
   pip install -e .[web]
   ```

2. **Redis Connection**
   ```bash
   # Check Redis is running
   docker ps | grep redis
   
   # Start Redis
   docker run -d -p 6379:6379 redis
   ```

3. **No Workers Available**
   ```bash
   # Start workers
   reggie worker
   
   # Check worker status
   reggie status
   ```

4. **Web Interface Not Loading**
   ```bash
   # Install web dependencies
   pip install -e .[web]
   
   # Start web server
   reggie web --host 0.0.0.0 --port 8000
   ```

### Validation

Run the validation script to check setup:
```bash
python3 validate.py
```

## 🚀 Production Deployment

### Recommended Setup

1. **Docker Compose** for container orchestration
2. **Multiple worker nodes** for scalability
3. **Redis persistence** for job durability
4. **Reverse proxy** (nginx) for web interface
5. **Log aggregation** for monitoring

### Security Considerations

1. **Network isolation** between components
2. **Authentication** for web interface (not implemented)
3. **Input validation** for configuration files
4. **Resource limits** for containers

### Scaling

- Add more worker containers: `docker-compose up -d --scale reggie-worker=3`
- Use external Redis cluster for high availability
- Deploy web interface behind load balancer
- Monitor resource usage and adjust container limits

## 📝 Development

### Project Structure
```
src/regression_testing_framework/
├── __init__.py
├── cli.py                 # CLI interface
├── celery_app.py         # Celery application
├── celery_config.py      # Celery configuration
├── test_runner.py        # Core test execution
├── config_parser.py      # Configuration parsing
├── database.py           # SQLite database
├── tasks/
│   ├── test_execution.py # Individual test tasks
│   └── orchestration.py  # Test suite orchestration
└── web/
    ├── main.py           # FastAPI application
    ├── api/              # REST API endpoints
    ├── templates/        # HTML templates
    └── static/           # CSS and JS
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

### Testing

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
ruff check .
```