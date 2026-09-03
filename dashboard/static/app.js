(function () {
  const $ = (id) => document.getElementById(id);
  const statusEl = $("status");
  const bodyEl = $("alert-body");
  const emptyEl = $("empty");
  let timer = null;

  function metrics(a) {
    const parts = [];
    if (a.failed_ssh != null) parts.push("failed_ssh=" + a.failed_ssh);
    if (a.peak_in_window != null) parts.push("peak_in_window=" + a.peak_in_window);
    if (a.threshold != null) parts.push("threshold=" + a.threshold);
    if (a.window_sec != null) parts.push("window_sec=" + a.window_sec);
    if (a.requests != null) parts.push("requests=" + a.requests);
    if (a.sample_path) parts.push("sample=" + a.sample_path);
    if (a.unique_ports != null) parts.push("unique_ports=" + a.unique_ports);
    if (a.packets != null) parts.push("packets=" + a.packets);
    return parts.join(" · ") || "—";
  }

  function setBusy(busy) {
    ["btn-generate", "btn-detect", "btn-refresh"].forEach((id) => {
      $(id).disabled = busy;
    });
  }

  function render(data) {
    const alerts = data.alerts || [];
    const counts = { critical: 0, high: 0, medium: 0 };
    alerts.forEach((a) => {
      const s = (a.severity || "").toLowerCase();
      if (counts[s] != null) counts[s] += 1;
    });
    $("n-critical").textContent = counts.critical;
    $("n-high").textContent = counts.high;
    $("n-medium").textContent = counts.medium;
    $("n-total").textContent = data.alert_count != null ? data.alert_count : alerts.length;

    const lc = data.log_counts || {};
    ["ssh_failed", "ssh_accepted", "http", "firewall"].forEach((k) => {
      const el = $("c-" + k);
      if (el) el.textContent = lc[k] != null ? lc[k] : "—";
    });

    bodyEl.innerHTML = "";
    if (data.missing || alerts.length === 0) {
      emptyEl.classList.remove("hidden");
    } else {
      emptyEl.classList.add("hidden");
    }
    alerts.forEach((a) => {
      const tr = document.createElement("tr");
      const sev = (a.severity || "unknown").toLowerCase();
      tr.innerHTML =
        '<td><span class="sev ' + sev + '">' + sev + "</span></td>" +
        "<td>" + (a.rule || a.title || "—") + "</td>" +
        "<td>" + (a.mitre || "—") + "</td>" +
        "<td><code>" + (a.src_ip || "—") + "</code></td>" +
        '<td class="metrics">' + metrics(a) + "</td>";
      bodyEl.appendChild(tr);
    });
    const when = new Date().toLocaleTimeString();
    statusEl.textContent =
      "alert_count=" + (data.alert_count != null ? data.alert_count : alerts.length) +
      " · updated " + when;
  }

  async function loadAlerts() {
    try {
      const res = await fetch("/api/alerts", { cache: "no-store" });
      const data = await res.json();
      render(data);
    } catch (err) {
      statusEl.textContent = "Failed to load /api/alerts";
    }
  }

  async function post(path, label) {
    setBusy(true);
    statusEl.textContent = label + "…";
    try {
      const res = await fetch(path, { method: "POST" });
      const data = await res.json();
      if (!data.ok) {
        statusEl.textContent = label + " failed: " + (data.stderr || data.error || res.status);
      } else {
        statusEl.textContent = label + " ok";
        if (data.alerts) render(data.alerts);
        else await loadAlerts();
      }
    } catch (err) {
      statusEl.textContent = label + " error";
    } finally {
      setBusy(false);
    }
  }

  $("btn-generate").addEventListener("click", () => post("/api/generate", "Generate"));
  $("btn-detect").addEventListener("click", () => post("/api/detect", "Detect"));
  $("btn-refresh").addEventListener("click", () => loadAlerts());

  function armLive() {
    if (timer) clearInterval(timer);
    timer = null;
    if ($("live").checked) {
      timer = setInterval(loadAlerts, 5000);
    }
  }
  $("live").addEventListener("change", armLive);

  loadAlerts();
  armLive();
})();
