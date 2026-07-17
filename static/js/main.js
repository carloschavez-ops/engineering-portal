// =====================
// PORTAL ING — MAIN JS
// =====================

document.addEventListener('DOMContentLoaded', () => {

    // ─── SIDEBAR MOBILE ───
    const sidebar  = document.getElementById('sidebar');
    const overlay  = document.getElementById('sidebarOverlay');
    const openBtn  = document.getElementById('sidebarOpen');
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
    const htmlEl      = document.documentElement;
    const themeIcon   = document.getElementById('themeIcon');

    const savedTheme = localStorage.getItem('portalTheme') || 'light';
    applyTheme(savedTheme);

    themeToggle?.addEventListener('click', () => {
        const current = htmlEl.getAttribute('data-theme');
        const next    = current === 'dark' ? 'light' : 'dark';
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
    const searchInput   = document.getElementById('globalSearch');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;

    searchInput?.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const q = searchInput.value.trim();
        if (!q) {
            searchResults?.classList.remove('open');
            if (searchResults) searchResults.innerHTML = '';
            return;
        }
        searchTimeout = setTimeout(() => fetchSearch(q), 250);
    });

    searchInput?.addEventListener('blur', () => {
        setTimeout(() => searchResults?.classList.remove('open'), 200);
    });
    searchInput?.addEventListener('focus', () => {
        if (searchInput.value.trim()) searchResults?.classList.add('open');
    });

    async function fetchSearch(q) {
        try {
            // Apunta al endpoint de apps.py que respeta roles
            const res  = await fetch(`/apps/api/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            renderSearchResults(data);
        } catch (e) {
            console.error('Search error', e);
        }
    }

    function renderSearchResults(items) {
        if (!items.length) {
            searchResults.innerHTML = '<div class="sd-item"><span class="sd-name" style="color:var(--txt3)">Sin resultados</span></div>';
            searchResults.classList.add('open');
            return;
        }
        searchResults.innerHTML = items.map(item => `
            <a href="/apps/${item.id}/open" class="sd-item">
                <div class="sd-ico" style="background:${item.color}22;color:${item.color}">
                    <i data-feather="${item.icono}"></i>
                </div>
                <div>
                    <div class="sd-name">${item.nombre}</div>
                    <div class="sd-cat">${item.categoria}</div>
                </div>
            </a>
        `).join('');
        searchResults.classList.add('open');
        if (typeof feather !== 'undefined') feather.replace();
    }

    // ─── AUTO DISMISS ALERTS ───
    document.querySelectorAll('.flash').forEach(flash => {
        setTimeout(() => {
            flash.style.opacity    = '0';
            flash.style.transition = 'opacity .5s';
            setTimeout(() => flash.remove(), 500);
        }, 4000);
    });

 // ─── SIDEBAR GROUPS (SOLO MÓVIL) ───
document.querySelectorAll('.sb-group-btn').forEach(btn => {

    btn.addEventListener('click', () => {

        // En PC no hace nada
        if (window.innerWidth >= 992){
            return;
        }

        const group = btn.parentElement;

        document.querySelectorAll('.sb-group').forEach(g => {
            if(g !== group){
                g.classList.remove('open');
            }
        });

        group.classList.toggle('open');

    });

});

});