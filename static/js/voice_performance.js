Chart.register(ChartDataLabels);

let state={
    filters:null,rows:[],selectedCampaigns:new Set(),
    charts:{general:null,hour:null,matrix:null,wins:null,campBar:null,campHour:null}
};
const palette=["#000049","#FB5C28","#345F99","#1D9A63","#7A4EAB","#D49A20","#C43D6A","#4A8897"];
const byId=id=>document.getElementById(id);
const fmtInt=n=>Number(n||0).toLocaleString("pt-BR");
const fmtPct=n=>`${Number(n||0).toFixed(2).replace(".",",")}%`;
const rateClass=v=>Number(v)===0?"rate-zero":Number(v)>=12?"rate-good":"rate-mid";
const medalForRank=r=>r===1?"🥇":r===2?"🥈":r===3?"🥉":"";
const badgeClass=r=>r===1?"gold":r===2?"silver":r===3?"bronze":"";

function showToast(msg,error=false){const e=byId("toast");e.textContent=msg;e.classList.toggle("error",error);e.classList.add("show");setTimeout(()=>e.classList.remove("show"),2800)}

async function loadFilters(){
    const r=await fetch("/cliente/voice-performance/painel/api/filters");
    state.filters=await r.json();
    const d=byId("dateFilter");
    const t=byId("tenantFilter");
    if(!d.value){
        const latest=(state.filters.dates||[])[0];
        d.value=latest || new Date().toISOString().slice(0,10);
    }
    t.innerHTML="";
    (state.filters.tenants||[]).forEach(x=>{
        const o=document.createElement("option");
        o.value=x;o.textContent=x;t.appendChild(o);
    });
    if(state.filters.control?.last_refresh_local){
        byId("lastRefresh").textContent=state.filters.control.last_refresh_local;
    }
    updateLegacyNote();
    await refreshScopeFilters();
}

async function refreshScopeFilters(){
    const selectedDate=byId("dateFilter").value;
    const all=await fetch(`/cliente/voice-performance/painel/api/data?date=${encodeURIComponent(selectedDate)}`);
    const payload=await all.json();
    const rows=payload.rows||[];
    const tenants=[...new Set(rows.map(r=>String(r.tenant)))].sort();
    const tenantSel=byId("tenantFilter");
    const previousTenant=tenantSel.value;
    tenantSel.innerHTML="";
    tenants.forEach(x=>{const o=document.createElement("option");o.value=x;o.textContent=x;tenantSel.appendChild(o)});
    if(tenants.includes(previousTenant))tenantSel.value=previousTenant;
    state.filters.tenants=tenants;
    state.filters.campaigns={};
    tenants.forEach(tenant=>{
        state.filters.campaigns[tenant]=[...new Set(rows.filter(r=>String(r.tenant)===tenant).map(r=>String(r.campaign)))].sort();
    });
    state.selectedCampaigns.clear();
    buildCampaignPills();
}

function updateLegacyNote(){
    const d=byId("dateFilter").value;
    const note=byId("legacyNote");
    if(!note)return;
    note.classList.toggle("hidden", !(d && d < "2026-09-03"));
}

function buildCampaignPills(){
    const tenant=byId("tenantFilter").value,list=state.filters?.campaigns?.[tenant]||[],wrap=byId("campaignFilters");wrap.innerHTML="";
    if(state.selectedCampaigns.size===0)list.forEach(c=>state.selectedCampaigns.add(c));
    else{
        state.selectedCampaigns=new Set([...state.selectedCampaigns].filter(c=>list.includes(c)));
        if(state.selectedCampaigns.size===0)list.forEach(c=>state.selectedCampaigns.add(c));
    }
    list.forEach(c=>{const b=document.createElement("button");b.className="pill"+(state.selectedCampaigns.has(c)?" active":"");b.textContent=c;b.onclick=()=>{if(state.selectedCampaigns.has(c)){if(state.selectedCampaigns.size>1)state.selectedCampaigns.delete(c)}else state.selectedCampaigns.add(c);buildCampaignPills();loadData()};wrap.appendChild(b)});
    ["matrixCampaign"].forEach(id=>{
        const sel=byId(id);sel.innerHTML="";
        [...state.selectedCampaigns].sort().forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=`Campanha ${c}`;sel.appendChild(o)});
    });
}

