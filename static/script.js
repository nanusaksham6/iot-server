let vibChartInstance = null;
let fftChartInstance = null;
let currentAsset = "motor_01";
let currentModel = "gradient_boosting";

// 🔄 SECURE HIGH-SPEED PANEL ROUTING MECHANISM
function switchScadaActiveTab(targetTab) {
    document.getElementById('btnNavCore').classList.remove('active');
    document.getElementById('btnNavTelemetry').classList.remove('active');
    document.getElementById('btnNavFFT').classList.remove('active');
    document.getElementById('btnNavAI').classList.remove('active');

    document.getElementById('panelViewCore').classList.remove('active-panel');
    document.getElementById('panelViewTelemetry').classList.remove('active-panel');
    document.getElementById('panelViewFFT').classList.remove('active-panel');
    document.getElementById('panelViewAI').classList.remove('active-panel');

    if (targetTab === 'core') {
        document.getElementById('btnNavCore').classList.add('active');
        document.getElementById('panelViewCore').classList.add('active-panel');
    } else if (targetTab === 'telemetry') {
        document.getElementById('btnNavTelemetry').classList.add('active');
        document.getElementById('panelViewTelemetry').classList.add('active-panel');
    } else if (targetTab === 'fft') {
        document.getElementById('btnNavFFT').classList.add('active');
        document.getElementById('panelViewFFT').classList.add('active-panel');
    } else if (targetTab === 'ai') {
        document.getElementById('btnNavAI').classList.add('active');
        document.getElementById('panelViewAI').classList.add('active-panel');
    }
}

// 🔐 ENCRYPTED AUTH PIPELINE INTERACTION
function executeSystemAuthGate() {
    const emailInput = document.getElementById('txtGateEmail').value;
    const passwordInput = document.getElementById('txtGatePassword').value;

    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailInput, password: passwordInput })
    })
    .then(res => {
        if (!res.ok) throw new Error("Invalid master authorization credential bounds");
        return res.json();
    })
    .then(() => { window.location.reload(); })
    .catch(err => alert(err.message));
}

function executeSystemLogout() {
    if (confirm("Confirm decoupling of centralized monitoring node sessions?")) {
        fetch('/api/auth/logout', { method: 'POST' }).then(() => { window.location.reload(); });
    }
}

