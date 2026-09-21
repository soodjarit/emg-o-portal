/* Resizable + collapsible sidebar — shared across EMG-O Portal pages.
   Persists width/collapsed state in localStorage so it stays consistent site-wide. */
(function () {
  var MIN_W = 200, MAX_W = 480, DEFAULT_W = 272;
  var LS_WIDTH = 'emgoSidebarWidth';
  var LS_COLLAPSED = 'emgoSidebarCollapsed';

  document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    var container = sidebar.closest('.layout, .wrap') || sidebar.parentElement;

    var savedWidth = parseInt(localStorage.getItem(LS_WIDTH), 10);
    var width = isNaN(savedWidth) ? DEFAULT_W : Math.min(MAX_W, Math.max(MIN_W, savedWidth));
    var collapsed = localStorage.getItem(LS_COLLAPSED) === 'true';

    document.documentElement.style.setProperty('--sidebar-w', width + 'px');
    document.body.dataset.sidebarCollapsed = collapsed ? 'true' : 'false';

    var toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.className = 'sidebar-toggle-btn';
    toggleBtn.setAttribute('aria-label', 'พับ/ขยาย เมนูด้านซ้าย');
    toggleBtn.textContent = collapsed ? '›' : '‹';
    container.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', function () {
      collapsed = !collapsed;
      document.body.dataset.sidebarCollapsed = collapsed ? 'true' : 'false';
      toggleBtn.textContent = collapsed ? '›' : '‹';
      localStorage.setItem(LS_COLLAPSED, collapsed ? 'true' : 'false');
    });

    var handle = document.createElement('div');
    handle.className = 'sidebar-resize-handle';
    sidebar.appendChild(handle);

    var dragging = false, startX = 0, startWidth = width;

    handle.addEventListener('pointerdown', function (e) {
      if (collapsed) return;
      dragging = true;
      startX = e.clientX;
      startWidth = width;
      document.body.classList.add('sidebar-resizing');
      handle.setPointerCapture(e.pointerId);
    });

    handle.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      var next = Math.min(MAX_W, Math.max(MIN_W, startWidth + (e.clientX - startX)));
      width = next;
      document.documentElement.style.setProperty('--sidebar-w', width + 'px');
    });

    function endDrag(e) {
      if (!dragging) return;
      dragging = false;
      document.body.classList.remove('sidebar-resizing');
      localStorage.setItem(LS_WIDTH, String(width));
    }
    handle.addEventListener('pointerup', endDrag);
    handle.addEventListener('pointercancel', endDrag);
  });
})();
