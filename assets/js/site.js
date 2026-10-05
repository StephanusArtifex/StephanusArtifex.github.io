(() => {
  const toggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');

  const setNavOpen = (open) => {
    if (!toggle || !nav) return;
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  };

  if (toggle && nav) {
    toggle.addEventListener('click', () => setNavOpen(!nav.classList.contains('is-open')));

    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) setNavOpen(false);
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        setNavOpen(false);
        toggle.focus();
      }
    });

    document.addEventListener('click', (event) => {
      if (!nav.classList.contains('is-open')) return;
      if (!nav.contains(event.target) && !toggle.contains(event.target)) setNavOpen(false);
    });
  }

  const filters = document.querySelectorAll('[data-filter]');
  const cards = document.querySelectorAll('[data-project-card]');

  filters.forEach((button) => {
    button.addEventListener('click', () => {
      filters.forEach((item) => item.setAttribute('aria-pressed', 'false'));
      button.setAttribute('aria-pressed', 'true');
      const category = button.dataset.filter;
      cards.forEach((card) => {
        const show = category === 'all' || card.dataset.category.split(/\s+/).includes(category);
        card.hidden = !show;
      });
    });
  });
})();
