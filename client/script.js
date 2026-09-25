// ===== HealthAI prototype – frontend logic (mock data, no backend yet) =====
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
let userName = "Ardina";
let role = "patient";

// ---------- Role toggle (Patient / Doctor) ----------
document.querySelectorAll(".role").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".role").forEach((x) => x.classList.remove("on"));
    b.classList.add("on");
    role = b.dataset.role;
  })
);

// ---------- Screen navigation ----------
function showScreen(id) {
  $$(".screen").forEach((s) => s.classList.remove("active"));
  $("#" + id).classList.add("active");
  window.scrollTo(0, 0);
}
$$("[data-go]").forEach((el) =>
  el.addEventListener("click", (e) => { e.preventDefault(); showScreen(el.dataset.go); })
);

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2200);
}

// ---------- Auth (client-side validation only) ----------
const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

$("#loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const email = $("#loginEmail").value.trim();
  const pass = $("#loginPass").value;
  if (!emailOk(email)) return ($("#loginError").textContent = "Enter a valid email address.");
  if (pass.length < 6) return ($("#loginError").textContent = "Password must be at least 6 characters.");
  $("#loginError").textContent = "";
  role === "doctor" ? showScreen("doctor") : enterApp();
});

$("#signupForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const name = $("#suName").value.trim();
  if (!name) return ($("#signupError").textContent = "Enter your name.");
  if (!emailOk($("#suEmail").value.trim())) return ($("#signupError").textContent = "Enter a valid email address.");
  if ($("#suPass").value.length < 6) return ($("#signupError").textContent = "Password must be at least 6 characters.");
  $("#signupError").textContent = "";
  userName = name.split(" ")[0];
  toast("Account created");
  enterApp();
});

function enterApp() {
  const h = new Date().getHours();
  const part = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  $("#greeting").textContent = `${part}, ${userName}`;
  showScreen("app");
  drawChart();
}
$("#logoutBtn").addEventListener("click", () => showScreen("landing"));

// ---------- Sidebar pages ----------
$$("#sideNav a").forEach((a) =>
  a.addEventListener("click", () => {
    $$("#sideNav a").forEach((x) => x.classList.remove("active"));
    a.classList.add("active");
    $$(".page").forEach((p) => p.classList.remove("active"));
    $("#page-" + a.dataset.page).classList.add("active");
    if (a.dataset.page === "soon") $("#soonTitle").textContent = a.textContent;
  })
);

// ---------- Dashboard: weight chart ----------
function drawChart() {
  const data = [72, 71.8, 71.9, 71.5, 71.6, 71.3, 71.2, 71.0];
  const min = 70.5, max = 72.5, w = 400, h = 120;
  const pts = data.map((v, i) => [
    20 + (i * (w - 40)) / (data.length - 1),
    10 + ((max - v) / (max - min)) * (h - 20),
  ]);
  const path = pts.map((p, i) => (i ? "L" : "M") + p[0] + " " + p[1]).join(" ");
  $("#weightChart").innerHTML =
    `<path d="${path}" fill="none" stroke="#1f7a6c" stroke-width="2.5"/>` +
    pts.map((p) => `<circle cx="${p[0]}" cy="${p[1]}" r="3.5" fill="#1f7a6c"/>`).join("");
}

$$(".dose").forEach((d) =>
  d.addEventListener("click", () => {
    d.classList.toggle("done");
    toast(d.classList.contains("done") ? `${d.textContent.replace("✓ ", "")} dose marked as taken` : "Dose unmarked");
  })
);

// ---------- AI Assistant (mock responses; will call LLM API later) ----------
function mockReply(q) {
  q = q.toLowerCase();
  if (q.includes("chest pain") || q.includes("breath"))
    return "Chest pain or difficulty breathing can be serious. Please contact emergency services or see a doctor right away.";
  if (q.includes("report") || q.includes("blood"))
    return "I found your uploaded blood report (20 Aug). Hemoglobin is 10.2, below the reference range 12–16. WBC and glucose are within range. This alone doesn't establish a diagnosis — please discuss it with your doctor.";
  if (q.includes("headache"))
    return "I can share general information. Headaches are often linked to stress, dehydration or poor sleep. Rest and fluids may help. See a doctor if it's severe, sudden, or lasts more than a few days.";
  return "I can help you understand general health information and your uploaded reports. Could you tell me a bit more?";
}
function addMsg(text, who) {
  const m = document.createElement("div");
  m.className = "msg " + who;
  m.textContent = text;
  $("#chat").appendChild(m);
  $("#chat").scrollTop = $("#chat").scrollHeight;
  return m;
}
$("#chatForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("#chatText").value.trim();
  if (!q) return;
  addMsg(q, "user");
  $("#chatText").value = "";
  const t = addMsg("HealthAI is typing…", "ai typing");
  setTimeout(() => { t.classList.remove("typing"); t.textContent = mockReply(q); }, 900);
});

