# Replai v3.0 — Unified Design
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os, httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Replai — AI Reply Assistant</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232563eb'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='serif' font-size='18' font-style='italic' fill='white'%3Er%3C/text%3E%3C/svg%3E"/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  <style>
/* ── REPLAI SHARED DESIGN SYSTEM ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #ffffff;
  --bg2: #f5f5f7;
  --bg3: #e8e8ed;
  --surface: #ffffff;
  --border: #d2d2d7;
  --text: #1d1d1f;
  --text2: #3d3d3f;
  --muted: #6e6e73;
  --muted2: #a1a1aa;
  --accent: #2563eb;
  --accent-h: #1d4ed8;
  --accent-light: rgba(37,99,235,0.08);
  --accent-border: rgba(37,99,235,0.2);
  --green: #16a34a;
  --green-bg: #f0fdf4;
  --green-border: #bbf7d0;
  --red: #dc2626;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-full: 980px;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.07);
  --shadow-md: 0 4px 20px rgba(0,0,0,0.08);
  --shadow-lg: 0 20px 60px rgba(0,0,0,0.1);
  --nav-bg: rgba(255,255,255,0.86);
}
[data-theme="dark"] {
  --bg: #000000;
  --bg2: #111111;
  --bg3: #1c1c1e;
  --surface: #1c1c1e;
  --border: #3a3a3c;
  --text: #f5f5f7;
  --text2: #d1d1d6;
  --muted: #98989d;
  --muted2: #636366;
  --accent: #3b82f6;
  --accent-h: #2563eb;
  --accent-light: rgba(59,130,246,0.12);
  --accent-border: rgba(59,130,246,0.25);
  --green: #4ade80;
  --green-bg: rgba(74,222,128,0.08);
  --green-border: rgba(74,222,128,0.2);
  --shadow-md: 0 4px 20px rgba(0,0,0,0.3);
  --shadow-lg: 0 20px 60px rgba(0,0,0,0.5);
  --nav-bg: rgba(0,0,0,0.86);
}

html { scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  transition: background .3s, color .3s;
}

/* NAV */
.r-nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  height: 52px; display: flex; align-items: center;
  justify-content: space-between; padding: 0 24px;
  background: var(--nav-bg);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--border);
  transition: background .3s, border-color .3s;
}
.r-logo { font-size: 18px; font-weight: 700; color: var(--text); text-decoration: none; letter-spacing: -.03em; }
.r-logo span { color: var(--accent); }
.r-nav-links { display: flex; align-items: center; gap: 28px; list-style: none; }
.r-nav-links a { font-size: 14px; color: var(--muted); text-decoration: none; transition: color .2s; }
.r-nav-links a:hover { color: var(--text); }
.r-nav-right { display: flex; align-items: center; gap: 8px; }

/* THEME BUTTON */
.r-theme-btn {
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid var(--border); background: var(--bg2);
  color: var(--muted); cursor: pointer; font-size: 15px;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s;
}
.r-theme-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }

/* BUTTONS */
.r-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  font-family: 'Inter', sans-serif; font-weight: 500; cursor: pointer;
  transition: all .2s; text-decoration: none; border: none; outline: none;
  white-space: nowrap;
}
.r-btn-primary { background: var(--accent); color: white; border-radius: var(--radius-full); padding: 0 22px; height: 44px; font-size: 15px; }
.r-btn-primary:hover { background: var(--accent-h); transform: translateY(-1px); box-shadow: 0 4px 16px rgba(37,99,235,0.35); }
.r-btn-primary:active { transform: none; }
.r-btn-sm { height: 34px; padding: 0 16px; font-size: 13px; background: var(--accent); color: white; border-radius: var(--radius-full); }
.r-btn-sm:hover { background: var(--accent-h); }
.r-btn-ghost { background: transparent; color: var(--muted); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0 20px; height: 44px; font-size: 15px; }
.r-btn-ghost:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-light); }

/* INPUTS */
.r-input {
  height: 50px; padding: 0 18px; border: 1px solid var(--border);
  border-radius: var(--radius-full); font-family: 'Inter', sans-serif; font-size: 15px;
  color: var(--text); background: var(--bg); outline: none;
  transition: border-color .2s, box-shadow .2s;
  -webkit-appearance: none;
}
.r-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
.r-input::placeholder { color: var(--muted2); }

/* DIVIDER */
.r-divider { height: 1px; background: var(--border); max-width: 1000px; margin: 0 auto; }

/* SECTION */
.r-section { padding: 96px 24px; max-width: 1000px; margin: 0 auto; }
.r-eyebrow { font-size: 13px; font-weight: 500; color: var(--accent); letter-spacing: .05em; text-transform: uppercase; margin-bottom: 14px; }
.r-h2 { font-size: clamp(32px,5vw,52px); font-weight: 700; letter-spacing: -.03em; line-height: 1.08; color: var(--text); margin-bottom: 14px; }
.r-lead { font-size: 18px; color: var(--muted); line-height: 1.65; font-weight: 300; max-width: 540px; }

/* CARD */
.r-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 28px; transition: background .3s, border-color .3s; }
.r-card:hover { border-color: var(--accent-border); }

