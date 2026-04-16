document.addEventListener('DOMContentLoaded', function() {
    const sendBtn = document.getElementById('sendBtn');
    const promptTextarea = document.getElementById('prompt');
    const responseDiv = document.getElementById('response');
    const responseInfoDiv = document.getElementById('response-info');
    const infoContentDiv = document.getElementById('info-content');

    let isLoading = false;

    function showLoading() {
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
        isLoading = false;
        sendBtn.disabled = false;
        sendBtn.textContent = '发送请求';
    }

    function showResponse(data) {
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
        responseDiv.innerHTML = `
            <div class="error">
                ${message}
            </div>
        `;
        responseInfoDiv.style.display = 'none';
    }

    function getFormData() {
        return {
            prompt: promptTextarea.value.trim(),
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
        if (data.temperature < 0 || data.temperature > 2) {
            alert('Temperature 必须在 0-2 之间');
            return false;
        }
        if (data.max_tokens < 1 || data.max_tokens > 8192) {
            alert('Max Tokens 必须在 1-8192 之间');
            return false;
        }
        return true;
    }

    async function sendRequest() {
        if (isLoading) return;

        const formData = getFormData();

        if (!validateForm(formData)) {
            return;
        }

        showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

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

    sendBtn.addEventListener('click', sendRequest);

    promptTextarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            sendRequest();
        }
    });
});
