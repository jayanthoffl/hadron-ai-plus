const $ = id => document.getElementById(id);
const $$ = id => document.getElementById(id);
const money = n => n == null || Number.isNaN(Number(n)) ? "—" : "$" + Number(n).toLocaleString(undefined,{maximumFractionDigits:0});

let requests = [];
let leftRequests = [];
let rightRequests = [];
let activeReq = null;
let activeSide = null; // 'LEFT' or 'RIGHT' or null
let graphState = 'INITIAL'; // INITIAL, EXPANDED, SELECTED
let isLoggedIn = false;

// Session & Auth 30-min Expiration
const AUTH_KEY = 'optimus_auth_time';
const SPLASH_KEY = 'optimus_splash_done';
const AUTH_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

function checkAuthValid() {
  const authTime = localStorage.getItem(AUTH_KEY);
  if (!authTime) return false;
  const elapsed = Date.now() - parseInt(authTime, 10);
  return elapsed < AUTH_TIMEOUT_MS;
}

// Positions & Animation State
let currentRootX = null;
let currentLeftX = null;
let currentRightX = null;
let currentInactiveOpacity = 1.0;
let animFrameId = null;
let logIntervalId = null;
let loadingStartTime = null;
let newRequestDrawTimes = {}; // track sys_id -> startTime for new requests

let activeFannedData = null;

// Splitting requests into Even (Left, max 3) and Odd (Right, max 3)
function splitRequests() {
  leftRequests = [];
  rightRequests = [];
  requests.forEach((req, idx) => {
    if (idx % 2 === 0) {
      if (rightRequests.length < 3) rightRequests.push(req);
    } else {
      if (leftRequests.length < 3) leftRequests.push(req);
    }
  });
}

// Draw smooth directional radial sigmoid cubic bezier curve
function drawLine(id, x1, y1, x2, y2, highlight=false, opacity=1.0, blurPx=0, drawProgress=1.0) {
  const svg = $("svgLayer");
  if (!svg) return;
  let path = $(`line-${id}`);
  if (!path) {
    path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("id", `line-${id}`);
    svg.appendChild(path);
  }
  const dx = Math.abs(x2 - x1);
  const dy = y2 - y1;
  const dir = x2 >= x1 ? 1 : -1;
  const alpha = 0.42;
  const beta  = 0.18;
  const cx1 = x1 + dir * (dx * alpha);
  const cy1 = y1 + dy * beta;
  const cx2 = x2 - dir * (dx * alpha);
  const cy2 = y2 - dy * beta;
  path.setAttribute("d", `M ${x1},${y1} C ${cx1},${cy1} ${cx2},${cy2} ${x2},${y2}`);
  path.setAttribute("class", `line-path ${highlight?'highlight':''}`);
  path.style.opacity = String(opacity);
  path.style.filter = blurPx > 0 ? `blur(${blurPx.toFixed(1)}px)` : 'none';

  if (drawProgress < 1.0) {
    const len = path.getTotalLength ? path.getTotalLength() : 800;
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len * (1.0 - Math.max(0, drawProgress));
  } else {
    path.style.strokeDasharray = 'none';
    path.style.strokeDashoffset = '0';
  }
}

function hideLine(id) {
  const path = $(`line-${id}`);
  if(path) path.style.opacity = '0';
}

// Draw HTML node
function renderNode(id, html, x, y, className, onClick=null, opacity=1.0, blurPx=0) {
  let el = $(`node-${id}`);
  if (!el) {
    el = document.createElement("div");
    el.id = `node-${id}`;
    el.style.left = `${window.innerWidth/2}px`;
    el.style.top = `${window.innerHeight/2}px`;
    el.style.opacity = '0';
    $("nodesLayer").appendChild(el);
    el.getBoundingClientRect();
  }
  el.className = className;
  el.innerHTML = html;
  el.style.left = `${Math.round(x)}px`;
  el.style.top = `${Math.round(y)}px`;
  el.style.opacity = String(opacity);
  el.style.filter = blurPx > 0 ? `blur(${blurPx.toFixed(1)}px)` : 'none';
  el.style.pointerEvents = opacity < 0.3 ? 'none' : 'auto';
  if(onClick) el.onclick = onClick;
}

function hideNode(id) {
  const el = $(`node-${id}`);
  if(el) {
    el.style.opacity = '0';
    el.style.pointerEvents = 'none';
    el.classList.remove('flip-animate');
  }
}

/* ── 1-TIME SPLASH SCREEN & 30-MIN LOGIN FLOW ───────── */
function initSplashAndLogin() {
  const splashOverlay = $('splashOverlay');
  const loginOverlay = $('loginOverlay');

  const hasSeenSplash = sessionStorage.getItem(SPLASH_KEY) === 'true';
  const isValidAuth = checkAuthValid();

  if (isValidAuth) {
    isLoggedIn = true;
  }

  // If splash was already seen in this tab (e.g. normal refresh)
  if (hasSeenSplash) {
    if (splashOverlay) {
      splashOverlay.style.display = 'none';
    }
    if (isValidAuth) {
      if (loginOverlay) loginOverlay.style.display = 'none';
      loadRequests();
    } else {
      if (loginOverlay) loginOverlay.classList.remove('hidden-fade');
    }
    return;
  }

  // Initial landing in session -> run 1.5s clean white splash screen
  sessionStorage.setItem(SPLASH_KEY, 'true');

  const splashLogText = $('splashLogText');
  setTimeout(() => {
    if (splashLogText) splashLogText.textContent = 'Authenticating HADRON Executive Engine...';
  }, 600);

  setTimeout(() => {
    if (splashLogText) splashLogText.textContent = 'ServiceNow Instance Handshake Verified';
  }, 1100);

  setTimeout(() => {
    if (splashOverlay) splashOverlay.classList.add('fade-out');
    setTimeout(() => {
      if (splashOverlay) splashOverlay.style.display = 'none';
      if (isValidAuth) {
        if (loginOverlay) loginOverlay.style.display = 'none';
        loadRequests();
      } else {
        if (loginOverlay) loginOverlay.classList.remove('hidden-fade');
      }
    }, 500);
  }, 1500);
}