/* BADGE */
.r-badge { display: inline-flex; align-items: center; gap: 7px; background: var(--green-bg); border: 1px solid var(--green-border); color: var(--green); padding: 5px 14px; border-radius: var(--radius-full); font-size: 12px; font-weight: 500; }
.r-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: r-pulse 2s infinite; }

/* REVEAL */
.r-reveal { opacity: 0; transform: translateY(20px); transition: opacity .6s ease, transform .6s ease; }
.r-reveal.r-visible { opacity: 1; transform: translateY(0); }

/* FOOTER */
.r-footer { border-top: 1px solid var(--border); padding: 48px 24px 32px; max-width: 1000px; margin: 0 auto; transition: border-color .3s; }
.r-footer-top { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.r-footer-brand p { font-size: 14px; color: var(--muted); margin-top: 10px; line-height: 1.6; max-width: 220px; }
.r-footer-col h4 { font-size: 12px; font-weight: 600; color: var(--text); letter-spacing: .05em; text-transform: uppercase; margin-bottom: 16px; }
.r-footer-col a { display: block; font-size: 14px; color: var(--muted); text-decoration: none; margin-bottom: 10px; transition: color .2s; }
.r-footer-col a:hover { color: var(--text); }
.r-footer-bottom { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; padding-top: 24px; border-top: 1px solid var(--border); }
.r-footer-copy { font-size: 13px; color: var(--muted2); }
.r-social { display: flex; gap: 8px; }
.r-social-btn { width: 34px; height: 34px; border: 1px solid var(--border); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: var(--muted); text-decoration: none; font-size: 13px; font-weight: 700; transition: all .2s; }
.r-social-btn:hover { border-color: var(--accent); color: var(--accent); }

@keyframes r-pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

@media (max-width: 680px) {
  .r-nav-links { display: none; }
  .r-nav { padding: 0 16px; }
  .r-footer-top { grid-template-columns: 1fr 1fr; }
  .r-section { padding: 70px 20px; }
}
@media (max-width: 480px) {
  .r-footer-top { grid-template-columns: 1fr; }
}


/* APP LAYOUT */
.app-wrap { min-height: 100vh; padding-top: 52px; }
.app-main { max-width: 960px; margin: 0 auto; padding: 40px 24px 80px; }
.app-header { margin-bottom: 28px; }
.app-header h1 { font-size: clamp(26px,4vw,36px); font-weight: 700; letter-spacing: -.03em; margin-bottom: 4px; }
.app-header h1 span { color: var(--accent); }
.app-header p { font-size: 15px; color: var(--muted); }

/* TABS */
.tabs { display: flex; gap: 2px; background: var(--bg2); border-radius: var(--radius-md); padding: 3px; margin-bottom: 24px; border: 1px solid var(--border); }
.tab { flex: 1; padding: 9px; border-radius: 9px; border: none; background: transparent; color: var(--muted); font-family: 'Inter',sans-serif; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .2s; text-align: center; }
.tab.active { background: var(--surface); color: var(--text); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
.tab-content { display: none; }
.tab-content.active { display: block; }

/* COLS */
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
@media(max-width:700px){ .cols{grid-template-columns:1fr} }

/* PANEL */
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); overflow: hidden; transition: background .3s, border-color .3s; }
.panel-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.panel-title { font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.panel-body { padding: 18px; }
textarea { width: 100%; background: transparent; border: none; outline: none; color: var(--text); font-family: 'Inter',sans-serif; font-size: 14px; font-weight: 400; line-height: 1.7; resize: none; min-height: 200px; }
textarea::placeholder { color: var(--muted2); }

/* OPTIONS */
.opts { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.opt-label { font-size: 10px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); display: flex; align-items: center; margin-right: 4px; }
.chip { padding: 5px 13px; border-radius: var(--radius-full); border: 1px solid var(--border); font-size: 12px; font-weight: 500; color: var(--muted); cursor: pointer; transition: all .2s; background: transparent; font-family: 'Inter',sans-serif; }
.chip:hover { border-color: var(--accent-border); color: var(--text); }
.chip.active { background: var(--accent-light); border-color: var(--accent-border); color: var(--accent); }

/* GENDER */
.gender-row { display: flex; gap: 8px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.g-btn { flex: 1; padding: 9px 6px; border-radius: var(--radius-md); border: 1px solid var(--border); cursor: pointer; transition: all .2s; background: transparent; font-family: 'Inter',sans-serif; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.g-btn:hover { border-color: var(--accent-border); }
.g-btn.active { background: var(--accent-light); border-color: var(--accent-border); }
.g-icon { font-size: 18px; }
.g-name { font-size: 10px; font-weight: 600; color: var(--muted); letter-spacing: .04em; text-transform: uppercase; }
.g-btn.active .g-name { color: var(--accent); }

/* CONTEXT */
.ctx-wrap { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.ctx-label { font-size: 10px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin-bottom: 7px; }
.ctx-input { width: 100%; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 9px 13px; color: var(--text); font-family: 'Inter',sans-serif; font-size: 13px; outline: none; transition: border-color .2s, background .3s; }
.ctx-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
.ctx-input::placeholder { color: var(--muted2); }

/* GENERATE BTN */
.gen-btn { width: 100%; background: var(--accent); color: white; border: none; padding: 14px; border-radius: var(--radius-md); font-family: 'Inter',sans-serif; font-size: 15px; font-weight: 600; cursor: pointer; transition: background .2s, transform .15s; display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; }
.gen-btn:hover { background: var(--accent-h); }
.gen-btn:active { transform: scale(.98); }
.gen-btn:disabled { opacity: .45; cursor: not-allowed; transform: none; }
.spinner { width: 15px; height: 15px; border: 2px solid rgba(255,255,255,.3); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; display: none; }

/* OUTPUT */
.out-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; gap: 10px; color: var(--muted2); text-align: center; }
.out-empty-icon { font-size: 28px; opacity: .4; }
.out-text { display: none; font-size: 14px; line-height: 1.75; color: var(--text); white-space: pre-wrap; min-height: 200px; }
.out-text.show { display: block; }
.out-actions { display: none; gap: 8px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.out-actions.show { display: flex; }
.copy-btn { flex: 1; background: var(--accent); color: white; border: none; padding: 10px; border-radius: var(--radius-md); font-family: 'Inter',sans-serif; font-size: 13px; font-weight: 600; cursor: pointer; transition: background .2s; }
.copy-btn:hover { background: var(--accent-h); }
.redo-btn { background: var(--bg2); color: var(--muted); border: 1px solid var(--border); padding: 10px 14px; border-radius: var(--radius-md); font-family: 'Inter',sans-serif; font-size: 13px; cursor: pointer; transition: all .2s; }
.redo-btn:hover { border-color: var(--accent-border); color: var(--accent); }

/* LIMIT BAR */
.limit-bar { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 10px 16px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; transition: background .3s; }
.limit-text { font-size: 13px; color: var(--muted); white-space: nowrap; }
.limit-text strong { color: var(--text); font-weight: 600; }
.limit-track { flex: 1; height: 4px; background: var(--bg3); border-radius: 2px; overflow: hidden; }
.limit-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width .5s ease; }
.limit-fill.warn { background: #f59e0b; }
.limit-fill.danger { background: var(--red); }
.limit-cta { font-size: 12px; color: var(--accent); cursor: pointer; white-space: nowrap; font-weight: 500; }
.limit-cta:hover { text-decoration: underline; }

/* HISTORY */
.hist-panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); overflow: hidden; }
.hist-item { padding: 14px 18px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background .2s; }
.hist-item:last-child { border-bottom: none; }
.hist-item:hover { background: var(--bg2); }
.hist-meta { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 4px; color: var(--text); }
.hist-time { color: var(--muted2); font-weight: 400; font-size: 12px; }
.hist-preview { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hist-empty { padding: 40px; text-align: center; color: var(--muted2); font-size: 13px; }

/* STYLE TAB */
.style-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 22px; margin-bottom: 12px; transition: background .3s; }
.style-card h3 { font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
.style-ta { width: 100%; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 11px 13px; color: var(--text); font-family: 'Inter',sans-serif; font-size: 13px; line-height: 1.65; resize: none; outline: none; min-height: 90px; transition: border-color .2s, background .3s; }
.style-ta:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
.style-ta::placeholder { color: var(--muted2); }

/* AUTH MODAL */
.auth-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(8px); z-index: 300; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-overlay.hidden { display: none; }
.auth-modal { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 36px; max-width: 380px; width: 100%; position: relative; transition: background .3s; }
.auth-close { position: absolute; top: 14px; right: 14px; width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--border); background: var(--bg2); color: var(--muted); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; transition: all .2s; }
.auth-close:hover { border-color: var(--accent); color: var(--accent); }
.auth-modal h2 { font-size: 22px; font-weight: 700; letter-spacing: -.02em; margin-bottom: 6px; }
.auth-modal > p { font-size: 14px; color: var(--muted); margin-bottom: 20px; line-height: 1.5; }
.auth-tabs { display: flex; gap: 2px; background: var(--bg2); border-radius: var(--radius-md); padding: 3px; margin-bottom: 20px; }
.auth-tab { flex: 1; padding: 8px; border-radius: 9px; border: none; background: transparent; color: var(--muted); font-family: 'Inter',sans-serif; font-size: 13px; font-weight: 500; cursor: pointer; transition: all .2s; }
.auth-tab.active { background: var(--surface); color: var(--text); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 11px; font-weight: 600; color: var(--muted); margin-bottom: 6px; letter-spacing: .04em; text-transform: uppercase; }
.field input { width: 100%; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 10px 13px; color: var(--text); font-family: 'Inter',sans-serif; font-size: 14px; outline: none; transition: border-color .2s; }
.field input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
.field input::placeholder { color: var(--muted2); }
.auth-btn { width: 100%; padding: 12px; border-radius: var(--radius-md); border: none; background: var(--accent); color: white; font-family: 'Inter',sans-serif; font-size: 14px; font-weight: 600; cursor: pointer; transition: background .2s; margin-top: 4px; }
.auth-btn:hover { background: var(--accent-h); }
.auth-btn:disabled { opacity: .45; cursor: not-allowed; }
.auth-msg { font-size: 12px; margin-top: 10px; text-align: center; padding: 8px; border-radius: var(--radius-sm); }
.auth-msg.err { color: var(--red); background: rgba(220,38,38,0.08); }
.auth-msg.ok { color: var(--green); background: var(--green-bg); }

/* NAV USER */
.user-wrap { position: relative; }
.user-btn { display: flex; align-items: center; gap: 8px; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-full); padding: 5px 14px 5px 5px; cursor: pointer; font-family: 'Inter',sans-serif; font-size: 13px; color: var(--text); transition: border-color .2s; }
.user-btn:hover { border-color: var(--accent-border); }
.u-avatar { width: 26px; height: 26px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: white; flex-shrink: 0; }
.u-dropdown { display: none; position: absolute; right: 0; top: calc(100% + 8px); background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 6px; min-width: 200px; box-shadow: var(--shadow-lg); z-index: 200; }
.u-dropdown.open { display: block; }
.u-head { padding: 10px 12px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.u-head-label { font-size: 10px; color: var(--muted2); margin-bottom: 2px; }
.u-head-email { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.u-stat { padding: 8px 12px; font-size: 13px; color: var(--muted); display: flex; justify-content: space-between; }
.u-stat span:last-child { color: var(--accent); font-weight: 600; }
.u-logout { width: 100%; text-align: left; padding: 9px 12px; border: none; background: transparent; color: var(--red); font-family: 'Inter',sans-serif; font-size: 13px; cursor: pointer; border-radius: var(--radius-sm); transition: background .2s; margin-top: 4px; border-top: 1px solid var(--border); }
.u-logout:hover { background: rgba(220,38,38,0.08); }

/* CHAR COUNT */
.char-c { font-size: 11px; color: var(--muted2); }

/* TOAST */
#r-toast { position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%) translateY(20px); background: var(--text); color: var(--bg); padding: 10px 22px; border-radius: var(--radius-full); font-size: 13px; font-weight: 500; opacity: 0; transition: all .3s; z-index: 1000; pointer-events: none; white-space: nowrap; }
#r-toast.r-toast-show { opacity: 1; transform: translateX(-50%) translateY(0); }

@keyframes spin { to{ transform: rotate(360deg); } }
.dots::after { content: ''; animation: dots 1.2s infinite; }
@keyframes dots { 0%{content:''} 33%{content:'.'} 66%{content:'..'} 100%{content:'...'} }
  </style>
</head>
<body>

<!-- AUTH MODAL -->
<div class="auth-overlay hidden" id="authOverlay">
  <div class="auth-modal">
    <button class="auth-close" id="authClose">✕</button>
    <h2>Welcome to Replai</h2>
    <p>Sign in to save your history and unlock 50 replies/day.</p>
    <div class="auth-tabs">
      <button class="auth-tab active" id="loginTab">Sign In</button>
      <button class="auth-tab" id="signupTab">Sign Up</button>
    </div>
    <div id="loginForm">
      <div class="field"><label>Email</label><input type="email" id="loginEmail" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="loginPass" placeholder="••••••••"/></div>
      <button class="auth-btn" id="loginBtn">Sign In</button>
      <div id="loginMsg"></div>
    </div>
    <div id="signupForm" style="display:none">
      <div class="field"><label>Email</label><input type="email" id="signupEmail" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="signupPass" placeholder="Min 6 characters"/></div>
      <button class="auth-btn" id="signupBtn">Create Account</button>
      <div id="signupMsg"></div>
    </div>
  </div>
</div>

<!-- NAV -->
<nav class="r-nav">
  <a href="/" class="r-logo">repl<span>ai</span></a>
  <div class="r-nav-right">
    <button class="r-theme-btn">🌙</button>
    <div id="navAuth"></div>
  </div>
</nav>

<!-- APP -->
<div class="app-wrap">
  <div class="app-main">
    <div class="app-header">
      <h1>Generate a <span>perfect reply.</span></h1>
      <p>Paste any message and get an AI-crafted response in seconds.</p>
    </div>

    <!-- LIMIT BAR -->
    <div class="limit-bar">
      <div class="limit-text"><strong id="limitUsed">0</strong> / <strong id="limitMax">20</strong> replies today</div>
      <div class="limit-track"><div class="limit-fill" id="limitFill" style="width:0%"></div></div>
      <span class="limit-cta" id="limitCta">Sign in for 50/day →</span>
    </div>

    <!-- TABS -->
    <div class="tabs">
      <button class="tab active" id="tab-reply-btn">✦ Reply</button>
      <button class="tab" id="tab-history-btn">History</button>
      <button class="tab" id="tab-style-btn">My Style</button>
    </div>

    <!-- REPLY TAB -->
    <div class="tab-content active" id="tab-reply">
      <div class="cols">
        <div>
          <div class="panel">
            <div class="panel-head">
              <span class="panel-title">Incoming message</span>
              <span class="char-c" id="charCount">0 chars</span>
            </div>
            <div class="panel-body">
              <textarea id="inputMsg" placeholder="Paste the message you received here..."></textarea>
              <div class="opts">
                <span class="opt-label">Tone</span>
                <button class="chip active" data-tone="Professional">Professional</button>
                <button class="chip" data-tone="Friendly">Friendly</button>
                <button class="chip" data-tone="Brief">Brief</button>
                <button class="chip" data-tone="Formal">Formal</button>
              </div>
              <div class="opts">
                <span class="opt-label">Lang</span>
                <button class="chip active" data-lang="Auto">Auto</button>
                <button class="chip" data-lang="English">English</button>
                <button class="chip" data-lang="Russian">Russian</button>
                <button class="chip" data-lang="Azerbaijani">Azerbaijani</button>
                <button class="chip" data-lang="Turkish">Turkish</button>
                <button class="chip" data-lang="Arabic">Arabic</button>
                <button class="chip" data-lang="Spanish">Spanish</button>
                <button class="chip" data-lang="French">French</button>
                <button class="chip" data-lang="German">German</button>
              </div>
              <div class="gender-row">
                <button class="g-btn active" data-gender="auto"><span class="g-icon">🤖</span><span class="g-name">Auto</span></button>
                <button class="g-btn" data-gender="male"><span class="g-icon">👨</span><span class="g-name">Male</span></button>
                <button class="g-btn" data-gender="female"><span class="g-icon">👩</span><span class="g-name">Female</span></button>
              </div>
              <div class="ctx-wrap">
                <div class="ctx-label">Extra context (optional)</div>
                <input class="ctx-input" id="extraCtx" placeholder="e.g. decline politely, ask for more time..."/>
              </div>
            </div>
          </div>
          <button class="gen-btn" id="genBtn">
            <div class="spinner" id="spinner"></div>
            <span id="genLabel">✦ Generate Reply</span>
          </button>
        </div>
        <div>
          <div class="panel">
            <div class="panel-head">
              <span class="panel-title">AI Reply</span>
              <span class="char-c" id="outCharCount"></span>
            </div>
            <div class="panel-body">
              <div class="out-empty" id="outEmpty">
                <div class="out-empty-icon">✦</div>
                <p style="font-size:13px;max-width:160px;line-height:1.5">Your AI reply will appear here</p>
              </div>
              <div class="out-text" id="outText"></div>
              <div class="out-actions" id="outActions">
                <button class="copy-btn" id="copyBtn"><span id="copyLbl">Copy Reply</span></button>
                <button class="redo-btn" id="redoBtn">↻ Redo</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- HISTORY TAB -->
    <div class="tab-content" id="tab-history">
      <div class="hist-panel" id="histList">
        <div class="hist-empty">No replies yet. Generate your first reply!</div>
      </div>
    </div>

    <!-- STYLE TAB -->
    <div class="tab-content" id="tab-style">
      <div class="style-card">
        <h3>Your writing style</h3>
        <p style="font-size:13px;color:var(--muted);margin-bottom:10px;line-height:1.6">Paste 2–3 examples of how you write. Replai will match your tone.</p>
        <textarea class="style-ta" id="styleEx" placeholder="Example: Hey John, thanks for reaching out! Let me check and get back to you by Thursday."></textarea>
      </div>
      <div class="style-card">
        <h3>About you</h3>
        <p style="font-size:13px;color:var(--muted);margin-bottom:10px;line-height:1.6">Tell Replai about your role so replies are always relevant.</p>
        <textarea class="style-ta" id="aboutMe" placeholder="e.g. I'm a freelance designer. I keep emails short and always end with a clear next step." style="min-height:70px"></textarea>
        <p style="margin-top:8px;font-size:12px;color:var(--muted2)">✓ Saved automatically</p>
      </div>
    </div>
  </div>
</div>

<div id="r-toast"></div>

<script>
// ── REPLAI SHARED JS ──
(function() {
  // Theme
  const html = document.documentElement;
  const saved = localStorage.getItem('replai_theme') || 'light';
  html.setAttribute('data-theme', saved);

  function setTheme(t) {
    html.setAttribute('data-theme', t);
    localStorage.setItem('replai_theme', t);
    document.querySelectorAll('.r-theme-btn').forEach(btn => {
      btn.textContent = t === 'dark' ? '☀️' : '🌙';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Init theme btn icons
    document.querySelectorAll('.r-theme-btn').forEach(btn => {
      btn.textContent = saved === 'dark' ? '☀️' : '🌙';
      btn.addEventListener('click', () => {
        setTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
      });
    });

    // Reveal on scroll
    const io = new IntersectionObserver(entries => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          setTimeout(() => e.target.classList.add('r-visible'), i * 60);
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('.r-reveal').forEach(el => io.observe(el));

    // Waitlist forms
    document.querySelectorAll('[data-wl-form]').forEach(form => {
      const emailId = form.dataset.wlEmail;
      const btnId   = form.dataset.wlBtn;
      const okId    = form.dataset.wlOk;

      document.getElementById(btnId)?.addEventListener('click', () => submitWl(emailId, btnId, form.id, okId));
      document.getElementById(emailId)?.addEventListener('keydown', e => {
        if (e.key === 'Enter') document.getElementById(btnId)?.click();
      });
    });
  });

  let wlCount = 247;

  window.submitWl = async function(emailId, btnId, formId, okId) {
    const inp = document.getElementById(emailId);
    const btn = document.getElementById(btnId);
    const frm = document.getElementById(formId);
    const ok  = document.getElementById(okId);
    const email = inp.value.trim();

    if (!email || !email.includes('@')) {
      inp.style.borderColor = '#dc2626';
      inp.style.boxShadow = '0 0 0 3px rgba(220,38,38,0.1)';
      inp.animate([{transform:'translateX(-5px)'},{transform:'translateX(5px)'},{transform:'translateX(-3px)'},{transform:'translateX(3px)'},{transform:'translateX(0)'}],{duration:280});
      setTimeout(() => { inp.style.borderColor=''; inp.style.boxShadow=''; }, 1500);
      return;
    }

    btn.textContent = 'Joining...';
    btn.disabled = true;

    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_key: 'ecee2f4f-27fe-4e68-9098-5882736cf6ca',
          subject: '🎉 New Replai Waitlist Signup',
          from_name: 'Replai', email,
          message: `Waitlist: ${email}`
        })
      });
      if ((await res.json()).success) {
        wlCount++;
        frm.style.opacity = '0';
        frm.style.transform = 'translateY(-8px)';
        frm.style.transition = 'all .35s ease';
        setTimeout(() => {
          frm.style.display = 'none';
          if (ok) { ok.style.display = 'flex'; }
        }, 350);
        document.querySelectorAll('.wl-count').forEach(el => el.textContent = wlCount);
      } else throw new Error();
    } catch {
      btn.textContent = 'Try again';
      btn.disabled = false;
    }
  };

  window.showToast = function(msg) {
    const t = document.getElementById('r-toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('r-toast-show');
    setTimeout(() => t.classList.remove('r-toast-show'), 2500);
  };
})();


// ── SUPABASE ──────────────────────────────────────────────────
const { createClient } = supabase;
const sb = createClient(
  'https://bangwkorrlhpmjzmgudt.supabase.co',
  'sb_publishable_iqcJprNPDgpZtbsibf4DLg_MzJ-X_Je'
);

// ── STATE ─────────────────────────────────────────────────────
let currentUser = null;
let currentReply = '';
let isGenerating = false;
let history = JSON.parse(localStorage.getItem('replai_history') || '[]');
const FREE_LIMIT = 20, AUTH_LIMIT = 50;

// ── TABS ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  ['reply','history','style'].forEach(name => {
    document.getElementById('tab-' + name + '-btn').addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      document.getElementById('tab-' + name + '-btn').classList.add('active');
      document.getElementById('tab-' + name).classList.add('active');
      if (name === 'history') renderHistory();
    });
  });

  // Chips
  document.querySelectorAll('.chip[data-tone]').forEach(c => {
    c.addEventListener('click', () => {
      document.querySelectorAll('.chip[data-tone]').forEach(x => x.classList.remove('active'));
      c.classList.add('active');
    });
  });
  document.querySelectorAll('.chip[data-lang]').forEach(c => {
    c.addEventListener('click', () => {
      document.querySelectorAll('.chip[data-lang]').forEach(x => x.classList.remove('active'));
      c.classList.add('active');
    });
  });
  document.querySelectorAll('.g-btn').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('.g-btn').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
    });
  });

  // Char count
  document.getElementById('inputMsg').addEventListener('input', () => {
    document.getElementById('charCount').textContent = document.getElementById('inputMsg').value.length + ' chars';
  });

  // Style autosave
  ['styleEx','aboutMe'].forEach(id => {
    document.getElementById(id).addEventListener('input', () => {
      localStorage.setItem('replai_style', document.getElementById('styleEx').value);
      localStorage.setItem('replai_about', document.getElementById('aboutMe').value);
    });
  });

  // Load style
  const s = localStorage.getItem('replai_style');
  const a = localStorage.getItem('replai_about');
  if (s) document.getElementById('styleEx').value = s;
  if (a) document.getElementById('aboutMe').value = a;

  // Generate
  document.getElementById('genBtn').addEventListener('click', generateReply);
  document.getElementById('redoBtn').addEventListener('click', generateReply);

  // Copy
  document.getElementById('copyBtn').addEventListener('click', () => {
    if (!currentReply) return;
    navigator.clipboard.writeText(currentReply).then(() => {
      document.getElementById('copyLbl').textContent = '✓ Copied!';
      setTimeout(() => document.getElementById('copyLbl').textContent = 'Copy Reply', 2000);
      window.showToast('Copied to clipboard ✓');
    });
  });

  // Auth modal
  document.getElementById('authClose').addEventListener('click', closeAuth);
  document.getElementById('authOverlay').addEventListener('click', e => { if (e.target.id === 'authOverlay') closeAuth(); });
  document.getElementById('loginTab').addEventListener('click', () => switchAuth('login'));
  document.getElementById('signupTab').addEventListener('click', () => switchAuth('signup'));
  document.getElementById('loginBtn').addEventListener('click', doLogin);
  document.getElementById('signupBtn').addEventListener('click', doSignup);
  document.getElementById('loginPass').addEventListener('keydown', e => { if(e.key==='Enter') doLogin(); });
  document.getElementById('signupPass').addEventListener('keydown', e => { if(e.key==='Enter') doSignup(); });
  document.getElementById('limitCta').addEventListener('click', openAuth);

  // Init
  initAuth();
  updateLimitBar();
  renderHistory();
});

