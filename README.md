# Canary Deployment Demo

A production-grade Canary deployment pipeline built with Jenkins, Docker, and Nginx.

## What it does
- Deploys new version as canary alongside stable
- Gradually shifts traffic: 10% → 50% → 100%
- Health checks canary at each traffic stage
- Rolls back automatically if any health check fails
- Zero downtime throughout the entire promotion cycle

## Architecture

User → Nginx (port 8090)

↓

Weighted upstream:

├── stable container (port 5001) ← previous version

└── canary container (port 5002) ← new version

## Tech Stack
- Python 3.11 + Flask
- Nginx (weighted load balancing)
- Docker
- Jenkins (CI/CD pipeline)
- GitHub (Pipeline as Code)

## Pipeline Stages
1. Checkout SCM
2. Build Canary image
3. Deploy Canary at 10% — stable:9, canary:1
4. Health check at 10%
5. Promote to 50% — stable:5, canary:5
6. Health check at 50%
7. Promote to 100% — canary:1
8. Decommission Stable — canary becomes new stable

## Rollback Strategy
If any health check fails:
- Canary container stopped and removed automatically
- Nginx upstream reset to point only to stable
- 100% traffic returns to stable instantly
- No manual intervention required

## Key difference from Blue-Green
Blue-Green switches traffic instantly (0% or 100%).
Canary shifts traffic gradually (10% → 50% → 100%),
limiting blast radius if something goes wrong.

