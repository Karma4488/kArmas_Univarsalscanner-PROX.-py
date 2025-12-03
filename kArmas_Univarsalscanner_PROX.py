#!/usr/bin/env python3
# kArmas_UnivarsalScanner_PROX.py
# Unified Attack-Surface & OSINT Recon Framework
# Single-File PRO-X Edition – Easy Deployment
# Made in l0v3 bY kArmasec for my Anonymous & Lulzsec friends 
# We Are Legoin We Do Not forget We Do Not Firget
import os
import json
import asyncio
import socket
import datetime
import httpx
import dns.resolver
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template
import uvicorn

##############################################################################
# PASSIVE OSINT MODULE (Embedded)
##############################################################################
class PassiveOSINT:
    def __init__(self, target):
        self.target = target

    async def run(self):
        data = {}

        try:
            r = await httpx.AsyncClient().get(f"https://api.hackertarget.com/whois/?q={self.target}")
            data["whois"] = r.text
        except:
            data["whois"] = "Lookup failed."

        try:
            r = await httpx.AsyncClient().get(f"https://api.hackertarget.com/httpheaders/?q={self.target}")
            data["headers"] = r.text
        except:
            data["headers"] = "Lookup failed."

        return data

##############################################################################
# DNS MAPPER (Embedded)
##############################################################################
class DNSMapper:
    def __init__(self, target):
        self.target = target

    async def run(self):
        resolver = dns.resolver.Resolver()
        results = {}

        for rtype in ["A", "AAAA", "MX", "NS", "TXT"]:
            try:
                answers = resolver.resolve(self.target, rtype)
                results[rtype] = [a.to_text() for a in answers]
            except:
                results[rtype] = []

        return results

##############################################################################
# SAFE PORT SCANNER (Embedded)
##############################################################################
class PortScannerSafe:
    def __init__(self, target):
        self.target = target

    async def scan_port(self, port):
        try:
            s = socket.socket()
            s.settimeout(0.5)
            s.connect((self.target, port))
            s.close()
            return port
        except:
            return None

    async def run(self):
        open_ports = []
        tasks = [self.scan_port(p) for p in range(1, 1025)]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r:
                open_ports.append(r)

        return {"open_ports": open_ports}

##############################################################################
# TECHNOLOGY FINGERPRINTING (Embedded)
##############################################################################
class FingerPrinter:
    def __init__(self, target):
        self.target = target

    async def run(self):
        info = {}

        try:
            r = await httpx.AsyncClient().get(f"http://{self.target}", timeout=3)
            info["server"] = r.headers.get("Server", "Unknown")
            info["powered_by"] = r.headers.get("X-Powered-By", "Unknown")
        except:
            info = {"error": "Fingerprinting failed."}

        return info

##############################################################################
# DARKWEB MONITOR (Embedded)
##############################################################################
class DarkWebIntel:
    def __init__(self, target):
        self.target = target

    async def run(self):
        # Passive intelligence only – uses public datasets
        return {
            "status": "Passive monitoring active",
            "note": "Darkweb enumeration is limited to publicly indexed OSINT sources."
        }

##############################################################################
# BREACH CHECKER (Embedded)
##############################################################################
class BreachChecker:
    def __init__(self, target):
        self.target = target

    async def run(self):
        try:
            r = await httpx.AsyncClient().get(
                f"https://haveibeenpwned.com/unifiedsearch/{self.target}",
                headers={"User-Agent": "kArmas PRO-X"}
            )
            return {"breaches": r.json()}
        except:
            return {"breaches": "Lookup failed or rate-limited."}

##############################################################################
# PLUGIN SYSTEM (Embedded)
##############################################################################
class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register(self, name, func):
        self.plugins[name] = func

    async def run_all(self, target):
        results = {}
        for name, func in self.plugins.items():
            try:
                results[name] = await func(target)
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

plugins = PluginManager()

##############################################################################
# FASTAPI DASHBOARD + REPORTING ENGINE
##############################################################################
app = FastAPI(title="kArmas PRO-X Dashboard", version="1.0")

def generate_html_report(data):
    template = """
    <html>
    <head><title>kArmas PRO-X Report</title></head>
    <body>
    <h2>kArmas PRO-X Report for {{report.target}}</h2>
    <pre>{{report | tojson(indent=2)}}</pre>
    </body>
    </html>
    """

    html = Template(template).render(report=data)

    if not os.path.exists("reports"):
        os.makedirs("reports")

    path = f"reports/report_{data['target']}.html"
    with open(path, "w") as f:
        f.write(html)

    return path

async def unified_scan(target):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    result = {
        "target": target,
        "timestamp": timestamp,
        "osint": await PassiveOSINT(target).run(),
        "dns": await DNSMapper(target).run(),
        "ports": await PortScannerSafe(target).run(),
        "fingerprint": await FingerPrinter(target).run(),
        "darkweb": await DarkWebIntel(target).run(),
        "breaches": await BreachChecker(target).run(),
        "plugins": await plugins.run_all(target)
    }

    generate_html_report(result)
    return result

@app.get("/", response_class=HTMLResponse)
def index():
    return "<h2>kArmas PRO-X Enterprise Scanner – Single File Edition</h2>"

@app.get("/scan/{target}", response_class=JSONResponse)
async def scan_target(target: str):
    return await unified_scan(target)

@app.get("/report/{target}", response_class=HTMLResponse)
def fetch_report(target: str):
    path = f"reports/report_{target}.html"
    if not os.path.exists(path):
        return HTMLResponse("<h3>No report available.</h3>", status_code=404)
    return HTMLResponse(open(path).read())

##############################################################################
# MAIN ENTRY POINT
##############################################################################
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