function handleLoginSubmit(e) {
  if (e) e.preventDefault();
  const u = $('loginUser')?.value.trim();
  const p = $('loginPass')?.value.trim();
  const err = $('loginError');

  if (u === 'admin' && p === 'gM1T6@iJepI*') {
    if (err) err.style.display = 'none';
    localStorage.setItem(AUTH_KEY, Date.now().toString());
    isLoggedIn = true;
    const loginOverlay = $('loginOverlay');
    if (loginOverlay) {
      loginOverlay.classList.add('fade-out');
      setTimeout(() => {
        loginOverlay.style.display = 'none';
        loadRequests();
      }, 500);
    }
  } else {
    if (err) err.style.display = 'block';
  }
}

function handleLogout() {
  localStorage.removeItem(AUTH_KEY);
  sessionStorage.removeItem(SPLASH_KEY);
  isLoggedIn = false;
  location.reload(); // Hard reload to reset state and show login
}

async function loadRequests(preserveState = false) {
  try {
    const r = await fetch("/api/requests");
    const data = await r.json();
    const newRequests = data.requests || [];
    
    if (preserveState && activeSide && graphState === 'SELECTED') {
      const currentIds = new Set(requests.map(req => req.sys_id));
      const added = newRequests.filter(req => !currentIds.has(req.sys_id));
      requests = newRequests;
      
      if (added.length > 0) {
        const newReq = added[0];
        // Record creation time for draw animation of root line
        newRequestDrawTimes[newReq.sys_id] = performance.now();
        if (activeSide === 'LEFT') {
          leftRequests.unshift(newReq);
          if (leftRequests.length > 3) leftRequests.pop();
        } else {
          rightRequests.unshift(newReq);
          if (rightRequests.length > 3) rightRequests.pop();
        }
      }
      renderGraphFrame();
    } else {
      requests = newRequests;
      splitRequests();
      activeReq = null;
      activeSide = null;
      activeFannedData = null;
      
      const W = window.innerWidth;
      currentRootX = W / 2;
      currentLeftX = W / 2 - 320;
      currentRightX = W / 2 + 320;
      currentInactiveOpacity = 1.0;

      animateGraphToState('EXPANDED', null, 800);
    }
  } catch (e) {
    console.error("Failed to load requests", e);
  }
}

function handleOrbClick() {
  activeReq = null;
  activeSide = null;
  activeFannedData = null;
  if (logIntervalId) clearInterval(logIntervalId);
  if ($("rightPanel")) {
    $("rightPanel").style.opacity = '0';
    setTimeout(() => $("rightPanel").style.display = 'none', 400);
  }
  for (let i = 0; i < 15; i++) {
    hideNode(`sub-${i}`);
    hideLine(`fan-${i}`);
  }
  document.querySelectorAll('.line-path.highlight').forEach(el => hideLine(el.id.replace('line-','')));
  animateGraphToState('EXPANDED', null, 1100);
}

