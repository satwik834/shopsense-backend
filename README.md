# ShopSense Backend

ShopSense is a multi-vendor e-commerce analytics platform designed to provide actionable business intelligence, vendor performance tracking, and customer insights.

## Base Stack
- **Backend Framework:** FastAPI (Python)
- **Database:** SQLite  with SQLAlchemy ORM

## Project Structure
```text
infyspring/
├── app/
│   ├── core/
│   │   ├── config.py         # Application settings
│   │   └── database.py       # Database connection & session setup
│   ├── models/               # SQLAlchemy ORM models (Vendors, Products, Customers, Transactions)
│   ├── schemas/              # Pydantic validation schemas
│   ├── api/                  # API endpoints
│   └── main.py               # Application entry point
├── scripts/                  # Helper & initialization scripts
├── requirements.txt          # Python dependencies
└── README.md
```

## Getting Started

### 1. Set up Virtual Environment
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
uvicorn app.main:app --reload
```

Interactive API documentation available at `http://127.0.0.1:8000/docs`.
