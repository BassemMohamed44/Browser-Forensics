const CHART_AVAILABLE = typeof window.Chart !== "undefined";
const LUCIDE_AVAILABLE = typeof window.lucide !== "undefined";

function refreshIcons() {
  if (LUCIDE_AVAILABLE) {
    try { lucide.createIcons(); } catch (e) { console.warn("lucide render failed", e); }
  }
}
refreshIcons();

const state = {
  charts: {},
};

function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), 2800);
}

function setStatus(title, sub, progress, tone) {
  document.getElementById("status-title").textContent = title;
  document.getElementById("status-sub").textContent = sub;
  document.getElementById("status-bar-fill").style.width = `${progress}%`;
  const pill = document.getElementById("status-pill");
  pill.style.borderColor = tone === "error" ? "rgba(239,68,68,0.35)" : "rgba(34,197,94,0.25)";
  pill.style.background = tone === "error" ? "rgba(239,68,68,0.08)" : "rgba(34,197,94,0.08)";
}

function fmt(n) {
  if (n === undefined || n === null) return "—";
  return n.toLocaleString();
}

// ---------------------------------------------------------------------
// Filters -> query string
// ---------------------------------------------------------------------
function currentFilterParams() {
  const params = new URLSearchParams();
  const browser = document.getElementById("f-browser").value;
  const profile = document.getElementById("f-profile").value;
  const dateFrom = document.getElementById("f-date-from").value;
  const dateTo = document.getElementById("f-date-to").value;
  const keyword = document.getElementById("f-keyword").value;
  const includeDup = document.getElementById("f-duplicates").checked;
  const topSites = document.getElementById("f-topsites").checked;

  if (browser) params.set("browser", browser);
  if (profile) params.set("profile", profile);
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  if (keyword) params.set("keyword", keyword);
  params.set("include_duplicates", includeDup ? "true" : "false");
  params.set("top_sites_only", topSites ? "true" : "false");
  return params;
}

// ---------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------
function renderCards(cards) {
  document.querySelectorAll("[data-field]").forEach((el) => {
    const key = el.getAttribute("data-field");
    el.textContent = fmt(cards[key]);
  });
}

function renderFilterOptions(filters) {
  const browserSel = document.getElementById("f-browser");
  const profileSel = document.getElementById("f-profile");
  const keepBrowser = browserSel.value;
  const keepProfile = profileSel.value;

  browserSel.innerHTML = '<option value="all">All Browsers</option>';
  filters.browsers.forEach((b) => {
    const opt = document.createElement("option");
    opt.value = b;
    opt.textContent = b;
    browserSel.appendChild(opt);
  });
  browserSel.value = keepBrowser || "all";

  profileSel.innerHTML = '<option value="all">All Profiles</option>';
  filters.profiles.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    profileSel.appendChild(opt);
  });
  profileSel.value = keepProfile || "all";
}

const BROWSER_COLORS = {
  "Google Chrome": "#3b82f6",
  "Google Chrome Beta": "#60a5fa",
  "Microsoft Edge": "#22c55e",
  "Brave": "#f59e0b",
  "Opera": "#ef4444",
  "Vivaldi": "#a855f7",
  "Chromium": "#06b6d4",
  "Mozilla Firefox": "#f97316",
  "Firefox ESR": "#fb923c",
};
function colorFor(name, idx) {
  return BROWSER_COLORS[name] || ["#3b82f6", "#22c55e", "#f59e0b", "#a855f7", "#06b6d4", "#ef4444"][idx % 6];
}

function renderTimeline(data) {
  const empty = document.getElementById("timeline-empty");
  const ctx = document.getElementById("chart-timeline");
  if (!CHART_AVAILABLE) {
    ctx.style.display = "none";
    empty.textContent = "Chart library unavailable (blocked network?) — timeline chart disabled.";
    empty.classList.add("show");
    return;
  }
  if (!data.labels.length) {
    empty.textContent = "Run a scan to see activity over time.";
    empty.classList.add("show");
    ctx.style.display = "none";
    return;
  }
  empty.classList.remove("show");
  ctx.style.display = "block";

  if (state.charts.timeline) state.charts.timeline.destroy();
  state.charts.timeline = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59,130,246,0.12)",
        fill: true,
        tension: 0.35,
        pointRadius: 0,
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#5b6478", maxTicksLimit: 8 } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#5b6478" } },
      },
    },
  });
}

