let modelConfig = null;
let currentUser = null;
let currentPage = 'dashboard';
const TOKEN_KEY = 'auth_token';

const PAGE_TITLES = {
    dashboard: '项目总览',
    script: '脚本工坊',
    visual: '视觉工坊',
    voice: '配音实验室',
    tasks: '任务中心',
    debug: '调试台',
    admin: '管理员后台'
};

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    const token = getStoredToken();
    if (token) {
        await checkAuthStatus();
    } else {
        showLandingPage();
    }

    await loadConfig();
    bindGlobalEvents();
}

function getStoredToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setStoredToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearStoredToken() {
    localStorage.removeItem(TOKEN_KEY);
}

async function checkAuthStatus() {
    const token = getStoredToken();
    if (!token) {
        showLandingPage();
        return;
    }

    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            showWorkspace();
        } else {
            clearStoredToken();
            showLandingPage();
        }
    } catch (error) {
        console.error('检查认证状态失败:', error);
        clearStoredToken();
        showLandingPage();
    }
}

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

    updateUserInfo();
    bindWorkspaceEvents();
    navigateTo('dashboard');
}

function updateUserInfo() {
    if (!currentUser) return;

    const welcomeUsername = document.getElementById('welcome-username');
    const userAvatar = document.getElementById('user-avatar');
    const userNameSidebar = document.getElementById('user-name-sidebar');
    const userRoleSidebar = document.getElementById('user-role-sidebar');

    if (welcomeUsername) {
        welcomeUsername.textContent = currentUser.username;
    }
    if (userAvatar) {
        userAvatar.textContent = currentUser.username.charAt(0).toUpperCase();
    }
    if (userNameSidebar) {
        userNameSidebar.textContent = currentUser.username;
    }
    if (userRoleSidebar) {
        userRoleSidebar.textContent = currentUser.is_admin ? '管理员' : '普通用户';
    }
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
        loginForm.addEventListener('submit', handleLogin);
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
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
                navigateTo(page);
            }
        });
    });

    document.querySelectorAll('.module-card[data-target]').forEach(card => {
        card.addEventListener('click', function() {
            const target = this.dataset.target;
            if (target) {
                navigateTo(target);
            }
        });
    });

    const sidebarLogoutBtn = document.getElementById('sidebar-logout-btn');
    if (sidebarLogoutBtn) {
        sidebarLogoutBtn.addEventListener('click', handleLogout);
    }

    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    bindDebugPageEvents();
}

function bindDebugPageEvents() {
    const debugSendBtn = document.getElementById('debug-sendBtn');
    if (debugSendBtn) {
        debugSendBtn.addEventListener('click', sendDebugRequest);
    }

    const debugPrompt = document.getElementById('debug-prompt');
    if (debugPrompt) {
        debugPrompt.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                sendDebugRequest();
            }
        });
    }

    initializeDebugFormWithConfig();
}

