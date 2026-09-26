(() => {
  'use strict';
  const search = document.getElementById('help-search');
  const count = document.getElementById('search-count');
  const empty = document.getElementById('help-empty');
  const sections = [...document.querySelectorAll('.help-content > .help-section')];
  const normalize = value => value.toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  const update = () => {
    const query = normalize(search.value.trim());
    let matches = 0;
    for (const section of sections) {
      const topics = [...section.querySelectorAll('.help-topic')];
      const heading = section.querySelector('h2')?.textContent || '';
      const intro = [...section.children].filter(node => node.matches?.('p')).map(node => node.textContent).join(' ');
      const wholeSection = !query || normalize(`${heading} ${intro} ${section.id}`).includes(query);
      let shown = 0;
      for (const topic of topics) {
        const visible = wholeSection || normalize(topic.textContent).includes(query);
        topic.hidden = !visible;
        if (visible) shown++;
        if (topic.tagName === 'DETAILS' && query && visible) topic.open = true;
        if (topic.tagName === 'DETAILS' && !query) topic.open = false;
      }
      const visible = wholeSection || shown > 0 || (!topics.length && normalize(section.textContent).includes(query));
      section.hidden = !visible;
      if (visible && query) matches++;
    }
    count.hidden = !query;
    count.textContent = query ? `${matches} ${matches === 1 ? 'section' : 'sections'} found` : '';
    empty.hidden = !query || matches > 0;
  };
  search.addEventListener('input', update);
  document.getElementById('clear-search').addEventListener('click', () => { search.value = ''; update(); search.focus(); });
  document.addEventListener('keydown', event => {
    const typing = /^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if (event.key === '/' && !typing && !event.altKey && !event.ctrlKey && !event.metaKey) {
      event.preventDefault(); search.focus();
    } else if (event.key === 'Escape' && document.activeElement === search) {
      search.value = ''; update(); search.blur();
    }
  });
  document.querySelectorAll('.help-toc a').forEach(link => link.addEventListener('click', () => {
    if (search.value) { search.value = ''; update(); }
  }));

  const connection = document.getElementById('help-connection');
  const indicator = connection.closest('.top-status');
  let checking = false;
  let preview = location.protocol === 'file:';
  const updateConnection = async () => {
    if (checking) return;
    checking = true;
    try {
      const response = await fetch('/api/state', { cache: 'no-store' });
      if (response.status === 404) preview = true;
      if (!response.ok) throw new Error('Controller unavailable');
      connection.textContent = window.RobStatus.connection(await response.json());
      indicator.dataset.connection = 'connected';
    } catch {
      connection.textContent = preview ? window.RobStatus.preview : window.RobStatus.offline;
      indicator.dataset.connection = preview ? 'preview' : 'offline';
    } finally {
      checking = false;
    }
  };
  updateConnection();
  setInterval(updateConnection, 2000);
})();