// ── AUTH ──────────────────────────────────────────────────────
async function initAuth() {
  const { data: { session } } = await sb.auth.getSession();
  if (session) currentUser = session.user;
  renderNav();
  updateLimitBar();
  sb.auth.onAuthStateChange((_e, session) => {
    currentUser = session?.user || null;
    renderNav();
    updateLimitBar();
  });
}

function openAuth() { document.getElementById('authOverlay').classList.remove('hidden'); }
function closeAuth() { document.getElementById('authOverlay').classList.add('hidden'); }
function switchAuth(mode) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(mode + 'Tab').classList.add('active');
  document.getElementById('loginForm').style.display = mode === 'login' ? 'block' : 'none';
  document.getElementById('signupForm').style.display = mode === 'signup' ? 'block' : 'none';
}

async function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pass = document.getElementById('loginPass').value;
  const msg = document.getElementById('loginMsg');
  const btn = document.getElementById('loginBtn');
  if (!email || !pass) { showAuthMsg(msg, 'Fill in all fields', 'err'); return; }
  btn.disabled = true; btn.textContent = 'Signing in...';
  const { error } = await sb.auth.signInWithPassword({ email, password: pass });
  btn.disabled = false; btn.textContent = 'Sign In';
  if (error) showAuthMsg(msg, error.message, 'err');
  else { closeAuth(); window.showToast('Welcome back! ✦'); }
}