async function loadData(){
    const p=new URLSearchParams({date:byId("dateFilter").value,tenant:byId("tenantFilter").value});
    [...state.selectedCampaigns].forEach(c=>p.append("campaign",c));
    const r=await fetch(`/cliente/voice-performance/painel/api/data?${p.toString()}`),data=await r.json();state.rows=data.rows||[];
    updateGlobalKpis(data.kpis||{});renderAll();
    if(data.control?.last_refresh_local)byId("lastRefresh").textContent=data.control.last_refresh_local;
}

function updateGlobalKpis(k){
    byId("kpiFeedbacks").textContent=fmtInt(k.feedbacks);byId("kpiSuccesses").textContent=fmtInt(k.sucessos);byId("kpiRate").textContent=fmtPct(k.taxa);
    byId("kpiVoices").textContent=k.vozes||0;byId("kpiCampaigns").textContent=k.campanhas||0;byId("heroFeedback").textContent=fmtInt(k.feedbacks);
}

function aggCampaignHour(){
    const m={};state.rows.forEach(r=>{const k=`${r.campaign}|${r.hora}`;if(!m[k])m[k]={campaign:String(r.campaign),hora:+r.hora,f:0,s:0};m[k].f+=+r.feedbacks;m[k].s+=+r.sucessos});
    return Object.values(m).map(x=>({...x,taxa:x.f?x.s/x.f*100:0}));
}
function chartOptions(labels=true){
    return {responsive:true,maintainAspectRatio:false,animation:{duration:900,easing:"easeOutQuart"},interaction:{mode:"index",intersect:false},plugins:{legend:{position:"top",labels:{usePointStyle:true,boxWidth:8}},datalabels:{display:labels,formatter:v=>fmtPct(v),color:"#000049",backgroundColor:"rgba(255,255,255,.90)",borderRadius:5,padding:3,font:{size:9,weight:"800"},anchor:"end",align:"top",offset:4,clamp:true}},scales:{y:{beginAtZero:true,ticks:{callback:v=>`${v}%`},grid:{color:"#EEF0F4"}},x:{grid:{display:false}}}};
}
function renderLine(canvasId,storeKey,data,labelKey="campaign"){
    const hours=[...new Set(data.map(x=>x.hora))].sort((a,b)=>a-b),series=[...new Set(data.map(x=>x[labelKey]))].sort();
    const datasets=series.map((s,i)=>({label:s,data:hours.map(h=>{const x=data.find(v=>String(v[labelKey])===String(s)&&v.hora===h);return x?+x.taxa.toFixed(2):null}),borderColor:palette[i%palette.length],backgroundColor:palette[i%palette.length],borderWidth:3,pointRadius:5,pointHoverRadius:7,tension:.36,spanGaps:true}));
    if(state.charts[storeKey])state.charts[storeKey].destroy();
    state.charts[storeKey]=new Chart(byId(canvasId),{type:"line",data:{labels:hours.map(h=>`${h}h`),datasets},options:chartOptions(true)});
}

function renderGeneral(){
    const data=aggCampaignHour();renderLine("generalCampaignChart","general",data);
    const agg={};state.rows.forEach(r=>{const c=String(r.campaign);if(!agg[c])agg[c]={f:0,s:0};agg[c].f+=+r.feedbacks;agg[c].s+=+r.sucessos});
    const rows=Object.entries(agg).map(([c,x])=>({c,f:x.f,s:x.s,t:x.f?x.s/x.f*100:0})).sort((a,b)=>b.t-a.t),max=Math.max(...rows.map(x=>x.t),1);
    byId("generalSummary").innerHTML=rows.map(x=>`<div class="summary-row ${x.t===0?"zero":""}"><div class="campaign">${x.c}</div><div><div class="bar"><span style="width:${Math.max(2,x.t/max*100)}%"></span></div><small>${fmtInt(x.f)} feedbacks</small></div><strong>${fmtPct(x.t)}</strong></div>`).join("");
}

