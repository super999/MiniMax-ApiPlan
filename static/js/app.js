let modelConfig = null;
let currentUser = null;
const TOKEN_KEY = 'auth_token';

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    const token = getStoredToken();
    if (token) {
        await checkAuthStatus();
    } else {
        showNotAuthenticated();
    }

    await loadConfig();
    bindEvents();
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
        showNotAuthenticated();
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
            showAuthenticated();
        } else {
            clearStoredToken();
            showNotAuthenticated();
        }
    } catch (error) {
        console.error('检查认证状态失败:', error);
        clearStoredToken();
        showNotAuthenticated();
    }
}

function showAuthenticated() {
    const authStatusDiv = document.getElementById('auth-status');
    const loginPromptDiv = document.getElementById('login-prompt');
    const chatSectionDiv = document.getElementById('chat-section');

    authStatusDiv.innerHTML = `
        <div class="user-info">
            <span class="username">${currentUser.username}</span>
            <button id="logout-btn" class="btn-logout">退出登录</button>
        </div>
    `;

    loginPromptDiv.style.display = 'none';
    chatSectionDiv.style.display = 'grid';

    document.getElementById('logout-btn').addEventListener('click', handleLogout);
}

function showNotAuthenticated() {
    const authStatusDiv = document.getElementById('auth-status');
    const loginPromptDiv = document.getElementById('login-prompt');
    const chatSectionDiv = document.getElementById('chat-section');

    authStatusDiv.innerHTML = `
        <button id="header-login-btn" class="btn-login">登录</button>
        <button id="header-register-btn" class="btn-register">注册</button>
    `;

    loginPromptDiv.style.display = 'flex';
    chatSectionDiv.style.display = 'none';

    document.getElementById('header-login-btn').addEventListener('click', () => openModal('login'));
    document.getElementById('header-register-btn').addEventListener('click', () => openModal('register'));
}

function bindEvents() {
    document.getElementById('show-login-btn').addEventListener('click', () => openModal('login'));
    document.getElementById('show-register-btn').addEventListener('click', () => openModal('register'));

    document.getElementById('switch-to-register').addEventListener('click', (e) => {
        e.preventDefault();
        switchModal('register');
    });
    document.getElementById('switch-to-login').addEventListener('click', (e) => {
        e.preventDefault();
        switchModal('login');
    });

    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    document.getElementById('modal-overlay').addEventListener('click', closeAllModals);

    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);

    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendRequest);
    }

    const promptTextarea = document.getElementById('prompt');
    if (promptTextarea) {
        promptTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                sendRequest();
            }
        });
    }
}

function openModal(type) {
    const overlay = document.getElementById('modal-overlay');
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');

    overlay.style.display = 'block';
    
    if (type === 'login') {
        loginModal.style.display = 'block';
        registerModal.style.display = 'none';
        document.getElementById('login-username').focus();
    } else {
        loginModal.style.display = 'none';
        registerModal.style.display = 'block';
        document.getElementById('register-username').focus();
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

    overlay.style.display = 'none';
    loginModal.style.display = 'none';
    registerModal.style.display = 'none';

    clearFormErrors();
}

function clearFormErrors() {
    document.getElementById('login-error').style.display = 'none';
    document.getElementById('register-error').style.display = 'none';
}

function showFormError(type, message) {
    const errorDiv = document.getElementById(`${type}-error`);
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

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
            showAuthenticated();
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

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

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
                showAuthenticated();
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
    showNotAuthenticated();
}

async function loadConfig() {
    try {
        const response = await fetch('/static/config/model_config.json');
        if (!response.ok) {
            throw new Error(`配置文件加载失败: ${response.status}`);
        }
        modelConfig = await response.json();
        initializeFormWithConfig();
    } catch (error) {
        console.error('加载配置文件失败:', error);
    }
}

function initializeFormWithConfig() {
    if (!modelConfig) return;

    const modelSelect = document.getElementById('model');
    const temperatureInput = document.getElementById('temperature');
    const maxTokensInput = document.getElementById('max_tokens');

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

function getFormData() {
    return {
        prompt: document.getElementById('prompt').value.trim(),
        model: document.getElementById('model').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        max_tokens: parseInt(document.getElementById('max_tokens').value)
    };
}

function validateForm(data) {
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

let isLoading = false;

function showLoading() {
    const sendBtn = document.getElementById('sendBtn');
    const responseDiv = document.getElementById('response');
    const responseInfoDiv = document.getElementById('response-info');

    isLoading = true;
    sendBtn.disabled = true;
    sendBtn.textContent = '请求中...';

    responseDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>正在处理请求，请稍候...</span>
        </div>
    `;
    responseInfoDiv.style.display = 'none';
}

function hideLoading() {
    const sendBtn = document.getElementById('sendBtn');

    isLoading = false;
    sendBtn.disabled = false;
    sendBtn.textContent = '发送请求';
}

function showResponse(data) {
    const responseDiv = document.getElementById('response');
    const responseInfoDiv = document.getElementById('response-info');
    const infoContentDiv = document.getElementById('info-content');

    responseDiv.innerHTML = '';

    if (data.success && data.content) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'success';
        contentDiv.textContent = data.content;
        responseDiv.appendChild(contentDiv);

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

        infoContentDiv.innerHTML = infoHtml;
    } else {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = data.error_msg || '请求失败，请稍后重试';
        responseDiv.appendChild(errorDiv);
    }
}

function showError(message) {
    const responseDiv = document.getElementById('response');
    const responseInfoDiv = document.getElementById('response-info');

    responseDiv.innerHTML = `
        <div class="error">
            ${message}
        </div>
    `;
    responseInfoDiv.style.display = 'none';
}

async function sendRequest() {
    if (isLoading) return;

    const token = getStoredToken();
    if (!token) {
        openModal('login');
        return;
    }

    const formData = getFormData();

    if (!validateForm(formData)) {
        return;
    }

    showLoading();

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
            showNotAuthenticated();
            openModal('login');
            hideLoading();
            return;
        }

        if (!response.ok) {
            throw new Error(`HTTP 错误: ${response.status}`);
        }

        const data = await response.json();
        showResponse(data);

    } catch (error) {
        console.error('请求错误:', error);
        showError(`请求失败: ${error.message}`);
    } finally {
        hideLoading();
    }
}