function navigateTo(page) {
    if (!PAGE_TITLES[page]) {
        page = 'dashboard';
    }

    currentPage = page;

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
        initializeDebugFormWithConfig();
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

function openModal(type) {
    const overlay = document.getElementById('modal-overlay');
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');

    if (!overlay || !loginModal || !registerModal) return;

    overlay.style.display = 'block';
    
    if (type === 'login') {
        loginModal.style.display = 'block';
        registerModal.style.display = 'none';
        const loginUsername = document.getElementById('login-username');
        if (loginUsername) loginUsername.focus();
    } else {
        loginModal.style.display = 'none';
        registerModal.style.display = 'block';
        const registerUsername = document.getElementById('register-username');
        if (registerUsername) registerUsername.focus();
    }

    clearFormErrors();
}

function switchModal(type) {
    openModal(type);
}

function closeAllModals() {
    const overlay = document.getElementById('modal-overlay');
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');

    if (overlay) overlay.style.display = 'none';
    if (loginModal) loginModal.style.display = 'none';
    if (registerModal) registerModal.style.display = 'none';

    clearFormErrors();
}

function clearFormErrors() {
    const loginError = document.getElementById('login-error');
    const registerError = document.getElementById('register-error');
    if (loginError) loginError.style.display = 'none';
    if (registerError) registerError.style.display = 'none';
}

function showFormError(type, message) {
    const errorDiv = document.getElementById(`${type}-error`);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username')?.value.trim();
    const password = document.getElementById('login-password')?.value;

    if (!username || !password) {
        showFormError('login', '请输入用户名和密码');
        return;
    }

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            setStoredToken(data.access_token);
            currentUser = data.user;
            closeAllModals();
            showWorkspace();
        } else {
            showFormError('login', data.detail || '登录失败，请检查用户名和密码');
        }
    } catch (error) {
        console.error('登录请求失败:', error);
        showFormError('login', '网络错误，请稍后重试');
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('register-username')?.value.trim();
    const email = document.getElementById('register-email')?.value.trim();
    const password = document.getElementById('register-password')?.value;
    const confirmPassword = document.getElementById('register-confirm-password')?.value;

    if (!username || !password) {
        showFormError('register', '请填写用户名和密码');
        return;
    }

    if (password !== confirmPassword) {
        showFormError('register', '两次输入的密码不一致');
        return;
    }

    if (password.length < 6) {
        showFormError('register', '密码长度至少为6个字符');
        return;
    }

    if (username.length < 3) {
        showFormError('register', '用户名长度至少为3个字符');
        return;
    }

    const requestData = {
        username: username,
        password: password
    };

    if (email) {
        requestData.email = email;
    }

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (response.ok) {
            const loginResponse = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const loginData = await loginResponse.json();

            if (loginResponse.ok) {
                setStoredToken(loginData.access_token);
                currentUser = loginData.user;
                closeAllModals();
                showWorkspace();
            } else {
                openModal('login');
                showFormError('login', '注册成功，请登录');
            }
        } else {
            showFormError('register', data.detail || '注册失败，请重试');
        }
    } catch (error) {
        console.error('注册请求失败:', error);
        showFormError('register', '网络错误，请稍后重试');
    }
}

async function handleLogout() {
    const token = getStoredToken();
    
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
    } catch (error) {
        console.error('退出登录请求失败:', error);
    }

    clearStoredToken();
    currentUser = null;
    showLandingPage();
}

async function loadConfig() {
    try {
        const response = await fetch('/static/config/model_config.json');
        if (!response.ok) {
            throw new Error(`配置文件加载失败: ${response.status}`);
        }
        modelConfig = await response.json();
    } catch (error) {
        console.error('加载配置文件失败:', error);
    }
}

function initializeDebugFormWithConfig() {
    if (!modelConfig) return;

    const modelSelect = document.getElementById('debug-model');
    const temperatureInput = document.getElementById('debug-temperature');
    const maxTokensInput = document.getElementById('debug-max_tokens');

    if (modelSelect) {
        modelSelect.innerHTML = '';
        modelConfig.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.value;
            option.textContent = model.label;
            if (model.default) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
    }

    if (temperatureInput) {
        const tempParams = modelConfig.parameters.temperature;
        temperatureInput.min = tempParams.min;
        temperatureInput.max = tempParams.max;
        temperatureInput.step = tempParams.step;
        temperatureInput.value = tempParams.default;
    }

    if (maxTokensInput) {
        const maxTokensParams = modelConfig.parameters.max_tokens;
        maxTokensInput.min = maxTokensParams.min;
        maxTokensInput.max = maxTokensParams.max;
        maxTokensInput.value = maxTokensParams.default;
    }
}

function getDebugFormData() {
    return {
        prompt: document.getElementById('debug-prompt')?.value.trim() || '',
        model: document.getElementById('debug-model')?.value || '',
        temperature: parseFloat(document.getElementById('debug-temperature')?.value || 0),
        max_tokens: parseInt(document.getElementById('debug-max_tokens')?.value || 0)
    };
}

