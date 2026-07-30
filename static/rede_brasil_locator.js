let hourlyChart = null;
const qs = (id) => document.getElementById(id);

function addOption(select, value, text, selected = false) {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = text;
    opt.selected = selected;
    select.appendChild(opt);
}

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
    return response.json();
}

function fillSelect(select, values, allLabel = null, preferred = null) {
    select.innerHTML = "";
    if (allLabel) addOption(select, "__all__", allLabel);
    values.forEach(v => addOption(select, v, v));
    if (preferred && values.includes(preferred)) {
        select.value = preferred;
    } else if (values.length && !allLabel) {
        select.value = values[0];
    } else if (values.length && allLabel && select.value === "") {
        select.value = "__all__";
    }
}

function keepOrResetOptions(select, values, allLabel = null) {
    const current = select.value;
    fillSelect(select, values, allLabel);
    if (current && ((allLabel && current === "__all__") || values.includes(current))) {
        select.value = current;
    } else if (!allLabel && values.length) {
        select.value = values[0];
    } else if (allLabel) {
        select.value = "__all__";
    }
}

function parseIntBR(text) {
    if (typeof text === "number") return text;
    if (!text) return 0;
    return parseInt(String(text).replace(/\./g, "").replace(/[^\d-]/g, ""), 10) || 0;
}


function metricValue(obj, key) {
    return obj && obj[key] ? obj[key] : "0";
}

function funnelHTML(title, values, theme, type) {
    const metrics = type === "locator"
        ? [
            ["MAILING", metricValue(values, "Mailing")],
            ["TENTATIVAS", metricValue(values, "Tentativas")],
            ["ATENDIDAS", metricValue(values, "Atendidas")],
            ["ATEND. ATH", metricValue(values, "Atendidas ATH")],
            ["SUCESSO NEGÓCIO", metricValue(values, "Sucesso Negócio")]
        ]
        : [
            ["MAILING", metricValue(values, "Mailing")],
            ["TENTATIVAS", metricValue(values, "Tentativas")],
            ["ATENDIDAS", metricValue(values, "Atendidas")],
            ["CPC", metricValue(values, "CPC")],
            ["ACORDO", metricValue(values, "Acordo")]
        ];

    const kpis = type === "locator"
        ? [
            ["HIT RATE", metricValue(values, "Hit Rate")],
            ["INTERAÇÃO", metricValue(values, "Sucesso Interação")],
            ["PERDA", metricValue(values, "% Perda")],
            ["ABANDONO", metricValue(values, "% Abandono")]
        ]
        : [
            ["HIT RATE", metricValue(values, "Hit Rate")],
            ["LOC", metricValue(values, "LOC")],
            ["CONVERSÃO", metricValue(values, "Conversão")],
            ["TMA", metricValue(values, "TMA")]
        ];

    return `
        <div class="ada-funnel-wrap ${theme}">
            <div class="ada-funnel-date ${theme}">${title}</div>
            <div class="ada-funnel">
                ${metrics.map(([label, value]) => `
                    <div class="ada-segment">
                        <span>${label}</span>
                        <b>${value}</b>
                    </div>
                `).join("")}
            </div>
            <div class="ada-kpi-grid">
                ${kpis.map(([label, value]) => `
                    <div class="ada-kpi">
                        <span>${label}</span>
                        <b>${value}</b>
                    </div>
                `).join("")}
            </div>
        </div>
    `;
}

function buildComparativeFunnel(locator, comparativa, selected = {}) {
    const locTitle = "LOCATOR";
    const compTitle = "COMPARATIVA";

    qs("locatorFunnelPlot").innerHTML = `
        <div class="ada-funnel-comparison">
            ${funnelHTML(locTitle, locator, "blue", "locator")}
            ${funnelHTML(compTitle, comparativa, "orange", "comparativa")}
        </div>
    `;
}

function buildVariation(rows) {
    qs("variationRows").innerHTML = rows.map(row => `
        <tr>
            <td>${row.indicador}</td>
            <td class="num">${row.locator}</td>
            <td class="num">${row.comparativa}</td>
            <td class="num"><span class="delta ${row.sinal}">${row.sinal === "up" ? "▲" : "▼"} ${row.variacao}</span></td>
        </tr>
    `).join("");
}

function buildHourlyConsolidated(data) {
    const rows = (data && data.rows) || [];
    const total = (data && data.total) || {};
    qs("hourlyConsolidatedRows").innerHTML = rows.map(row => `
        <tr>
            <td><span class="hour-chip">${row["Hora"]}h</span></td>
            <td class="num">${row["Logados"]}</td>
            <td class="num">${row["Mailing"]}</td>
            <td class="num">${row["Tentativas"]}</td>
            <td class="num">${row["Atendidas"]}</td>
            <td class="num">${row["CPC"]}</td>
            <td class="num">${row["Acordo"]}</td>
            <td class="num productivity">${row["CPC/Logados"]}</td>
            <td class="num productivity">${row["Acordo/Logados"]}</td>
            <td class="num productivity">${row["Acordo/Mailing"]}</td>
        </tr>
    `).join("");

    qs("hourlyConsolidatedTotal").innerHTML = total && total.Hora ? `
        <tr class="total-row">
            <td>${total["Hora"]}</td>
            <td class="num">${total["Logados"]}</td>
            <td class="num">${total["Mailing"]}</td>
            <td class="num">${total["Tentativas"]}</td>
            <td class="num">${total["Atendidas"]}</td>
            <td class="num">${total["CPC"]}</td>
            <td class="num">${total["Acordo"]}</td>
            <td class="num productivity">${total["CPC/Logados"]}</td>
            <td class="num productivity">${total["Acordo/Logados"]}</td>
            <td class="num productivity">${total["Acordo/Mailing"]}</td>
        </tr>
    ` : "";
}