function renderGraphFrame() {
  const W = window.innerWidth;
  const H = window.innerHeight;
  const TOPBAR = 56;
  const PANEL_RESERVE = 210; // Reserved bottom dock height for constant Y layout across all states
  const graphH = H - TOPBAR - PANEL_RESERVE;
  const cy = TOPBAR + graphH / 2;

  if (currentRootX == null) currentRootX = W / 2;
  if (currentLeftX == null) currentLeftX = W / 2 - 320;
  if (currentRightX == null) currentRightX = W / 2 + 320;

  const rootX = currentRootX;
  const rootY = cy;
  const orbCenterY = rootY - 45; // Exact vertical center of the 3D sphere circle (.orb-core)
  const activeCount = requests.length || 12;

  // Render Center Orb with Add Request button built-in for 100% lockstep physical movement
  renderNode('root', `
    <div class="orb-core"></div>
    <div class="orb-label">
      <h3>Opportunity Pipeline</h3>
      <p>HADRON Executive</p>
      <div class="orb-tag"><span class="dot-live"></span> ${activeCount} Active Deals</div>
    </div>
    <button class="orb-add-btn" onclick="event.stopPropagation(); if ($('modal')) $('modal').classList.remove('hidden');">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      Add Request
    </button>
  `, rootX, rootY, "node-orb", handleOrbClick);

  hideNode('orb-add-btn');

  if (graphState === 'INITIAL') return;

  const leftX = currentLeftX;
  const rightX = currentRightX;

  // Uniform Vertical Gap (70px center-to-center)
  const V_GAP = 70;
  
  const lastReqId = requests.length > 0 ? requests[requests.length - 1].sys_id : null;

  // Render LEFT Column Cards (Even - Max 3)
  const leftTotalH = Math.max(0, (leftRequests.length - 1) * V_GAP);
  const leftStartY = cy - leftTotalH / 2;

  leftRequests.forEach((req, i) => {
    const y = leftStartY + (i * V_GAP);
    const isActive = activeReq?.sys_id === req.sys_id;
    const isDimmed = graphState === 'SELECTED' && activeSide === 'RIGHT';

    const opacity = isDimmed ? currentInactiveOpacity : 1.0;
    const blurPx = isDimmed ? Math.max(0, (1.0 - currentInactiveOpacity) / 0.75 * 6) : 0;

    const iconHtml = isActive
      ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`
      : `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="4"/></svg>`;

    const cardClass = `node-cat ${isActive ? 'active' : ''} ${isDimmed ? 'dimmed-blur' : ''}`;

    const isLast = req.sys_id === lastReqId;

    const createTime = newRequestDrawTimes[req.sys_id];
    let dp = 1.0;
    if (createTime) {
      dp = Math.min(1.0, (performance.now() - createTime) / 1200);
    }
    const nodeOpacity = dp < 1.0 ? dp * opacity : opacity;

    renderNode(req.sys_id, `
      <div class="cat-icon">${iconHtml}</div>
      <div class="cat-text">
        <h3>${req.number}</h3>
        <p>${req.customer_name || 'Unknown Customer'}</p>
      </div>
    `, leftX, y, cardClass, () => selectRequest(req, leftX, y, 'LEFT'), nodeOpacity, blurPx);

    const HALF = 110;
    drawLine(`root-${req.sys_id}`, rootX - 32, orbCenterY, leftX + HALF, y, isActive, opacity, blurPx, dp);
  });

  if (graphState !== 'SELECTED' && requests.length > 6) {
    const extraCount = requests.length - 6;
    renderNode('show-more', `
      <div class="orb-label" style="padding:4px 12px; border-radius:12px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); backdrop-filter:blur(10px); cursor:default; pointer-events:auto;">
        <span style="font-size:0.75rem; color:#94a3b8; font-weight:700; text-transform:uppercase;">+${extraCount} More Deals</span>
      </div>
    `, rootX, cy + 180, "node-orb", null, 1.0, 0);
  } else {
    hideNode('show-more');
  }

  // Render RIGHT Column Cards (Odd - Max 3)
  const rightTotalH = Math.max(0, (rightRequests.length - 1) * V_GAP);
  const rightStartY = cy - rightTotalH / 2;

  rightRequests.forEach((req, i) => {
    const y = rightStartY + (i * V_GAP);
    const isActive = activeReq?.sys_id === req.sys_id;
    const isDimmed = graphState === 'SELECTED' && activeSide === 'LEFT';

    const opacity = isDimmed ? currentInactiveOpacity : 1.0;
    const blurPx = isDimmed ? Math.max(0, (1.0 - currentInactiveOpacity) / 0.75 * 6) : 0;

    const iconHtml = isActive
      ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`
      : `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="4"/></svg>`;

    const cardClass = `node-cat ${isActive ? 'active' : ''} ${isDimmed ? 'dimmed-blur' : ''}`;

    const isLast = req.sys_id === lastReqId;

    const createTime = newRequestDrawTimes[req.sys_id];
    let dp = 1.0;
    if (createTime) {
      dp = Math.min(1.0, (performance.now() - createTime) / 1200);
    }
    const nodeOpacity = dp < 1.0 ? dp * opacity : opacity;

    renderNode(req.sys_id, `
      <div class="cat-icon">${iconHtml}</div>
      <div class="cat-text">
        <h3>${req.number}</h3>
        <p>${req.customer_name || 'Unknown Customer'}</p>
      </div>
    `, rightX, y, cardClass, () => selectRequest(req, rightX, y, 'RIGHT'), nodeOpacity, blurPx);

    const HALF = 110;
    drawLine(`root-${req.sys_id}`, rootX + 32, orbCenterY, rightX - HALF, y, isActive, opacity, blurPx, dp);
  });

  // Continuously render fanned factor cards glued to selected card every frame
  if (graphState === 'SELECTED' && activeReq) {
    const isLeft = activeSide === 'LEFT';
    const cardX = isLeft ? currentLeftX : currentRightX;
    const cardEl = $(`node-${activeReq.sys_id}`);
    const startY = cardEl ? (cardEl.offsetTop + cardEl.offsetHeight / 2) : cy;
    const startX = isLeft ? (cardX - 110) : (cardX + 110);

    if (activeFannedData) {
      drawFannedNodes(activeFannedData, startX, startY, activeSide);
    } else {
      drawFannedNodesLoading(startX, startY, activeSide);
    }
  }
}

function animateGraphToState(targetState, targetSide, duration = 1100) {
  if (animFrameId) cancelAnimationFrame(animFrameId);

  const W = window.innerWidth;

  if (currentRootX == null) currentRootX = W / 2;
  if (currentLeftX == null) currentLeftX = W / 2 - 320;
  if (currentRightX == null) currentRightX = W / 2 + 320;

  const startRootX = currentRootX;
  const startLeftX = currentLeftX;
  const startRightX = currentRightX;
  const startInactiveOpacity = currentInactiveOpacity;

  let endRootX = W / 2;
  let endLeftX = W / 2 - 320;
  let endRightX = W / 2 + 320;
  let endInactiveOpacity = 1.0;

  if (targetState === 'SELECTED') {
    endInactiveOpacity = 0.25;
    if (targetSide === 'RIGHT') {
      endRootX = Math.round(W * 0.14);
      endLeftX = Math.round(endRootX - 220); // Moves in lockstep with Orb
      endRightX = Math.round(W * 0.32);
    } else {
      endRootX = Math.round(W * 0.86);
      endRightX = Math.round(endRootX + 220); // Moves in lockstep with Orb
      endLeftX = Math.round(W * 0.68);
    }
  }

  graphState = targetState;
  activeSide = targetSide;

  if (duration <= 0) {
    currentRootX = endRootX;
    currentLeftX = endLeftX;
    currentRightX = endRightX;
    currentInactiveOpacity = endInactiveOpacity;
    renderGraphFrame();
    return;
  }

  const startTime = performance.now();

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    // Quartic easeOut curve: silky smooth fluid deceleration without abrupt starts or stops
    const ease = 1 - Math.pow(1 - progress, 4);

    currentRootX = startRootX + (endRootX - startRootX) * ease;
    currentLeftX = startLeftX + (endLeftX - startLeftX) * ease;
    currentRightX = startRightX + (endRightX - startRightX) * ease;
    currentInactiveOpacity = startInactiveOpacity + (endInactiveOpacity - startInactiveOpacity) * ease;

    renderGraphFrame();

    if (progress < 1) {
      animFrameId = requestAnimationFrame(step);
    } else {
      animFrameId = null;
    }
  }

  animFrameId = requestAnimationFrame(step);
}

function renderGraph() {
  renderGraphFrame();
}

