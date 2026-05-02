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
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{
      --bg:#0a0a0a;--bg2:#111;--surface:#161616;--border:rgba(255,255,255,0.07);
      --text:#f0ede8;--muted:rgba(240,237,232,0.4);--accent:#c8f05a;
      --accent-dim:rgba(200,240,90,0.1);--red:#ff6b6b;
    }
    [data-theme="light"]{
      --bg:#f8f7f4;--bg2:#eeeee8;--surface:#fff;--border:rgba(0,0,0,0.08);
      --text:#1a1a1a;--muted:rgba(26,26,26,0.45);--accent:#4a8a00;
      --accent-dim:rgba(74,138,0,0.1);
    }
    html{scroll-behavior:smooth}
    body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-weight:300;min-height:100vh;transition:background .3s,color .3s}

    /* NAV */
    nav{position:sticky;top:0;z-index:100;padding:0 32px;height:56px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);background:rgba(10,10,10,.85);backdrop-filter:blur(20px);transition:background .3s}
    [data-theme="light"] nav{background:rgba(248,247,244,.9)}
    .logo{font-family:'Instrument Serif',serif;font-size:20px;letter-spacing:-.02em}
    .logo span{color:var(--accent)}
    .nav-right{display:flex;align-items:center;gap:10px}
    .theme-btn{width:34px;height:34px;border-radius:50%;border:1px solid var(--border);background:var(--surface);color:var(--text);display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;transition:border-color .2s,background .3s}
    .theme-btn:hover{border-color:var(--accent)}
    .user-pill{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);padding:6px 12px;border:1px solid var(--border);border-radius:100px;background:var(--surface)}
    .user-pill .dot{width:7px;height:7px;border-radius:50%;background:var(--accent)}
    .btn-sm{padding:7px 16px;border-radius:100px;border:none;font-family:'DM Sans',sans-serif;font-size:12px;font-weight:500;cursor:pointer;transition:opacity .2s}
    .btn-accent{background:var(--accent);color:#0a0a0a}
    [data-theme="light"] .btn-accent{background:#1a1a1a;color:#fff}
    .btn-ghost{background:transparent;color:var(--muted);border:1px solid var(--border)}
    .btn-ghost:hover{border-color:var(--accent);color:var(--text)}
    .btn-accent:hover{opacity:.85}

    /* ONBOARDING OVERLAY */
    .onboarding{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(8px);z-index:200;display:flex;align-items:center;justify-content:center;padding:24px}
    [data-theme="light"] .onboarding{background:rgba(0,0,0,.4)}
    .onboarding.hidden{display:none}
    .onboard-card{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:40px;max-width:480px;width:100%;text-align:center;transition:background .3s}
    .onboard-steps{display:flex;gap:8px;justify-content:center;margin-bottom:32px}
    .onboard-step{width:6px;height:6px;border-radius:50%;background:var(--border);transition:background .3s}
    .onboard-step.active{background:var(--accent);width:20px;border-radius:3px}
    .onboard-icon{font-size:48px;margin-bottom:20px}
    .onboard-card h2{font-family:'Instrument Serif',serif;font-size:28px;letter-spacing:-.02em;margin-bottom:12px}
    .onboard-card p{font-size:15px;color:var(--muted);line-height:1.7;margin-bottom:28px}
    .btn-onboard{width:100%;padding:14px;border-radius:12px;border:none;background:var(--accent);color:#0a0a0a;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer;transition:opacity .2s}
    [data-theme="light"] .btn-onboard{background:#1a1a1a;color:#fff}
    .btn-onboard:hover{opacity:.85}
    .skip-link{margin-top:14px;font-size:13px;color:var(--muted);cursor:pointer;display:block}
    .skip-link:hover{color:var(--text)}

    /* AUTH MODAL */
    .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(8px);z-index:300;display:flex;align-items:center;justify-content:center;padding:24px}
    .modal-overlay.hidden{display:none}
    .modal{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:36px;max-width:400px;width:100%;transition:background .3s}
    .modal h2{font-family:'Instrument Serif',serif;font-size:26px;letter-spacing:-.02em;margin-bottom:8px}
    .modal p{font-size:14px;color:var(--muted);margin-bottom:24px;line-height:1.6}
    .modal-tabs{display:flex;gap:2px;background:var(--bg2);border-radius:10px;padding:3px;margin-bottom:24px}
    .modal-tab{flex:1;padding:8px;border-radius:8px;border:none;background:transparent;color:var(--muted);font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s}
    .modal-tab.active{background:var(--surface);color:var(--text);border:1px solid var(--border)}
    .field{margin-bottom:14px}
    .field label{display:block;font-size:12px;font-weight:500;color:var(--muted);margin-bottom:6px;letter-spacing:.04em;text-transform:uppercase}
    .field input{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:11px 14px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;outline:none;transition:border-color .2s}
    .field input:focus{border-color:rgba(200,240,90,.4)}
    .btn-full{width:100%;padding:13px;border-radius:10px;border:none;background:var(--accent);color:#0a0a0a;font-family:'DM Sans',sans-serif;font-size:14px;font-weight:500;cursor:pointer;transition:opacity .2s;margin-top:4px}
    [data-theme="light"] .btn-full{background:#1a1a1a;color:#fff}
    .btn-full:hover{opacity:.85}
    .btn-full:disabled{opacity:.4;cursor:not-allowed}
    .auth-error{font-size:13px;color:var(--red);margin-top:10px;text-align:center}
    .auth-success{font-size:13px;color:var(--accent);margin-top:10px;text-align:center}
    .modal-close{position:absolute;top:16px;right:16px;width:30px;height:30px;border-radius:50%;border:1px solid var(--border);background:var(--surface);color:var(--muted);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px}
    .modal{position:relative}

    /* LIMIT BAR */
    .limit-bar{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:12px;transition:background .3s}
    .limit-info{font-size:13px;color:var(--muted)}
    .limit-info strong{color:var(--text);font-weight:500}
    .limit-track{flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden}
    .limit-fill{height:100%;background:var(--accent);border-radius:2px;transition:width .5s ease}
    .limit-fill.warn{background:#febc2e}
    .limit-fill.danger{background:var(--red)}
    .limit-upgrade{font-size:12px;color:var(--accent);cursor:pointer;white-space:nowrap;font-weight:500}
    .limit-upgrade:hover{text-decoration:underline}

    /* APP */
    .app{max-width:1000px;margin:0 auto;padding:32px 24px 80px}
    .page-header{margin-bottom:28px}
    .page-header h1{font-family:'Instrument Serif',serif;font-size:clamp(28px,4vw,42px);letter-spacing:-.02em;line-height:1.1;margin-bottom:6px}
    .page-header h1 em{font-style:italic;color:var(--accent)}
    .page-header p{color:var(--muted);font-size:14px}

    .tabs{display:flex;gap:2px;background:var(--bg2);border-radius:10px;padding:3px;margin-bottom:20px}
    .tab{flex:1;padding:8px;border-radius:8px;border:none;background:transparent;color:var(--muted);font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s;text-align:center}
    .tab.active{background:var(--surface);color:var(--text);border:1px solid var(--border)}
    .tab-content{display:none}
    .tab-content.active{display:block}

    .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
    @media(max-width:680px){.cols{grid-template-columns:1fr}}

    .panel{background:var(--surface);border:1px solid var(--border);border-radius:20px;overflow:hidden;transition:background .3s}
    .panel-header{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
    .panel-title{font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
    .panel-body{padding:20px}

    textarea{width:100%;background:transparent;border:none;outline:none;color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;font-weight:300;line-height:1.7;resize:none;min-height:200px}
    textarea::placeholder{color:var(--muted)}

    .options-row{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
    .opt-label{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;margin-right:4px}
    .chip{padding:5px 13px;border-radius:100px;border:1px solid var(--border);font-size:12px;color:var(--muted);cursor:pointer;transition:all .2s;background:transparent;font-family:'DM Sans',sans-serif}
    .chip:hover{border-color:rgba(200,240,90,.25);color:var(--text)}
    .chip.active{background:var(--accent-dim);border-color:rgba(200,240,90,.35);color:var(--accent)}

    .context-section{margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
    .ctx-label{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:7px}
    .ctx-input{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:9px 13px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;outline:none;transition:border-color .2s}
    .ctx-input:focus{border-color:rgba(200,240,90,.4)}
    .ctx-input::placeholder{color:var(--muted)}

    .btn-generate{width:100%;background:var(--accent);color:#0a0a0a;border:none;padding:14px;border-radius:12px;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:500;cursor:pointer;transition:opacity .2s,transform .15s;display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px}
    [data-theme="light"] .btn-generate{background:#1a1a1a;color:#fff}
    .btn-generate:hover{opacity:.88}
    .btn-generate:active{transform:scale(.98)}
    .btn-generate:disabled{opacity:.35;cursor:not-allowed;transform:none}
    .spinner{width:15px;height:15px;border:2px solid rgba(10,10,10,.3);border-top-color:#0a0a0a;border-radius:50%;animation:spin .7s linear infinite;display:none}
    [data-theme="light"] .spinner{border-color:rgba(255,255,255,.3);border-top-color:#fff}

    .output-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:200px;gap:10px;color:var(--muted);text-align:center}
    .output-empty .icon{font-size:32px;opacity:.3}
    .output-empty p{font-size:13px;max-width:180px;line-height:1.6}
    .output-text{display:none;font-size:14px;line-height:1.8;color:var(--text);white-space:pre-wrap;min-height:200px}
    .output-text.visible{display:block}
    .output-actions{display:none;gap:8px;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
    .output-actions.visible{display:flex}
    .btn-copy{flex:1;background:var(--accent);color:#0a0a0a;border:none;padding:10px;border-radius:10px;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;cursor:pointer;transition:opacity .2s}
    [data-theme="light"] .btn-copy{background:#1a1a1a;color:#fff}
    .btn-copy:hover{opacity:.85}
    .btn-regen{background:var(--bg2);color:var(--muted);border:1px solid var(--border);padding:10px 14px;border-radius:10px;font-family:'DM Sans',sans-serif;font-size:13px;cursor:pointer;transition:all .2s}
    .btn-regen:hover{border-color:rgba(200,240,90,.25);color:var(--text)}

    .style-panel{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:24px;margin-bottom:14px;transition:background .3s}
    .style-panel h3{font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
    .style-textarea{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:11px 13px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:13px;font-weight:300;line-height:1.7;resize:none;outline:none;min-height:90px;transition:border-color .2s,background .3s}
    .style-textarea:focus{border-color:rgba(200,240,90,.4)}
    .style-textarea::placeholder{color:var(--muted)}

    .history-panel{background:var(--surface);border:1px solid var(--border);border-radius:20px;overflow:hidden;transition:background .3s}
    .history-item{padding:14px 20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .2s}
    .history-item:last-child{border-bottom:none}
    .history-item:hover{background:var(--bg2)}
    .history-meta{display:flex;justify-content:space-between;font-size:13px;font-weight:500;margin-bottom:4px}
    .history-meta span{color:var(--muted);font-weight:300;font-size:12px}
    .history-preview{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .history-empty{padding:40px;text-align:center;color:var(--muted);font-size:13px}

    .char-count{font-size:11px;color:var(--muted)}

    .toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--surface);border:1px solid var(--border);border-radius:100px;padding:11px 22px;font-size:13px;color:var(--text);opacity:0;transition:all .3s;z-index:1000;pointer-events:none;white-space:nowrap}
    .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
    .toast.success{border-color:rgba(200,240,90,.3);color:var(--accent)}
    .toast.error{border-color:rgba(255,107,107,.3);color:var(--red)}

    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    .dots::after{content:'';animation:dots 1.2s infinite}
    @keyframes dots{0%{content:''}33%{content:'.'}66%{content:'..'}100%{content:'...'}}
  </style>
</head>
<body>

<!-- ONBOARDING -->
<div class="onboarding hidden" id="onboarding">
  <div class="onboard-card">
    <div class="onboard-steps">
      <div class="onboard-step active" id="os0"></div>
      <div class="onboard-step" id="os1"></div>
      <div class="onboard-step" id="os2"></div>
    </div>
    <div id="onboard-content"></div>
  </div>
</div>

<!-- AUTH MODAL -->
<div class="modal-overlay hidden" id="authModal">
  <div class="modal">
    <button class="modal-close" onclick="closeAuth()">✕</button>
    <h2>Welcome to Replai</h2>
    <p>Sign in to save your history and unlock more daily replies.</p>
    <div class="modal-tabs">
      <button class="modal-tab active" onclick="switchAuth('login', this)">Sign In</button>
      <button class="modal-tab" onclick="switchAuth('signup', this)">Sign Up</button>
    </div>
    <div id="auth-login">
      <div class="field"><label>Email</label><input type="email" id="login-email" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="login-pass" placeholder="••••••••"/></div>
      <button class="btn-full" onclick="doLogin()">Sign In →</button>
      <div id="login-msg"></div>
    </div>
    <div id="auth-signup" style="display:none">
      <div class="field"><label>Email</label><input type="email" id="signup-email" placeholder="you@example.com"/></div>
      <div class="field"><label>Password</label><input type="password" id="signup-pass" placeholder="Min 6 characters"/></div>
      <button class="btn-full" onclick="doSignup()">Create Account →</button>
      <div id="signup-msg"></div>
    </div>
  </div>
</div>

<!-- NAV -->
<nav>
  <div class="logo">repl<span>ai</span></div>
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

  <!-- LIMIT BAR -->
  <div class="limit-bar" id="limitBar">
    <div class="limit-info"><strong id="limitUsed">0</strong> / <strong id="limitMax">20</strong> replies today</div>
    <div class="limit-track"><div class="limit-fill" id="limitFill" style="width:0%"></div></div>
    <span class="limit-upgrade" onclick="openAuth()" id="limitUpgrade">Sign in for more →</span>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('reply',this)">✦ Reply</button>
    <button class="tab" onclick="switchTab('history',this)">History</button>
    <button class="tab" onclick="switchTab('style',this)">My Style</button>
  </div>

  <!-- REPLY TAB -->
  <div class="tab-content active" id="tab-reply">
    <div class="cols">
      <div>
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">Incoming message</span>
            <span class="char-count" id="charCount">0 chars</span>
          </div>
          <div class="panel-body">
            <textarea id="inputMsg" placeholder="Paste the email or message you received here..." oninput="updateCharCount()"></textarea>
            <div class="options-row">
              <span class="opt-label">Tone</span>
              <button class="chip active" onclick="selectChip(this)">Professional</button>
              <button class="chip" onclick="selectChip(this)">Friendly</button>
              <button class="chip" onclick="selectChip(this)">Brief</button>
              <button class="chip" onclick="selectChip(this)">Formal</button>
            </div>
            <div class="options-row">
              <span class="opt-label">Lang</span>
              <button class="chip active" onclick="selectChip(this)">English</button>
              <button class="chip" onclick="selectChip(this)">Russian</button>
              <button class="chip" onclick="selectChip(this)">Auto</button>
            </div>
            <div class="context-section">
              <div class="ctx-label">Extra context (optional)</div>
              <input class="ctx-input" id="extraContext" placeholder="e.g. decline politely, ask for more time..."/>
            </div>
          </div>
        </div>
        <button class="btn-generate" id="generateBtn" onclick="generateReply()">
          <div class="spinner" id="spinner"></div>
          <span id="generateLabel">✦ Generate Reply</span>
        </button>
      </div>
      <div>
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">AI Reply</span>
            <span class="char-count" id="outputCharCount"></span>
          </div>
          <div class="panel-body">
            <div class="output-empty" id="outputEmpty">
              <div class="icon">✦</div>
              <p>Your AI reply will appear here</p>
            </div>
            <div class="output-text" id="outputText"></div>
            <div class="output-actions" id="outputActions">
              <button class="btn-copy" onclick="copyReply()"><span id="copyLabel">Copy Reply</span></button>
              <button class="btn-regen" onclick="generateReply()">↻ Redo</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- HISTORY TAB -->
  <div class="tab-content" id="tab-history">
    <div class="history-panel" id="historyList">
      <div class="history-empty">No replies yet. Generate your first reply!</div>
    </div>
  </div>

  <!-- STYLE TAB -->
  <div class="tab-content" id="tab-style">
    <div class="style-panel">
      <h3>Your writing style</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:12px;line-height:1.6">Paste 2–3 examples of how you normally write. Replai will match your tone.</p>
      <textarea class="style-textarea" id="styleExamples" placeholder="Example: Hey John, thanks for reaching out! Let me check and get back to you by Thursday." oninput="saveStyle()"></textarea>
    </div>
    <div class="style-panel">
      <h3>About you</h3>
      <p style="font-size:13px;color:var(--muted);margin-bottom:12px;line-height:1.6">Tell Replai about your role so replies are always relevant.</p>
      <textarea class="style-textarea" id="aboutMe" placeholder="e.g. I'm a freelance designer. I keep emails short and always end with a clear next step." oninput="saveStyle()" style="min-height:70px"></textarea>
      <p style="margin-top:10px;font-size:12px;color:var(--muted)">✓ Saved automatically</p>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
  // ── SUPABASE ──────────────────────────────────────────────
  const { createClient } = supabase;
  const sb = createClient('https://bangwkorrlhpmjzmgudt.supabase.co', 'sb_publishable_iqcJprNPDgpZtbsibf4DLg_MzJ-X_Je');

  // ── STATE ─────────────────────────────────────────────────
  let currentUser = null;
  let currentReply = '';
  let isGenerating = false;
  let history = JSON.parse(localStorage.getItem('replai_history') || '[]');
  const FREE_LIMIT = 20;
  const AUTH_LIMIT = 50;

  // ── ONBOARDING ────────────────────────────────────────────
  const onboardSlides = [
    { icon:'✉️', title:'Paste any message', text:'Copy an email, WhatsApp, or any text you received and paste it into the left panel.' },
    { icon:'🎯', title:'Pick your tone', text:'Choose Professional, Friendly, Brief or Formal. Add extra context if needed.' },
    { icon:'✦', title:'Copy & send', text:'Get a perfect reply in seconds. Copy it and send — done! Sign up to get 50 replies/day.' },
  ];
  let onboardStep = 0;

  function showOnboarding() {
    if (localStorage.getItem('replai_onboarded')) return;
    document.getElementById('onboarding').classList.remove('hidden');
    renderOnboardSlide();
  }

  function renderOnboardSlide() {
    const s = onboardSlides[onboardStep];
    document.getElementById('onboard-content').innerHTML = `
      <div class="onboard-icon">${s.icon}</div>
      <h2>${s.title}</h2>
      <p>${s.text}</p>
      <button class="btn-onboard" onclick="nextOnboard()">${onboardStep < onboardSlides.length - 1 ? 'Next →' : 'Get Started ✦'}</button>
      ${onboardStep === 0 ? '<span class="skip-link" onclick="skipOnboard()">Skip intro</span>' : ''}
    `;
    for (let i = 0; i < 3; i++) {
      document.getElementById('os' + i).className = 'onboard-step' + (i === onboardStep ? ' active' : '');
    }
  }

  function nextOnboard() {
    if (onboardStep < onboardSlides.length - 1) {
      onboardStep++;
      renderOnboardSlide();
    } else {
      skipOnboard();
    }
  }

  function skipOnboard() {
    localStorage.setItem('replai_onboarded', '1');
    document.getElementById('onboarding').classList.add('hidden');
  }

  // ── THEME ─────────────────────────────────────────────────
  const html = document.documentElement;
  const themeBtn = document.getElementById('themeBtn');
  setTheme(localStorage.getItem('replai_theme') || 'dark');

  function setTheme(t) {
    html.setAttribute('data-theme', t);
    themeBtn.textContent = t === 'dark' ? '🌙' : '☀️';
    localStorage.setItem('replai_theme', t);
  }
  function toggleTheme() {
    setTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  }

  // ── AUTH ──────────────────────────────────────────────────
  function openAuth() { document.getElementById('authModal').classList.remove('hidden'); }
  function closeAuth() { document.getElementById('authModal').classList.add('hidden'); }

  function switchAuth(mode, el) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('auth-login').style.display = mode === 'login' ? 'block' : 'none';
    document.getElementById('auth-signup').style.display = mode === 'signup' ? 'block' : 'none';
  }

  async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const pass = document.getElementById('login-pass').value;
    const msg = document.getElementById('login-msg');
    if (!email || !pass) { msg.className = 'auth-error'; msg.textContent = 'Fill in all fields'; return; }
    msg.className = ''; msg.textContent = 'Signing in...';
    const { error } = await sb.auth.signInWithPassword({ email, password: pass });
    if (error) { msg.className = 'auth-error'; msg.textContent = error.message; }
    else { closeAuth(); showToast('Welcome back! ✦', 'success'); }
  }

  async function doSignup() {
    const email = document.getElementById('signup-email').value.trim();
    const pass = document.getElementById('signup-pass').value;
    const msg = document.getElementById('signup-msg');
    if (!email || !pass) { msg.className = 'auth-error'; msg.textContent = 'Fill in all fields'; return; }
    if (pass.length < 6) { msg.className = 'auth-error'; msg.textContent = 'Password min 6 characters'; return; }
    msg.className = ''; msg.textContent = 'Creating account...';
    const { error } = await sb.auth.signUp({ email, password: pass });
    if (error) { msg.className = 'auth-error'; msg.textContent = error.message; }
    else { msg.className = 'auth-success'; msg.textContent = '✓ Check your email to confirm!'; }
  }

  async function doLogout() {
    await sb.auth.signOut();
    currentUser = null;
    updateNavAuth();
    updateLimitBar();
    showToast('Signed out', '');
  }

  function updateNavAuth() {
    const el = document.getElementById('navAuth');
    if (currentUser) {
      const email = currentUser.email.split('@')[0];
      el.innerHTML = `
        <div class="user-pill"><div class="dot"></div><span>${email}</span></div>
        <button class="btn-sm btn-ghost" onclick="doLogout()">Sign out</button>
      `;
    } else {
      el.innerHTML = `<button class="btn-sm btn-accent" onclick="openAuth()">Sign in</button>`;
    }
  }

  // ── LIMITS ────────────────────────────────────────────────
  function getTodayKey() {
    return 'replai_count_' + new Date().toISOString().slice(0, 10);
  }

  function getUsedToday() {
    return parseInt(localStorage.getItem(getTodayKey()) || '0');
  }

  function incrementUsed() {
    const key = getTodayKey();
    localStorage.setItem(key, (getUsedToday() + 1).toString());
  }

  function getLimit() { return currentUser ? AUTH_LIMIT : FREE_LIMIT; }

  function updateLimitBar() {
    const used = getUsedToday();
    const max = getLimit();
    const pct = Math.min((used / max) * 100, 100);
    document.getElementById('limitUsed').textContent = used;
    document.getElementById('limitMax').textContent = max;
    const fill = document.getElementById('limitFill');
    fill.style.width = pct + '%';
    fill.className = 'limit-fill' + (pct >= 90 ? ' danger' : pct >= 70 ? ' warn' : '');
    const upgrade = document.getElementById('limitUpgrade');
    if (currentUser) { upgrade.style.display = 'none'; }
    else { upgrade.style.display = 'block'; upgrade.textContent = 'Sign in for 50/day →'; }
  }

  // ── TABS ──────────────────────────────────────────────────
  function switchTab(name, el) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
    if (name === 'history') renderHistory();
  }

  function selectChip(el) {
    el.closest('.options-row').querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
  }

  function getChip(label) {
    const rows = document.querySelectorAll('.options-row');
    for (const row of rows) {
      if (row.querySelector('.opt-label')?.textContent.toLowerCase().includes(label)) {
        return row.querySelector('.chip.active')?.textContent || '';
      }
    }
    return '';
  }

  function updateCharCount() {
    document.getElementById('charCount').textContent = document.getElementById('inputMsg').value.length + ' chars';
  }

  function saveStyle() {
    localStorage.setItem('replai_style', document.getElementById('styleExamples').value);
    localStorage.setItem('replai_about', document.getElementById('aboutMe').value);
  }

  function loadStyle() {
    const s = localStorage.getItem('replai_style');
    const a = localStorage.getItem('replai_about');
    if (s) document.getElementById('styleExamples').value = s;
    if (a) document.getElementById('aboutMe').value = a;
  }

  // ── GENERATE ──────────────────────────────────────────────
  async function generateReply() {
    if (isGenerating) return;
    const msg = document.getElementById('inputMsg').value.trim();
    if (!msg) { showToast('Paste a message first', 'error'); return; }

    const used = getUsedToday();
    const limit = getLimit();
    if (used >= limit) {
      if (!currentUser) {
        showToast('Daily limit reached — sign in for more!', 'error');
        openAuth();
      } else {
        showToast('Daily limit reached (' + limit + '/day)', 'error');
      }
      return;
    }

    isGenerating = true;
    const btn = document.getElementById('generateBtn');
    const spinner = document.getElementById('spinner');
    const label = document.getElementById('generateLabel');
    btn.disabled = true;
    spinner.style.display = 'block';
    label.textContent = 'Generating';
    label.classList.add('dots');

    document.getElementById('outputEmpty').style.display = 'none';
    document.getElementById('outputText').classList.add('visible');
    document.getElementById('outputText').innerHTML = '<span style="color:var(--muted)">Writing your reply...</span>';
    document.getElementById('outputActions').classList.remove('visible');

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          tone: getChip('tone'),
          language: getChip('lang'),
          context: document.getElementById('extraContext').value.trim(),
          style_examples: localStorage.getItem('replai_style') || '',
          about_me: localStorage.getItem('replai_about') || ''
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Server error');

      currentReply = data.reply;
      incrementUsed();
      updateLimitBar();

      document.getElementById('outputText').textContent = currentReply;
      document.getElementById('outputCharCount').textContent = currentReply.length + ' chars';
      document.getElementById('outputActions').classList.add('visible');
      saveToHistory(msg, currentReply, getChip('tone'));

    } catch(e) {
      document.getElementById('outputText').innerHTML = '';
      document.getElementById('outputEmpty').style.display = 'flex';
      showToast('Error: ' + e.message, 'error');
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
      document.getElementById('copyLabel').textContent = '✓ Copied!';
      setTimeout(() => document.getElementById('copyLabel').textContent = 'Copy Reply', 2000);
      showToast('Copied ✓', 'success');
    });
  }

  // ── HISTORY ───────────────────────────────────────────────
  function saveToHistory(incoming, reply, tone) {
    history.unshift({ id: Date.now(), incoming: incoming.slice(0, 100), reply, tone, time: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) });
    if (history.length > 30) history.pop();
    localStorage.setItem('replai_history', JSON.stringify(history));
  }

  function renderHistory() {
    const el = document.getElementById('historyList');
    if (!history.length) { el.innerHTML = '<div class="history-empty">No replies yet.</div>'; return; }
    el.innerHTML = history.map(h => `
      <div class="history-item" onclick="loadHistory(${h.id})">
        <div class="history-meta"><span>${h.tone}</span><span>${h.time}</span></div>
        <div class="history-preview">${h.incoming.replace(/</g,'&lt;')}...</div>
      </div>`).join('');
  }

  function loadHistory(id) {
    const item = history.find(h => h.id === id);
    if (!item) return;
    currentReply = item.reply;
    document.getElementById('outputEmpty').style.display = 'none';
    document.getElementById('outputText').classList.add('visible');
    document.getElementById('outputText').textContent = item.reply;
    document.getElementById('outputActions').classList.add('visible');
    document.getElementById('outputCharCount').textContent = item.reply.length + ' chars';
    document.querySelectorAll('.tab')[0].click();
  }

  // ── TOAST ─────────────────────────────────────────────────
  function showToast(msg, type) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.className = 'toast ' + (type||'') + ' show';
    setTimeout(() => t.classList.remove('show'), 3000);
  }

  // ── INIT ──────────────────────────────────────────────────
  window.onload = async () => {
    loadStyle();
    renderHistory();
    updateLimitBar();

    // Auth state
    const { data: { session } } = await sb.auth.getSession();
    if (session) { currentUser = session.user; }
    updateNavAuth();
    updateLimitBar();

    sb.auth.onAuthStateChange((_event, session) => {
      currentUser = session?.user || null;
      updateNavAuth();
      updateLimitBar();
    });

    // Show onboarding after short delay
    setTimeout(showOnboarding, 600);
  };

  // Close modal on outside click
  document.getElementById('authModal').addEventListener('click', function(e) {
    if (e.target === this) closeAuth();
  });
  document.getElementById('onboarding').addEventListener('click', function(e) {
    if (e.target === this) skipOnboard();
  });

  // Enter keys for auth
  ['login-pass','signup-pass'].forEach(id => {
    document.getElementById(id)?.addEventListener('keydown', e => {
      if (e.key === 'Enter') id.includes('login') ? doLogin() : doSignup();
    });
  });
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
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
                    "max_tokens": 1024, "temperature": 0.7
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
