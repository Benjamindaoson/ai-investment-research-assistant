/**
 * StockTitan AI Engine - Unified Logic Engine
 * Silicon Valley UX + Wall Street Rigor (Chinese Localized)
 */

const API = 'http://127.0.0.1:8000';

const state = {
  activeSubject: 'AAPL',
  feed: [
    { id: 1, type: 'ALPHA', symbol: 'AAPL', title: '毛利结构性扩张周期', body: '服务业务营收占比提升至 26%，毛利贡献超 70%。供应链显示 H2 订单量稳健。', time: '08:42', impact: '+4.2% Alpha', thesis: '近期财报超预期代表了结构性的增长基石转变。服务业务以 14% 的增速扩张，有效抵消了二级市场硬件周期的疲软。供应链交叉分析显示，“毛利扩张”周期将于下半年开启。', verdict: '买入 (BUY)', confidence: 88, target: 215, sources: [{ tag: '来源: Form 10-K / 财报原文片段', text: '“服务业务毛利率达到 74.2%，高于去年同期的 72.8%，主要由订阅量增长驱动...”' }, { tag: '来源: 路透社情报 / 供应链数据流', text: '“由于积压订单强于预期，富士康已提前启动 Pro 型号的增产计划。”' }] },
    { id: 2, type: 'MOMENTUM', symbol: 'NVDA', title: '算力需求结构性突破', body: '确认突破 $850 关键阻力位。机构资金流向显示 H1 需求深度远超预期。', time: '09:15', impact: '+6.8% Exp', thesis: '英伟达在 Blackwell 架构上的领先优势正在转化为实质性的定价权。', verdict: '强力买入 (STRONG BUY)', confidence: 92, target: 1100, sources: [{ tag: '来源: 行业调研', text: '“算力芯片预分配订单量已达到溢出状态。”' }] },
    { id: 3, type: 'RISK', symbol: 'TSLA', title: '供应链摩擦预警', body: '柏林工厂零部件瓶颈。正在评估产能爬坡风险。', time: '09:30', impact: '-2.1% Alpha', thesis: '柏林工厂的物流瓶颈可能拖累 Q2 交付量。整车毛利仍面临短期压力。', verdict: '中性 (HOLD)', confidence: 55, target: 240, sources: [{ tag: '来源: 内部监控', text: '“产线交付周期延长 2-3 周。”' }] }
  ],
  marketData: null,
  currentMarket: 'CN'
};

// ── NAVIGATION ──
function go(pageId, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  document.getElementById('page-' + pageId).classList.add('active');

  if (el) {
    el.classList.add('active');
  } else {
    const nav = document.querySelector(`.nav-item[onclick*="'${pageId}'"]`);
    if (nav) nav.classList.add('active');
  }

  // Module-specific initializers
  if (pageId === 'lobby') runLobby();
  if (pageId === 'home') { renderFeed(); selectSubject(state.feed[0].symbol, state.feed[0].id); }
  if (pageId === 'diag') runDiag();
}

// ── CLOCK & TICKER ──
function initBasics() {
  setInterval(() => {
    const clock = document.getElementById('clock');
    if (clock) clock.textContent = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  }, 1000);

  const ticks = [
    { s: 'AAPL', p: 185.50, c: +1.24 }, { s: 'TSLA', p: 248.32, c: -3.14 },
    { s: 'NVDA', p: 881.60, c: +1.43 }, { s: 'MSFT', p: 415.20, c: +0.15 },
    { s: 'AMZN', p: 188.80, c: +0.95 }, { s: 'META', p: 517.10, c: +1.20 }
  ];
  const ticker = document.getElementById('tickerStrip');
  if (ticker) {
    ticker.innerHTML = ticks.map(t => `
            <div class="ticker-item">
                <span style="color:var(--text-2)">${t.s}</span>
                <span>$${t.p.toFixed(2)}</span>
                <span class="${t.c >= 0 ? 'up' : 'dn'}">${t.c >= 0 ? '+' : ''}${t.c.toFixed(2)}%</span>
            </div>
        `).join('');
  }
}