async function selectRequest(req, reqX, reqY, side = 'RIGHT', forceRun = false) {
  activeReq = req;
  activeSide = side;

  animateGraphToState('SELECTED', side, 1100);

  const rightPanel = $("rightPanel");
  if (rightPanel) {
    rightPanel.style.display = "flex";
    setTimeout(() => rightPanel.style.opacity = '1', 50);
  }

  if ($("panelHeaderLabel")) $("panelHeaderLabel").textContent = `Analysis overview for ${req.number}`;
  if ($("rTitle")) $("rTitle").textContent = req.service_product_name || 'Unknown Service';
  if ($("rStatus")) $("rStatus").textContent = req.status || "READY";
  if ($("rDate")) {
    const today = new Date();
    const formatted = today.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    $("rDate").textContent = `Last update ${formatted}`;
  }

  if (req.executive_summary && !forceRun) {
    activeFannedData = req;
    renderGraphFrame();
    populateRightPanel(req);
    return;
  }

  // Loading State
  activeFannedData = null;
  loadingStartTime = performance.now();
  if ($("rConf")) $("rConf").textContent = "—";
  if ($("mainSummary")) $("mainSummary").textContent = "Analyzing the request and gathering available pricing evidence…";
  if ($("rFloor")) $("rFloor").textContent = "—";
  if ($("rMargin")) $("rMargin").textContent = "—";
  if ($("rSignals")) $("rSignals").textContent = "—";
  if ($("rOffers")) $("rOffers").textContent = "—";
  if ($("rStatus")) $("rStatus").textContent = "ANALYZING";

  renderGraphFrame();

  if (!window.loadingAnimFrameId) {
    function loop() {
      if (graphState === 'SELECTED' && !activeFannedData) {
        renderGraphFrame();
        window.loadingAnimFrameId = requestAnimationFrame(loop);
      } else {
        window.loadingAnimFrameId = null;
      }
    }
    window.loadingAnimFrameId = requestAnimationFrame(loop);
  }

  try {
    const res = await fetch("/api/analyze",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          customer_name: req.customer_name,
          service_product_name: req.service_product_name,
          commercial_objective: req.commercial_objective,
          additional_context: req.additional_context,
          record_sys_id: req.sys_id
        })
      });

    const responseText = await res.text();
    let data;
    try { data = JSON.parse(responseText); }
    catch (_) { throw new Error(`Analysis service returned HTTP ${res.status} with an unreadable response.`); }
    if(!res.ok) throw new Error(data.detail || data.error || `Analysis failed (HTTP ${res.status}).`);

    Object.assign(req, data);
    req.status = "READY";
    if ($("rStatus")) $("rStatus").textContent = "READY";

    activeFannedData = req;
    renderGraphFrame();
    populateRightPanel(data);

  } catch(e) {
    if ($("mainSummary")) $("mainSummary").textContent = "Analysis Failed: " + e.message;
    if ($("rStatus")) $("rStatus").textContent = "FAILED";
    activeFannedData = 'ERROR'; // Stop it from defaulting to loading
    window.loadingAnimFrameId = null; // Explicitly cancel the loop condition
    const W = window.innerWidth;
    const isLeft = side === 'LEFT';
    const cardX = isLeft ? currentLeftX : currentRightX;
    const startX = isLeft ? (cardX - 110) : (cardX + 110);
    const cy = 56 + (window.innerHeight - 56 - 210) / 2;
    drawFannedNodesError(e.message, startX, cy, side);
  }
}

function drawFannedNodesLoading(startX, startY, side = 'RIGHT') {
  const isLeft = side === 'LEFT';
  const GAP = 140;
  const FANNED_W = 480;
  const endX = isLeft ? Math.round(startX - GAP - FANNED_W) : Math.round(startX + GAP);
  const lineTargetX = isLeft ? Math.round(startX - GAP) : endX;

  let itemStartY = startY - (3 * 38) / 2;
  for(let i=0; i<15; i++) {
    hideNode(`sub-${i}`);
    hideLine(`fan-${i}`);
  }

  const elapsed = performance.now() - loadingStartTime;

  const logs = ["> Waiting for the HADRON analysis response…"];

  for(let i=0; i<logs.length; i++) {
    const itemDelay = i * 800; // 800ms stagger between lines
    const drawDuration = 600; // 600ms to sketch the line
    
    if (elapsed < itemDelay) {
      continue;
    }
    
    let dp = (elapsed - itemDelay) / drawDuration;
    if (dp > 1.0) dp = 1.0;
    
    const nodeOpacity = dp; // fade node in as line draws
    const y = itemStartY + (i * 38);
    renderNode(`sub-${i}`, `
      <div class="item-left shimmer-box" style="position:relative; overflow:hidden;">
        <div class="item-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z"/></svg></div>
        <div class="item-title term-text" id="term-title-${i}" style="color:#38bdf8; font-family: monospace; font-size:0.75rem;">${logs[i]}<span class="blink-cursor">_</span></div>
      </div>
      <div class="item-tag running-tag pulsing-border">
        <span class="bars running-bars"><i class="pulse-bar"></i><i class="pulse-bar"></i><i class="pulse-bar"></i></span>
        <span style="font-family: monospace; font-weight: 600; letter-spacing: 0.8px;">RUNNING</span>
      </div>
    `, endX, y, "node-item", null, nodeOpacity);
    drawLine(`fan-${i}`, startX, startY, lineTargetX, y, true, 1.0, 0, dp);
  }

}

function drawFannedNodesError(errorMsg, startX, startY, side = 'RIGHT') {
  if (logIntervalId) {
    clearInterval(logIntervalId);
    logIntervalId = null;
  }
  const isLeft = side === 'LEFT';
  const GAP = 140;
  const FANNED_W = 480;
  const endX = isLeft ? Math.round(startX - GAP - FANNED_W) : Math.round(startX + GAP);
  const lineTargetX = isLeft ? Math.round(startX - GAP) : endX;

  const items = [
    { title: 'API Connection Failed', sub: 'Connectivity Error' },
    { title: 'Optimization Halted', sub: 'Process Terminated' }
  ];

  let itemStartY = startY - ((items.length-1) * 38) / 2;
  for(let i=0; i<15; i++) {
    hideNode(`sub-${i}`);
    hideLine(`fan-${i}`);
  }

  items.forEach((item, i) => {
    const y = itemStartY + (i * 38);
    renderNode(`sub-${i}`, `
      <div class="item-left">
        <div class="item-icon" style="color:#ef4444"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
        <div class="item-title" style="color:#ef4444">${item.title}</div>
      </div>
      <div class="item-tag risk">
        ${item.sub}
      </div>
    `, endX, y, "node-item");

    drawLine(`fan-${i}`, startX, startY, lineTargetX, y, false);
  });
}

