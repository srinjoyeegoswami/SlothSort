"""
SlothSort — Demo Sandbox Generator 📂
Creates realistic messy files for safe testing and hackathon demo recording.
No real personal data — just convincing fakes.
"""

import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def _create_text_file(folder: Path, name: str, content: str):
    (folder / name).write_text(content, encoding="utf-8")


def _create_fake_image(folder: Path, name: str, text: str, color: tuple):
    """Create a small PNG with text overlay to simulate a screenshot."""
    img = Image.new("RGB", (800, 600), color)
    draw = ImageDraw.Draw(img)
    # Use default font
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except (OSError, IOError):
        font = ImageFont.load_default()
    draw.text((40, 40), text, fill=(255, 255, 255), font=font)
    draw.text((40, 540), f"Fake screenshot — {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill=(200, 200, 200))
    img.save(folder / name)


def generate_demo_files(target_folder: Path) -> list[str]:
    """Generate 8 realistic messy files and return list of created filenames."""
    target_folder.mkdir(parents=True, exist_ok=True)
    created = []

    # 1. Fake invoice PDF-like text file (simulating a messy download)
    name = "final_v2_REAL(1).txt"
    _create_text_file(target_folder, name, """
INVOICE #INV-2026-0847
Acme Cloud Services LLC
Date: October 15, 2026

Bill To: John Doe
         123 Developer Lane
         San Francisco, CA 94102

Item                          Qty    Price     Total
─────────────────────────────────────────────────────
Premium API Access (Monthly)   1    $49.99    $49.99
Extra Storage (50GB)           1    $12.00    $12.00
Priority Support               1    $25.00    $25.00
─────────────────────────────────────────────────────
                              Subtotal:       $86.99
                              Tax (8.5%):      $7.39
                              TOTAL:          $94.38

Payment Due: November 1, 2026
Thank you for your business!
""".strip())
    created.append(name)

    # 2. Lecture notes
    name = "notes_untitled_44.md"
    _create_text_file(target_folder, name, """
# CS 301 — Distributed Systems Lecture Notes
## Week 7: Consensus Algorithms

### Paxos Protocol
- Proposed by Leslie Lamport (1998)
- Three roles: Proposer, Acceptor, Learner
- Guarantees safety but not liveness in asynchronous networks

### Raft (Easier Consensus)
- Leader election via randomized timeouts
- Log replication: leader appends entries, followers replicate
- Much easier to understand than Paxos

### Key Takeaways
- CAP theorem: you can only pick 2 of Consistency, Availability, Partition tolerance
- In practice, most systems choose AP with eventual consistency
- Raft is used in etcd (Kubernetes) and CockroachDB
""".strip())
    created.append(name)

    # 3. Code snippet
    name = "test_api_handler_BACKUP.py"
    _create_text_file(target_folder, name, '''
"""FastAPI endpoint for user authentication — backup copy."""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import hashlib
import secrets

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

# In-memory store (demo only)
users_db = {
    "admin": hashlib.sha256(b"supersecret").hexdigest(),
}

@app.post("/login")
async def login(req: LoginRequest):
    hashed = hashlib.sha256(req.password.encode()).hexdigest()
    if req.username in users_db and users_db[req.username] == hashed:
        token = secrets.token_hex(32)
        return {"token": token, "message": "Login successful"}
    raise HTTPException(401, "Invalid credentials")

@app.get("/health")
async def health():
    return {"status": "ok"}
'''.strip())
    created.append(name)

    # 4. Screenshot-like image
    name = "Screenshot_2026-10-19_142210.png"
    _create_fake_image(target_folder, name,
                       "Dashboard — Monthly Revenue\n\n"
                       "Revenue: $142,380\n"
                       "Users: 8,241\n"
                       "Churn: 2.1%\n\n"
                       "[ Chart placeholder ]",
                       (30, 40, 80))
    created.append(name)

    # 5. Another screenshot
    name = "IMG_20261018_WA0047.png"
    _create_fake_image(target_folder, name,
                       "WhatsApp Chat Screenshot\n\n"
                       "Alex: Hey, did you finish the presentation?\n"
                       "You: Almost done, sending tonight\n"
                       "Alex: Cool, the client meeting is at 10am\n"
                       "You: Got it 👍",
                       (20, 60, 40))
    created.append(name)

    # 6. CSV data file
    name = "export_data(3)_FINAL.csv"
    _create_text_file(target_folder, name, """date,category,amount,description
2026-09-01,Groceries,47.82,Whole Foods Market
2026-09-03,Transport,12.50,Uber ride to office
2026-09-05,Subscription,14.99,Netflix monthly
2026-09-07,Dining,38.20,Dinner at Olive Garden
2026-09-10,Utilities,156.00,Electric bill September
2026-09-12,Groceries,62.15,Trader Joe's weekly shop
2026-09-15,Healthcare,25.00,Pharmacy co-pay
2026-09-18,Shopping,89.99,Amazon — wireless headphones
""".strip())
    created.append(name)

    # 7. Personal document
    name = "cover letter draft_v3 EDITME.txt"
    _create_text_file(target_folder, name, """
Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position
at TechCorp Inc., as advertised on LinkedIn.

With over 5 years of experience in full-stack development, specializing in Python,
React, and cloud infrastructure (AWS/GCP), I have consistently delivered scalable
solutions that drive business growth. At my current role at StartupXYZ, I led the
migration of our monolithic architecture to microservices, reducing deployment time
by 73% and improving system reliability to 99.95% uptime.

I am particularly drawn to TechCorp's mission of democratizing AI tools for small
businesses. My experience building developer platforms and my passion for open-source
contribution (500+ GitHub contributions in 2025) align perfectly with your team's goals.

I look forward to discussing how my skills can contribute to TechCorp's continued
innovation.

Best regards,
Jane Developer
""".strip())
    created.append(name)

    # 8. JSON config dump
    name = "config_dump_oct2026.json"
    _create_text_file(target_folder, name, """{
  "app_name": "MyProject",
  "version": "2.4.1",
  "environment": "production",
  "database": {
    "host": "db.internal.example.com",
    "port": 5432,
    "name": "myproject_prod",
    "pool_size": 20
  },
  "redis": {
    "host": "redis.internal.example.com",
    "port": 6379,
    "ttl_seconds": 3600
  },
  "features": {
    "dark_mode": true,
    "beta_ai_assistant": true,
    "export_to_pdf": false
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "output": "stdout"
  }
}""")
    created.append(name)

    return created


if __name__ == "__main__":
    demo = Path(__file__).resolve().parent.parent / "demo_messy_folder"
    files = generate_demo_files(demo)
    print(f"[OK] Generated {len(files)} demo files in {demo}")
    for f in files:
        print(f"   - {f}")