// ---------- Symptom checker ----------
$$(".chip").forEach((c) => c.addEventListener("click", () => c.classList.toggle("on")));
$("#symNext").addEventListener("click", () => {
  if (!$$(".chip.on").length) return toast("Select at least one symptom");
  $("#symStep2").classList.remove("hidden");
});
$("#symResult").addEventListener("click", () => {
  const syms = [...$$(".chip.on")].map((c) => c.textContent);
  const urgent = [...$$(".redflag")].some((c) => c.checked) || $("#symSev").value === "Severe";
  $("#symStep3").innerHTML = `
    ${urgent ? `<div class="urgent"><strong>Seek medical care soon.</strong> Some of what you reported needs a doctor's attention.</div>` : ""}
    <h3>Possible explanations for ${syms.join(", ").toLowerCase()} (${$("#symDur").value})</h3>
    <ol style="padding-left:1.2rem;margin-bottom:1rem">
      <li>Common cold</li><li>Viral respiratory infection</li><li>Other possibilities</li>
    </ol>
    <h3>General self-care</h3>
    <ul style="padding-left:1.2rem"><li>Stay hydrated</li><li>Get adequate rest</li><li>Monitor your symptoms</li></ul>
    <p class="disclaimer">This is general information, not a diagnosis.</p>`;
  $("#symStep3").classList.remove("hidden");
});

// ---------- Document upload + analysis (mock of OCR → extraction → LLM pipeline) ----------
const sampleReport = [
  { name: "Hemoglobin", value: 10.2, low: 12, high: 16, unit: "g/dL" },
  { name: "WBC", value: 7500, low: 4000, high: 11000, unit: "/µL" },
  { name: "Glucose (fasting)", value: 95, low: 70, high: 100, unit: "mg/dL" },
];

function runAnalysis(title) {
  const box = $("#analysis");
  box.classList.remove("hidden");
  const steps = ["Reading document (OCR)…", "Extracting parameters…", "Comparing with reference ranges…", "Generating explanation…"];
  box.innerHTML = `<h3>Analyzing ${title}</h3><p id="stepText">${steps[0]}</p><div class="progress"><div id="bar"></div></div>`;
  let i = 0;
  const timer = setInterval(() => {
    i++;
    $("#bar").style.width = (i / steps.length) * 100 + "%";
    if (i < steps.length) $("#stepText").textContent = steps[i];
    else { clearInterval(timer); showResult(title); }
  }, 600);
  box.scrollIntoView({ behavior: "smooth" });
}

function showResult(title) {
  const rows = sampleReport.map((p) => {
    const out = p.value < p.low || p.value > p.high;
    return `<tr><td>${p.name}</td><td class="${out ? "out" : "ok"}">${p.value.toLocaleString()} ${p.unit}</td>
      <td>${p.low.toLocaleString()}–${p.high.toLocaleString()}</td><td>${out ? "Outside range" : "Normal"}</td></tr>`;
  }).join("");
  const flagged = sampleReport.filter((p) => p.value < p.low || p.value > p.high).map((p) => p.name);
  $("#analysis").innerHTML = `
    <h3>${title} analysis · 20 Aug 2026</h3>
    <table class="doc-table"><tr><th>Parameter</th><th>Value</th><th>Reference</th><th>Status</th></tr>${rows}</table>
    <div class="ai-note" style="margin-top:1rem"><strong>AI explanation:</strong>
      ${flagged.length ? `Your ${flagged.join(", ").toLowerCase()} value is outside the reference range shown on the report.` : "All values are within range."}
      This result alone does not establish a diagnosis. Discuss it with a healthcare professional if appropriate.</div>
    <button class="btn primary" style="margin-top:1rem" id="askReport">Ask AI about this report</button>`;
  $("#askReport").addEventListener("click", () => $('[data-page="assistant"]').click());
}

$$("[data-analyze]").forEach((b) =>
  b.addEventListener("click", () => runAnalysis(b.closest("tr").cells[0].textContent))
);

function handleFile(file) {
  if (!file) return;
  if (!/\.(pdf|jpe?g|png)$/i.test(file.name)) return toast("Only PDF, JPG or PNG files are supported");
  const row = $("#docTable").insertRow(0);
  row.innerHTML = `<td>${file.name}</td><td>Today</td><td><button class="btn small">Analyze</button></td>`;
  row.querySelector("button").addEventListener("click", () => runAnalysis(file.name));
  toast("Document uploaded");
  runAnalysis(file.name);
}
$("#fileInput").addEventListener("change", (e) => handleFile(e.target.files[0]));
const dz = $("#dropzone");
dz.addEventListener("dragover", (e) => { e.preventDefault(); dz.classList.add("over"); });
dz.addEventListener("dragleave", () => dz.classList.remove("over"));
dz.addEventListener("drop", (e) => { e.preventDefault(); dz.classList.remove("over"); handleFile(e.dataTransfer.files[0]); });

// ---------- Medicines ----------
$("#medForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const n = $("#medName").value.trim(), d = $("#medDose").value.trim();
  if (!n || !d) return toast("Enter medicine name and dose");
  $("#medTable").insertRow().innerHTML = `<td>${n}</td><td>${d}</td><td>${$("#medTime").value}</td>`;
  $("#medName").value = $("#medDose").value = "";
  toast("Medicine added");
});

// ---------- Doctor: view a patient's reports ----------
$$("[data-view]").forEach((b) =>
  b.addEventListener("click", () => {
    const rows = sampleReport.map((p) => {
      const out = p.value < p.low || p.value > p.high;
      return `<tr><td>${p.name}</td><td class="${out ? "out" : "ok"}">${p.value.toLocaleString()} ${p.unit}</td><td>${p.low.toLocaleString()}–${p.high.toLocaleString()}</td></tr>`;
    }).join("");
    const box = $("#patientView");
    box.innerHTML = `<h3>${b.dataset.view} · Blood report (20 Aug 2026)</h3>
      <table class="doc-table"><tr><th>Parameter</th><th>Value</th><th>Reference</th></tr>${rows}</table>
      <div class="ai-note" style="margin-top:1rem"><strong>AI summary for doctor:</strong> Hemoglobin below reference range; WBC and glucose within range.</div>`;
    box.classList.remove("hidden");
    box.scrollIntoView({ behavior: "smooth" });
  })
);