async function doSignup() {
  const email = document.getElementById('signupEmail').value.trim();
  const pass = document.getElementById('signupPass').value;
  const msg = document.getElementById('signupMsg');
  const btn = document.getElementById('signupBtn');
  if (!email || !pass) { showAuthMsg(msg, 'Fill in all fields', 'err'); return; }
  if (pass.length < 6) { showAuthMsg(msg, 'Password min 6 characters', 'err'); return; }
  btn.disabled = true; btn.textContent = 'Creating...';
  const { error } = await sb.auth.signUp({ email, password: pass });
  btn.disabled = false; btn.textContent = 'Create Account';
  if (error) showAuthMsg(msg, error.message, 'err');
  else showAuthMsg(msg, '✓ Check your email to confirm!', 'ok');
}

function showAuthMsg(el, text, type) {
  el.className = 'auth-msg ' + type;
  el.textContent = text;
}

async function doLogout() {
  await sb.auth.signOut();
  window.showToast('Signed out');
}

// ── NAV ───────────────────────────────────────────────────────
function renderNav() {
  const el = document.getElementById('navAuth');
  if (currentUser) {
    const letter = currentUser.email[0].toUpperCase();
    const short = currentUser.email.split('@')[0];
    el.innerHTML = `
      <div class="user-wrap" id="userWrap">
        <button class="user-btn" id="userBtn">
          <div class="u-avatar">${letter}</div>
          <span>${short}</span>
          <span style="color:var(--muted);font-size:10px">▾</span>
        </button>
        <div class="u-dropdown" id="uDrop">
          <div class="u-head">
            <div class="u-head-label">Signed in as</div>
            <div class="u-head-email">${currentUser.email}</div>
          </div>
          <div class="u-stat"><span>Replies today</span><span>${getUsedToday()} / ${getLimit()}</span></div>
          <button class="u-logout" onclick="doLogout()">Sign out</button>
        </div>
      </div>`;
    document.getElementById('userBtn').addEventListener('click', () => {
      document.getElementById('uDrop').classList.toggle('open');
    });
    document.addEventListener('click', e => {
      const wrap = document.getElementById('userWrap');
      if (wrap && !wrap.contains(e.target)) document.getElementById('uDrop')?.classList.remove('open');
    });
  } else {
    el.innerHTML = `<button class="r-btn r-btn-sm" onclick="openAuth()">Sign in</button>`;
  }
}