function drawFannedNodes(data, startX, startY, side = 'RIGHT') {
  if (logIntervalId) {
    clearInterval(logIntervalId);
    logIntervalId = null;
  }
  const isLeft = side === 'LEFT';
  const GAP = 140;
  const FANNED_W = 480;
  const endX = isLeft ? Math.round(startX - GAP - FANNED_W) : Math.round(startX + GAP);
  const lineTargetX = isLeft ? Math.round(startX - GAP) : endX;

  let items = [];

  let offers = data.offer_set || [];
  if(typeof offers==='string') { try{offers=JSON.parse(offers)}catch(e){offers=[]} }
  if (!Array.isArray(offers)) offers = [];
  if (offers.length === 0) offers = [{ name: 'Offer data unavailable', price: null, icon: 'chart' }];

  const iconMap = {
    chart: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
    target: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
    user: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    crown: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="2 4 6 18 12 10 18 18 22 4 17 8 12 2 7 8 2 4"/></svg>`
  };

  offers.forEach((o, i) => {
    const iconName = o.icon || (i===0?'chart':i===1?'target':i===2?'user':'crown');
    items.push({
      title: o.name,
      val: money(o.price),
      icon: iconMap[iconName] || iconMap.chart,
      type: 'offer'
    });
  });

  let risks = data.risks || [];
  if(typeof risks==='string') { try{risks=JSON.parse(risks)}catch(e){risks=[]} }
  if (!Array.isArray(risks)) risks = [];
  if (risks.length === 0) risks = [{ title: 'No risk details returned', icon: 'msg' }];

  const riskIconMap = {
    doc: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`,
    gear: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
    msg: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`
  };

  risks.forEach((r, i) => {
    const iconName = r.icon || (i===0?'doc':i===1?'gear':'msg');
    items.push({
      title: r.title || r.type || 'Risk Signal',
      tagText: 'Risk Factor',
      icon: riskIconMap[iconName] || riskIconMap.doc,
      type: 'risk'
    });
  });

  const parsePayload = value => {
    if (typeof value !== 'string') return value || {};
    try { return JSON.parse(value); } catch (_) { return {}; }
  };
  const customer = parsePayload(data.customer_intelligence);
  const market = parsePayload(data.market_intelligence);
  const intent = parsePayload(data.request_intent);

  items.push({
    title: 'Customer Evidence',
    subText: 'Internal record',
    valText: customer.data_availability === 'FOUND' ? 'Found' : 'Missing',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    type: 'signal'
  });
  items.push({
    title: 'Market Evidence',
    subText: market.pricing_environment || 'Pricing status',
    valText: market.market_reference_price ? money(market.market_reference_price) : 'Missing',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
    type: 'signal'
  });
  items.push({
    title: 'Scenario Model',
    subText: 'Extraction confidence',
    valText: Number.isFinite(Number(intent.extraction_confidence)) ? `${Math.round(Number(intent.extraction_confidence) * 100)}%` : '—',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><circle cx="19" cy="19" r="2"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><path d="M12 9V5M12 15v4M9 12H5M15 12h4"/></svg>`,
    type: 'signal'
  });
  items.push({
    title: 'Compliance Evidence',
    subText: 'Audit status',
    valText: 'Not assessed',
    icon: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    type: 'signal'
  });

  const totalCount = items.length;
  const itemHeight = 34;
  const itemGap = 5;
  const totalH = totalCount * (itemHeight + itemGap) - itemGap;
  let itemStartY = startY - (totalH / 2) + (itemHeight / 2);

  const topBound = 70;
  const bottomBound = window.innerHeight - 210 - 20 - totalH;
  if (itemStartY < topBound) itemStartY = topBound;
  if (itemStartY > bottomBound && bottomBound > topBound) itemStartY = bottomBound;

  for(let i=0; i<15; i++) {
    hideNode(`sub-${i}`);
    hideLine(`fan-${i}`);
  }

  items.forEach((item, i) => {
    const y = itemStartY + (i * (itemHeight + itemGap));

    let rightBadge = '';
    if (item.type === 'offer') {
      rightBadge = `<div class="item-tag" style="background:rgba(56,189,248,0.12);border-color:rgba(56,189,248,0.3);color:var(--cyan);font-weight:700;"><span class="bars"><i class="on"></i><i class="on"></i><i class="on"></i></span>${item.val}</div>`;
    } else if (item.type === 'risk') {
      rightBadge = `<div class="item-tag risk"><span class="bars"><i class="on"></i><i class="on"></i><i></i></span>${item.tagText}</div>`;
    } else {
      rightBadge = `<div class="item-tag"><span class="bars"><i class="on"></i><i class="on"></i><i></i></span>${item.subText} <b style="color:#fff;margin-left:4px;">${item.valText}</b></div>`;
    }

    renderNode(`sub-${i}`, `
      <div class="item-left">
        <div class="item-icon">${item.icon}</div>
        <div class="item-title" title="${item.title}">${item.title}</div>
      </div>
      ${rightBadge}
    `, endX, y, "node-item flip-animate");

    const nodeEl = $(`sub-${i}`);
    if (nodeEl) nodeEl.style.animationDelay = `${i * 60}ms`;

    drawLine(`fan-${i}`, startX, startY, lineTargetX, y, true);
  });
}

/* ── DONUT GAUGES ──────────────────────────── */
function animateDonut(arcId, pct) {
  const circ = 2 * Math.PI * 30; // r=30 → ~188.5
  const arc = $(arcId);
  if (!arc) return;
  const fill = Math.max(0, Math.min(1, pct / 100));
  arc.setAttribute('stroke-dasharray', `${fill * circ} ${circ}`);
}

