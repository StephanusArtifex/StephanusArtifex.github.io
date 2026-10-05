(() => {
  const dataEl = document.querySelector('#notes-data');
  const items = [...document.querySelectorAll('[data-note]')];
  const preview = document.querySelector('[data-note-preview]');
  if (!dataEl || !preview || !items.length) return;

  let notes = {};
  try {
    notes = JSON.parse(dataEl.textContent || '{}');
  } catch {
    return;
  }

  function renderNote(key, { focus = false } = {}) {
    const note = notes[key];
    if (!note) return;

    items.forEach((item) => {
      const active = item.dataset.note === key;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });

    preview.querySelector('[data-preview-title]').textContent = note.title;
    preview.querySelector('[data-preview-category]').textContent = note.category;
    preview.querySelector('[data-preview-abstract]').textContent = note.excerpt;
    preview.querySelector('[data-preview-date]').textContent = note.date;

    const image = preview.querySelector('[data-preview-image]');
    if (note.image) {
      image.src = note.image;
      image.alt = `${note.title} visual preview`;
      image.hidden = false;
    } else {
      image.hidden = true;
      image.removeAttribute('src');
      image.alt = '';
    }

    const link = preview.querySelector('[data-preview-link]');
    link.href = note.href;
    link.textContent = note.draft ? 'Read draft →' : 'Read article →';

    if (focus) preview.focus({ preventScroll: true });
  }

  items.forEach((item) => {
    item.setAttribute('aria-pressed', 'false');
    item.addEventListener('click', () => renderNote(item.dataset.note));
    item.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      event.preventDefault();
      const index = items.indexOf(item);
      const next = event.key === 'ArrowDown'
        ? items[(index + 1) % items.length]
        : items[(index - 1 + items.length) % items.length];
      next.focus();
      renderNote(next.dataset.note);
    });
  });

  const first = document.querySelector('[data-note].is-featured') || items[0];
  if (first) renderNote(first.dataset.note);
})();
