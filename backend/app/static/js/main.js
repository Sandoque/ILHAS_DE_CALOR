// Navbar interactions and dark-mode placeholder
(function () {
  const toggle = document.getElementById('toggle-theme');
  if (toggle) {
    toggle.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
    });
  }
})();