// ── LOBBY: PROFESSIONAL TRADING TERMINAL STYLE ──
async function runLobby() {
  const idxArea = document.getElementById('lobby-indices');
  const listArea = document.getElementById('lobby-list');
  if (!idxArea || !listArea) return;

  idxArea.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:40px; color:var(--text-2);"><div class="spinner" style="margin:0 auto 16px;"></div>正在同步全球交易系统数据...</div>`;

  try {
    const resp = await fetch(API + '/api/market/overview');
    if (!resp.ok) throw new Error("API Connection Failed");
    state.marketData = await resp.json();

    renderLobbyIndices();
    renderLobbyList();

  } catch (e) {
    idxArea.innerHTML = `<div style="grid-column:1/-1; color:var(--red); text-align:center; padding:40px;">行情中心同步失败: ${e.message}<br><button class="btn btn-g" style="margin-top:10px" onclick="runLobby()">重试连接</button></div>`;
  }
}

function renderLobbyIndices() {
  const area = document.getElementById('lobby-indices');
  if (!area || !state.marketData) return;

  area.innerHTML = state.marketData.indices.map(idx => {
    const isUp = idx.change >= 0;
    const colorClass = isUp ? 'idx-status-up' : 'idx-status-dn';
    const colorText = isUp ? 'var(--green)' : 'var(--red)';

    return `
            <div class="idx-card ${colorClass}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; font-size:1.1rem; color:var(--text-0)">${idx.name}</span>
                    <span style="font-family:var(--f-mono); font-size:0.75rem; color:var(--text-2)">${idx.symbol}</span>
                </div>
                <div style="font-family:var(--f-mono); font-size:2rem; font-weight:800; color:${colorText}; margin:12px 0;">
                    ${idx.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </div>
                <div style="display:flex; gap:12px; font-weight:800; font-size:0.95rem; color:${colorText}">
                    <span>${isUp ? '+' : ''}${idx.change}</span>
                    <span>${isUp ? '+' : ''}${idx.pct_change}%</span>
                </div>
            </div>
        `;
  }).join('');
}