function renderGeneralHourVoice(){
    const agg={};
    state.rows.forEach(r=>{const key=`${r.hora}|${r.voz}`;if(!agg[key])agg[key]={hora:+r.hora,voz:r.voz,feedbacks:0,sucessos:0};agg[key].feedbacks+=Number(r.feedbacks);agg[key].sucessos+=Number(r.sucessos)});
    const data=Object.values(agg).map(x=>({...x,taxa:x.feedbacks?x.sucessos/x.feedbacks*100:0}));
    const hours=[...new Set(data.map(x=>x.hora))].sort((a,b)=>a-b);
    let html="";
    hours.forEach(h=>{
        const hourRows=data.filter(x=>x.hora===h).sort((a,b)=>b.taxa-a.taxa);
        html+=`<div class="hour-voice-card"><div class="hour-voice-card-head"><strong>${h}h</strong><span>${fmtInt(hourRows.reduce((a,x)=>a+x.feedbacks,0))} feedbacks</span></div><div class="hour-voice-items">${hourRows.map((x,i)=>`<div class="hour-voice-item ${i===0?"top-voice":""}"><div class="hour-voice-name">${i===0?'<span class="mini-medal">🥇</span>':""}<span>${x.voz}</span></div><strong class="${rateClass(x.taxa)}">${fmtPct(x.taxa)}</strong></div>`).join("")}</div></div>`;
    });
    byId("generalHourVoiceGrid").innerHTML=html || "<p>Sem dados.</p>";
}

function renderGeneralMedals(){
    const groups={};state.rows.forEach(r=>{const h=+r.hora;if(!groups[h])groups[h]=[];groups[h].push(r)});
    const html=Object.keys(groups).map(Number).sort((a,b)=>a-b).map(h=>{
        const top=groups[h].slice().sort((a,b)=>+a.ranking_hora-+b.ranking_hora||+b.taxa_sucesso_pct-+a.taxa_sucesso_pct||+b.feedbacks-+a.feedbacks)[0];
        if(!top)return "";
        return `<div class="medal-item medal-live-item"><div class="medal-icon">🥇</div><div><div class="medal-hour">${h}H</div><div class="medal-voice">${top.voz}<small>• Camp. ${top.campaign}</small></div></div><div class="medal-rate">${fmtPct(top.taxa_sucesso_pct)}</div></div>`;
    }).join("");
    byId("generalHourMedals").innerHTML=html || "<p>Sem dados.</p>";
}

