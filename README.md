### Getting started

#### Backend Setup
```bash
# Install uv. Alternatively, you can just run `pip install uv`.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies.
uv sync

# Start application.
cd src/digest
uv run main.py
```

#### Development with Docker (Recommended)
```bash
# Start all services (PostgreSQL, Backend, Frontend)
docker compose up

# The services will be available at:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
# - PostgreSQL: localhost:5432
```

#### Frontend Development (Local Setup)
```bash
# Navigate to frontend directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

