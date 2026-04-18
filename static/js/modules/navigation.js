const NavigationModule = {
    navigateTo(page) {
        if (!PAGE_TITLES[page]) {
            page = 'dashboard';
        }

        AppState.set('currentPage', page);

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });

        document.querySelectorAll('.page-content').forEach(pageEl => {
            pageEl.style.display = 'none';
        });

        const targetPage = document.getElementById(`${page}-page`);
        if (targetPage) {
            targetPage.style.display = 'block';
        }

        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            pageTitle.textContent = PAGE_TITLES[page] || '工作台';
        }

        if (page === 'debug') {
            DebugModule.initializeForm();
        }

        if (page === 'script') {
            ScriptWorkshopModule.initialize();
        }

        return page;
    },
    
    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    }
};
