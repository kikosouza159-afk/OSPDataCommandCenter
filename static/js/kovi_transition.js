(() => {
  const overlay = document.getElementById('koviTransition');
  if (!overlay) return;

  const video = overlay.querySelector('.kovi-transition__video');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const DURATION = reducedMotion.matches ? 420 : 1480;
  let navigating = false;

  function findKoviCard(){
    return Array.from(document.querySelectorAll('.client-card')).find(card => {
      const href = (card.getAttribute('href') || '').toLowerCase();
      const name = (card.dataset.name || '').toLowerCase();
      return href === '/cliente/kovi' || href.endsWith('/cliente/kovi') || name === 'kovi';
    });
  }

  function enableOptionalVideo(){
    if (!video) return false;
    const sourceUrl = (overlay.dataset.videoUrl || '').trim();
    if (!sourceUrl) return false;
    video.src = sourceUrl;
    video.muted = true;
    video.playsInline = true;
    video.preload = 'auto';
    video.addEventListener('canplaythrough', () => overlay.classList.add('video-mode'), { once:true });
    video.addEventListener('error', () => overlay.classList.remove('video-mode'), { once:true });
    video.load();
    return true;
  }

  function warmDestination(url){
    // Starts server work while the transition plays. Failure never blocks navigation.
    try { fetch(url, { credentials:'same-origin', cache:'default', redirect:'follow' }).catch(() => {}); } catch (_) {}
  }

  function startTransition(event, card){
    if (navigating) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button === 1) return;
    event.preventDefault();
    navigating = true;

    const destination = card.dataset.koviTarget || '/cliente/kovi/painel';
    overlay.classList.add('is-active');
    overlay.setAttribute('aria-hidden', 'false');
    document.documentElement.style.cursor = 'wait';
    document.body.style.pointerEvents = 'none';
    overlay.style.pointerEvents = 'all';

    if (overlay.classList.contains('video-mode') && video){
      try { video.currentTime = 0; video.play().catch(() => overlay.classList.remove('video-mode')); } catch (_) {}
    }

    warmDestination(destination);

    const fallback = window.setTimeout(() => { window.location.assign(destination); }, DURATION + 900);
    window.setTimeout(() => {
      window.clearTimeout(fallback);
      window.location.assign(destination);
    }, DURATION);
  }

  const card = findKoviCard();
  if (!card) return;
  card.dataset.koviTarget = '/cliente/kovi/painel';
  card.addEventListener('click', (event) => startTransition(event, card));
  enableOptionalVideo();
})();