function renderMatrix(){
    const camp=byId("matrixCampaign").value||[...state.selectedCampaigns][0];
    const rows=state.rows.filter(r=>String(r.campaign)===String(camp));
    const voices=[...new Set(rows.map(r=>r.voz))].sort();
    const hours=[...new Set(rows.map(r=>+r.hora))].sort((a,b)=>a-b);
    const max=Math.max(...rows.map(r=>+r.taxa_sucesso_pct),1);
    const heatColor=v=>{if(v===null)return "#F3F4F7";if(v===0)return "#FDE7E3";if(v/max>.75)return "#A8C5E7";if(v/max>.5)return "#D6E4F4";if(v/max>.25)return "#FFE5CC";return "#FFF1E5"};
    const voiceExtremes={};
    voices.forEach(v=>{
        const voiceRows=rows.filter(r=>r.voz===v).map(r=>({hora:+r.hora,taxa:+r.taxa_sucesso_pct}));
        if(!voiceRows.length){voiceExtremes[v]={best:null,worst:null};return}
        const maxTaxa=Math.max(...voiceRows.map(x=>x.taxa));
        const minTaxa=Math.min(...voiceRows.map(x=>x.taxa));
        if(maxTaxa===minTaxa)voiceExtremes[v]={best:null,worst:null};
        else voiceExtremes[v]={best:voiceRows.find(x=>x.taxa===maxTaxa)?.hora??null,worst:voiceRows.find(x=>x.taxa===minTaxa)?.hora??null};
    });
    let html='<table class="heat-table"><thead><tr><th>Voz</th>';
    html+=hours.map(h=>`<th>${h}h</th>`).join("");
    html+='<th class="heat-summary-head">Melhor</th><th class="heat-summary-head">Pior</th></tr></thead><tbody>';
    voices.forEach(v=>{
        const ext=voiceExtremes[v];html+=`<tr><td class="heat-voice">${v}</td>`;
        html+=hours.map(h=>{const x=rows.find(r=>r.voz===v&&+r.hora===h);const val=x?+x.taxa_sucesso_pct:null;let cls="",badge="";if(ext.best===h){cls=" heat-best-blink";badge='<span class="cell-status best-cell-dot"></span>'}else if(ext.worst===h){cls=" heat-worst-blink";badge='<span class="cell-status worst-cell-dot"></span>'}return `<td class="${cls}" style="background:${heatColor(val)}">${badge}${val===null?"—":fmtPct(val)}</td>`}).join("");
        const bestRow=ext.best!==null?rows.find(r=>r.voz===v&&+r.hora===ext.best):null;
        const worstRow=ext.worst!==null?rows.find(r=>r.voz===v&&+r.hora===ext.worst):null;
        html+=`<td class="heat-summary best-summary">${bestRow?`${ext.best}h • ${fmtPct(bestRow.taxa_sucesso_pct)}`:"Estável"}</td><td class="heat-summary worst-summary">${worstRow?`${ext.worst}h • ${fmtPct(worstRow.taxa_sucesso_pct)}`:"Estável"}</td></tr>`;
    });
    byId("heatmap").innerHTML=html+"</tbody></table>";
    const data=[];voices.forEach(v=>hours.forEach(h=>{const x=rows.find(r=>r.voz===v&&+r.hora===h);if(x)data.push({voz:v,hora:h,taxa:+x.taxa_sucesso_pct})}));
    const datasets=voices.map((v,i)=>({label:v,data:hours.map(h=>{const x=data.find(d=>d.voz===v&&d.hora===h);return x?x.taxa:null}),borderColor:palette[i%palette.length],backgroundColor:palette[i%palette.length],borderWidth:2.5,pointRadius:4,tension:.34,spanGaps:true}));
    if(state.charts.matrix)state.charts.matrix.destroy();
    state.charts.matrix=new Chart(byId("matrixVoiceChart"),{type:"line",data:{labels:hours.map(h=>`${h}h`),datasets},options:chartOptions(true)});
    const analysis=voices.map(v=>{const vr=rows.filter(r=>r.voz===v);const f=vr.reduce((a,x)=>a+Number(x.feedbacks),0);const s=vr.reduce((a,x)=>a+Number(x.sucessos),0);const t=f?s/f*100:0;const wins=vr.filter(x=>+x.ranking_hora===1).length;const ext=voiceExtremes[v];return{v,f,s,t,wins,best:ext.best,worst:ext.worst}}).sort((a,b)=>b.t-a.t);
    byId("voiceAnalysis").innerHTML=analysis.map(x=>`<div class="voice-row extended"><div><strong>${x.v}</strong><small>${x.wins}x Top 1</small></div><div class="voice-rate">${fmtPct(x.t)}</div><div class="voice-extreme-mini"><span class="mini-best">▲ ${x.best!==null?`${x.best}h`:"-"}</span><span class="mini-worst">▼ ${x.worst!==null?`${x.worst}h`:"-"}</span></div></div>`).join("");
}

