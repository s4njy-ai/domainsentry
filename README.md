# DomainSentry

![DomainSentry Dashboard](screenshots/dashboard.png)

DomainSentry is a world-class OSINT platform for monitoring newly registered domains with advanced enrichment, real-time risk scoring, and cyber news aggregation. Built with modern full-stack technologies and SRE best practices.

## ✨ Features

### 🔍 Domain Intelligence
- **Real-time monitoring** of newly registered domains via crt.sh (Certificate Transparency logs)
- **WHOIS enrichment** via whoisxmlapi.com (mockable for development)
- **Threat intelligence** integration with VirusTotal & AbuseIPDB (optional)
- **RSS feed aggregation** from KrebsOnSecurity, BleepingComputer, and other sources

### 🚨 Advanced Risk Engine
- **ML-lite scoring** using scikit-learn (entropy analysis, N-gram patterns)
- **Configurable YAML weights** for customizable risk calculations
- **95%+ test coverage** with comprehensive test suite
- **Real-time scoring** with streaming updates

### 🎨 Modern Frontend
- **shadcn/ui** component library with dark mode support
- **TanStack Query/Table** for efficient data fetching and display
- **Recharts** for visualizations (risk trends, TLD distribution, timeline)
- **Infinite scroll** with search and autocomplete
- **Export functionality** (CSV via PapaParse, PDF via jsPDF)
- **PWA manifest** for mobile installability
- **Responsive design** with loading skeletons and error toasts (Sonner)

### 🔒 Security & Auth
- **Clerk.dev integration** for authentication (environment-based)
- **JWT API guard** for secure endpoints
- **CSP headers** for enhanced security

### 🚀 Production-Ready Backend
- **Redis caching** via aioredis for performance
- **Celery/RQ** for production job queues
- **Rate limiting** via slowapi
- **Structured logging** with structlog
- **Prometheus metrics** for observability
- **Alembic migrations** with initial data seeding
- **Docker-compose** for easy deployment (backend + Postgres + Redis + Celery)

### 📊 Observability
- **Health dashboards** for system monitoring
- **Error tracking** stubs for production monitoring
- **Real-time SSE** for job status and news updates

### 🔧 Developer Experience
- **TDD approach** with comprehensive test suite
- **Pinned dependencies** for reproducible builds
- **GitHub Actions CI/CD** for automated linting, testing, and deployment
- **Vercel/Netlify** deployment scripts

## 🏗️ Architecture

```
domainsentry/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core config, security, dependencies
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   └── utils/         # Utilities
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   └── requirements.txt
├── frontend/              # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utilities, API client
│   │   ├── pages/        # Page components
│   │   └── styles/       # Global styles
│   ├── public/           # Static assets
│   └── package.json
├── docker-compose.yml     # Production stack
├── docker-compose.dev.yml # Development stack
├── .github/workflows/    # CI/CD pipelines
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Development Setup

1. **Clone and install:**
```bash
git clone https://github.com/s4njy-ai/domainsentry.git
cd domainsentry
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
```

3. **Frontend setup:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your configuration
```

4. **Run with Docker Compose (recommended):**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

Access the application at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB GUI): http://localhost:8080

### Production Deployment

1. **Deploy with Docker Compose:**
```bash
docker-compose up -d
```

2. **Deploy to Vercel/Netlify:**
```bash
# Frontend deployment
cd frontend
vercel deploy  # or netlify deploy
```

3. **CI/CD with GitHub Actions:**
Push to main branch to trigger automatic deployment.

## 📦 Docker Images

Pre-built Docker images are available on GitHub Packages:
```bash
docker pull ghcr.io/s4njy-ai/domainsentry-backend:latest
docker pull ghcr.io/s4njy-ai/domainsentry-frontend:latest
```

## 🔧 Configuration

### Environment Variables

See `.env.example` files in both backend and frontend directories for required environment variables.

### Risk Engine Configuration

Configure risk weights in `backend/config/risk_weights.yaml`:
```yaml
weights:
  domain_length: 0.15
  entropy_score: 0.25
  tld_risk: 0.20
  keyword_matches: 0.30
  age_days: 0.10
```

### Provider Configuration

Enable/disable providers in `backend/config/providers.yaml`:
```yaml
providers:
  crt_sh:
    enabled: true
    api_url: "https://crt.sh/"
  whoisxmlapi:
    enabled: true
    api_key: ${WHOISXMLAPI_KEY}
    mock: false  # Set to true for development
  virustotal:
    enabled: false  # Optional
    api_key: ${VIRUSTOTAL_KEY}
  abuseipdb:
    enabled: false  # Optional
    api_key: ${ABUSEIPDB_KEY}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
npm run e2e  # End-to-end tests
```

## 📊 Monitoring & Observability

- **Prometheus metrics**: http://localhost:8000/metrics
- **Health checks**: http://localhost:8000/health
- **Structured logs**: View in Kibana or via Docker logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://reactjs.org/) and [Vite](https://vitejs.dev/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Database migrations with [Alembic](https://alembic.sqlalchemy.org/)
- Job queue with [Celery](https://docs.celeryq.dev/)
- Charts with [Recharts](https://recharts.org/)

## 📞 Support

For issues and feature requests, please use [GitHub Issues](https://github.com/s4njy-ai/domainsentry/issues).