import os
import ast
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "enterprise-starter", ".env"))

app = FastAPI(title="Enterprise Webhook Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# In-memory store for latest 30 events
EVENT_HISTORY = []

def process_event_with_ai(event_id: str, payload: dict):
    event = next((e for e in EVENT_HISTORY if e["id"] == event_id), None)
    if not client:
        if event:
            event["status"] = "Skipped"
            event["ai_analysis"] = "GEMINI_API_KEY not configured in .env"
        return

    prompt = f"Analyze this enterprise webhook and outline 3 brief, actionable steps:\n{json.dumps(payload, default=str)}"
    try:
        res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        if event:
            event["status"] = "Completed"
            event["ai_analysis"] = res.text
    except Exception as e:
        if event:
            event["status"] = "Failed"
            event["ai_analysis"] = str(e)

@app.get("/api/events")
def get_events():
    return EVENT_HISTORY

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        body = (await request.body()).decode("utf-8", errors="ignore")
        try:
            payload = ast.literal_eval(body)
        except Exception:
            payload = {"raw_body": body}

    event_id = f"evt_{uuid.uuid4().hex[:6]}"
    record = {
        "id": event_id,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "payload": payload,
        "status": "Processing",
        "ai_analysis": None
    }
    EVENT_HISTORY.insert(0, record)
    if len(EVENT_HISTORY) > 30:
        EVENT_HISTORY.pop()

    print(f"\n[RECEIVED EVENT {event_id}]: {payload}")
    background_tasks.add_task(process_event_with_ai, event_id, payload)
    return {"status": "success", "event_id": event_id, "message": "Event queued successfully"}

@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Webhook & AI Monitor</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    body { background: #0f172a; color: #f8fafc; padding: 24px; max-width: 1200px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid #334155; padding-bottom: 16px; }
    .badge { font-size: 12px; padding: 4px 10px; border-radius: 99px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
    .badge-green { background: #064e3b; color: #34d399; }
    .badge-purple { background: #4c1d95; color: #c084fc; }
    .badge-amber { background: #78350f; color: #fcd34d; }
    .grid { display: grid; grid-template-columns: 360px 1fr; gap: 24px; }
    @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
    h2 { font-size: 16px; margin-bottom: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .btn-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
    button { background: #334155; color: #fff; border: none; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-size: 14px; text-align: left; font-weight: 500; }
    button:hover { background: #475569; }
    .btn-primary { background: #6366f1; text-align: center; font-weight: 600; width: 100%; margin-top: 10px; }
    .btn-primary:hover { background: #4f46e5; }
    textarea { width: 100%; height: 140px; background: #090d16; color: #38bdf8; border: 1px solid #334155; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 13px; outline: none; }
    .event-card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
    .event-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; }
    pre { background: #090d16; color: #94a3b8; padding: 10px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin-bottom: 10px; }
    .ai-box { background: rgba(99, 102, 241, 0.1); border-left: 3px solid #818cf8; padding: 10px 12px; border-radius: 4px; font-size: 13px; line-height: 1.5; white-space: pre-wrap; color: #e2e8f0; }
  </style>
</head>
<body>
  <header>
    <div>
      <h1 style="font-size: 20px;">Enterprise Webhook & AI Monitor</h1>
      <p style="font-size: 13px; color: #94a3b8;">Real-time ingestion and automated Gemini triage</p>
    </div>
    <div style="display: flex; gap: 8px;">
      <span class="badge badge-green">● Port 8000 Live</span>
      <span class="badge badge-purple">● Gemini Active</span>
    </div>
  </header>

  <div class="grid">
    <!-- Simulator Panel -->
    <div class="card">
      <h2>Quick Simulator</h2>
      <div class="btn-group">
        <button onclick="setPayload({event: 'payment_failed', amount: 99.00, customer: 'Acme Corp', reason: 'expired_card'})">💳 Payment Failed</button>
        <button onclick="setPayload({event: 'server_outage', host: 'prod-api-01', cpu: '98%', status: 'unresponsive'})">🚨 Server Outage</button>
        <button onclick="setPayload({event: 'subscription_upgraded', plan: 'Enterprise Plus', seats: 100})">🚀 Plan Upgraded</button>
      </div>

      <h2>Custom Payload</h2>
      <textarea id="payload-input">{
  "event": "payment_failed",
  "amount": 99.00,
  "customer": "Acme Corp",
  "reason": "expired_card"
}</textarea>
      <button class="btn-primary" onclick="sendWebhook()">Send Webhook</button>
    </div>

    <!-- Live Event Feed -->
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <h2>Live Webhook Feed</h2>
        <span id="counter" style="font-size: 13px; color: #94a3b8;">0 events</span>
      </div>
      <div id="feed">
        <p style="color: #64748b; font-size: 14px;">No events yet. Click one of the simulator buttons to fire a test webhook.</p>
      </div>
    </div>
  </div>

  <script>
    function setPayload(obj) {
      document.getElementById('payload-input').value = JSON.stringify(obj, null, 2);
    }

    async function sendWebhook() {
      try {
        const body = JSON.parse(document.getElementById('payload-input').value);
        await fetch('/webhook', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        loadEvents();
      } catch (err) {
        alert('Error: ' + err.message);
      }
    }

    async function loadEvents() {
      try {
        const res = await fetch('/api/events');
        const events = await res.json();
        document.getElementById('counter').innerText = events.length + ' events';
        
        const feed = document.getElementById('feed');
        if (!events.length) return;

        feed.innerHTML = events.map(e => `
          <div class="event-card">
            <div class="event-header">
              <span><strong>${e.id}</strong> · ${e.timestamp}</span>
              <span class="badge ${e.status === 'Completed' ? 'badge-green' : 'badge-amber'}">${e.status}</span>
            </div>
            <pre>${JSON.stringify(e.payload, null, 2)}</pre>
            ${e.ai_analysis ? `<div class="ai-box"><strong>Gemini AI Action Plan:</strong>\n${e.ai_analysis}</div>` : ''}
          </div>
        `).join('');
      } catch (e) {
        console.error(e);
      }
    }

    loadEvents();
    setInterval(loadEvents, 2000);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