// ── LIMITS ────────────────────────────────────────────────────
function todayKey() { return 'rc_' + new Date().toISOString().slice(0,10); }
function getUsedToday() { return parseInt(localStorage.getItem(todayKey()) || '0'); }
function incUsed() { localStorage.setItem(todayKey(), getUsedToday() + 1); }
function getLimit() { return currentUser ? AUTH_LIMIT : FREE_LIMIT; }

function updateLimitBar() {
  const used = getUsedToday(), max = getLimit(), pct = Math.min((used/max)*100, 100);
  document.getElementById('limitUsed').textContent = used;
  document.getElementById('limitMax').textContent = max;
  const fill = document.getElementById('limitFill');
  fill.style.width = pct + '%';
  fill.className = 'limit-fill' + (pct >= 90 ? ' danger' : pct >= 70 ? ' warn' : '');
  const cta = document.getElementById('limitCta');
  cta.style.display = currentUser ? 'none' : 'block';
}

// ── GENERATE ──────────────────────────────────────────────────
async function generateReply() {
  if (isGenerating) return;
  const msg = document.getElementById('inputMsg').value.trim();
  if (!msg) { window.showToast('Paste a message first'); return; }
  if (getUsedToday() >= getLimit()) {
    window.showToast(currentUser ? 'Daily limit reached' : 'Sign in for more replies!');
    if (!currentUser) openAuth();
    return;
  }

  isGenerating = true;
  const btn = document.getElementById('genBtn');
  const spinner = document.getElementById('spinner');
  const label = document.getElementById('genLabel');
  btn.disabled = true; spinner.style.display = 'block';
  label.textContent = 'Generating'; label.classList.add('dots');

  document.getElementById('outEmpty').style.display = 'none';
  document.getElementById('outText').classList.remove('show');
  document.getElementById('outText').innerHTML = '';
  document.getElementById('outActions').classList.remove('show');

  try {
    const tone = document.querySelector('.chip[data-tone].active')?.dataset.tone || 'Professional';
    const lang = document.querySelector('.chip[data-lang].active')?.dataset.lang || 'Auto';
    const gender = document.querySelector('.g-btn.active')?.dataset.gender || 'auto';
    const ctx = document.getElementById('extraCtx').value.trim();

    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg, tone, language: lang, gender, context: ctx,
        style_examples: localStorage.getItem('replai_style') || '',
        about_me: localStorage.getItem('replai_about') || ''
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Server error');

    currentReply = data.reply;
    incUsed(); updateLimitBar(); renderNav();
    document.getElementById('outText').textContent = currentReply;
    document.getElementById('outText').classList.add('show');
    document.getElementById('outCharCount').textContent = currentReply.length + ' chars';
    document.getElementById('outActions').classList.add('show');
    saveHistory(msg, currentReply, tone);
  } catch(e) {
    document.getElementById('outEmpty').style.display = 'flex';
    window.showToast('Error: ' + e.message);
  } finally {
    isGenerating = false; btn.disabled = false;
    spinner.style.display = 'none';
    label.textContent = '✦ Generate Reply'; label.classList.remove('dots');
  }
}