/* ── 3D EXTRUDED PIE & DONUT CHART RENDERER ── */
const PIE_COLORS = ['#e2c079','#6ab0ff','#34d399','#818cf8','#f87171','#fb923c','#38bdf8'];

function draw3DPieChart(svgId, legendId, segments) {
  const svg = $(svgId);
  const legend = $(legendId);
  if (!svg) return;

  const total = segments.reduce((s, g) => s + (Number(g.value) || 0), 0);
  if (total === 0) { svg.innerHTML = ''; if (legend) legend.innerHTML = ''; return; }

  const cx = 80, cy = 60, r = 54, inner = 30, depth = 18;
  let startAngle = -Math.PI / 2;
  let topPaths = '';
  let wallPaths = '';

  segments.forEach((seg, i) => {
    const baseColor = seg.color || PIE_COLORS[i % PIE_COLORS.length];
    const val = Number(seg.value) || 0;
    const angle = (val / total) * 2 * Math.PI;
    if (angle === 0) return;

    const endAngle = startAngle + angle;

    const x1o = cx + r * Math.cos(startAngle);
    const y1o = cy + r * Math.sin(startAngle);
    const x2o = cx + r * Math.cos(endAngle);
    const y2o = cy + r * Math.sin(endAngle);

    const x1i = cx + inner * Math.cos(endAngle);
    const y1i = cy + inner * Math.sin(endAngle);
    const x2i = cx + inner * Math.cos(startAngle);
    const y2i = cy + inner * Math.sin(startAngle);

    const large = angle > Math.PI ? 1 : 0;

    wallPaths += `<path d="M${x1o},${y1o} A${r},${r} 0 ${large},1 ${x2o},${y2o} L${x2o},${y2o+depth} A${r},${r} 0 ${large},0 ${x1o},${y1o+depth} Z" fill="${baseColor}" filter="brightness(0.65)" opacity="0.95"/>`;
    topPaths += `<path d="M${x1o},${y1o} A${r},${r} 0 ${large},1 ${x2o},${y2o} L${x1i},${y1i} A${inner},${inner} 0 ${large},0 ${x2i},${y2i} Z" fill="${baseColor}" filter="brightness(1.15)" opacity="0.98"/>`;

    startAngle = endAngle;
  });

  svg.innerHTML = `<g class="pie-3d-group">${wallPaths}${topPaths}</g>`;

  if (legend) {
    legend.innerHTML = segments.map((seg, i) => {
      const color = seg.color || PIE_COLORS[i % PIE_COLORS.length];
      const val = Number(seg.value) || 0;
      const pct = total > 0 ? ((val / total) * 100).toFixed(0) : 0;
      return `<div class="pie-legend-item-3d">
        <span><span class="dot" style="background:${color}"></span>${seg.label}</span>
        <b style="color:#fff;margin-left:auto;">${pct}%</b>
      </div>`;
    }).join('');
  }
}

