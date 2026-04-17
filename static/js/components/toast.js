import { escapeHtml } from '../utils/helpers.js';

const TOAST_CONFIG = {
    duration: 3000,
    autoClose: true,
    maxToasts: 5
};

const TOAST_ICONS = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
};

function showToast(type, title, message, options = {}) {
    const container = document.getElementById('toast-container');
    if (!container) return null;

    const config = { ...TOAST_CONFIG, ...options };
    
    while (container.children.length >= config.maxToasts) {
        const oldestToast = container.firstElementChild;
        if (oldestToast) {
            removeToast(oldestToast);
        }
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = TOAST_ICONS[type] || TOAST_ICONS.info;
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <div class="toast-content">
            <div class="toast-title">${escapeHtml(title)}</div>
            ${message ? `<div class="toast-message">${escapeHtml(message)}</div>` : ''}
        </div>
        <button class="toast-close" aria-label="关闭">×</button>
    `;

    container.appendChild(toast);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => removeToast(toast));
    }

    if (config.autoClose) {
        const timeoutId = setTimeout(() => {
            removeToast(toast);
        }, config.duration);
        
        toast.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
        });
        
        toast.addEventListener('mouseleave', () => {
            setTimeout(() => {
                removeToast(toast);
            }, config.duration);
        });
    }

    return toast;
}

function removeToast(toast) {
    if (!toast || toast.classList.contains('hiding')) return;
    
    toast.classList.add('hiding');
    
    toast.addEventListener('animationend', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, { once: true });
}

function showSuccess(title, message) {
    return showToast('success', title, message);
}

function showError(title, message) {
    return showToast('error', title, message);
}

function showWarning(title, message) {
    return showToast('warning', title, message);
}

function showInfo(title, message) {
    return showToast('info', title, message);
}

export {
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo
};
