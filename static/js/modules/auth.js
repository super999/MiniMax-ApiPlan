const AuthModule = {
    async checkStatus() {
        const token = StorageService.getToken();
        if (!token) {
            return false;
        }

        try {
            const response = await ApiService.get('/api/auth/me');

            if (response.ok) {
                AppState.set('currentUser', await response.json());
                return true;
            } else {
                StorageService.clearToken();
                return false;
            }
        } catch (error) {
            console.error('检查认证状态失败:', error);
            StorageService.clearToken();
            return false;
        }
    },
    
    async handleLogin(e) {
        e.preventDefault();

        const username = document.getElementById('login-username')?.value.trim();
        const password = document.getElementById('login-password')?.value;

        if (!username || !password) {
            showFormError('login', '请输入用户名和密码');
            return false;
        }

        try {
            const response = await ApiService.post('/api/auth/login', { username, password });

            const data = await response.json();

            if (response.ok) {
                StorageService.setToken(data.access_token);
                AppState.set('currentUser', data.user);
                closeAllModals();
                return true;
            } else {
                showFormError('login', data.detail || '登录失败，请检查用户名和密码');
                return false;
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            showFormError('login', '网络错误，请稍后重试');
            return false;
        }
    },
    
    async handleRegister(e) {
        e.preventDefault();

        const username = document.getElementById('register-username')?.value.trim();
        const email = document.getElementById('register-email')?.value.trim();
        const password = document.getElementById('register-password')?.value;
        const confirmPassword = document.getElementById('register-confirm-password')?.value;

        if (!username || !password) {
            showFormError('register', '请填写用户名和密码');
            return false;
        }

        if (password !== confirmPassword) {
            showFormError('register', '两次输入的密码不一致');
            return false;
        }

        if (password.length < 6) {
            showFormError('register', '密码长度至少为6个字符');
            return false;
        }

        if (username.length < 3) {
            showFormError('register', '用户名长度至少为3个字符');
            return false;
        }

        const requestData = {
            username: username,
            password: password
        };

        if (email) {
            requestData.email = email;
        }

        try {
            const response = await ApiService.post('/api/auth/register', requestData);

            const data = await response.json();

            if (response.ok) {
                const loginResponse = await ApiService.post('/api/auth/login', { username, password });

                const loginData = await loginResponse.json();

                if (loginResponse.ok) {
                    StorageService.setToken(loginData.access_token);
                    AppState.set('currentUser', loginData.user);
                    closeAllModals();
                    return true;
                } else {
                    return 'login';
                }
            } else {
                showFormError('register', data.detail || '注册失败，请重试');
                return false;
            }
        } catch (error) {
            console.error('注册请求失败:', error);
            showFormError('register', '网络错误，请稍后重试');
            return false;
        }
    },
    
    async handleLogout() {
        const token = StorageService.getToken();
        
        try {
            await ApiService.post('/api/auth/logout');
        } catch (error) {
            console.error('退出登录请求失败:', error);
        }

        StorageService.clearToken();
        AppState.reset();
        return true;
    },
    
    updateUserInfo() {
        const currentUser = AppState.get('currentUser');
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
};