/* ── UPDATE EXPANDED MAIN BOTTOM DASHBOARD ── */
function updateMain3DIntelligence(data) {
  if (!data) return;

  let econ = data.internal_economics;
  if (typeof econ === 'string') { try { econ = JSON.parse(econ); } catch(e) { econ = {}; } }
  econ = econ || {};

  let offers = data.offer_set;
  if (typeof offers === 'string') { try { offers = JSON.parse(offers); } catch(e) { offers = []; } }
  if (!Array.isArray(offers)) offers = [];

  const balancedOffer = offers.find(o => o.name?.toLowerCase().includes('balanced')) || offers[0];
  const balancedPriceNum = balancedOffer && Number.isFinite(Number(balancedOffer.price)) ? Number(balancedOffer.price) : null;

  if (balancedPriceNum !== null) {
    animateNumber('rBalancedOffer', 0, balancedPriceNum, v => money(v), 900);
    animateNumber('balancedPriceBadge', 0, balancedPriceNum, v => money(v), 900);
    animateNumber('skpiBalanced', 0, balancedPriceNum, v => money(v), 900);
  } else {
    ['rBalancedOffer', 'balancedPriceBadge', 'skpiBalanced'].forEach(id => { if ($(id)) $(id).textContent = '—'; });
  }

  let risks = data.risks;
  if (typeof risks === 'string') { try { risks = JSON.parse(risks); } catch(e) { risks = []; } }
  if (!Array.isArray(risks)) risks = [];

  const parseData = value => {
    if (typeof value !== 'string') return value || {};
    try { return JSON.parse(value); } catch (_) { return {}; }
  };
  const service = parseData(data.service_intelligence);
  const customer = parseData(data.customer_intelligence);
  const market = parseData(data.market_intelligence);
  const commercial = parseData(data.commercial_context);

  const minPrice = Number(econ.minimum_viable_price) || null;
  if ($('skpiFloor')) $('skpiFloor').textContent = minPrice === null ? '—' : money(minPrice);
  if ($('skpiComplexity')) $('skpiComplexity').textContent = service.complexity != null && Number.isFinite(Number(service.complexity)) ? Number(service.complexity).toFixed(2) : '—';
  if ($('skpiHighRisks')) $('skpiHighRisks').textContent = risks.filter(r => (r.severity || '').toUpperCase() === 'HIGH').length;
  const offerEl = $('mainOffers');
  if (offerEl) {
    offerEl.innerHTML = offers.slice(0, 4).map((o, i) => {
      const isRec = o.recommended === true;
      const priceSignal = Number.isFinite(Number(o.win_signal)) ? `${Math.round(Number(o.win_signal) * 100)}%` : '—';
      const riskScore = Number.isFinite(Number(o.risk_score)) ? Number(o.risk_score).toFixed(2) : '—';
      const strategicValue = Number.isFinite(Number(o.strategic_value)) ? `${Math.round(Number(o.strategic_value) * 100)}%` : '—';

      return `
        <div class="expanded-offer-card ${isRec?'highlight-card':''}">
          <div class="o-top-row">
            <span class="o-name">${o.name || 'Commercial Offer'}</span>
            ${isRec ? `<span class="o-rec-tag">Recommended</span>` : ''}
          </div>
          <div class="o-price">${money(o.price)}</div>
          <div class="o-margin">Expected Margin ${Number.isFinite(Number(o.expected_margin)) ? (Number(o.expected_margin)*100).toFixed(1)+'%' : '—'}</div>
          
          <div class="offer-metrics-row">
            <div class="om-item">
              <small>Price Signal*</small>
              <strong>${priceSignal}</strong>
            </div>
            <div class="om-item">
              <small>Risk Score</small>
              <strong class="cyan">${riskScore}</strong>
            </div>
            <div class="om-item">
              <small>Strategy Weight</small>
              <strong class="green">${strategicValue}</strong>
            </div>
          </div>
        </div>`;
    }).join('');
  }

  const riskEl = $('mainRisks');
  if (riskEl) {
    riskEl.innerHTML = risks.map(r => `
      <div class="expanded-risk-item">
        <span class="risk-badge-3d">${r.severity || r.type || 'HIGH'}</span>
        <span class="risk-text-3d">${r.title || r.description || JSON.stringify(r)}</span>
      </div>`).join('');
  }

  const execSummaryText = data.executive_summary || 'No executive summary was returned. Review the analysis response and its evidence before using the offer values.';

  if ($('mainSummary')) {
    const el = $('mainSummary');
    if (window.typingIntervalId) clearInterval(window.typingIntervalId);
    el.textContent = execSummaryText;
  }
  const costText = econ.economics_source === 'INSUFFICIENT_SCOPE' || !(Number(econ.estimated_cost) > 0)
    ? 'unavailable' : money(econ.estimated_cost);
  const floorText = minPrice === null ? 'unavailable' : money(minPrice);
  const marginText = Number.isFinite(Number(econ.target_margin)) ? `${(Number(econ.target_margin) * 100).toFixed(1)}%` : 'unavailable';
  const balancedMargin = balancedOffer && Number.isFinite(Number(balancedOffer.expected_margin))
    ? `${(Number(balancedOffer.expected_margin) * 100).toFixed(1)}%` : 'unavailable';
  if ($('economicJustification')) {
    const method = econ.economics_source === 'CATALOG' ? 'catalog-backed cost data' : econ.economics_source === 'INSUFFICIENT_SCOPE' ? 'not calculated because scope evidence is missing' : 'a provisional rate-card model';
    $('economicJustification').textContent = `Estimated delivery cost: ${costText}. Minimum viable price: ${floorText} at a ${marginText} target margin. ${method}. Balanced scenario margin: ${balancedMargin}.`;
  }
  if ($('marketJustification')) {
    const marketText = market.market_reference_price
      ? `Market reference: ${money(market.market_reference_price)}${market.pricing_environment ? ` (${market.pricing_environment})` : ''}.`
      : 'No usable market price reference was found; the offers are not market-validated.';
    const customerText = customer.data_availability === 'FOUND'
      ? `Internal customer record found for ${customer.customer_name || 'the customer'}.`
      : 'No internal customer record was found.';
    const capacityText = econ.required_capacity != null
      ? `Estimated staffing is ${econ.required_capacity} role FTE versus ${econ.capacity_available} available FTE.`
      : 'Staffing demand is not estimated, so capacity feasibility is unverified.';
    const historyText = econ.historical_deal_count
      ? `${econ.historical_deal_count} historical deals are available for comparison.`
      : 'No usable historical deal values are available.';
    const budgetText = econ.project_budget != null
      ? `Stated project budget: ${money(econ.project_budget)}.`
      : 'No project-specific budget was supplied.';
    const pipelineText = econ.pipeline_gap != null
      ? `Company quarterly target-to-pipeline gap: ${money(econ.pipeline_gap)}; this is a sales planning metric, not available cash.`
      : '';
    const accountText = customer.active_budget != null
      ? `Internal account file lists ${money(customer.active_budget)} in active program budget; this is not confirmed as this project's budget.`
      : '';
    const synthesisText = data.synthesis_mode === 'deterministic_fallback'
      ? 'Executive text used deterministic fallback.'
      : data.synthesis_mode === 'gemini' ? 'Executive text synthesized by Gemini.' : 'Synthesis mode not recorded.';
    $('marketJustification').textContent = `${customerText} ${marketText} ${capacityText} ${budgetText} ${accountText} ${pipelineText} ${historyText} ${synthesisText}`;
  }
  if ($('analysisMethodNote')) {
    $('analysisMethodNote').textContent = '* Price signal is a rule-based scenario indicator, not a measured probability of winning the deal.';
  }

  const totalOfferVal = offers.reduce((s, o) => s + (o.price || 0), 0);
  if (totalOfferVal > 0) {
    draw3DPieChart('offerPie', 'offerLegend', offers.slice(0, 4).map((o, i) => ({
      label: o.name || `Offer ${i+1}`,
      value: o.price || 1,
      color: ['#e2c079', '#6ab0ff', '#34d399', '#818cf8'][i % 4]
    })));
  }

  const estimatedCost = Number(econ.estimated_cost) || 0;
  const marginPct = Number(econ.target_margin) || 0;
  if (estimatedCost > 0 && marginPct > 0 && marginPct < 1) {
    const marginAmt = estimatedCost * marginPct / (1 - marginPct);
    draw3DPieChart('marginPie', 'marginLegend', [
      { label: 'Estimated Cost', value: Math.round(estimatedCost), color: '#6ab0ff' },
      { label: 'Target Margin Build', value: Math.round(marginAmt), color: '#e2c079' }
    ]);
  } else {
    draw3DPieChart('marginPie', 'marginLegend', []);
  }

  const riskCounts = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  risks.forEach(r => {
    const sev = (r.severity || r.type || 'MEDIUM').toUpperCase();
    if (riskCounts[sev] !== undefined) riskCounts[sev]++; else riskCounts.MEDIUM++;
  });
  draw3DPieChart('riskPie', 'riskLegend', [
    { label: 'High Severity', value: riskCounts.HIGH, color: '#f87171' },
    { label: 'Medium Severity', value: riskCounts.MEDIUM, color: '#fb923c' },
    { label: 'Low Severity', value: riskCounts.LOW, color: '#34d399' }
  ]);

  const signalValues = [
    ['sigDemandVal', 'sigDemandFill', market.demand_signal || 'No data'],
    ['sigCompVal', 'sigCompFill', market.competitor_signals?.length ? `${market.competitor_signals.length} signals` : 'No data'],
    ['sigEnvVal', 'sigEnvFill', market.pricing_environment || 'No data'],
    ['sigUrgVal', 'sigUrgFill', commercial.urgency_signal || 'No data']
  ];
  signalValues.forEach(([valueId, fillId, value]) => {
    if ($(valueId)) $(valueId).textContent = value;
    if ($(fillId)) $(fillId).style.height = '0%';
  });

}

