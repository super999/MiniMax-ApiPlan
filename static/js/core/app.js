function showLandingPage() {
    const landingPage = document.getElementById('landing-page');
    const workspacePage = document.getElementById('workspace-page');

    if (landingPage) {
        landingPage.style.display = 'block';
    }
    if (workspacePage) {
        workspacePage.style.display = 'none';
    }

    bindLandingEvents();
}

function showWorkspace() {
    const landingPage = document.getElementById('landing-page');
    const workspacePage = document.getElementById('workspace-page');

    if (landingPage) {
        landingPage.style.display = 'none';
    }
    if (workspacePage) {
        workspacePage.style.display = 'flex';
    }

    AuthModule.updateUserInfo();
    bindWorkspaceEvents();
    NavigationModule.navigateTo('dashboard');
    ProjectsModule.loadProjects();
}

function bindLandingEvents() {
    const landingLoginBtn = document.getElementById('landing-login-btn');
    const landingRegisterBtn = document.getElementById('landing-register-btn');
    const heroLoginBtn = document.getElementById('hero-login-btn');

    if (landingLoginBtn) {
        landingLoginBtn.addEventListener('click', () => openModal('login'));
    }
    if (landingRegisterBtn) {
        landingRegisterBtn.addEventListener('click', () => openModal('register'));
    }
    if (heroLoginBtn) {
        heroLoginBtn.addEventListener('click', () => openModal('login'));
    }
}

function bindWorkspaceEvents() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const page = this.dataset.page;
            if (page) {
                NavigationModule.navigateTo(page);
            }
        });
    });

    document.querySelectorAll('.module-card[data-target]').forEach(card => {
        card.addEventListener('click', function() {
            const target = this.dataset.target;
            if (target) {
                NavigationModule.navigateTo(target);
            }
        });
    });

    const sidebarLogoutBtn = document.getElementById('sidebar-logout-btn');
    if (sidebarLogoutBtn) {
        sidebarLogoutBtn.addEventListener('click', async () => {
            await AuthModule.handleLogout();
            showLandingPage();
        });
    }

    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', NavigationModule.toggleSidebar);
    }

    DebugModule.bindEvents();
    ProjectsModule.bindEvents();
}

function bindGlobalEvents() {
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    const modalOverlay = document.getElementById('modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeAllModals);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            const result = await AuthModule.handleLogin(e);
            if (result === true) {
                showWorkspace();
            }
        });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            const result = await AuthModule.handleRegister(e);
            if (result === true) {
                showWorkspace();
            } else if (result === 'login') {
                openModal('login');
            }
        });
    }

    const switchToRegister = document.getElementById('switch-to-register');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', (e) => {
            e.preventDefault();
            switchModal('register');
        });
    }

    const switchToLogin = document.getElementById('switch-to-login');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            switchModal('login');
        });
    }
}

async function initializeApp() {
    const isAuthenticated = await AuthModule.checkStatus();
    if (isAuthenticated) {
        showWorkspace();
    } else {
        showLandingPage();
    }

    await ConfigService.load();
    bindGlobalEvents();
}

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});