function renderChart(hourly) {
    const ctx = qs("hourlyChart");
    if (hourlyChart) hourlyChart.destroy();

    hourlyChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: hourly.horas,
            datasets: [
                {
                    label: "Tentativas",
                    data: hourly.tentativas,
                    borderColor: "#4ea3ff",
                    backgroundColor: "rgba(78, 163, 255, 0.15)",
                    pointBackgroundColor: "#4ea3ff",
                    pointBorderColor: "#d7ebff",
                    pointRadius: 4,
                    tension: 0.35,
                    fill: true,
                    yAxisID: "y",
                },
                {
                    label: "Atendidas",
                    data: hourly.atendidas,
                    borderColor: "#FB5C28",
                    backgroundColor: "rgba(251, 92, 40, 0.08)",
                    pointBackgroundColor: "#FB5C28",
                    pointBorderColor: "#ffd7ca",
                    pointRadius: 4,
                    tension: 0.35,
                    fill: false,
                    yAxisID: "y1",
                },
                {
                    label: "Transferidas",
                    data: hourly.transferencias,
                    borderColor: "#59e169",
                    backgroundColor: "rgba(89, 225, 105, 0.10)",
                    pointBackgroundColor: "#59e169",
                    pointBorderColor: "#d6ffd9",
                    pointRadius: 4,
                    tension: 0.35,
                    fill: false,
                    yAxisID: "y1",
                },
                {
                    label: "Sucesso Negócio",
                    data: hourly.sucesso_negocio,
                    borderColor: "#ffcf57",
                    backgroundColor: "rgba(255, 207, 87, 0.22)",
                    pointBackgroundColor: "#ffcf57",
                    pointBorderColor: "#fff3c4",
                    pointRadius: 4,
                    tension: 0.35,
                    fill: false,
                    yAxisID: "y2",
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    labels: { color: "#ffffff", font: { size: 13, weight: "bold" }, usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: "rgba(0, 0, 73, .96)",
                    borderColor: "#345f99",
                    borderWidth: 1,
                    titleColor: "#ffffff",
                    bodyColor: "#ffffff",
                    padding: 12
                }
            },
            scales: {
                x: {
                    ticks: { color: "#dcebff", font: { weight: "bold" } },
                    grid: { color: "rgba(130, 180, 255, 0.10)" }
                },
                y: {
                    beginAtZero: true,
                    position: "left",
                    ticks: {
                        color: "#4ea3ff",
                        callback: value => value >= 1000 ? `${Math.round(value / 1000)}k` : value
                    },
                    grid: { color: "rgba(130, 180, 255, 0.16)" }
                },
                y1: {
                    beginAtZero: true,
                    position: "right",
                    ticks: { color: "#FB5C28" },
                    grid: { drawOnChartArea: false }
                },
                y2: {
                    beginAtZero: true,
                    position: "right",
                    offset: true,
                    ticks: { color: "#ffcf57" },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

function updateAvailableOptions(payload) {
    keepOrResetOptions(qs("filterLocator"), payload.available.locator_campaigns);
    keepOrResetOptions(qs("filterComparativa"), payload.available.comparativa_campaigns);
    qs("filterLocator").value = payload.selected.locator_campaign;
    qs("filterComparativa").value = payload.selected.comparativa_campaign;
}

async function loadData() {
    const params = new URLSearchParams({
        data: qs("filterData").value,
        locator_campaign: qs("filterLocator").value,
        comparativa_campaign: qs("filterComparativa").value,
    });

    const payload = await fetchJson(`/cliente/rede-brasil/painel/api/data?${params.toString()}`);

    updateAvailableOptions(payload);

    qs("locatorName").textContent = payload.selected.locator_campaign || "-";
    qs("compName").textContent = payload.selected.comparativa_campaign || "-";
    qs("locatorSelected").textContent = payload.selected.locator_campaign || "-";
    qs("compSelected").textContent = payload.selected.comparativa_campaign || "-";

    qs("ovAth").textContent = payload.locator["ATH médio"];
    qs("ovTentativas").textContent = payload.locator["Tentativas"];
    qs("ovAtendidas").textContent = payload.locator["Atendidas"];
    qs("ovCpc").textContent = payload.locator["Transferências"];
    qs("ovAcordo").textContent = payload.locator["Sucesso Negócio"];
    qs("ovTma").textContent = payload.locator["TMA Locator"];

    buildComparativeFunnel(payload.locator, payload.comparativa, payload.selected);

    qs("kpiHit").textContent = payload.locator["Hit Rate"];
    qs("kpiInteracao").textContent = payload.locator["Sucesso Interação"];
    qs("kpiPerda").textContent = payload.locator["% Perda"];
    qs("kpiAbandono").textContent = payload.locator["% Abandono"];
    qs("kpiSla").textContent = payload.locator["SLA"];
    qs("kpiCusto").textContent = payload.locator["Custo"];

    qs("compMailing").textContent = payload.comparativa["Mailing"];
    qs("compTentativas").textContent = payload.comparativa["Tentativas"];
    qs("compAtendidas").textContent = payload.comparativa["Atendidas"];
    qs("compCpc").textContent = payload.comparativa["CPC"];
    qs("compAcordo").textContent = payload.comparativa["Acordo"];

    buildVariation(payload.variation);
    buildHourlyConsolidated(payload.hourly_consolidated);
    renderChart(payload.hourly);
}

function startCircuitBackground() {
    const canvas = qs("circuitCanvas");
    const ctx = canvas.getContext("2d");
    let w = 0, h = 0, time = 0;
    const nodes = [];
    const particles = [];

    function resize() {
        w = canvas.width = window.innerWidth * Math.min(window.devicePixelRatio || 1, 1.5);
        h = canvas.height = window.innerHeight * Math.min(window.devicePixelRatio || 1, 1.5);
        canvas.style.width = window.innerWidth + "px";
        canvas.style.height = window.innerHeight + "px";
        nodes.length = 0;
        particles.length = 0;

        const gap = Math.max(110, Math.min(window.innerWidth, window.innerHeight) / 7);
        for (let x = 60; x < w; x += gap) {
            for (let y = 50; y < h; y += gap * 0.85) {
                if (Math.random() > 0.18) nodes.push({ x: x + (Math.random() * 22 - 11), y: y + (Math.random() * 22 - 11) });
            }
        }
        for (let i = 0; i < 18; i++) createParticle();
    }

    function createParticle() {
        const from = nodes[Math.floor(Math.random() * nodes.length)];
        const to = nodes[Math.floor(Math.random() * nodes.length)];
        particles.push({ from, to, t: Math.random(), speed: 0.002 + Math.random() * 0.003, color: Math.random() > 0.5 ? "#35d6ff" : "#FB5C28" });
    }

    function drawCircuit() {
        ctx.clearRect(0, 0, w, h);

        ctx.lineWidth = 1;
        nodes.forEach((a, i) => {
            for (let j = i + 1; j < nodes.length; j++) {
                const b = nodes[j];
                const dist = Math.hypot(a.x - b.x, a.y - b.y);
                if (dist < 155) {
                    ctx.strokeStyle = `rgba(90, 160, 255, ${0.08 - dist / 3000})`;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    if (Math.random() > 0.45) {
                        ctx.lineTo(b.x, a.y);
                        ctx.lineTo(b.x, b.y);
                    } else {
                        ctx.lineTo(b.x, b.y);
                    }
                    ctx.stroke();
                }
            }
        });

        nodes.forEach((n, idx) => {
            const pulse = 2 + Math.sin(time * 0.002 + idx) * 1.4;
            ctx.beginPath();
            ctx.fillStyle = "rgba(78, 163, 255, 0.45)";
            ctx.arc(n.x, n.y, pulse, 0, Math.PI * 2);
            ctx.fill();
        });

        particles.forEach((p) => {
            if (!p.from || !p.to) return;
            p.t += p.speed;
            if (p.t >= 1) {
                p.from = p.to;
                p.to = nodes[Math.floor(Math.random() * nodes.length)];
                p.t = 0;
            }
            const x = p.from.x + (p.to.x - p.from.x) * p.t;
            const y = p.from.y + (p.to.y - p.from.y) * p.t;
            ctx.beginPath();
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 10;
            ctx.arc(x, y, 2.4, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        time += 16;
        requestAnimationFrame(drawCircuit);
    }

    window.addEventListener("resize", resize);
    resize();
    drawCircuit();
}

async function init() {
    try {
        const options = await fetchJson("/cliente/rede-brasil/painel/api/options");

        fillSelect(qs("filterData"), options.datas, null, options.datas[options.datas.length - 1]);
        fillSelect(qs("filterLocator"), options.locator_campaigns);
        fillSelect(qs("filterComparativa"), options.comparativa_campaigns);

        const locPreferred = "ATV - ATIVO 0 - OPERACAO_LOC";
        const compPreferred = "ATV - ATIVO 0 -  OPERACAO";
        if (options.locator_campaigns.includes(locPreferred)) qs("filterLocator").value = locPreferred;
        if (options.comparativa_campaigns.includes(compPreferred)) qs("filterComparativa").value = compPreferred;

        ["filterData", "filterLocator", "filterComparativa"].forEach(id => {
            qs(id).addEventListener("change", loadData);
        });

        qs("btnReload").addEventListener("click", loadData);

        await loadData();
    } catch (error) {
        console.error(error);
        alert("Erro ao carregar o painel: " + error.message);
    }
}

init();
