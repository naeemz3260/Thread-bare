const SEV_COLORS = {
    Critical: "#d6304a",
    High: "#d9711f",
    Medium: "#c48a12",
    Low: "#2563eb",
    Info: "#8a8a97",
};
const SEV_ORDER = ["Critical", "High", "Medium", "Low", "Info"];

const uploadView = document.getElementById("upload-view");
const scanView = document.getElementById("scan-view");
const resultsView = document.getElementById("results-view");

const fileInput = document.getElementById("file-input");
const dzText = document.getElementById("dz-text");
const dropzone = document.getElementById("dropzone");
const scanForm = document.getElementById("scan-form");
const scanBtn = document.getElementById("scan-btn");

const progressFill = document.getElementById("progress-fill");
const progressLabel = document.getElementById("progress-label");
const terminalLog = document.getElementById("terminal-log");

const summaryCards = document.getElementById("summary-cards");
const findingsList = document.getElementById("findings-list");
const scanAgainBtn = document.getElementById("scan-again-btn");

let selectedFile = null;

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
        selectedFile = fileInput.files[0];
        dzText.innerHTML = `${selectedFile.name} <span class="dz-sub">ready to scan</span>`;
        scanBtn.disabled = false;
    }
});

["dragover", "dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        if (evt === "dragover") dropzone.classList.add("dragover");
        if (evt === "dragleave" || evt === "drop") dropzone.classList.remove("dragover");
    });
});
dropzone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event("change"));
    }
});

scanForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    uploadView.classList.add("hidden");
    scanView.classList.remove("hidden");
    terminalLog.innerHTML = `<div class="term-line term-boot">&gt; connecting to claude-sonnet-5 ...</div>`;
    progressFill.style.width = "6%";
    progressLabel.textContent = "scanning...";
    appendLog("> uploading project archive...", "term-active");

    const formData = new FormData();
    formData.append("project", selectedFile);

    // Indeterminate progress animation while the single synchronous
    // request is in flight (serverless functions return one full
    // response rather than being polled for incremental status).
    let pct = 6;
    const pulse = setInterval(() => {
        pct = Math.min(pct + Math.random() * 6, 92);
        progressFill.style.width = `${pct}%`;
    }, 500);

    try {
        const res = await fetch("/api/scan", { method: "POST", body: formData });
        const data = await res.json();
        clearInterval(pulse);

        if (data.error) {
            appendLog(`✗ ${data.error}`, "term-found");
            progressFill.style.width = "0%";
            return;
        }

        progressFill.style.width = "100%";
        progressLabel.textContent = `${data.done} / ${data.total}`;
        appendLog(`✓ scanned ${data.done} file(s)`, "term-active");
        appendLog(`> scan complete — ${data.findings.length} finding(s)`, "term-found");
        setTimeout(() => renderResults(data.findings), 500);
    } catch (err) {
        clearInterval(pulse);
        appendLog(`✗ could not reach server: ${err}`, "term-found");
    }
});

function appendLog(text, cls = "term-active") {
    const line = document.createElement("div");
    line.className = `term-line ${cls}`;
    line.textContent = text;
    terminalLog.appendChild(line);
    terminalLog.scrollTop = terminalLog.scrollHeight;
}

function renderResults(findings) {
    scanView.classList.add("hidden");
    resultsView.classList.remove("hidden");

    const counts = {};
    SEV_ORDER.forEach((s) => (counts[s] = 0));
    findings.forEach((f) => {
        const sev = SEV_ORDER.includes(f.severity) ? f.severity : "Info";
        counts[sev] = (counts[sev] || 0) + 1;
    });

    summaryCards.innerHTML = SEV_ORDER.map(
        (sev) => `
        <div class="summary-card" style="border-top-color:${SEV_COLORS[sev]}">
            <div class="count">${counts[sev]}</div>
            <div class="label">${sev}</div>
        </div>`
    ).join("");

    const sorted = [...findings].sort(
        (a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity)
    );

    if (sorted.length === 0) {
        findingsList.innerHTML = `<div class="finding">No vulnerabilities found. Clean scan.</div>`;
        return;
    }

    findingsList.innerHTML = sorted
        .map((f, i) => {
            const color = SEV_COLORS[f.severity] || SEV_COLORS.Info;
            return `
            <div class="finding">
                <div class="finding-top">
                    <span class="sev-badge" style="background:${color}">${f.severity || "Info"}</span>
                    <span class="finding-title">${i + 1}. ${escapeHtml(f.title || "Unknown")}</span>
                    ${f.cwe ? `<span class="cwe-tag">${escapeHtml(f.cwe)}</span>` : ""}
                </div>
                <div class="finding-meta">${escapeHtml(f.file || "")} : line ${f.line ?? "?"}</div>
                <div class="finding-explanation">${escapeHtml(f.explanation || "")}</div>
                ${f.vulnerable_code ? `<div class="finding-code">${escapeHtml(f.vulnerable_code)}</div>` : ""}
                ${f.remediation ? `<div class="finding-fix"><strong>Fix:</strong> ${escapeHtml(f.remediation)}</div>` : ""}
            </div>`;
        })
        .join("");
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

scanAgainBtn.addEventListener("click", () => {
    resultsView.classList.add("hidden");
    uploadView.classList.remove("hidden");
    selectedFile = null;
    fileInput.value = "";
    dzText.innerHTML = `drop_project.zip <span class="dz-sub">or click to browse</span>`;
    scanBtn.disabled = true;
});