function renderDonut(donut) {
  const total = donut.reduce((sum, d) => sum + d.count, 0);
  document.getElementById("donut-total").textContent = fmt(total);

  const ctx = document.getElementById("chart-donut");
  if (CHART_AVAILABLE) {
    if (state.charts.donut) state.charts.donut.destroy();
    state.charts.donut = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: donut.map((d) => d.browser),
        datasets: [{
          data: donut.map((d) => d.count),
          backgroundColor: donut.map((d, i) => colorFor(d.browser, i)),
          borderWidth: 0,
        }],
      },
      options: {
        cutout: "72%",
        plugins: { legend: { display: false }, tooltip: { enabled: true } },
      },
    });
  } else {
    ctx.style.display = "none";
  }

  const legend = document.getElementById("donut-legend");
  legend.innerHTML = "";
  donut.forEach((d, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="name"><span class="dot" style="background:${colorFor(d.browser, i)}"></span>${d.browser}</span><span class="pct">${d.pct}%</span>`;
    legend.appendChild(li);
  });
}

function renderTopSites(rows) {
  const tbody = document.querySelector("#table-top-sites tbody");
  const empty = document.getElementById("top-sites-empty");
  tbody.innerHTML = "";
  if (!rows.length) {
    empty.classList.add("show");
    return;
  }
  empty.classList.remove("show");
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="rank">${r.rank}</td>
      <td>${r.domain}</td>
      <td>${fmt(r.visits)}</td>
      <td>${r.last_visit}</td>
      <td><span class="browser-cell">${r.browser}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderBar(data) {
  const ctx = document.getElementById("chart-bar");
  if (!CHART_AVAILABLE) {
    ctx.style.display = "none";
    return;
  }
  if (state.charts.bar) state.charts.bar.destroy();
  state.charts.bar = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values,
        backgroundColor: "#3b82f6",
        borderRadius: 4,
        maxBarThickness: 26,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#5b6478" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#5b6478" } },
      },
    },
  });
}

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
function renderHeatmap(matrix) {
  const el = document.getElementById("heatmap");
  el.innerHTML = "";
  const max = Math.max(1, ...matrix.flat());

  matrix.forEach((row, dayIdx) => {
    const rowEl = document.createElement("div");
    rowEl.className = "heat-row";
    const label = document.createElement("div");
    label.className = "heat-row-label";
    label.textContent = DAY_LABELS[dayIdx];
    rowEl.appendChild(label);

    row.forEach((count) => {
      const cell = document.createElement("div");
      cell.className = "heat-cell";
      const intensity = count / max;
      cell.style.background = `rgba(59,130,246,${0.06 + intensity * 0.85})`;
      cell.title = `${count} visit(s)`;
      rowEl.appendChild(cell);
    });
    el.appendChild(rowEl);
  });

  const hourRow = document.createElement("div");
  hourRow.className = "heat-hours";
  [0, 6, 12, 18, 23].forEach((h) => {
    const span = document.createElement("span");
    span.textContent = h;
    hourRow.appendChild(span);
  });
  el.appendChild(hourRow);
}

function renderLogs(logs) {
  const container = document.getElementById("log-list");
  container.innerHTML = "";
  if (!logs.length) {
    container.innerHTML = '<div class="empty-hint show">No activity yet — run a scan.</div>';
    return;
  }
  logs.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "log-row";
    row.innerHTML = `
      <span class="log-time">${entry.time}</span>
      <span class="log-msg">${entry.message}</span>
      <i data-lucide="${entry.ok ? "check-circle-2" : "alert-triangle"}" class="log-status ${entry.ok ? "ok" : "warn"}"></i>
    `;
    container.appendChild(row);
  });
  refreshIcons();
}

function renderSummary(summary) {
  const list = document.getElementById("summary-list");
  const labels = {
    total_records: "Total Records",
    unique_domains: "Unique Domains",
    duplicate_visits: "Duplicate Visits",
    browsers_detected: "Browsers Detected",
    profiles_found: "Profiles Found",
    errors: "Read Errors",
  };
  list.innerHTML = "";
  Object.entries(labels).forEach(([key, label]) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${label}</span><span>${fmt(summary[key])}</span>`;
    list.appendChild(li);
  });
}

