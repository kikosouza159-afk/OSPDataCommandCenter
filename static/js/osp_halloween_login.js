(() => {
  'use strict';
  const visual = document.querySelector('.login-visual');
  if (!visual) return;
  document.body.classList.add('osp-halloween');
  const bat = '<svg viewBox="0 0 120 55" aria-hidden="true"><path fill="currentColor" d="M60 18c-7-13-14-15-22-12l5 12C30 8 16 9 0 5c5 10 8 20 9 29 13-5 26-3 35 6 3-13 11-16 16-17 5 1 13 4 16 17 9-9 22-11 35-6 1-9 4-19 9-29-16 4-30 3-43 13l5-12c-8-3-15-1-22 12z"/></svg>';
  const ghost = '<svg viewBox="0 0 80 100" aria-hidden="true"><defs><linearGradient id="osp-ghost-grad" x2="0" y2="1"><stop stop-color="#fff" stop-opacity=".96"/><stop offset="1" stop-color="#99d9ff" stop-opacity=".35"/></linearGradient></defs><path d="M10 43C10 17 24 6 40 6s30 11 30 37v47L57 80 45 91 31 80 19 91 10 83Z" fill="url(#osp-ghost-grad)"/><ellipse cx="30" cy="45" rx="5" ry="8" fill="#142642"/><ellipse cx="50" cy="45" rx="5" ry="8" fill="#142642"/><ellipse cx="40" cy="65" rx="4" ry="6" fill="#294264"/></svg>';
  const layer = document.createElement('div');
  layer.className = 'halloween-layer';
  layer.setAttribute('aria-hidden', 'true');
  layer.innerHTML = '<div class="halloween-moon"></div><div class="halloween-fog"></div>';
  for (let i = 0; i < 7; i++) {
    const b = document.createElement('div'); b.className = 'halloween-bat';
    b.style.setProperty('--top', (8 + (i * 13) % 66) + '%');
    b.style.setProperty('--size', (37 + i * 7) + 'px');
    b.style.setProperty('--duration', (13 + i * 3) + 's');
    b.style.setProperty('--delay', (-i * 4) + 's');
    b.innerHTML = bat; layer.appendChild(b);
  }
  for (let i = 0; i < 3; i++) {
    const g = document.createElement('div'); g.className = 'halloween-ghost';
    g.style.setProperty('--left', [ '9%', '46%', '75%' ][i]);
    g.style.setProperty('--top', [ '48%', '22%', '65%' ][i]);
    g.style.setProperty('--size', (45 + i * 11) + 'px');
    g.style.setProperty('--duration', (15 + i * 4) + 's');
    g.style.setProperty('--delay', (-i * 6) + 's');
    g.innerHTML = ghost.replace('osp-ghost-grad', 'osp-ghost-grad-' + i).replace('osp-ghost-grad', 'osp-ghost-grad-' + i);
    layer.appendChild(g);
  }
  visual.insertAdjacentHTML('beforeend', '<div class="halloween-caption">OSP · Intelligence Lab</div><div class="halloween-ui" aria-label="Indicadores ilustrativos"><div class="halloween-kpi"><div class="kpi-label">Performance · demonstração</div><div class="kpi-value">87% <span>↗ +24,8%</span></div><svg viewBox="0 0 180 70" aria-hidden="true"><polyline points="0,60 28,41 50,48 80,19 107,35 142,8 180,14"/></svg></div><div class="halloween-kpi-row"><div class="halloween-kpi"><div class="kpi-label">Projetos</div><div class="kpi-value">86 <span>↗</span></div></div><div class="halloween-kpi"><div class="kpi-label">Estratégia</div><div class="kpi-value">OSP <span>●</span></div></div></div></div><div class="halloween-season">🎃 HALLOWEEN EDITION</div>');
  document.body.appendChild(layer);
})();