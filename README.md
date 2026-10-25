# GEMINI-FAULT_DETECTION

Enterprise-grade real-time webhook ingestion and automated fault detection powered by FastAPI and Google Gemini AI.

## 🚀 Overview

GEMINI-FAULT_DETECTION receives enterprise webhook events (payment failures, server outages, infrastructure alerts, security incidents) and uses Google Gemini to perform automated incident triage in the background, providing immediate actionable operational steps.

It also features a built-in single-page live monitoring dashboard with real-time event simulation and feed tracking.

## ✨ Key Features

- **Fast & Resilient Webhook Ingestion**: Receives webhooks on `POST /webhook` and returns an immediate `200 OK` acknowledgment while executing AI triage asynchronously.
- **Automated Gemini AI Incident Triage**: Analyzes structured and semi-structured payloads to generate concise, high-priority action plans for operations teams.
- **Graceful Fallback Parsing**: Safely parses strict JSON, single-quoted payloads (`ast.literal_eval`), or raw text bodies without crashing the server.
- **Real-Time Web Dashboard**: Built-in dark mode dashboard at `GET /` featuring:
  - Quick simulator buttons (Payment Failure, Server Outage, Plan Upgraded)
  - Custom JSON payload editor
  - Live auto-polling event feed (refreshes every 2s)
  - Status indicators for FastAPI and Gemini connectivity

## 🛠️ Tech Stack

- **Framework**: FastAPI + Uvicorn
- **AI Model**: Google Gemini (`google-genai` SDK)
- **Environment**: Python 3.10+ / `python-dotenv`

## 📦 Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CMS105/GEMINI-FAULT_DETECTION.git
   cd GEMINI-FAULT_DETECTION
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy the example environment file and add your Google Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GEMINI_API_KEY="your_actual_gemini_api_key"
   ```

5. **Start the Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Access Dashboard**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Webhook & AI Live Monitoring Dashboard |
| `POST` | `/webhook` | Ingests webhook event and queues AI analysis |
| `GET` | `/api/events` | Returns recent 30 webhook events and AI analyses |
| `GET` | `/docs` | Interactive Swagger API documentation |
