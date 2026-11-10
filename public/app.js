'use strict';

(() => {
  const cards = Array.from(document.querySelectorAll('.scene-card'));
  const dialog = document.querySelector('#image-viewer');
  const jumpSelect = document.querySelector('#scene-select');
  const previousButton = document.querySelector('#previous-scene');
  const nextButton = document.querySelector('#next-scene');
  const image = document.querySelector('#viewer-image');
  let activeIndex = 0;
  let opener = null;

  function displayScene(index) {
    if (index < 0 || index >= cards.length) return;
    activeIndex = index;
    const card = cards[index];
    const title = card.querySelector('h3').textContent;
    const link = card.querySelector('.scene-image-link');
    const download = card.querySelector('.download-link');
    document.querySelector('#viewer-title').textContent = title;
    document.querySelector('#viewer-counter').textContent = `CENA ${index + 1} DE ${cards.length}`;
    document.querySelector('#viewer-page').textContent = `Página ${card.dataset.page} do livro`;
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    image.width = Number(card.dataset.width);
    image.height = Number(card.dataset.height);
    const viewerDownload = document.querySelector('#viewer-download');
    viewerDownload.href = download.href;
    viewerDownload.download = download.download;
    document.querySelector('#viewer-original').href = download.href;
    previousButton.disabled = index === 0;
    nextButton.disabled = index === cards.length - 1;
    // Avoid leaving focus on a button when it becomes disabled at the ends.
    if (document.activeElement === previousButton && previousButton.disabled) nextButton.focus();
    if (document.activeElement === nextButton && nextButton.disabled) previousButton.focus();
  }

  cards.forEach((card, index) => {
    card.querySelector('.scene-image-link').addEventListener('click', (event) => {
      // Preserve regular link behaviour for new tabs and browsers without dialog.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || typeof dialog.showModal !== 'function') return;
      event.preventDefault();
      opener = event.currentTarget;
      displayScene(index);
      dialog.showModal();
      document.body.classList.add('modal-open');
    });
  });

  document.querySelector('.close-viewer').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('modal-open');
    if (opener) opener.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); displayScene(activeIndex - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); displayScene(activeIndex + 1); }
  });
  previousButton.addEventListener('click', () => displayScene(activeIndex - 1));
  nextButton.addEventListener('click', () => displayScene(activeIndex + 1));

  jumpSelect.addEventListener('change', () => {
    const target = document.getElementById(jumpSelect.value);
    if (!target) return;
    target.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    target.querySelector('.scene-image-link').focus({ preventScroll: true });
  });

  const shareButton = document.querySelector('#share-page');
  const shareStatus = document.querySelector('#share-status');
  if (shareButton && shareStatus) {
    const canonicalUrl = document.querySelector('link[rel="canonical"]')?.href || window.location.href;
    const shareData = {
      title: document.title,
      text: 'Uma história de Natal para ler, imaginar, colorir e criar memórias em família.',
      url: canonicalUrl,
    };

    async function copyPageLink() {
      try {
        await navigator.clipboard.writeText(canonicalUrl);
        shareStatus.textContent = 'Link copiado. Agora você pode enviá-lo para quem quiser.';
      } catch {
        window.prompt('Copie o link para compartilhar esta página:', canonicalUrl);
        shareStatus.textContent = 'Você pode copiar o link e enviá-lo a alguém especial.';
      }
    }

    shareButton.addEventListener('click', async () => {
      shareStatus.textContent = '';
      if (typeof navigator.share === 'function') {
        try {
          await navigator.share(shareData);
          return;
        } catch (error) {
          if (error?.name === 'AbortError') return;
        }
      }
      await copyPageLink();
    });
  }
})();