// ---------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------
async function loadDashboard() {
  const params = currentFilterParams();
  const res = await fetch(`/api/dashboard?${params.toString()}`);
  const data = await res.json();

  if (!data.scanned) {
    setStatus("Ready", "Run a scan to begin", 0, "ok");
    return;
  }

  const renderers = [
    ["cards", () => renderCards(data.cards)],
    ["filters", () => renderFilterOptions(data.filters)],
    ["timeline", () => renderTimeline(data.activity_timeline)],
    ["donut", () => renderDonut(data.browsers_overview)],
    ["top sites", () => renderTopSites(data.top_sites)],
    ["bar chart", () => renderBar(data.visits_by_day)],
    ["heatmap", () => renderHeatmap(data.hour_heatmap)],
    ["logs", () => renderLogs(data.recent_logs)],
    ["summary", () => renderSummary(data.summary)],
  ];
  for (const [name, fn] of renderers) {
    try {
      fn();
    } catch (err) {
      console.error(`Failed to render ${name}:`, err);
    }
  }

  const errTone = data.summary.errors > 0 ? "error" : "ok";
  setStatus(
    data.summary.errors > 0 ? "Completed with warnings" : "Ready",
    `Last scan: ${data.scanned_at || "—"}`,
    100,
    errTone
  );
}

async function runScan() {
  setStatus("Scanning…", "Detecting browsers and reading history", 35, "ok");
  toast("Scan started…");
  try {
    const res = await fetch("/api/scan", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    const data = await res.json();
    if (!data.ok) {
      toast(`Scan failed: ${data.error}`);
      setStatus("Scan failed", data.error, 100, "error");
      return;
    }
    toast(`Scan complete — ${data.summary.records_found.toLocaleString()} records found`);
    await loadDashboard();
  } catch (err) {
    toast("Scan failed — see console for details.");
    console.error(err);
  }
}

function downloadExport(format) {
  window.location.href = `/api/export?format=${encodeURIComponent(format)}`;
}

// ---------------------------------------------------------------------
// Wiring
// ---------------------------------------------------------------------
document.getElementById("filters-form").addEventListener("submit", (e) => {
  e.preventDefault();
  loadDashboard();
});

document.querySelectorAll('.nav-item[data-action="scan"]').forEach((el) => el.addEventListener("click", runScan));
document.getElementById("qa-scan").addEventListener("click", runScan);

document.querySelectorAll('[data-action="export"]').forEach((el) =>
  el.addEventListener("click", () => downloadExport("all"))
);
document.getElementById("qa-export-csv").addEventListener("click", () => downloadExport("csv"));
document.getElementById("qa-export-all").addEventListener("click", () => downloadExport("all"));

document.getElementById("btn-export-json").addEventListener("click", (e) => {
  e.stopPropagation();
  document.querySelector(".export-split").classList.toggle("open");
});
document.querySelectorAll(".export-menu button").forEach((btn) => {
  btn.addEventListener("click", () => {
    downloadExport(btn.getAttribute("data-format"));
    document.querySelector(".export-split").classList.remove("open");
  });
});
document.addEventListener("click", (e) => {
  if (!e.target.closest(".export-split")) {
    document.querySelector(".export-split").classList.remove("open");
  }
});

document.querySelectorAll('.nav-item[data-focus]').forEach((el) => {
  el.addEventListener("click", () => {
    const target = el.getAttribute("data-focus");
    if (target === "keyword") document.getElementById("f-keyword").focus();
    if (target === "stats") document.getElementById("stats").scrollIntoView({ behavior: "smooth" });
    if (target === "logs") document.getElementById("log-list").scrollIntoView({ behavior: "smooth" });
  });
});
document.getElementById("qa-search-focus").addEventListener("click", () => {
  document.getElementById("f-keyword").focus();
});

// ---------------------------------------------------------------------
// Theme toggle (persisted in localStorage across reloads)
// ---------------------------------------------------------------------
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const label = document.getElementById("theme-label");
  const icon = document.querySelector("#theme-toggle i");
  if (label) label.textContent = theme === "light" ? "Light" : "Dark";
  if (icon && LUCIDE_AVAILABLE) {
    icon.setAttribute("data-lucide", theme === "light" ? "sun" : "moon");
    refreshIcons();
  }
}

function initTheme() {
  const saved = localStorage.getItem("bhe-theme");
  const theme = saved === "light" ? "light" : "dark";
  applyTheme(theme);
}

document.getElementById("theme-toggle").addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  const next = current === "light" ? "dark" : "light";
  localStorage.setItem("bhe-theme", next);
  applyTheme(next);
});

initTheme();

loadDashboard();
