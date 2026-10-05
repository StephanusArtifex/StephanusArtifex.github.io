(() => {
  const index = document.querySelector('[data-about-index]');
  if (!index) return;

  const links = [...index.querySelectorAll('a[href^="#"]')];
  const entries = links
    .map((link) => ({ link, section: document.querySelector(link.getAttribute('href')) }))
    .filter((entry) => entry.section);

  if (!entries.length) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const header = document.querySelector('.site-header');

  const setActive = (id) => {
    for (const { link, section } of entries) {
      const active = section.id === id;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  };

  const scrollToSection = (section, pushHash = true) => {
    const headerHeight = header ? header.getBoundingClientRect().height : 0;
    const top = section.getBoundingClientRect().top + window.scrollY - headerHeight - 18;
    window.scrollTo({ top, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    if (pushHash) history.pushState(null, '', `#${section.id}`);
    setActive(section.id);
  };

  links.forEach((link) => {
    link.addEventListener('click', (event) => {
      const section = document.querySelector(link.getAttribute('href'));
      if (!section) return;
      event.preventDefault();
      scrollToSection(section);
    });
  });

  let ticking = false;
  const updateFromScroll = () => {
    ticking = false;
    const headerHeight = header ? header.getBoundingClientRect().height : 0;
    const anchorY = headerHeight + 32;
    let current = entries[0];

    for (const entry of entries) {
      const rect = entry.section.getBoundingClientRect();
      if (rect.top <= anchorY) current = entry;
      else break;
    }

    setActive(current.section.id);
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateFromScroll);
      ticking = true;
    }
  }, { passive: true });

  window.addEventListener('hashchange', () => {
    const id = location.hash.slice(1);
    const match = entries.find(({ section }) => section.id === id);
    if (match) setActive(id);
  });

  if (location.hash) {
    const match = entries.find(({ section }) => `#${section.id}` === location.hash);
    if (match) requestAnimationFrame(() => scrollToSection(match.section, false));
  } else {
    updateFromScroll();
  }
})();
