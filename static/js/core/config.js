const ConfigService = {
    async load() {
        try {
            const response = await fetch('/static/config/model_config.json');
            if (!response.ok) {
                throw new Error(`配置文件加载失败: ${response.status}`);
            }
            AppState.set('modelConfig', await response.json());
            return AppState.get('modelConfig');
        } catch (error) {
            console.error('加载配置文件失败:', error);
            return null;
        }
    },
    
    get() {
        return AppState.get('modelConfig');
    }
};