function renderRanking(){
    const byVoice={};state.rows.forEach(r=>{if(!byVoice[r.voz])byVoice[r.voz]={f:0,s:0,w:0};byVoice[r.voz].f+=+r.feedbacks;byVoice[r.voz].s+=+r.sucessos;if(+r.ranking_hora===1)byVoice[r.voz].w++});
    const rank=Object.entries(byVoice).map(([v,x])=>({v,...x,t:x.f?x.s/x.f*100:0})).sort((a,b)=>b.t-a.t);
    const top=rank.slice(0,3),order=[top[1],top[0],top[2]];
    byId("podium").innerHTML=order.map((x,i)=>{if(!x)return"";const cls=i===1?"first":i===0?"second":"third",med=i===1?"🥇":i===0?"🥈":"🥉";return `<div class="podium-card ${cls}"><div class="podium-medal">${med}</div><h3>${x.v}</h3><div class="pod-rate">${fmtPct(x.t)}</div><small>${fmtInt(x.f)} feedbacks • ${x.w} vitórias</small></div>`}).join("");
    byId("rankingTable").innerHTML=`<table class="data-table"><thead><tr><th>Posição</th><th>Voz</th><th>Feedbacks</th><th>Sucessos</th><th>Vitórias</th><th>Taxa</th></tr></thead><tbody>${rank.map((x,i)=>`<tr><td><span class="rank-badge ${badgeClass(i+1)}">${medalForRank(i+1)||i+1}</span></td><td><strong>${x.v}</strong></td><td>${fmtInt(x.f)}</td><td>${fmtInt(x.s)}</td><td>${x.w}</td><td class="${rateClass(x.t)}">${fmtPct(x.t)}</td></tr>`).join("")}</tbody></table>`;
    if(state.charts.wins)state.charts.wins.destroy();
    state.charts.wins=new Chart(byId("winsChart"),{type:"bar",data:{labels:rank.map(x=>x.v),datasets:[{label:"Top 1",data:rank.map(x=>x.w),backgroundColor:rank.map((_,i)=>palette[i%palette.length]),borderRadius:8}]},options:{responsive:true,maintainAspectRatio:false,animation:{duration:900},plugins:{legend:{display:false},datalabels:{display:true,anchor:"end",align:"top",color:"#000049",font:{weight:"800"}}},scales:{y:{beginAtZero:true,grid:{color:"#EEF0F4"}},x:{grid:{display:false}}}}});
}

function renderAll(){renderGeneral();renderGeneralHourVoice();renderGeneralMedals();renderMatrix();renderRanking()}

async function refreshCache(){
    const btn=byId("refreshBtn");btn.disabled=true;btn.innerHTML="↻ Atualizando...";
    try{const date=byId("dateFilter").value;const r=await fetch("/cliente/voice-performance/painel/api/refresh",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({date})});const d=await r.json();if(!r.ok)throw new Error(d.message||"Erro ao atualizar");showToast(`${d.rows} linhas atualizadas no cache.`);await refreshScopeFilters();await loadData()}catch(e){showToast(e.message,true)}finally{btn.disabled=false;btn.innerHTML="↻ Carregar / Atualizar data"}
}

document.addEventListener("DOMContentLoaded",async()=>{
    await loadFilters();await loadData();
    document.querySelectorAll(".tab-btn").forEach(btn=>btn.addEventListener("click",()=>{
        document.querySelectorAll(".tab-btn").forEach(x=>x.classList.remove("active"));btn.classList.add("active");
        document.querySelectorAll(".tab-page").forEach(x=>x.classList.remove("active"));byId(`tab-${btn.dataset.tab}`).classList.add("active");
        setTimeout(()=>Object.values(state.charts).forEach(c=>c?.resize()),80);
    }));
    byId("dateFilter").addEventListener("change",async()=>{updateLegacyNote();await refreshScopeFilters();await loadData()});
    byId("tenantFilter").addEventListener("change",()=>{state.selectedCampaigns.clear();buildCampaignPills();loadData()});
    byId("matrixCampaign").addEventListener("change",renderMatrix);
    byId("refreshBtn").addEventListener("click",refreshCache);
});
