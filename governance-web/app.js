const buttons = document.querySelectorAll('[data-view-button]');
const views = document.querySelectorAll('[data-view]');

buttons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = button.dataset.viewButton;
    buttons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    views.forEach((view) => {
      view.hidden = view.dataset.view !== target;
    });
});
