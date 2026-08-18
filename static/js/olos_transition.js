(() => {
  const overlay = document.getElementById('olosTransition');
  if (!overlay) return;

  const video = overlay.querySelector('.olos-transition__video');
  const title = overlay.querySelector('[data-transition-title]');
  const subtitle = overlay.querySelector('[data-transition-subtitle]');
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DEFAULT_DURATION = prefersReduced ? 650 : 4700;
  let busy = false;
  let timer = null;

  const sleep = ms => new Promise(resolve => window.setTimeout(resolve, ms));

  function playVideo() {
    if (!video) return;
    try {
      video.currentTime = 0;
      const p = video.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    } catch (_) {}
  }

  function setStatus(mainText, subText) {
    if (title && mainText) title.textContent = mainText;
    if (subtitle && subText) subtitle.textContent = subText;
  }

  function show(options = {}) {
    setStatus(
      options.title || 'Carregando dados...',
      options.subtitle || 'Preparando sua visão no OSP Command Center'
    );
    overlay.classList.add('is-active');
    overlay.setAttribute('aria-hidden', 'false');
    document.documentElement.style.cursor = 'wait';
    playVideo();
  }

  function hide() {
    overlay.classList.remove('is-active');
    overlay.setAttribute('aria-hidden', 'true');
    document.documentElement.style.cursor = '';
    if (video) { try { video.pause(); } catch (_) {} }
  }

  /**
   * Troca o documento usando o HTML que já foi carregado pelo fetch.
   * Isso evita uma segunda requisição ao painel depois do vídeo.
   */
  function commitPreparedPage(html, finalUrl) {
    try {
      if (finalUrl) window.history.replaceState({}, '', finalUrl);
      document.open();
      document.write(html);
      document.close();
    } catch (_) {
      window.location.assign(finalUrl || window.location.href);
    }
  }

  async function fetchPreparedPage(url, fetchOptions = {}) {
    const response = await fetch(url, {
      credentials: 'same-origin',
      cache: 'no-store',
      redirect: 'follow',
      ...fetchOptions,
      headers: {
        'X-Olos-Transition': '1',
        ...(fetchOptions.headers || {})
      }
    });
    const html = await response.text();
    return { response, html, finalUrl: response.url || url };
  }

  /**
   * Abre um cliente e, simultaneamente, busca/processa o HTML do painel.
   * A tela só troca quando o vídeo mínimo terminou E a resposta está pronta.
   */
  async function navigate(url, options = {}) {
    if (busy || !url) return;
    busy = true;
    show(options);

    const duration = Number(options.duration || DEFAULT_DURATION);
    const minimumVideoTime = sleep(duration);

    try {
      const preparedPromise = fetchPreparedPage(url);
      const [prepared] = await Promise.all([preparedPromise, minimumVideoTime]);

      if (!prepared.response.ok) {
        throw new Error(`HTTP ${prepared.response.status}`);
      }

      setStatus('Dados carregados', 'Abrindo painel...');
      await sleep(prefersReduced ? 80 : 180);
      commitPreparedPage(prepared.html, prepared.finalUrl);
    } catch (error) {
      // Se o pre-carregamento falhar, não bloqueia o usuário.
      setStatus('Finalizando carregamento...', 'Abrindo painel pelo modo compatível');
      window.setTimeout(() => window.location.assign(url), 250);
    }
  }

  /**
   * No login, a própria autenticação é feita por fetch enquanto o vídeo roda.
   * Em sucesso o servidor devolve o dashboard já renderizado, sem novo redirect.
   */
  async function submitLogin(form) {
    if (busy || !form) return;
    busy = true;

    show({
      title: 'Entrando no Cockpit...',
      subtitle: 'Validando acesso e carregando o ambiente'
    });

    const duration = Number(overlay.dataset.autoDuration || DEFAULT_DURATION);
    const body = new FormData(form);

    try {
      const preparedPromise = fetchPreparedPage(form.action || window.location.href, {
        method: (form.method || 'POST').toUpperCase(),
        body,
        headers: { 'X-Olos-Async-Transition': '1' }
      });

      const prepared = await preparedPromise;

      // Credencial inválida: mostra o erro imediatamente, sem obrigar a assistir o vídeo inteiro.
      if (prepared.response.status === 401) {
        hide();
        busy = false;
        commitPreparedPage(prepared.html, prepared.finalUrl);
        return;
      }

      if (!prepared.response.ok) throw new Error(`HTTP ${prepared.response.status}`);

      // Mantém a assinatura visual completa; o dashboard já está pronto atrás da transição.
      await sleep(duration);
      setStatus('Ambiente pronto', 'Abrindo Cockpit...');
      await sleep(prefersReduced ? 80 : 180);
      commitPreparedPage(prepared.html, prepared.finalUrl);
    } catch (_) {
      // Fallback seguro para o POST tradicional.
      hide();
      busy = false;
      form.removeAttribute('data-olos-login-form');
      form.submit();
    }
  }

  function autoStart() {
    if (overlay.dataset.autoStart !== '1') return;
    busy = true;
    show({
      title: overlay.dataset.autoTitle || 'Carregando Cockpit...',
      subtitle: overlay.dataset.autoSubtitle || 'Inicializando ambiente e preparando os clientes'
    });
    const duration = Number(overlay.dataset.autoDuration || DEFAULT_DURATION);
    timer = window.setTimeout(() => {
      hide();
      busy = false;
    }, duration);
  }

  document.querySelectorAll('[data-olos-transition-link]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.defaultPrevented) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button === 1) return;
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#')) return;
      event.preventDefault();
      const clientName = link.dataset.clientName || '';
      navigate(href, {
        title: clientName ? `Carregando dados de ${clientName}...` : 'Carregando dados...',
        subtitle: 'Buscando e processando os dados enquanto a transição é exibida'
      });
    });
  });

  document.querySelectorAll('[data-olos-login-form]').forEach(form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      submitLogin(form);
    });
  });

  window.OlosTransition = { show, hide, navigate, submitLogin };
  autoStart();
})();