function initializeScadaCharts() {
    const ctxVib = document.getElementById('vibrationChart');
    if (!ctxVib) return;

    vibChartInstance = new Chart(ctxVib.getContext('2d'), {
        type: 'line',
        data: {
            labels: Array.from({length: 15}, (_, i) => i),
            datasets: [{
                borderColor: '#00ff87',
                borderWidth: 2,
                backgroundColor: 'rgba(0, 255, 135, 0.02)',
                data: Array(15).fill(0),
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748b' } },
                x: { grid: { display: false }, ticks: { color: '#64748b' } }
            }
        }
    });

    const ctxFft = document.getElementById('fftChart').getContext('2d');
    fftChartInstance = new Chart(ctxFft, {
        type: 'bar',
        data: {
            labels: ['1X', '2X', '3X', '4X', '5X', '6X', '7X', '8X', '9X', '10X'],
            datasets: [{ backgroundColor: '#0066ff', data: Array(10).fill(0) }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748b' } },
                x: { grid: { display: false }, ticks: { color: '#64748b' } }
            }
        }
    });
}

function switchMachineAsset(assetName) {
    currentAsset = assetName;
    document.getElementById('activeModelLabel').innerText = `PROCESSING FIELD BUS DATA NODES (${assetName.toUpperCase()})`;
    document.getElementById('sensorTable').innerHTML = '';
    document.getElementById('isolatedSensorTable').innerHTML = '';
}

function switchMLModel(modelName) {
    currentModel = modelName;
    if(modelName === "linear_regression") {
        document.getElementById('lblModelAlgo').innerText = "LinearRegression()";
        document.getElementById('lblModelMSE').innerText = "28.4";
    } else {
        document.getElementById('lblModelAlgo').innerText = "GradientBoostingRegressor()";
        document.getElementById('lblModelMSE').innerText = "14.2";
    }
}

function fetchPipelineStream() {
    if (!document.getElementById('vibrationChart')) return;

    fetch(`/api/telemetry?asset=${currentAsset}`)
        .then(res => {
            if(res.status === 403) { window.location.reload(); return; }
            return res.json();
        })
        .then(data => {
            if(!data) return;
            document.getElementById('temperature').innerText = data.temperature + " °C";
            document.getElementById('rpm').innerText = data.rpm + " RPM";
            document.getElementById('vibration').innerText = data.vibration + " mm/s";
            document.getElementById('healthPercent').innerText = data.health + "%";
            document.getElementById('lblConfidence').innerText = data.confidence + "%";
            document.getElementById('confidenceBar').style.width = data.confidence + "%";
            document.getElementById('lblRULValue').innerText = data.rul + " Hrs";
            document.getElementById('peakFreqBadge').innerText = "Peak: " + data.peak_freq + " Hz";

            document.getElementById('aiViewAlgo').innerText = currentModel === "linear_regression" ? "LinearRegression" : "GradientBoostingRegressor";
            document.getElementById('aiViewConfidence').innerText = data.confidence + "%";
            document.getElementById('aiViewRUL').innerText = data.rul + " Hrs";

            const gauge = document.getElementById('gaugeFillRing');
            gauge.setAttribute('stroke-dasharray', `${data.health}, 100`);

            const statusText = document.getElementById('statusText');
            const guard1Pill = document.getElementById('guard1Pill');
            const guard2Pill = document.getElementById('guard2Pill');

            // 🚨 HIGH FIDELITY SIDEBAR ALERT MATRIX INTEGRATION
            const sbHeader = document.getElementById('sidebarAlertHeader');
            const sbTitle = document.getElementById('lblSidebarAlertTitle');
            const sbBody = document.getElementById('lblSidebarAlertBody');
            const alertBox = document.querySelector('.sidebar-alert-box');

            if(data.status === "Normal") {
                statusText.innerText = "Healthy";
                statusText.className = "kpi-value txt-green";
                gauge.className = "circle-fill-path color-green";
                document.getElementById('guard1Icon').className = "dot-check-circle pass";
                document.getElementById('guard2Icon').className = "dot-check-circle pass";
                guard1Pill.className = "status-pill pass"; guard1Pill.innerText = "Normal";
                guard2Pill.className = "status-pill pass"; guard2Pill.innerText = "Normal";

                sbHeader.style.color = "var(--neon-green)";
                sbTitle.innerText = "AI Guard: NOMINAL";
                sbBody.innerText = `Node ${currentAsset.toUpperCase()} processing safely at ${data.temperature}°C. Operational matrix stable.`;
                alertBox.style.borderColor = "rgba(0, 255, 135, 0.1)";
                alertBox.style.background = "rgba(0, 255, 135, 0.01)";
            } else {
                statusText.innerText = "Critical Fault";
                statusText.className = "kpi-value txt-red";
                gauge.className = "circle-fill-path color-red";
                document.getElementById('guard1Icon').className = "dot-check-circle fail";
                document.getElementById('guard2Icon').className = "dot-check-circle fail";
                guard1Pill.className = "status-pill fail"; guard1Pill.innerText = "Breached";
                guard2Pill.className = "status-pill fail"; guard2Pill.innerText = "Breached";

                sbHeader.style.color = "var(--critical-red)";
                sbTitle.innerText = "AI ALERT: BREACH";
                sbBody.innerText = `CRITICAL ANOMALY! Velocity RMS reached ${data.vibration} mm/s on ${currentAsset.toUpperCase()}. Action required!`;
                alertBox.style.borderColor = "rgba(255, 51, 51, 0.2)";
                alertBox.style.background = "rgba(255, 51, 51, 0.03)";
            }

            const table = document.getElementById('sensorTable');
            const statusClass = data.status === "Normal" ? "tbl-status-ok" : "tbl-status-alert";
            const row = `<tr><td>${data.timestamp}</td><td>${data.temperature}</td><td>${data.vibration}</td><td class="${statusClass}">${data.status}</td></tr>`;
            table.insertAdjacentHTML('afterbegin', row);

            const isoTable = document.getElementById('isolatedSensorTable');
            const isoRow = `<tr><td>FRAME_${Date.now().toString().slice(-4)}</td><td>${data.temperature} °C</td><td>${data.vibration} mm/s</td><td class="${statusClass}">${data.status.toUpperCase()}</td></tr>`;
            isoTable.insertAdjacentHTML('afterbegin', isoRow);
            if(isoTable.children.length > 20) isoTable.lastChild.remove();

            const fftGrid = document.getElementById('fftNumericalGrid');
            fftGrid.innerHTML = data.fft.map((val, idx) => `
                <div style="background:#0c1424; padding:12px; border:1px solid var(--border-subtle); border-radius:4px; display:flex; justify-content:space-between; font-size:11px; font-family:'JetBrains Mono',monospace;">
                    <span style="color:var(--text-secondary);">${idx+1}X Harmonic:</span>
                    <span style="color:var(--neon-blue); font-weight:700;">${val} dB</span>
                </div>
            `).join('');

            vibChartInstance.data.datasets[0].data.shift();
            vibChartInstance.data.datasets[0].data.push(data.vibration);
            vibChartInstance.data.datasets[0].borderColor = data.status === "Normal" ? '#00ff87' : '#ff3333';
            vibChartInstance.update();

            fftChartInstance.data.datasets[0].data = data.fft;
            fftChartInstance.data.datasets[0].backgroundColor = data.status === "Normal" ? '#0066ff' : '#ff7b00';
            fftChartInstance.update();
        })
        .catch(err => console.error("Telemetry payload error stream:", err));
}

function startScadaClock() {
    const clockNode = document.getElementById('clockTime');
    if(!clockNode) return;
    setInterval(() => {
        const d = new Date();
        document.getElementById('clockTime').innerText = d.toLocaleTimeString();
        document.getElementById('clockDate').innerText = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }, 1000);
}

window.onload = () => {
    initializeScadaCharts();
    startScadaClock();
    if (document.getElementById('vibrationChart')) {
        setInterval(fetchPipelineStream, 2000);
    }
};