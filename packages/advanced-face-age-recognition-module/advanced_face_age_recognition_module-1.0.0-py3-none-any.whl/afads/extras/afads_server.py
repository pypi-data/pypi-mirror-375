# afads_server.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import numpy as np, cv2
from afads import AFADS

app = FastAPI(title="AFADS Demo")
engine = AFADS()

HTML = """<!doctype html><h1>AFADS Check</h1>
<form method="post" action="/check" enctype="multipart/form-data">
  <input type="file" name="file" accept="image/*" required>
  <p><label><input type="radio" name="rule" value="any" checked> If age detected → ALLOW</label></p>
  <p><label><input type="radio" name="rule" value="min"> If age ≥ <input type="number" name="years" value="18" min="10" max="30"></label></p>
  <button type="submit">Check</button>
</form>"""

@app.get("/", response_class=HTMLResponse)
async def index(): return HTML

@app.post("/check", response_class=HTMLResponse)
async def check(file: UploadFile = File(...), rule: str = Form("any"), years: int = Form(18)):
    data = await file.read()
    arr = np.frombuffer(data, np.uint8); bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None: return HTMLResponse("<p>Invalid image</p>", status_code=400)
    res = engine.assess(bgr, return_dict=True)
    age = res.get("estimated_age",-1); p18 = res.get("prob_over_18",0.0)
    if rule=="any": allow = age>=0
    else: allow = (p18>=0.85) if years==18 else (age>=years)
    return HTMLResponse(f"<h2>{'ALLOW ✅' if allow else 'DENY ❌'}</h2><p>Age≈ {age:.1f if age>=0 else '—'} | P(≥18)={p18:.2f}</p><p>{', '.join(res.get('warnings',[]))}</p><p><a href='/'>Back</a></p>")