function switchMarket(m, el) {
  state.currentMarket = m;
  document.querySelectorAll('.lobby-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  renderLobbyList();
}

function renderLobbyList() {
  const area = document.getElementById('lobby-list');
  if (!area || !state.marketData) return;

  const list = state.marketData.lists[state.currentMarket] || [];

  area.innerHTML = list.map(s => {
    const isUp = s.pct_change >= 0;
    const color = isUp ? 'var(--green)' : 'var(--red)';

    return `
            <div class="stock-row" onclick="selectStock('${s.symbol}')">
                <div style="display:flex; flex-direction:column; gap:2px;">
                    <span style="font-weight:800; font-size:0.95rem; color:var(--text-0)">${s.symbol}</span>
                    <span style="font-size:0.7rem; color:var(--text-2); font-weight:700;">热度标的</span>
                </div>
                <div style="text-align:right; font-family:var(--f-mono); font-weight:800; font-size:1rem;">
                    ${s.price.toFixed(2)}
                </div>
                <div style="text-align:right; font-family:var(--f-mono); font-weight:800; color:${color}">
                    ${isUp ? '+' : ''}${(s.price * s.pct_change / 100).toFixed(2)}
                </div>
                <div style="text-align:right;">
                    <span style="display:inline-block; width:70px; padding:6px 0; border-radius:6px; background:${color}; color:#fff; font-family:var(--f-mono); font-weight:800; font-size:0.85rem; text-align:center;">
                        ${isUp ? '+' : ''}${s.pct_change.toFixed(2)}%
                    </span>
                </div>
            </div>
        `;
  }).join('');
}

function selectStock(sym) {
  state.activeSubject = sym;
  go('home');
  // In a real app we'd trigger a search here
}

// ── HOME: FACTOR ANALYSIS ──
function renderFeed() {
  const scroll = document.getElementById('feedScroll');
  if (!scroll) return;
  scroll.innerHTML = state.feed.map(event => `
        <div class="event-card ${state.activeSubject === event.symbol ? 'active' : ''}" onclick="selectSubject('${event.symbol}', ${event.id})">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span class="badge badge-b">${event.type}</span>
                <span style="font-size:0.75rem; color:var(--text-2); font-family:var(--f-mono);">${event.time}</span>
            </div>
            <div style="font-family:var(--f-mono); font-weight:800; font-size:1.1rem; color:var(--text-0);">${event.symbol}</div>
            <div style="font-size:0.9rem; font-weight:600; color:var(--text-0); margin-top:4px;">${event.title}</div>
            <div style="font-size:0.8rem; color:var(--text-1); margin-top:6px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">${event.body}</div>
        </div>
    `).join('');
}

async function selectSubject(symbol, eventId) {
  state.activeSubject = symbol;
  renderFeed();
  const event = state.feed.find(f => f.id === eventId);
  if (!event) return;

  document.getElementById('workspaceHeader').innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="font-family:var(--f-mono); font-size:2.5rem; font-weight:800; letter-spacing:-0.04em;">${symbol}</div>
                <div style="font-weight:800; font-size:1rem; color:var(--accent); margin-top:4px;">因子探测: ${event.type}</div>
            </div>
            <div style="text-align:right">
                <div style="font-family:var(--f-mono); font-size:1.8rem; font-weight:700">$${(180 + Math.random() * 20).toFixed(2)}</div>
                <div class="${event.type === 'RISK' ? 'dn' : 'up'}" style="font-size:0.9rem; font-weight:600">${event.impact}</div>
            </div>
        </div>
    `;

  document.getElementById('workspaceContent').innerHTML = `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:32px;">
            <div class="card" style="text-align:center; border-color:var(--accent); min-height:160px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; font-weight:800; color:var(--accent); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">因子评估 (Factor Eval)</div>
                <div style="font-size:2.5rem; font-weight:800; color:${event.verdict.includes('买入') ? 'var(--green)' : 'var(--text-0)'}">${event.verdict}</div>
                <div style="font-family:var(--f-mono); font-size:1.1rem; font-weight:700; margin-top:8px;">预期目标: $${event.target}</div>
            </div>
            <div class="card" style="text-align:center; min-height:160px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:0.7rem; font-weight:800; color:var(--text-2); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">置信度得分</div>
                <div style="font-size:2.5rem; font-weight:800;">${event.confidence}%</div>
                <div style="font-size:0.8rem; color:var(--text-1); margin-top:8px;">基于 48 条类似信号</div>
            </div>
        </div>
        <div style="font-family:var(--f-title); font-size:1.1rem; font-weight:800; border-left:4px solid var(--accent); padding-left:12px; margin-bottom:12px;">投资论点 (Thesis)</div>
        <p style="font-size:1rem; line-height:1.7; color:var(--text-1); margin-bottom:32px;">${event.thesis}</p>
        <div style="font-family:var(--f-title); font-size:1.1rem; font-weight:800; border-left:4px solid var(--accent); padding-left:12px; margin-bottom:12px;">证据碎片 (Evidence)</div>
        ${event.sources.map(s => `
            <div style="background:var(--bg-page); padding:16px; border-radius:12px; margin-bottom:12px; font-size:0.85rem; border:1px solid var(--border);">
                <div style="color:var(--accent); font-weight:800; font-size:0.7rem; margin-bottom:4px;">${s.tag}</div>
                <div style="color:var(--text-1); line-height:1.5;">${s.text}</div>
            </div>
        `).join('')}
    `;

  document.getElementById('impactPanel').innerHTML = `
        <div class="card" style="background:linear-gradient(135deg, var(--primary), #1e293b); color:#fff; text-align:center;">
            <div style="font-size:0.8rem; opacity:0.8; font-weight:600;">模拟持仓动作</div>
            <div style="font-size:1.2rem; font-weight:800; margin-top:8px;">${event.verdict.includes('买入') ? '采纳“买入”建议' : '保持现有头寸'}</div>
            <button class="btn btn-p" style="width:100%; margin-top:20px; background:#fff; color:var(--primary);">执行投资决策 (Execute)</button>
        </div>
        <div class="card" style="margin-top:16px;">
            <div style="font-size:0.7rem; font-weight:800; color:var(--text-2); margin-bottom:12px;">风险分布迁移</div>
            <div style="height:120px; display:flex; align-items:flex-end; gap:8px;">
                <div style="flex:1; height:60%; background:var(--accent); border-radius:4px;"></div>
                <div style="flex:1; height:40%; background:var(--yellow); border-radius:4px;"></div>
                <div style="flex:1; height:25%; background:var(--red); border-radius:4px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.6rem; color:var(--text-2); font-weight:700">
                <span>SECTOR</span><span>BETA</span><span>VOL</span>
            </div>
        </div>
    `;
}

// ── ANALYST: REPORT AGENT ──
async function runAnalyst() {
  const sym = document.getElementById('an-sym').value.trim().toUpperCase();
  const result = document.getElementById('an-result');
  if (!sym) return;

  result.innerHTML = `
        <div class="card" style="width:100%; text-align:center; padding:60px;">
            <div class="spinner" style="margin:0 auto 20px;"></div>
            正在调度研报智能体 (LangGraph Agent)...
        </div>`;

  try {
    const resp = await fetch(API + '/api/v1/orchestrate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stock_code: sym, price: parseFloat(document.getElementById('an-price').value), news: [document.getElementById('an-news').value] })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const d = await resp.json();

    result.innerHTML = `
            <div class="card" style="width:100%;">
                <h2 style="margin-bottom:16px; font-family:var(--f-title);">${sym} 深度投研报告</h2>
                <div style="display:inline-block; padding:4px 12px; border-radius:20px; background:var(--accent-lt); color:var(--accent); font-weight:800; margin-bottom:20px;">评级: ${d.advice || 'HOLD'} (置信度 ${d.confidence}%)</div>
                <div style="font-size:1rem; line-height:1.7; color:var(--text-1); white-space:pre-wrap;">${d.executive_summary}</div>
                <div style="margin-top:24px; font-weight:800; font-size:1.1rem;">核心催化剂:</div>
                <ul style="margin-left:20px; margin-top:12px; font-size:0.95rem; color:var(--text-1); line-height:1.8;">
                    ${(d.catalysts || []).map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>`;
  } catch (e) {
    result.innerHTML = `<div class="card" style="color:var(--red)">分析失败: ${e.message}</div>`;
  }
}

// ── BACKTEST: QUANT LAB ──
async function runBacktest() {
  const sym = document.getElementById('bt-sym').value.trim().toUpperCase();
  const area = document.getElementById('bt-result');
  if (!sym) return;

  area.innerHTML = `
        <div class="card" style="text-align:center; padding:60px; color:var(--text-2)">
            <div class="spinner" style="margin:0 auto 16px;"></div>
            正在同步历史行情并执行向量化回测...
        </div>`;

  try {
    const payload = Array.from({ length: document.getElementById('bt-num').value }, (_, i) => ({
      id: `sig-${i}`,
      symbol: sym,
      direction: document.getElementById('bt-dir').value,
      entry_price: parseFloat(document.getElementById('bt-price').value) + (Math.random() - 0.5) * 10,
      confidence: Math.floor(Math.random() * 40 + 60),
      created_at: String(Math.floor(Date.now() / 1000) - i * 86400 * 5)
    }));

    const resp = await fetch(API + '/api/v1/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await resp.json();

    area.innerHTML = `
            <div class="card">
                <h3 style="margin-bottom:20px; font-weight:800;">因子绩效摘要: ${sym}</h3>
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:24px;">
                    <div class="card" style="background:var(--bg-page); text-align:center; padding:20px;">
                        <div style="font-size:0.75rem; color:var(--text-2); font-weight:800; text-transform:uppercase;">命中率 (Hit Rate)</div>
                        <div style="font-size:1.8rem; font-weight:800; color:var(--green); margin-top:8px;">${d.hit_rate_pct.toFixed(1)}%</div>
                    </div>
                    <div class="card" style="background:var(--bg-page); text-align:center; padding:20px;">
                        <div style="font-size:0.75rem; color:var(--text-2); font-weight:800; text-transform:uppercase;">Avg Return</div>
                        <div style="font-size:1.8rem; font-weight:800; color:var(--green); margin-top:8px;">+${d.avg_return_pct.toFixed(2)}%</div>
                    </div>
                    <div class="card" style="background:var(--bg-page); text-align:center; padding:20px;">
                        <div style="font-size:0.75rem; color:var(--text-2); font-weight:800; text-transform:uppercase;">治理状态</div>
                        <div style="font-size:1.2rem; font-weight:800; color:var(--accent); margin-top:8px;">${d.status}</div>
                    </div>
                </div>
                <div style="background:var(--accent-lt); border:1px solid var(--accent); padding:16px; border-radius:12px; color:var(--accent); font-weight:700;">
                    💡 当前因子分配权重: ${d.weight}x — 建议在量化池中增加此因子配置。
                </div>
            </div>`;
  } catch (e) {
    area.innerHTML = `<div class="card" style="color:var(--red)">回测失败: ${e.message}</div>`;
  }
}

// ── RERANK: INTELLIGENCE LIBRARY ──
async function runRerank() {
  const query = document.getElementById('rk-query').value.trim();
  const area = document.getElementById('rk-result');
  if (!query) return;

  area.innerHTML = `<div class="card" style="text-align:center; padding:40px;"><div class="spinner" style="margin:0 auto 16px;"></div>正在通过神经重排序搜索知识库...</div>`;

  try {
    const resp = await fetch(API + '/api/v1/rerank', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        candidates: [
          { stock_code: 'AAPL', title: 'Apple Services Growth Analysis', analysis: 'Highly sustainable margin expansion in Apple Services.' },
          { stock_code: 'TSLA', title: 'Tesla China EV Demand', analysis: 'Assessing Model 3 competitive landscape in mainland China.' },
          { stock_code: 'NVDA', title: 'H100/B200 GPU Pipeline', analysis: 'Deep dive into GPU supply chain lead times.' }
        ]
      })
    });
    const d = await resp.json();
    area.innerHTML = d.map((r, i) => `
            <div class="card" style="margin-bottom:12px; padding:16px; animation:fadeIn 0.3s ease ${i * 0.05}s forwards; opacity:0;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="padding:4px 10px; background:var(--bg-page); border-radius:12px; font-weight:800; font-size:0.75rem; color:var(--text-1)">${r.stock_code}</span>
                    <span style="font-family:var(--f-mono); font-weight:800; color:var(--accent); font-size:0.8rem;">RELEVANCE: ${(r.score * 10).toFixed(4)}</span>
                </div>
                <div style="font-weight:800; margin-bottom:6px; font-size:1.05rem;">${r.title}</div>
                <div style="font-size:0.9rem; color:var(--text-1); line-height:1.5;">${r.analysis}</div>
            </div>
        `).join('');
  } catch (e) {
    area.innerHTML = `<div class="card" style="color:var(--red)">检索失败: ${e.message}</div>`;
  }
}

// ── DIAG: ADMIN TERMINAL ──
async function runDiag() {
  const nodes = document.getElementById('diag-nodes');
  if (!nodes) return;

  nodes.innerHTML = `<div class="spinner" style="width:20px; height:20px;"></div>`;
  try {
    const alive = await fetch(API + '/health').then(r => r.ok).catch(() => false);
    nodes.innerHTML = ['/health', '/api/v1/orchestrate', '/api/v1/backtest', '/api/v1/rerank', '/api/market/overview'].map(p => `
            <div style="display:flex; justify-content:space-between; padding:16px; border-bottom:1px solid var(--border); font-family:var(--f-mono); font-size:0.9rem;">
                <span style="color:var(--text-1);">${p}</span>
                <span style="color:${alive ? 'var(--green)' : 'var(--red)'}; font-weight:800;">● ${alive ? 'CONNECTED' : 'OFFLINE'}</span>
            </div>
        `).join('');
  } catch (e) {
    nodes.innerHTML = "网络管理节点暂无法连通";
  }
}

window.onload = () => {
  initBasics();
  go('lobby');
};

// CSS SPIN ANIM
const style = document.createElement('style');
style.innerHTML = `
    .spinner {
        width: 32px; height: 32px;
        border: 3px solid rgba(0,0,0,0.05);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
`;
document.head.appendChild(style);
