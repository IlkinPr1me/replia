# Replai v3.0
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Replai — AI Reply Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-943P8C3YXD"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-943P8C3YXD');
  </script>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23c8f05a'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='serif' font-size='18' font-style='italic' fill='%230a0a0a'%3Er%3C/text%3E%3C/svg%3E"/>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23c8f05a'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-family='serif' font-size='18' font-style='italic' fill='%230a0a0a'%3Er%3C/text%3E%3C/svg%3E"/>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#0a0a0a;--bg2:#111;--surface:#161616;
      --border:rgba(255,255,255,0.07);--text:#f0ede8;
      --muted:rgba(240,237,232,0.4);--accent:#c8f05a;
      --accent-dim:rgba(200,240,90,0.1);--red:#ff6b6b;
    }
    [data-theme="light"]{
      --bg:#f8f7f4;--bg2:#eeeee8;--surface:#fff;
      --border:rgba(0,0,0,0.08);--text:#1a1a1a;
      --muted:rgba(26,26,26,0.45);--accent:#4a8a00;
      --accent-dim:rgba(74,138,0,0.1);
    }
    html{scroll-behavior:smooth}
    body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-weight:300;min-height:100vh;transition:background .3s,color .3s}

    /* NAV */
    nav{position:sticky;top:0;z-index:100;padding:0 28px;height:56px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);background:rgba(10,10,10,.9);backdrop-filter:blur(20px);transition:background .3s}
    [data-theme="light"] nav{background:rgba(248,247,244,.9)}
    .logo{font-family:'Instrument Serif',serif;font-size:20px;letter-spacing:-.02em;color:var(--text)}
    .logo span{color:var(--accent)}
    .nav-right{display:flex;align-items:center;gap:10px}

    .theme-btn{width:34px;height:34px;border-radius:50%;border:1px solid var(--border);background:var(--surface);color:var(--text);display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;transition:border-color .2s,background .3s}
    .theme-btn:hover{border-color:var(--accent)}

    /* USER DROPDOWN */
    .user-menu-wrap{position:relative;display:inline-block}
    .user-menu-btn{display:flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:100px;padding:5px 14px 5px 5px;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:13px;color:var(--text);transition:border-color .2s}
    .user-menu-btn:hover{border-color:rgba(200,240,90,.4)}
    .user-avatar{width:26px;height:26px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#0a0a0a;flex-shrink:0}
    .user-name{max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .arrow{color:var(--muted);font-size:9px}
    .user-dropdown{display:none;position:absolute;right:0;top:calc(100% + 8px);background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:6px;min-width:200px;box-shadow:0 8px 32px rgba(0,0,0,.4);z-index:500}
    [data-theme="light"] .user-dropdown{box-shadow:0 8px 32px rgba(0,0,0,.15)}
    .user-dropdown.open{display:block}
    .dropdown-header{padding:10px 12px;border-bottom:1px solid var(--border);margin-bottom:4px}
    .dropdown-header-label{font-size:11px;color:var(--muted);margin-bottom:3px}
    .dropdown-header-email{font-size:13px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .dropdown-stat{padding:8px 12px;font-size:13px;color:var(--muted);display:flex;justify-content:space-between;align-items:center}
    .dropdown-stat span:last-child{color:var(--accent);font-weight:500}
    .dropdown-divider{height:1px;background:var(--border);margin:4px 0}
    .dropdown-btn{width:100%;text-align:left;padding:9px 12px;border:none;background:transparent;color:var(--red);font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;border-radius:10px;transition:background .2s}
    .dropdown-btn:hover{background:rgba(255,107,107,.1)}

    .btn-signin{padding:8px 18px;border-radius:100px;border:none;background:var(--accent);color:#0a0a0a;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:opacity .2s}
    [data-theme="light"] .btn-signin{background:#1a1a1a;color:#fff}
    .btn-signin:hover{opacity:.85}

    /* ONBOARDING */
    .onboard-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);z-index:200;display:flex;align-items:center;justify-content:center;padding:24px}
    .onboard-overlay.hidden{display:none}
    .onboard-card{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:40px;max-width:460px;width:100%;text-align:center}
    .onboard-dots{display:flex;gap:6px;justify-content:center;margin-bottom:28px}
    .onboard-dot{height:6px;border-radius:3px;background:var(--border);transition:all .3s}
    .onboard-dot.active{width:20px;background:var(--accent)}
    .onboard-dot:not(.active){width:6px}
    .onboard-icon{font-size:48px;margin-bottom:18px}
    .onboard-card h2{font-family:'Instrument Serif',serif;font-size:26px;letter-spacing:-.02em;margin-bottom:10px}
    .onboard-card p{font-size:14px;color:var(--muted);line-height:1.7;margin-bottom:28px}
    .btn-onboard{width:100%;padding:14px;border-radius:12px;border:none;background:var(--accent);color:#0a0a0a;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer;transition:opacity .2s}
    [data-theme="light"] .btn-onboard{background:#1a1a1a;color:#fff}
    .btn-onboard:hover{opacity:.85}
    .skip-link{display:block;margin-top:14px;font-size:13px;color:var(--muted);cursor:pointer}
    .skip-link:hover{color:var(--text)}

    /* AUTH MODAL */
    .auth-overlay{position:fixed;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(8px);z-index:300;display:flex;align-items:center;justify-content:center;padding:24px}
    .auth-overlay.hidden{display:none}
    .auth-modal{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:36px;max-width:380px;width:100%;position:relative}
    .auth-close{position:absolute;top:14px;right:14px;width:28px;height:28px;border-radius:50%;border:1px solid var(--border);background:var(--bg2);color:var(--muted);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:all .2s}
    .auth-close:hover{border-color:var(--accent);color:var(--text)}
    .auth-modal h2{font-family:'Instrument Serif',serif;font-size:24px;letter-spacing:-.02em;margin-bottom:6px}
    .auth-modal > p{font-size:13px;color:var(--muted);margin-bottom:20px;line-height:1.6}
    .auth-tabs{display:flex;gap:2px;background:var(--bg2);border-radius:10px;padding:3px;margin-bottom:20px}
    .auth-tab{flex:1;padding:8px;border-radius:8px;border:none;background:transparent;color:var(--muted);font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s}
    .auth-tab.active{background:var(--surface);color:var(--text);border:1px solid var(--border)}
    .field{margin-bottom:12px}
    .field label{display:block;font-size:11px;font-weight:500;color:var(--muted);margin-bottom:5px;letter-spacing:.05em;text-transform:uppercase}
    .field input{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:10px 13px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;outline:none;transition:border-color .2s}
    .field input:focus{border-color:rgba(200,240,90,.4)}
    .field input::placeholder{color:var(--muted)}
    .btn-full{width:100%;padding:12px;border-radius:10px;border:none;background:var(--accent);color:#0a0a0a;font-family:'DM Sans',sans-serif;font-size:14px;font-weight:500;cursor:pointer;transition:opacity .2s;margin-top:6px}
    [data-theme="light"] .btn-full{background:#1a1a1a;color:#fff}
    .btn-full:hover{opacity:.85}
    .btn-full:disabled{opacity:.4;cursor:not-allowed}
    .msg{font-size:12px;margin-top:10px;text-align:center;padding:8px;border-radius:8px}
    .msg.error{color:var(--red);background:rgba(255,107,107,.1)}
    .msg.success{color:var(--accent);background:var(--accent-dim)}

    /* LIMIT BAR */
    .limit-bar{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:11px 16px;margin-bottom:16px;display:flex;align-items:center;gap:12px;transition:background .3s}
    .limit-text{font-size:13px;color:var(--muted);white-space:nowrap}
    .limit-text strong{color:var(--text);font-weight:500}
    .limit-track{flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden}
    .limit-fill{height:100%;background:var(--accent);border-radius:2px;transition:width .5s}
    .limit-fill.warn{background:#febc2e}
    .limit-fill.danger{background:var(--red)}
    .limit-cta{font-size:12px;color:var(--accent);cursor:pointer;white-space:nowrap;font-weight:500}
    .limit-cta:hover{text-decoration:underline}

    /* APP */
    .app{max-width:1000px;margin:0 auto;padding:32px 24px 80px}
    .page-header{margin-bottom:24px}
    .page-header h1{font-family:'Instrument Serif',serif;font-size:clamp(28px,4vw,40px);letter-spacing:-.02em;margin-bottom:5px}
    .page-header h1 em{font-style:italic;color:var(--accent)}
    .page-header p{color:var(--muted);font-size:14px}

    .tabs{display:flex;gap:2px;background:var(--bg2);border-radius:10px;padding:3px;margin-bottom:18px}
    .tab{flex:1;padding:8px;border-radius:8px;border:none;background:transparent;color:var(--muted);font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s;text-align:center}
    .tab.active{background:var(--surface);color:var(--text);border:1px solid var(--border)}
    .tab-content{display:none}
    .tab-content.active{display:block}

    .cols{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}
    @media(max-width:680px){.cols{grid-template-columns:1fr}}

    .panel{background:var(--surface);border:1px solid var(--border);border-radius:18px;overflow:hidden;transition:background .3s}
    .panel-head{padding:13px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
    .panel-title{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
    .panel-body{padding:18px}
    textarea{width:100%;background:transparent;border:none;outline:none;color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;font-weight:300;line-height:1.7;resize:none;min-height:200px}
    textarea::placeholder{color:var(--muted)}

    .opts-row{display:flex;flex-wrap:wrap;gap:6px;margin-top:13px;padding-top:13px;border-top:1px solid var(--border)}
    .opt-lbl{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;margin-right:4px}
    .chip{padding:5px 12px;border-radius:100px;border:1px solid var(--border);font-size:12px;color:var(--muted);cursor:pointer;transition:all .2s;background:transparent;font-family:'DM Sans',sans-serif}
    .chip:hover{border-color:rgba(200,240,90,.25);color:var(--text)}
    .chip.active{background:var(--accent-dim);border-color:rgba(200,240,90,.35);color:var(--accent)}

    .ctx-wrap{margin-top:13px;padding-top:13px;border-top:1px solid var(--border)}
    .ctx-lbl{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
    .ctx-input{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:9px 13px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;outline:none;transition:border-color .2s,background .3s}
    .ctx-input:focus{border-color:rgba(200,240,90,.4)}
    .ctx-input::placeholder{color:var(--muted)}

    .btn-gen{width:100%;background:var(--accent);color:#0a0a0a;border:none;padding:14px;border-radius:12px;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer;transition:opacity .2s,transform .15s;display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px}
    [data-theme="light"] .btn-gen{background:#1a1a1a;color:#fff}
    .btn-gen:hover{opacity:.88}
    .btn-gen:active{transform:scale(.98)}
    .btn-gen:disabled{opacity:.35;cursor:not-allowed;transform:none}
    .spinner{width:15px;height:15px;border:2px solid rgba(0,0,0,.2);border-top-color:#0a0a0a;border-radius:50%;animation:spin .7s linear infinite;display:none}
    [data-theme="light"] .spinner{border-color:rgba(255,255,255,.2);border-top-color:#fff}

    .out-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:200px;gap:10px;color:var(--muted);text-align:center}
    .out-icon{font-size:32px;opacity:.3}
    .out-empty p{font-size:13px;max-width:160px;line-height:1.6}
    .out-text{display:none;font-size:14px;line-height:1.8;color:var(--text);white-space:pre-wrap;min-height:200px}
    .out-text.show{display:block}
    .out-actions{display:none;gap:8px;margin-top:13px;padding-top:13px;border-top:1px solid var(--border)}
    .out-actions.show{display:flex}
    .btn-copy{flex:1;background:var(--accent);color:#0a0a0a;border:none;padding:10px;border-radius:10px;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:opacity .2s}
    [data-theme="light"] .btn-copy{background:#1a1a1a;color:#fff}
    .btn-copy:hover{opacity:.85}
    .btn-redo{background:var(--bg2);color:var(--muted);border:1px solid var(--border);padding:10px 14px;border-radius:10px;font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s}
    .btn-redo:hover{border-color:rgba(200,240,90,.25);color:var(--text)}

    .style-card{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:22px;margin-bottom:12px;transition:background .3s}
    .style-card h3{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
    .style-ta{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:11px 13px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;font-weight:300;line-height:1.7;resize:none;outline:none;min-height:90px;transition:border-color .2s,background .3s}
    .style-ta:focus{border-color:rgba(200,240,90,.4)}
    .style-ta::placeholder{color:var(--muted)}

    .hist-panel{background:var(--surface);border:1px solid var(--border);border-radius:18px;overflow:hidden;transition:background .3s}
    .hist-item{padding:13px 18px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .2s}
    .hist-item:last-child{border-bottom:none}
    .hist-item:hover{background:var(--bg2)}
    .hist-meta{display:flex;justify-content:space-between;font-size:13px;font-weight:500;margin-bottom:4px}
    .hist-meta span{color:var(--muted);font-weight:300;font-size:12px}
    .hist-preview{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .hist-empty{padding:40px;text-align:center;color:var(--muted);font-size:13px}

    .char-c{font-size:11px;color:var(--muted)}

    .toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--surface);border:1px solid var(--border);border-radius:100px;padding:10px 20px;font-size:13px;color:var(--text);opacity:0;transition:all .3s;z-index:1000;pointer-events:none;white-space:nowrap}
    .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
    .toast.ok{border-color:rgba(200,240,90,.3);color:var(--accent)}
    .toast.err{border-color:rgba(255,107,107,.3);color:var(--red)}

    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    .dots::after{content:'';animation:dots 1.2s infinite}
    @keyframes dots{0%{content:''}33%{content:'.'}66%{content:'..'}100%{content:'...'}}
  </style>
</head>
<body>

<!-- ONBOARDING -->
<div class="onboard-overlay hidden" id="onboarding">
  <div class="onboard-card">
    <div class="onboard-dots" id="onboardDots"></div>
    <div id="onboardContent"></div>
  </div>
</div>

<!-- AUTH -->
<div class="auth-overlay hidden" id="authOverlay">
  <div class="auth-modal">
    <button class="auth-close" onclick="closeAuth()">✕</button>
    <h2>Welcome to Replai</h2>
    <p>Sign in to save history and get 50 replies/day.</p>
    <div class="auth-tabs">
      <button class="auth-tab active" onclick="switchAuth('login',this)">Sign In</button>
      <button class="auth-tab" onclick="switchAuth('signup',this)">Sign Up</button>
    </div>
    <div id="authLogin">
      <div class="field"><label>Email</label><input type="email" id="loginEmail" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="loginPass" placeholder="••••••••"/></div>
      <button class="btn-full" id="loginBtn" onclick="doLogin()">Sign In →</button>
      <div id="loginMsg"></div>
    </div>
    <div id="authSignup" style="display:none">
      <div class="field"><label>Email</label><input type="email" id="signupEmail" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="signupPass" placeholder="Min 6 characters"/></div>
      <button class="btn-full" id="signupBtn" onclick="doSignup()">Create Account →</button>
      <div id="signupMsg"></div>
    </div>
  </div>
</div>

<!-- NAV -->
<nav>
  <div style="display:flex;align-items:center;gap:16px">
    <a href="https://thereplai.netlify.app" style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--muted);text-decoration:none;transition:color .2s" onmouseover="this.style.color='var(--text)'" onmouseout="this.style.color='var(--muted)'">
      ← Back
    </a>
    <a href="https://thereplai.netlify.app" style="text-decoration:none">
      <div class="logo">repl<span>ai</span></div>
    </a>
  </div>
  <div class="nav-right">
    <button class="theme-btn" onclick="toggleTheme()" id="themeBtn">🌙</button>
    <div id="navAuth"></div>
  </div>
</nav>

<!-- APP -->
<div class="app">
  <div class="page-header">
    <h1>Generate a <em>perfect reply.</em></h1>
    <p>Paste any message and get an AI-crafted response in seconds.</p>
  </div>

  <div class="limit-bar">
    <div class="limit-text"><strong id="limitUsed">0</strong> / <strong id="limitMax">20</strong> replies today</div>
    <div class="limit-track"><div class="limit-fill" id="limitFill" style="width:0%"></div></div>
    <span class="limit-cta" id="limitCta" onclick="openAuth()">Sign in for 50/day →</span>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('reply',this)">✦ Reply</button>
    <button class="tab" onclick="switchTab('history',this)">History</button>
    <button class="tab" onclick="switchTab('style',this)">My Style</button>
  </div>

  <div class="tab-content active" id="tab-reply">
    <div class="cols">
      <div>
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">Incoming message</span>
            <span class="char-c" id="charCount">0 chars</span>
          </div>
          <div class="panel-body">
            <textarea id="inputMsg" placeholder="Paste the email or message you received here..." oninput="updateCharCount()"></textarea>
            <div class="opts-row">
              <span class="opt-lbl">Tone</span>
              <button class="chip active" onclick="selectChip(this)">Professional</button>
              <button class="chip" onclick="selectChip(this)">Friendly</button>
              <button class="chip" onclick="selectChip(this)">Brief</button>
              <button class="chip" onclick="selectChip(this)">Formal</button>
            </div>
            <div class="opts-row">
              <span class="opt-lbl">Lang</span>
              <button class="chip active" onclick="selectChip(this)">English</button>
              <button class="chip" onclick="selectChip(this)">Russian</button>
              <button class="chip" onclick="selectChip(this)">Auto</button>
            </div>
            <div class="ctx-wrap">
              <div class="ctx-lbl">Extra context (optional)</div>
              <input class="ctx-input" id="extraCtx" placeholder="e.g. decline politely, ask for more time..."/>
            </div>
          </div>
        </div>
        <button class="btn-gen" id="genBtn" onclick="generateReply()">
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
              <div class="out-icon">✦</div>
              <p>Your AI reply will appear here</p>
            </div>
            <div class="out-text" id="outText"></div>
            <div class="out-actions" id="outActions">
              <button class="btn-copy" onclick="copyReply()"><span id="copyLbl">Copy Reply</span></button>
              <button class="btn-redo" onclick="generateReply()">↻ Redo</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="tab-content" id="tab-history">
    <div class="hist-panel" id="histList">
      <div class="hist-empty">No replies yet. Generate your first reply!</div>
    </div>
  </div>

  <div class="tab-content" id="tab-style">
    <div class="style-card">
      <h3>Your writing style</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:10px;line-height:1.6">Paste 2–3 examples of how you write. Replai will match your tone.</p>
      <textarea class="style-ta" id="styleEx" placeholder="Example: Hey John, thanks for reaching out! Let me check and get back to you by Thursday." oninput="saveStyle()"></textarea>
    </div>
    <div class="style-card">
      <h3>About you</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:10px;line-height:1.6">Tell Replai about your role so replies are always relevant.</p>
      <textarea class="style-ta" id="aboutMe" placeholder="e.g. I'm a freelance designer. I keep emails short and always end with a clear next step." oninput="saveStyle()" style="min-height:70px"></textarea>
      <p style="margin-top:8px;font-size:12px;color:var(--muted)">✓ Saved automatically</p>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ── SUPABASE ─────────────────────────────────────
const { createClient } = supabase;
const sb = createClient(
  'https://bangwkorrlhpmjzmgudt.supabase.co',
  'sb_publishable_iqcJprNPDgpZtbsibf4DLg_MzJ-X_Je'
);

// ── STATE ────────────────────────────────────────
let currentUser = null;
let currentReply = '';
let isGenerating = false;
let history = JSON.parse(localStorage.getItem('replai_history') || '[]');
const FREE_LIMIT = 20;
const AUTH_LIMIT = 50;

// ── THEME ────────────────────────────────────────
const html = document.documentElement;
setTheme(localStorage.getItem('replai_theme') || 'dark');

function setTheme(t) {
  html.setAttribute('data-theme', t);
  document.getElementById('themeBtn').textContent = t === 'dark' ? '🌙' : '☀️';
  localStorage.setItem('replai_theme', t);
}
function toggleTheme() {
  setTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
}

// ── ONBOARDING ───────────────────────────────────
const slides = [
  { icon:'✉️', title:'Paste any message', text:'Copy an email or text you received and paste it into the left panel. No account needed.' },
  { icon:'🎯', title:'Pick your tone', text:'Choose Professional, Friendly, Brief or Formal. Add extra context if needed.' },
  { icon:'✦',  title:'Copy & send', text:'Get a perfect reply in seconds. Copy it and send. Sign up to get 50 replies/day!' },
];
let slideIdx = 0;

function showOnboarding() {
  if (localStorage.getItem('replai_onboarded')) return;
  document.getElementById('onboarding').classList.remove('hidden');
  renderSlide();
}

function renderSlide() {
  const s = slides[slideIdx];
  const dots = slides.map((_, i) =>
    `<div class="onboard-dot ${i === slideIdx ? 'active' : ''}"></div>`
  ).join('');
  document.getElementById('onboardDots').innerHTML = dots;
  document.getElementById('onboardContent').innerHTML = `
    <div class="onboard-icon">${s.icon}</div>
    <h2>${s.title}</h2>
    <p>${s.text}</p>
    <button class="btn-onboard" onclick="nextSlide()">
      ${slideIdx < slides.length - 1 ? 'Next →' : 'Get Started ✦'}
    </button>
    ${slideIdx === 0 ? '<span class="skip-link" onclick="doneOnboard()">Skip intro</span>' : ''}
  `;
}

function nextSlide() {
  if (slideIdx < slides.length - 1) { slideIdx++; renderSlide(); }
  else doneOnboard();
}

function doneOnboard() {
  localStorage.setItem('replai_onboarded', '1');
  document.getElementById('onboarding').classList.add('hidden');
}

// ── AUTH ─────────────────────────────────────────
function openAuth() { document.getElementById('authOverlay').classList.remove('hidden'); }
function closeAuth() { document.getElementById('authOverlay').classList.add('hidden'); }

function switchAuth(mode, el) {
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('authLogin').style.display  = mode === 'login'  ? 'block' : 'none';
  document.getElementById('authSignup').style.display = mode === 'signup' ? 'block' : 'none';
}

async function doLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pass  = document.getElementById('loginPass').value;
  const msg   = document.getElementById('loginMsg');
  const btn   = document.getElementById('loginBtn');
  if (!email || !pass) { showMsg(msg, 'Fill in all fields', 'error'); return; }
  btn.disabled = true; btn.textContent = 'Signing in...';
  const { error } = await sb.auth.signInWithPassword({ email, password: pass });
  btn.disabled = false; btn.textContent = 'Sign In →';
  if (error) showMsg(msg, error.message, 'error');
  else { closeAuth(); showToast('Welcome back! ✦', 'ok'); }
}

async function doSignup() {
  const email = document.getElementById('signupEmail').value.trim();
  const pass  = document.getElementById('signupPass').value;
  const msg   = document.getElementById('signupMsg');
  const btn   = document.getElementById('signupBtn');
  if (!email || !pass) { showMsg(msg, 'Fill in all fields', 'error'); return; }
  if (pass.length < 6) { showMsg(msg, 'Password min 6 characters', 'error'); return; }
  btn.disabled = true; btn.textContent = 'Creating...';
  const { error } = await sb.auth.signUp({ email, password: pass });
  btn.disabled = false; btn.textContent = 'Create Account →';
  if (error) showMsg(msg, error.message, 'error');
  else showMsg(msg, '✓ Check your email to confirm!', 'success');
}

function showMsg(el, text, type) {
  el.className = 'msg ' + type;
  el.textContent = text;
}

async function doLogout() {
  await sb.auth.signOut();
  currentUser = null;
  renderNav();
  updateLimitBar();
  showToast('Signed out', '');
}

// ── NAV ──────────────────────────────────────────
function renderNav() {
  const el = document.getElementById('navAuth');
  if (currentUser) {
    const shortEmail = currentUser.email.split('@')[0];
    const letter = shortEmail[0].toUpperCase();
    el.innerHTML = `
      <div class="user-menu-wrap" id="userWrap">
        <button class="user-menu-btn" onclick="toggleDropdown()">
          <div class="user-avatar">${letter}</div>
          <span class="user-name">${shortEmail}</span>
          <span class="arrow">▾</span>
        </button>
        <div class="user-dropdown" id="userDropdown">
          <div class="dropdown-header">
            <div class="dropdown-header-label">Signed in as</div>
            <div class="dropdown-header-email">${currentUser.email}</div>
          </div>
          <div class="dropdown-stat">
            <span>Replies today</span>
            <span>${getUsedToday()} / ${getLimit()}</span>
          </div>
          <div class="dropdown-divider"></div>
          <button class="dropdown-btn" onclick="doLogout()">Sign out</button>
        </div>
      </div>
    `;
  } else {
    el.innerHTML = `<button class="btn-signin" onclick="openAuth()">Sign in</button>`;
  }
}

function toggleDropdown() {
  const d = document.getElementById('userDropdown');
  if (d) d.classList.toggle('open');
}

document.addEventListener('click', function(e) {
  const wrap = document.getElementById('userWrap');
  if (wrap && !wrap.contains(e.target)) {
    const d = document.getElementById('userDropdown');
    if (d) d.classList.remove('open');
  }
});

// ── LIMITS ───────────────────────────────────────
function todayKey() { return 'rc_' + new Date().toISOString().slice(0,10); }
function getUsedToday() { return parseInt(localStorage.getItem(todayKey()) || '0'); }
function incrementUsed() { localStorage.setItem(todayKey(), getUsedToday() + 1); }
function getLimit() { return currentUser ? AUTH_LIMIT : FREE_LIMIT; }

function updateLimitBar() {
  const used = getUsedToday();
  const max  = getLimit();
  const pct  = Math.min((used / max) * 100, 100);
  document.getElementById('limitUsed').textContent = used;
  document.getElementById('limitMax').textContent  = max;
  const fill = document.getElementById('limitFill');
  fill.style.width = pct + '%';
  fill.className = 'limit-fill' + (pct >= 90 ? ' danger' : pct >= 70 ? ' warn' : '');
  const cta = document.getElementById('limitCta');
  cta.style.display = currentUser ? 'none' : 'block';
}

// ── TABS ─────────────────────────────────────────
function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
  if (name === 'history') renderHistory();
}

function selectChip(el) {
  el.closest('.opts-row').querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}

function getChip(label) {
  for (const row of document.querySelectorAll('.opts-row')) {
    if (row.querySelector('.opt-lbl')?.textContent.toLowerCase().includes(label)) {
      return row.querySelector('.chip.active')?.textContent || '';
    }
  }
  return '';
}

function updateCharCount() {
  document.getElementById('charCount').textContent = document.getElementById('inputMsg').value.length + ' chars';
}

function saveStyle() {
  localStorage.setItem('replai_style', document.getElementById('styleEx').value);
  localStorage.setItem('replai_about', document.getElementById('aboutMe').value);
}
function loadStyle() {
  const s = localStorage.getItem('replai_style');
  const a = localStorage.getItem('replai_about');
  if (s) document.getElementById('styleEx').value = s;
  if (a) document.getElementById('aboutMe').value = a;
}

// ── GENERATE ─────────────────────────────────────
async function generateReply() {
  if (isGenerating) return;
  const msg = document.getElementById('inputMsg').value.trim();
  if (!msg) { showToast('Paste a message first', 'err'); return; }

  if (getUsedToday() >= getLimit()) {
    showToast(currentUser ? 'Daily limit reached' : 'Sign in for more replies!', 'err');
    if (!currentUser) openAuth();
    return;
  }

  isGenerating = true;
  const btn = document.getElementById('genBtn');
  const spinner = document.getElementById('spinner');
  const label = document.getElementById('genLabel');
  btn.disabled = true;
  spinner.style.display = 'block';
  label.textContent = 'Generating';
  label.classList.add('dots');

  document.getElementById('outEmpty').style.display = 'none';
  document.getElementById('outText').classList.add('show');
  document.getElementById('outText').innerHTML = '<span style="color:var(--muted)">Writing your reply...</span>';
  document.getElementById('outActions').classList.remove('show');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg,
        tone: getChip('tone'),
        language: getChip('lang'),
        context: document.getElementById('extraCtx').value.trim(),
        style_examples: localStorage.getItem('replai_style') || '',
        about_me: localStorage.getItem('replai_about') || ''
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Server error');

    currentReply = data.reply;
    incrementUsed();
    updateLimitBar();
    renderNav();

    document.getElementById('outText').textContent = currentReply;
    document.getElementById('outCharCount').textContent = currentReply.length + ' chars';
    document.getElementById('outActions').classList.add('show');
    saveToHistory(msg, currentReply, getChip('tone'));

  } catch(e) {
    document.getElementById('outText').innerHTML = '';
    document.getElementById('outEmpty').style.display = 'flex';
    showToast('Error: ' + e.message, 'err');
  } finally {
    isGenerating = false;
    btn.disabled = false;
    spinner.style.display = 'none';
    label.textContent = '✦ Generate Reply';
    label.classList.remove('dots');
  }
}

function copyReply() {
  if (!currentReply) return;
  navigator.clipboard.writeText(currentReply).then(() => {
    document.getElementById('copyLbl').textContent = '✓ Copied!';
    setTimeout(() => document.getElementById('copyLbl').textContent = 'Copy Reply', 2000);
    showToast('Copied ✓', 'ok');
  });
}

// ── HISTORY ──────────────────────────────────────
function saveToHistory(incoming, reply, tone) {
  history.unshift({
    id: Date.now(), incoming: incoming.slice(0,100), reply, tone,
    time: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})
  });
  if (history.length > 30) history.pop();
  localStorage.setItem('replai_history', JSON.stringify(history));
}

function renderHistory() {
  const el = document.getElementById('histList');
  if (!history.length) { el.innerHTML = '<div class="hist-empty">No replies yet.</div>'; return; }
  el.innerHTML = history.map(h => `
    <div class="hist-item" onclick="loadHistory(${h.id})">
      <div class="hist-meta"><span>${h.tone}</span><span>${h.time}</span></div>
      <div class="hist-preview">${h.incoming.replace(/</g,'&lt;')}...</div>
    </div>`).join('');
}

function loadHistory(id) {
  const item = history.find(h => h.id === id);
  if (!item) return;
  currentReply = item.reply;
  document.getElementById('outEmpty').style.display = 'none';
  document.getElementById('outText').classList.add('show');
  document.getElementById('outText').textContent = item.reply;
  document.getElementById('outActions').classList.add('show');
  document.getElementById('outCharCount').textContent = item.reply.length + ' chars';
  document.querySelectorAll('.tab')[0].click();
}

// ── TOAST ────────────────────────────────────────
function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + (type||'') + ' show';
  setTimeout(() => t.classList.remove('show'), 3000);
}

// ── INIT ─────────────────────────────────────────
window.onload = async () => {
  loadStyle();
  renderHistory();
  updateLimitBar();

  const { data: { session } } = await sb.auth.getSession();
  if (session) currentUser = session.user;
  renderNav();
  updateLimitBar();

  sb.auth.onAuthStateChange((_e, session) => {
    currentUser = session?.user || null;
    renderNav();
    updateLimitBar();
  });

  setTimeout(showOnboarding, 800);
};

// Close modals on outside click
document.getElementById('authOverlay').addEventListener('click', e => {
  if (e.target.id === 'authOverlay') closeAuth();
});
document.getElementById('onboarding').addEventListener('click', e => {
  if (e.target.id === 'onboarding') doneOnboard();
});

// Enter key for auth
document.getElementById('loginPass').addEventListener('keydown', e => { if(e.key==='Enter') doLogin(); });
document.getElementById('signupPass').addEventListener('keydown', e => { if(e.key==='Enter') doSignup(); });
</script>
</body>
</html>"""


class ReplyRequest(BaseModel):
    message: str
    tone: str = "Professional"
    language: str = "English"
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

    system = "You are Replai, an AI assistant that writes email and message replies on behalf of the user. Write a reply that sounds natural, human, and matches the requested tone. Output ONLY the reply text itself, ready to send. No explanations, no preamble."
    if req.about_me:
        system += f"\n\nAbout the user: {req.about_me}"
    if req.style_examples:
        system += f"\n\nExamples of how the user writes:\n{req.style_examples}"

    user_prompt = f"Write a {req.tone.lower()} reply to the following message"
    if req.language != "Auto":
        user_prompt += f" in {req.language}"
    user_prompt += f":\n\n---\n{req.message}\n---"
    if req.context:
        user_prompt += f"\n\nExtra instructions: {req.context}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
            )
            data = response.json()
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Groq error"))
            return {"reply": data["choices"][0]["message"]["content"]}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