function scrollToSection(id) {
  const el = $(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
    document.querySelectorAll('.nav-pill').forEach(btn => btn.classList.remove('active'));
    const btnMap = {
      'graphSection': 0,
      'secCommercial': 1,
      'secPricing': 2,
      'secRisk': 3,
      'secStrategy': 4
    };
    const idx = btnMap[id];
    if (idx !== undefined && document.querySelectorAll('.nav-pill')[idx]) {
      document.querySelectorAll('.nav-pill')[idx].classList.add('active');
    }
  }
}



function animateNumber(elId, startVal, endVal, formatFn, duration = 1200) {
  const el = $(elId);
  if (!el) return;
  const startTime = performance.now();
  function tick(now) {
    let dp = (now - startTime) / duration;
    if (dp > 1) dp = 1;
    dp = dp * (2 - dp); // ease out quad
    const current = startVal + (endVal - startVal) * dp;
    el.textContent = formatFn(current);
    if (dp < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function triggerPopIn(selector, delayMs = 100) {
  const items = document.querySelectorAll(selector);
  items.forEach((item, idx) => {
    item.classList.remove('pop-in-anim');
    void item.offsetWidth; // reflow
    item.style.animationDelay = `${idx * delayMs}ms`;
    item.classList.add('pop-in-anim');
  });
}

function populateRightPanel(data) {
  let econ = data.internal_economics;
  if (typeof econ === 'string') { try { econ = JSON.parse(econ); } catch(e) { econ = {}; } }
  econ = econ || {};

  let offers = data.offer_set;
  if (typeof offers === 'string') { try { offers = JSON.parse(offers); } catch(e) { offers = []; } }
  offers = Array.isArray(offers) ? offers : [];

  const confRaw = Number(data.confidence);
  const conf    = Number.isFinite(confRaw) ? confRaw : null;
  const margin  = Number.isFinite(Number(econ.target_margin)) ? Number(econ.target_margin) * 100 : null;
  const numOffers = offers.length;
  const floorVal = Number(econ.minimum_viable_price) || null;

  if (floorVal !== null) animateNumber('rFloor', 0, floorVal, v => money(v), 900);
  else if ($('rFloor')) $('rFloor').textContent = '—';
  if (margin !== null) {
    animateNumber('rMargin', 0, margin, v => v.toFixed(1) + ' %', 900);
    animateNumber('rMarginD', 0, margin, v => v.toFixed(1) + '%', 900);
  } else {
    if ($('rMargin')) $('rMargin').textContent = '—';
    if ($('rMarginD')) $('rMarginD').textContent = '—';
  }
  animateNumber('rOffers', 0, numOffers, v => Math.floor(v), 900);
  if (conf !== null) animateNumber('rConf', 0, conf * 100, v => `${v.toFixed(0)}%`, 900);
  else if ($('rConf')) $('rConf').textContent = '—';

  animateDonut('confArc', conf === null ? 0 : conf * 100);
  animateDonut('marginArc', margin === null ? 0 : margin);

  updateMain3DIntelligence(data);
  
  // Trigger staggered animations for panels
  setTimeout(() => {
    triggerPopIn('.expanded-offer-card', 150);
    triggerPopIn('.chart-box', 200);
    triggerPopIn('.metric-col', 100);
  }, 100);
}

// Window resize listener
window.addEventListener('resize', () => {
  if (requests.length > 0) {
    if (graphState) {
      animateGraphToState(graphState, activeSide, 0);
    } else {
      renderGraph();
    }
  }
});

// Modal bindings
if ($("newBtn")) $("newBtn").onclick = () => $("modal").classList.remove("hidden");
if ($("closeModal")) $("closeModal").onclick = () => $("modal").classList.add("hidden");
if ($("createBtn")) $("createBtn").onclick = async () => {
  $("createBtn").textContent = "Creating...";
  $("createBtn").disabled = true;
  try {
    const res = await fetch("/api/requests", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        customer_name: $("fCustomer").value,
        service_product_name: $("fService").value,
        commercial_objective: $("fObjective").value,
        additional_context: $("fContext").value
      })
    });
    if(!res.ok) throw new Error("Failed to create");
    const createdReq = await res.json();
    $("modal").classList.add("hidden");
    const wasSelected = (graphState === 'SELECTED');
    await loadRequests(wasSelected);
    
    // Auto-select the newly created request to trigger the terminal logs animation
    const fullReq = requests.find(r => r.sys_id === createdReq.sys_id);
    if (fullReq) {
      const isLeft = leftRequests.some(r => r.sys_id === fullReq.sys_id);
      fullReq.executive_summary = null;
      selectRequest(fullReq, 0, 0, isLeft ? 'LEFT' : 'RIGHT', true);
    }
  } catch(e) {
    alert(e.message);
  } finally {
    $("createBtn").textContent = "Create Analysis Request";
    $("createBtn").disabled = false;
  }
};

// Initialize Splash Screen & Login Gateway
initSplashAndLogin();