// ── HISTORY ───────────────────────────────────────────────────
function saveHistory(msg, reply, tone) {
  history.unshift({ id: Date.now(), msg: msg.slice(0,100), reply, tone, time: new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) });
  if (history.length > 30) history.pop();
  localStorage.setItem('replai_history', JSON.stringify(history));
}

function renderHistory() {
  const el = document.getElementById('histList');
  if (!history.length) { el.innerHTML = '<div class="hist-empty">No replies yet.</div>'; return; }
  el.innerHTML = history.map(h => `
    <div class="hist-item" data-id="${h.id}">
      <div class="hist-meta"><span>${h.tone}</span><span class="hist-time">${h.time}</span></div>
      <div class="hist-preview">${h.msg.replace(/</g,'&lt;')}...</div>
    </div>`).join('');
  el.querySelectorAll('.hist-item').forEach(item => {
    item.addEventListener('click', () => {
      const h = history.find(x => x.id === parseInt(item.dataset.id));
      if (!h) return;
      currentReply = h.reply;
      document.getElementById('outEmpty').style.display = 'none';
      document.getElementById('outText').classList.add('show');
      document.getElementById('outText').textContent = h.reply;
      document.getElementById('outActions').classList.add('show');
      document.getElementById('outCharCount').textContent = h.reply.length + ' chars';
      document.getElementById('tab-reply-btn').click();
    });
  });
}
</script>
</body>
</html>"""


class ReplyRequest(BaseModel):
    message: str
    tone: str = "Professional"
    language: str = "Auto"
    gender: str = "auto"
    context: str = ""
    style_examples: str = ""
    about_me: str = ""


@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE


@app.post("/api/generate")
async def generate_reply(req: ReplyRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    system = "You are Replai, an AI assistant that writes email and message replies. Write a reply that sounds natural, human, and matches the requested tone. Output ONLY the reply text itself, ready to send. No explanations, no preamble."

    if req.about_me:
        system += f"\n\nAbout the user: {req.about_me}"
    if req.style_examples:
        system += f"\n\nExamples of how the user writes:\n{req.style_examples}"

    if req.gender == "auto":
        system += "\n\nAnalyze the name and writing style to detect the gender of the person you are replying to and adjust your reply accordingly."
    elif req.gender == "male":
        system += "\n\nYou are replying to a male person."
    elif req.gender == "female":
        system += "\n\nYou are replying to a female person."

    prompt = f"Write a {req.tone.lower()} reply"
    if req.language != "Auto":
        prompt += f" in {req.language}"
    if "Latest message:" in req.message:
        prompt += f":\n\nConversation history (reply to the latest message):\n{req.message}"
    else:
        prompt += f":\n\n---\n{req.message}\n---"
    if req.context:
        prompt += f"\n\nExtra instructions: {req.context}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
            )
            data = res.json()
            if res.status_code != 200:
                raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Groq error"))
            return {"reply": data["choices"][0]["message"]["content"]}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
