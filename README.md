# ShopSense Analytics & AI Intelligence Platform

ShopSense is an enterprise multi-vendor e-commerce analytics, business intelligence, and decision intelligence platform. It combines real-time transaction processing, vendor performance tracking, RFM customer segmentation, RAG-powered shopping recommendation engines, executive store diagnostics, dynamic AI price optimization, and real-time WebSocket event streams into a unified web application.

---

## Technical Stack

### Backend Architecture
- **Framework**: FastAPI (Python 3.12)
- **Database & ORM**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT authentication with HTTP-Only cookie handling and Role-Based Access Control (Admin, Vendor, Customer)
- **Generative AI Engine**: Google Gemini REST API integration with dynamic runtime API key loading and multi-model failover (`gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemma-4-26b-a4b-it`)
- **Real-Time Communication**: Async WebSocket event distribution manager

### Frontend Architecture
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Visualization**: Recharts charting library
- **Icons**: Lucide React

---

## Key System Features

### 1. Multi-Vendor E-Commerce & Management Hub
- **Role-Based Workspaces**: Separate administrative views for System Administrators and Approved Merchants.
- **Vendor Governance**: Admin approval workflow for pending vendor applications and active catalog monitoring.
- **Product & Inventory Management**: CRUD operations for multi-vendor catalog listings, stock thresholds, and categories.

### 2. Business Intelligence & RFM Analytics
- **Interactive Visualizations**: Time-series revenue distribution charts, order volume trends, category performance, and top-selling product breakdown.
- **RFM Customer Segmentation**: Recency, Frequency, and Monetary scoring classifying buyers into VIP, Regular, New, and Inactive segments.
- **Data Exporting**: One-click CSV exports for inventory valuation and customer profile analytics.

### 3. AI & Decision Intelligence Studio
- **RAG AI Shopping Assistant**: Natural language product search engine combining local database vector scoring with generative AI catalog recommendation synthesis.
- **Executive Store Analyst**: Automated diagnostic engine generating multi-paragraph strategic advice on inventory risk, average order value, and customer retention. Supports vendor-specific audits and platform-wide marketplace overviews.

### 4. Merchant Intelligence Studio & Real-Time Event Hub
- **Real-Time Event Stream**: Live WebSocket event feed broadcasting real-time order placement notifications, inventory depletion warnings, and customer activity logs.
- **AI Product Copywriter**: Generative marketing copy generator crafting search-optimized product titles, descriptions, and feature bullet points.
- **Smart Price Optimizer**: Dynamic pricing engine calculating optimal price points based on stock velocity, competitor price trends, and demand elasticity.

---

## Project Structure

```text
infyspring/
├── app/
│   ├── core/
│   │   ├── config.py             # Application environment settings & model configs
│   │   ├── database.py           # SQLite connection & session manager
│   │   ├── deps.py               # Authentication & dependency injection guards
│   │   ├── security.py           # Password hashing & JWT token generators
│   │   └── websocket_manager.py  # Real-time WebSocket connection manager
│   ├── models/                   # SQLAlchemy ORM schemas (Admin, Vendor, Customer, Product, Transaction)
│   ├── routers/                  # API endpoints (Auth, Admin, Vendors, Products, AI, BI, WebSockets)
│   ├── schemas/                  # Pydantic data validation schemas
│   ├── services/                 # Core business logic & AI integration services
│   └── main.py                   # FastAPI application initialization & middleware setup
├── frontend/                     # React + Vite frontend application
│   ├── src/
│   │   ├── api.js                # Centralized API service client
│   │   ├── components/           # Reusable UI layout & navigation components
│   │   └── pages/                # Workspace views (Dashboard, Analytics, AI, Merchant Studio)
│   ├── package.json
│   └── vite.config.js
├── LICENSE                       # MIT License
├── requirements.txt              # Backend Python dependencies
└── README.md
```

---

## Installation & Setup Guide

### 1. Environment Setup
Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/satwik834/shopsense-backend.git
cd infyspring
```

Create and configure the environment variable file `.env` in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-flash-lite-latest
```

### 2. Backend Installation

Create and activate a Python virtual environment:

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Launch the FastAPI application server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API documentation will be accessible at `http://127.0.0.1:8000/docs`.

### 3. Frontend Installation

Navigate to the `frontend` directory:

```bash
cd frontend
npm install
npm run dev
```

The application frontend will be accessible at `http://localhost:5173`.

---

## License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/Users/Saathwik/Desktop/Projects/infyspring/LICENSE) file for full details.
