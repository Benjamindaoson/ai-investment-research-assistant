const state = {
  metrics: null,
  governance: [],
  signals: []
};

const ids = {
  sessionId: document.getElementById("sessionId"),
  strategy: document.getElementById("strategy"),
  symbols: document.getElementById("symbols"),
  limit: document.getElementById("limit"),
  message: document.getElementById("message"),
  batchStatus: document.getElementById("batchStatus"),
  signalTableBody: document.getElementById("signalTableBody"),
  govTableBody: document.getElementById("govTableBody"),
  creditEmpty: document.getElementById("creditEmpty"),
  creditCard: document.getElementById("creditCard"),
  creditSymbol: document.getElementById("creditSymbol"),
  creditDirection: document.getElementById("creditDirection"),
  creditScore: document.getElementById("creditScore"),
  creditMeta: document.getElementById("creditMeta"),
  creditBars: document.getElementById("creditBars"),
  kpiWeekly: document.getElementById("kpiWeekly"),
  kpiTotal: document.getElementById("kpiTotal"),
  kpiSharpe: document.getElementById("kpiSharpe"),
  kpiMdd: document.getElementById("kpiMdd"),
  kpiPf: document.getElementById("kpiPf")
};

const strategyChart = echarts.init(document.getElementById("strategyChart"));
const regimeChart = echarts.init(document.getElementById("regimeChart"));
const horizonChart = echarts.init(document.getElementById("horizonChart"));

function fmt(v, d = 2) {
  if (v === null || v === undefined || v === "") return "-";
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(d) : String(v);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();
  if (json.code !== 200) throw new Error(json.message || "API error");
  return json.data;
}

async function refreshMetricsAndGovernance() {
  const sessionId = ids.sessionId.value.trim();
  const qs = sessionId ? `?sessionId=${encodeURIComponent(sessionId)}` : "";
  const [metrics, governance] = await Promise.all([
    api(`/api/ai/product/signals/metrics${qs}`),
    api(`/api/ai/product/signals/governance${qs}`)
  ]);
  state.metrics = metrics || {};
  state.governance = governance || [];
  renderKpis();
  renderGovernance();
  renderCharts();
}

function renderKpis() {
  const m = state.metrics || {};
  ids.kpiWeekly.textContent = fmt(m.weeklyEffectiveSignals, 0);
  ids.kpiTotal.textContent = fmt(m.totalSignals, 0);
  ids.kpiSharpe.textContent = fmt(m.approximateSharpe, 2);
  ids.kpiMdd.textContent = `${fmt(m.maxDrawdownPct, 2)}%`;
  ids.kpiPf.textContent = fmt(m.approximateProfitFactor, 2);
}

function renderGovernance() {
  const rows = state.governance.map(x => {
    const status = (x.status || "ACTIVE").toUpperCase();
    const cls = status === "RETIRED" ? "chip-retired"
      : status === "DOWNWEIGHT" ? "chip-downweight" : "chip-active";
    return `<tr>
      <td>${x.strategyTemplateId || "-"}</td>
      <td><span class="chip ${cls}">${status}</span></td>
      <td>${fmt(x.weight, 2)}</td>
      <td>${fmt(x.hitRatePct, 2)}%</td>
      <td>${fmt(x.total, 0)}</td>
      <td>${x.reason || "-"}</td>
    </tr>`;
  }).join("");
  ids.govTableBody.innerHTML = rows || `<tr><td colspan="6">暂无治理数据</td></tr>`;
}

function renderCharts() {
  const m = state.metrics || {};
  const strategy = m.strategyRanking || [];
  const regime = m.regimeMetrics || [];
  const horizons = m.horizonMetrics || [];

  strategyChart.setOption({
    grid: { left: 50, right: 20, top: 30, bottom: 42 },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: strategy.map(x => x.strategyTemplateId),
      axisLabel: { color: "#b7c6eb" }
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#b7c6eb", formatter: "{value}%" },
      splitLine: { lineStyle: { color: "rgba(120,150,210,0.16)" } }
    },
    series: [{
      type: "bar",
      data: strategy.map(x => Number(x.hitRatePct || 0)),
      itemStyle: { color: "#38bdf8" },
      barMaxWidth: 34
    }]
  });

  regimeChart.setOption({
    tooltip: { trigger: "item" },
    legend: { bottom: 0, textStyle: { color: "#b7c6eb" } },
    series: [{
      type: "pie",
      radius: ["42%", "72%"],
      data: regime.map(x => ({ name: x.regime, value: Number(x.hitRatePct || 0) })),
      label: { color: "#e5edff", formatter: "{b}\n{c}%" },
      itemStyle: { borderColor: "#0c1733", borderWidth: 2 }
    }]
  });

  horizonChart.setOption({
    grid: { left: 40, right: 24, top: 28, bottom: 38 },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: horizons.map(x => x.horizon),
      axisLabel: { color: "#b7c6eb" }
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#b7c6eb", formatter: "{value}%" },
      splitLine: { lineStyle: { color: "rgba(120,150,210,0.16)" } }
    },
    series: [{
      type: "line",
      smooth: true,
      data: horizons.map(x => Number(x.hitRatePct || 0)),
      symbolSize: 10,
      lineStyle: { color: "#34d399", width: 3 },
      itemStyle: { color: "#34d399" },
      areaStyle: { color: "rgba(52,211,153,0.2)" }
    }]
  });
}

