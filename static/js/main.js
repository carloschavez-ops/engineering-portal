// =====================
// PORTAL ING — MAIN JS
// =====================

document.addEventListener('DOMContentLoaded', () => {
    // Feather icons are replaced after this script runs via inline script in base.html

    // ─── SIDEBAR MOBILE ───
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const openBtn = document.getElementById('sidebarOpen');
    const closeBtn = document.getElementById('sidebarClose');

    openBtn?.addEventListener('click', () => {
        sidebar?.classList.add('open');
        overlay?.classList.add('open');
    });

    const closeSidebar = () => {
        sidebar?.classList.remove('open');
        overlay?.classList.remove('open');
    };
    closeBtn?.addEventListener('click', closeSidebar);
    overlay?.addEventListener('click', closeSidebar);

    // ─── THEME TOGGLE ───
    const themeToggle = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');

    applyTheme('light');
    localStorage.setItem('portalTheme', 'light');

    themeToggle?.addEventListener('click', () => {
        const current = htmlEl.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
        localStorage.setItem('portalTheme', next);
    });

    function applyTheme(theme) {
        htmlEl.setAttribute('data-theme', theme);
        if (themeIcon) {
            themeIcon.setAttribute('data-feather', theme === 'dark' ? 'sun' : 'moon');
            if (typeof feather !== 'undefined') feather.replace();
        }
    }

    // ─── GLOBAL SEARCH ───
    const searchInput = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;

    searchInput?.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const q = searchInput.value.trim();
        if (!q) {
            searchResults.classList.remove('open');
            searchResults.innerHTML = '';
            return;
        }
        searchTimeout = setTimeout(() => fetchSearch(q), 250);
    });

    searchInput?.addEventListener('blur', () => {
        setTimeout(() => searchResults.classList.remove('open'), 200);
    });
    searchInput?.addEventListener('focus', () => {
        if (searchInput.value.trim()) searchResults.classList.add('open');
    });

    async function fetchSearch(q) {
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            renderSearchResults(data);
        } catch (e) {
            console.error('Search error', e);
        }
    }

    function renderSearchResults(items) {
        if (!items.length) {
            searchResults.innerHTML = '<div class="search-result-item"><span class="sr-name" style="color:var(--text-muted)">Sin resultados</span></div>';
            searchResults.classList.add('open');
            return;
        }
        searchResults.innerHTML = items.map(item => `
            <a href="/apps/${item.id}/open" target="_blank" class="search-result-item">
                <div class="sr-icon" style="background:${item.color}22;color:${item.color}">
                    <i data-feather="${item.icono}"></i>
                </div>
                <div>
                    <div class="sr-name">${item.nombre}</div>
                    <div class="sr-cat">${item.categoria}</div>
                </div>
            </a>
        `).join('');
        searchResults.classList.add('open');
        feather.replace();
    }

    // ─── AUTO DISMISS ALERTS ───
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity .5s';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});