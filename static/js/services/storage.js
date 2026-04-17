const TOKEN_KEY = 'auth_token';

const StorageService = {
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },
    
    setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    },
    
    clearToken() {
        localStorage.removeItem(TOKEN_KEY);
    }
};