function renderSignalTable() {
  const rows = state.signals.map(s => `<tr>
    <td>${s.symbol || "-"}</td>
    <td>${s.direction || "-"}</td>
    <td>${fmt(s.signalCreditScore, 2)}</td>
    <td>${fmt(s.riskBudgetPct, 2)}</td>
    <td>${fmt(s.expectedRMultiple, 2)}</td>
    <td>${s.positionSizing || "-"}</td>
    <td>${s.triggerCondition || "-"}</td>
    <td>${s.invalidationCondition || "-"}</td>
  </tr>`).join("");
  ids.signalTableBody.innerHTML = rows || `<tr><td colspan="8">暂无信号</td></tr>`;
}

function renderCreditCard() {
  if (!state.signals.length) {
    ids.creditEmpty.classList.remove("hidden");
    ids.creditCard.classList.add("hidden");
    return;
  }
  const top = [...state.signals].sort((a, b) =>
    Number(b.signalCreditScore || 0) - Number(a.signalCreditScore || 0))[0];
  ids.creditEmpty.classList.add("hidden");
  ids.creditCard.classList.remove("hidden");
  ids.creditSymbol.textContent = top.symbol || "-";
  ids.creditDirection.textContent = `${top.direction || "-"} | 置信 ${fmt(top.confidence, 0)}%`;
  ids.creditScore.textContent = fmt(top.signalCreditScore, 1);
  ids.creditMeta.textContent = `风险预算 ${fmt(top.riskBudgetPct, 2)}% · 预期R ${fmt(top.expectedRMultiple, 2)} · 仓位 ${top.positionSizing || "-"}`;

  const breakdown = top.creditBreakdown || {};
  const names = {
    historicalHitRate: "历史同类命中率",
    regimeFit: "Regime 匹配",
    dataFreshness: "数据新鲜度",
    sourceConsistency: "多源一致性",
    modelConfidence: "模型置信度"
  };
  ids.creditBars.innerHTML = Object.keys(names).map(key => {
    const value = Number(breakdown[key] || 0);
    return `<div class="bar-row">
      <span>${names[key]}</span>
      <div class="bar"><span style="width:${Math.max(0, Math.min(100, value))}%"></span></div>
      <span>${fmt(value, 0)}</span>
    </div>`;
  }).join("");
}

async function runBatch() {
  ids.batchStatus.textContent = "批量扫描执行中...";
  const payload = {
    sessionId: ids.sessionId.value.trim(),
    message: ids.message.value.trim(),
    strategyTemplateId: ids.strategy.value,
    symbols: ids.symbols.value.split(",").map(x => x.trim()).filter(Boolean),
    limit: Number(ids.limit.value || 10)
  };
  const signals = await api("/api/ai/product/signals/generate/batch", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  state.signals = signals || [];
  renderSignalTable();
  renderCreditCard();
  await refreshMetricsAndGovernance();
  ids.batchStatus.textContent = `完成：生成 ${state.signals.length} 条信号`;
}

document.getElementById("batchRunBtn").addEventListener("click", () => {
  runBatch().catch(e => {
    ids.batchStatus.textContent = `执行失败: ${e.message}`;
  });
});

document.getElementById("refreshAllBtn").addEventListener("click", () => {
  refreshMetricsAndGovernance().catch(e => {
    ids.batchStatus.textContent = `刷新失败: ${e.message}`;
  });
});

window.addEventListener("resize", () => {
  strategyChart.resize();
  regimeChart.resize();
  horizonChart.resize();
});

refreshMetricsAndGovernance().catch(e => {
  ids.batchStatus.textContent = `初始化失败: ${e.message}`;
});
