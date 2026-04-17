import { AppState } from '../core/state.js';
import { ConfigService } from '../core/config.js';
import { StorageService } from '../services/storage.js';
import { ApiService } from '../services/api.js';
import { showError } from '../components/toast.js';

let isDebugLoading = false;

const DebugModule = {
    initializeForm() {
        const modelConfig = ConfigService.get();
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
    },
    
    getFormData() {
        return {
            prompt: document.getElementById('debug-prompt')?.value.trim() || '',
            model: document.getElementById('debug-model')?.value || '',
            temperature: parseFloat(document.getElementById('debug-temperature')?.value || 0),
            max_tokens: parseInt(document.getElementById('debug-max_tokens')?.value || 0)
        };
    },
    
    validateForm(data) {
        if (!data.prompt) {
            showError('输入错误', '请输入 Prompt');
            return false;
        }

        const modelConfig = ConfigService.get();
        const tempParams = modelConfig ? modelConfig.parameters.temperature : { min: 0, max: 2 };
        const maxTokensParams = modelConfig ? modelConfig.parameters.max_tokens : { min: 1, max: 8192 };

        if (data.temperature < tempParams.min || data.temperature > tempParams.max) {
            showError('参数错误', `Temperature 必须在 ${tempParams.min}-${tempParams.max} 之间`);
            return false;
        }
        if (data.max_tokens < maxTokensParams.min || data.max_tokens > maxTokensParams.max) {
            showError('参数错误', `Max Tokens 必须在 ${maxTokensParams.min}-${maxTokensParams.max} 之间`);
            return false;
        }
        return true;
    },
    
    showLoading() {
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
    },
    
    hideLoading() {
        const sendBtn = document.getElementById('debug-sendBtn');

        isDebugLoading = false;
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送请求';
        }
    },
    
    showResponse(data) {
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
    },
    
    showError(message) {
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
    },
    
    async sendRequest() {
        if (isDebugLoading) return;

        const token = StorageService.getToken();
        if (!token) {
            return;
        }

        const formData = this.getFormData();

        if (!this.validateForm(formData)) {
            return;
        }

        this.showLoading();

        try {
            const response = await ApiService.post('/api/chat', formData);

            if (response.status === 401) {
                StorageService.clearToken();
                AppState.reset();
                this.hideLoading();
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP 错误: ${response.status}`);
            }

            const data = await response.json();
            this.showResponse(data);

        } catch (error) {
            console.error('请求错误:', error);
            this.showError(`请求失败: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    },
    
    bindEvents() {
        const debugSendBtn = document.getElementById('debug-sendBtn');
        if (debugSendBtn) {
            debugSendBtn.addEventListener('click', () => this.sendRequest());
        }

        const debugPrompt = document.getElementById('debug-prompt');
        if (debugPrompt) {
            debugPrompt.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    this.sendRequest();
                }
            });
        }

        this.initializeForm();
    }
};

export { DebugModule };
