const AppState = {
    modelConfig: null,
    currentUser: null,
    currentPage: 'dashboard',
    
    get(key) {
        return this[key];
    },
    
    set(key, value) {
        this[key] = value;
    },
    
    reset() {
        this.modelConfig = null;
        this.currentUser = null;
        this.currentPage = 'dashboard';
    }
};

const PAGE_TITLES = {
    dashboard: '项目总览',
    script: '脚本工坊',
    visual: '视觉工坊',
    voice: '配音实验室',
    tasks: '任务中心',
    debug: '调试台',
    admin: '管理员后台'
};