function validateDebugForm(data) {
    if (!data.prompt) {
        alert('请输入 Prompt');
        return false;
    }

    const tempParams = modelConfig ? modelConfig.parameters.temperature : { min: 0, max: 2 };
    const maxTokensParams = modelConfig ? modelConfig.parameters.max_tokens : { min: 1, max: 8192 };

    if (data.temperature < tempParams.min || data.temperature > tempParams.max) {
        alert(`Temperature 必须在 ${tempParams.min}-${tempParams.max} 之间`);
        return false;
    }
    if (data.max_tokens < maxTokensParams.min || data.max_tokens > maxTokensParams.max) {
        alert(`Max Tokens 必须在 ${maxTokensParams.min}-${maxTokensParams.max} 之间`);
        return false;
    }
    return true;
}

let isDebugLoading = false;

function showDebugLoading() {
    const sendBtn = document.getElementById('debug-sendBtn');
    const responseDiv = document.getElementById('debug-response');
    const responseInfoDiv = document.getElementById('debug-response-info');

    isDebugLoading = true;
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '请求中...';
    }

    if (responseDiv) {
        responseDiv.innerHTML = `
            <div class="loading-debug">
                <div class="spinner-debug"></div>
                <span>正在处理请求，请稍候...</span>
            </div>
        `;
    }
    if (responseInfoDiv) {
        responseInfoDiv.style.display = 'none';
    }
}

function hideDebugLoading() {
    const sendBtn = document.getElementById('debug-sendBtn');

    isDebugLoading = false;
    if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.textContent = '发送请求';
    }
}

function showDebugResponse(data) {
    const responseDiv = document.getElementById('debug-response');
    const responseInfoDiv = document.getElementById('debug-response-info');
    const infoContentDiv = document.getElementById('debug-info-content');

    if (!responseDiv) return;

    responseDiv.innerHTML = '';

    if (data.success && data.content) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'success-debug';
        contentDiv.textContent = data.content;
        responseDiv.appendChild(contentDiv);

        if (responseInfoDiv) {
            responseInfoDiv.style.display = 'block';
            let infoHtml = '';

            if (data.model) {
                infoHtml += `<p><strong>模型:</strong> ${data.model}</p>`;
            }
            if (data.latency_ms) {
                infoHtml += `<p><strong>耗时:</strong> ${data.latency_ms} ms</p>`;
            }
            if (data.request_id) {
                infoHtml += `<p><strong>请求ID:</strong> ${data.request_id}</p>`;
            }
            if (data.usage) {
                infoHtml += `<p><strong>Token 使用:</strong> 总计 ${data.usage.total_tokens} (输入: ${data.usage.prompt_tokens}, 输出: ${data.usage.completion_tokens})</p>`;
            }
            if (data.timestamp) {
                infoHtml += `<p><strong>时间:</strong> ${new Date(data.timestamp).toLocaleString('zh-CN')}</p>`;
            }

            if (infoContentDiv) {
                infoContentDiv.innerHTML = infoHtml;
            }
        }
    } else {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-debug';
        errorDiv.textContent = data.error_msg || '请求失败，请稍后重试';
        responseDiv.appendChild(errorDiv);
    }
}

function showDebugError(message) {
    const responseDiv = document.getElementById('debug-response');
    const responseInfoDiv = document.getElementById('debug-response-info');

    if (responseDiv) {
        responseDiv.innerHTML = `
            <div class="error-debug">
                ${message}
            </div>
        `;
    }
    if (responseInfoDiv) {
        responseInfoDiv.style.display = 'none';
    }
}

async function sendDebugRequest() {
    if (isDebugLoading) return;

    const token = getStoredToken();
    if (!token) {
        showLandingPage();
        openModal('login');
        return;
    }

    const formData = getDebugFormData();

    if (!validateDebugForm(formData)) {
        return;
    }

    showDebugLoading();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        if (response.status === 401) {
            clearStoredToken();
            currentUser = null;
            showLandingPage();
            openModal('login');
            hideDebugLoading();
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP 错误: ${response.status}`);
        }

        const data = await response.json();
        showDebugResponse(data);

    } catch (error) {
        console.error('请求错误:', error);
        showDebugError(`请求失败: ${error.message}`);
    } finally {
        hideDebugLoading();
    }
}
