let confirmDialogResolver = null;

function showConfirmDialog(options) {
    return new Promise((resolve) => {
        const dialog = document.getElementById('confirm-dialog');
        const iconEl = document.getElementById('confirm-dialog-icon');
        const titleEl = document.getElementById('confirm-dialog-title');
        const messageEl = document.getElementById('confirm-dialog-message');
        const cancelBtn = document.getElementById('confirm-dialog-cancel');
        const confirmBtn = document.getElementById('confirm-dialog-confirm');

        if (!dialog || !iconEl || !titleEl || !messageEl || !cancelBtn || !confirmBtn) {
            console.error('Confirm dialog elements not found');
            resolve(false);
            return;
        }

        const config = {
            title: options.title || '确认操作',
            message: options.message || '确定要执行此操作吗？',
            icon: options.icon || 'warning',
            confirmText: options.confirmText || '确定',
            cancelText: options.cancelText || '取消',
            type: options.type || 'warning'
        };

        iconEl.className = `confirm-dialog-icon ${config.type}`;
        iconEl.textContent = config.icon === 'warning' ? '⚠️' : config.icon === 'danger' ? '🗑️' : 'ℹ️';
        titleEl.textContent = config.title;
        messageEl.textContent = config.message;
        cancelBtn.textContent = config.cancelText;
        confirmBtn.textContent = config.confirmText;

        confirmBtn.className = 'btn-primary';
        if (config.type === 'danger') {
            confirmBtn.classList.add('danger');
        }

        confirmDialogResolver = resolve;

        const handleConfirm = () => {
            closeConfirmDialog();
            resolve(true);
        };

        const handleCancel = () => {
            closeConfirmDialog();
            resolve(false);
        };

        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                handleCancel();
                document.removeEventListener('keydown', handleKeydown);
            } else if (e.key === 'Enter') {
                handleConfirm();
                document.removeEventListener('keydown', handleKeydown);
            }
        };

        confirmBtn.replaceWith(confirmBtn.cloneNode(true));
        cancelBtn.replaceWith(cancelBtn.cloneNode(true));

        const newConfirmBtn = document.getElementById('confirm-dialog-confirm');
        const newCancelBtn = document.getElementById('confirm-dialog-cancel');

        newConfirmBtn.addEventListener('click', handleConfirm);
        newCancelBtn.addEventListener('click', handleCancel);
        document.addEventListener('keydown', handleKeydown);

        dialog.style.display = 'flex';
        newConfirmBtn.focus();
    });
}

function closeConfirmDialog() {
    const dialog = document.getElementById('confirm-dialog');
    if (dialog) {
        dialog.style.display = 'none';
    }
    confirmDialogResolver = null;
}

export { showConfirmDialog, closeConfirmDialog };
