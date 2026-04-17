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

function openCreateProjectModal() {
    const modal = document.getElementById('create-project-modal');
    const overlay = document.getElementById('modal-overlay');
    
    if (modal) {
        modal.style.display = 'block';
        const projectName = document.getElementById('project-name');
        if (projectName) projectName.focus();
    }
    if (overlay) {
        overlay.style.display = 'block';
    }
    
    clearCreateProjectForm();
}

function closeCreateProjectModal() {
    const modal = document.getElementById('create-project-modal');
    const overlay = document.getElementById('modal-overlay');
    
    if (modal) {
        modal.style.display = 'none';
    }
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    clearCreateProjectForm();
}

function clearCreateProjectForm() {
    const form = document.getElementById('create-project-form');
    const errorDiv = document.getElementById('create-project-error');
    
    if (form) {
        form.reset();
    }
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
}

function showCreateProjectError(message) {
    const errorDiv = document.getElementById('create-project-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}
