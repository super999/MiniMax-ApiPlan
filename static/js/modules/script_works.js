const ScriptWorksModule = {
    currentProjectId: null,
    currentScriptWorkId: null,
    currentChapterId: null,
    projects: [],
    scriptWorks: [],
    chapters: [],

    async init() {
        this.bindEvents();
    },

    bindEvents() {
        // 项目选择器
        const projectSelect = document.getElementById('script-project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', (e) => this.handleProjectChange(e));
        }

        // 脚本作品选择器
        const scriptWorkSelect = document.getElementById('script-work-select');
        if (scriptWorkSelect) {
            scriptWorkSelect.addEventListener('change', (e) => this.handleScriptWorkChange(e));
        }

        // 新建脚本作品按钮
        const createScriptWorkBtn = document.getElementById('create-script-work-btn');
        if (createScriptWorkBtn) {
            createScriptWorkBtn.addEventListener('click', () => this.openCreateScriptWorkModal());
        }

        const welcomeCreateScriptBtn = document.getElementById('welcome-create-script-btn');
        if (welcomeCreateScriptBtn) {
            welcomeCreateScriptBtn.addEventListener('click', () => this.openCreateScriptWorkModal());
        }

        // 新建章节按钮
        const createChapterBtn = document.getElementById('create-chapter-btn');
        if (createChapterBtn) {
            createChapterBtn.addEventListener('click', () => this.openCreateChapterModal());
        }

        // 标签页切换
        const tabBtns = document.querySelectorAll('.script-tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTabChange(e.target));
        });

        // 保存大纲
        const saveOutlineBtn = document.getElementById('save-outline-btn');
        if (saveOutlineBtn) {
            saveOutlineBtn.addEventListener('click', () => this.saveOutline());
        }

        // 保存人物设定
        const saveCharactersBtn = document.getElementById('save-characters-btn');
        if (saveCharactersBtn) {
            saveCharactersBtn.addEventListener('click', () => this.saveCharacters());
        }

        // 保存章节
        const saveChapterBtn = document.getElementById('save-chapter-btn');
        if (saveChapterBtn) {
            saveChapterBtn.addEventListener('click', () => this.saveChapter());
        }

        // 删除章节
        const deleteChapterBtn = document.getElementById('delete-chapter-btn');
        if (deleteChapterBtn) {
            deleteChapterBtn.addEventListener('click', () => this.deleteChapter());
        }

        // 新建脚本作品表单
        const createScriptWorkForm = document.getElementById('create-script-work-form');
        if (createScriptWorkForm) {
            createScriptWorkForm.addEventListener('submit', (e) => this.handleCreateScriptWork(e));
        }

        // 新建章节表单
        const createChapterForm = document.getElementById('create-chapter-form');
        if (createChapterForm) {
            createChapterForm.addEventListener('submit', (e) => this.handleCreateChapter(e));
        }

        // 关闭按钮
        const closeCreateScriptWork = document.getElementById('close-create-script-work');
        if (closeCreateScriptWork) {
            closeCreateScriptWork.addEventListener('click', () => this.closeCreateScriptWorkModal());
        }

        const closeCreateChapter = document.getElementById('close-create-chapter');
        if (closeCreateChapter) {
            closeCreateChapter.addEventListener('click', () => this.closeCreateChapterModal());
        }
    },

    // 加载项目列表
    async loadProjects() {
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get('/api/projects');
            if (response.ok) {
                this.projects = await response.json();
                this.renderProjectOptions();
            }
        } catch (error) {
            console.error('加载项目列表失败:', error);
        }
    },

    // 渲染项目选项
    renderProjectOptions() {
        const projectSelect = document.getElementById('script-project-select');
        if (!projectSelect) return;

        projectSelect.innerHTML = '<option value="">请选择项目</option>';
        this.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            if (this.currentProjectId && this.currentProjectId === project.id) {
                option.selected = true;
            }
            projectSelect.appendChild(option);
        });
    },

    // 项目变更处理
    async handleProjectChange(e) {
        const projectId = e.target.value ? parseInt(e.target.value) : null;
        this.currentProjectId = projectId;
        this.currentScriptWorkId = null;
        this.scriptWorks = [];
        this.chapters = [];

        // 重置脚本作品选择器
        const scriptWorkSelect = document.getElementById('script-work-select');
        if (scriptWorkSelect) {
            scriptWorkSelect.innerHTML = '<option value="">请选择脚本作品</option>';
        }

        // 隐藏编辑器
        this.hideEditor();

        if (projectId) {
            await this.loadScriptWorks(projectId);
        }
    },

    // 加载脚本作品列表
    async loadScriptWorks(projectId) {
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get(`/api/script-works?project_id=${projectId}`);
            if (response.ok) {
                this.scriptWorks = await response.json();
                this.renderScriptWorkOptions();
            }
        } catch (error) {
            console.error('加载脚本作品列表失败:', error);
        }
    },

    // 渲染脚本作品选项
    renderScriptWorkOptions() {
        const scriptWorkSelect = document.getElementById('script-work-select');
        if (!scriptWorkSelect) return;

        scriptWorkSelect.innerHTML = '<option value="">请选择脚本作品</option>';
        this.scriptWorks.forEach(work => {
            const option = document.createElement('option');
            option.value = work.id;
            option.textContent = work.title;
            scriptWorkSelect.appendChild(option);
        });

        // 根据是否有脚本作品显示/隐藏编辑器
        if (this.scriptWorks.length > 0) {
            // 如果有脚本作品，保持隐藏状态，等待用户选择
            this.hideEditor();
        } else {
            // 如果没有脚本作品，显示引导区域
            this.showNoScriptWorkContainer();
        }
    },

    // 脚本作品变更处理
    async handleScriptWorkChange(e) {
        const scriptWorkId = e.target.value ? parseInt(e.target.value) : null;
        this.currentScriptWorkId = scriptWorkId;
        this.currentChapterId = null;
        this.chapters = [];

        if (scriptWorkId) {
            await this.loadScriptWorkDetail(scriptWorkId);
        } else {
            this.hideEditor();
        }
    },

    // 加载脚本作品详情
    async loadScriptWorkDetail(scriptWorkId) {
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get(`/api/script-works/${scriptWorkId}`);
            if (response.ok) {
                const data = await response.json();
                this.chapters = data.chapters || [];
                this.populateEditor(data);
                this.showEditor();
            }
        } catch (error) {
            console.error('加载脚本作品详情失败:', error);
            showError('加载失败', '无法加载脚本作品详情');
        }
    },

    // 填充编辑器内容
    populateEditor(data) {
        // 填充大纲
        const outlineEditor = document.getElementById('outline-editor');
        if (outlineEditor) {
            outlineEditor.value = data.outline || '';
        }

        // 填充人物设定
        const charactersEditor = document.getElementById('characters-editor');
        if (charactersEditor) {
            charactersEditor.value = data.characters || '';
        }

        // 渲染章节列表
        this.renderChaptersList();
    },

    // 渲染章节列表
    renderChaptersList() {
        const chaptersList = document.getElementById('chapters-list');
        const emptyState = chaptersList?.querySelector('.empty-state');
        const chapterEditorContainer = document.getElementById('chapter-editor-container');

        if (!chaptersList) return;

        // 清空现有章节（保留空状态）
        const existingChapters = chaptersList.querySelectorAll('.chapter-item');
        existingChapters.forEach(ch => ch.remove());

        if (this.chapters.length === 0) {
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            if (chapterEditorContainer) {
                chapterEditorContainer.style.display = 'none';
            }
            return;
        }

        if (emptyState) {
            emptyState.style.display = 'none';
        }

        // 按章节号排序
        const sortedChapters = [...this.chapters].sort((a, b) => a.chapter_number - b.chapter_number);

        sortedChapters.forEach(chapter => {
            const chapterItem = document.createElement('div');
            chapterItem.className = 'chapter-item';
            chapterItem.dataset.chapterId = chapter.id;
            chapterItem.innerHTML = `
                <div class="chapter-item-info">
                    <span class="chapter-item-number">第${chapter.chapter_number}集</span>
                    <span class="chapter-item-title">${chapter.title}</span>
                </div>
                <div class="chapter-item-status ${chapter.status}">${this.getStatusLabel(chapter.status)}</div>
            `;

            chapterItem.addEventListener('click', () => this.selectChapter(chapter));
            chaptersList.appendChild(chapterItem);
        });
    },

    // 获取状态标签
    getStatusLabel(status) {
        const labels = {
            'draft': '草稿',
            'generating': '生成中',
            'completed': '已完成',
            'failed': '失败'
        };
        return labels[status] || '草稿';
    },

    // 选择章节
    selectChapter(chapter) {
        this.currentChapterId = chapter.id;

        // 更新选中状态
        const chapterItems = document.querySelectorAll('.chapter-item');
        chapterItems.forEach(item => {
            item.classList.remove('active');
            if (parseInt(item.dataset.chapterId) === chapter.id) {
                item.classList.add('active');
            }
        });

        // 显示章节编辑器
        const chapterEditorContainer = document.getElementById('chapter-editor-container');
        if (chapterEditorContainer) {
            chapterEditorContainer.style.display = 'block';
        }

        // 填充章节数据
        document.getElementById('current-chapter-number').textContent = chapter.chapter_number;
        document.getElementById('current-chapter-title').value = chapter.title || '';
        document.getElementById('chapter-outline-editor').value = chapter.outline || '';
        document.getElementById('chapter-content-editor').value = chapter.content || '';

        // 清除状态
        this.clearStatus('chapter');
    },

    // 标签页切换
    handleTabChange(tabBtn) {
        // 更新按钮状态
        const tabBtns = document.querySelectorAll('.script-tab-btn');
        tabBtns.forEach(btn => btn.classList.remove('active'));
        tabBtn.classList.add('active');

        // 获取目标标签页
        const tabName = tabBtn.dataset.tab;

        // 隐藏所有内容
        const tabContents = document.querySelectorAll('.script-tab-content');
        tabContents.forEach(content => {
            content.style.display = 'none';
            content.classList.remove('active');
        });

        // 显示目标内容
        const targetTab = document.getElementById(`${tabName}-tab`);
        if (targetTab) {
            targetTab.style.display = 'block';
            targetTab.classList.add('active');
        }
    },

    // 保存大纲
    async saveOutline() {
        if (!this.currentScriptWorkId) {
            showError('保存失败', '请先选择一个脚本作品');
            return;
        }

        const outlineEditor = document.getElementById('outline-editor');
        const outline = outlineEditor?.value || '';

        const submitBtn = document.getElementById('save-outline-btn');
        const originalText = submitBtn?.textContent;

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '保存中...';
            }

            const response = await ApiService.request(`/api/script-works/${this.currentScriptWorkId}/outline`, {
                method: 'PUT',
                body: JSON.stringify({ outline })
            });

            if (response.ok) {
                this.showStatus('outline', '保存成功', 'success');
                showSuccess('保存成功', '大纲已保存');
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showStatus('outline', '保存失败', 'error');
                showError('保存失败', errorData.detail || '保存大纲失败');
            }
        } catch (error) {
            console.error('保存大纲失败:', error);
            this.showStatus('outline', '保存失败', 'error');
            showError('保存失败', '网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    // 保存人物设定
    async saveCharacters() {
        if (!this.currentScriptWorkId) {
            showError('保存失败', '请先选择一个脚本作品');
            return;
        }

        const charactersEditor = document.getElementById('characters-editor');
        const characters = charactersEditor?.value || '';

        const submitBtn = document.getElementById('save-characters-btn');
        const originalText = submitBtn?.textContent;

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '保存中...';
            }

            const response = await ApiService.request(`/api/script-works/${this.currentScriptWorkId}/characters`, {
                method: 'PUT',
                body: JSON.stringify({ characters })
            });

            if (response.ok) {
                this.showStatus('characters', '保存成功', 'success');
                showSuccess('保存成功', '人物设定已保存');
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showStatus('characters', '保存失败', 'error');
                showError('保存失败', errorData.detail || '保存人物设定失败');
            }
        } catch (error) {
            console.error('保存人物设定失败:', error);
            this.showStatus('characters', '保存失败', 'error');
            showError('保存失败', '网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    // 保存章节
    async saveChapter() {
        if (!this.currentChapterId) {
            showError('保存失败', '请先选择一个章节');
            return;
        }

        const title = document.getElementById('current-chapter-title')?.value || '';
        const outline = document.getElementById('chapter-outline-editor')?.value || '';
        const content = document.getElementById('chapter-content-editor')?.value || '';

        if (!title) {
            showError('保存失败', '章节标题不能为空');
            return;
        }

        const submitBtn = document.getElementById('save-chapter-btn');
        const originalText = submitBtn?.textContent;

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '保存中...';
            }

            const response = await ApiService.request(`/api/script-works/${this.currentScriptWorkId}/chapters/${this.currentChapterId}`, {
                method: 'PUT',
                body: JSON.stringify({ title, outline, content })
            });

            if (response.ok) {
                // 更新本地章节数据
                const updatedChapter = await response.json();
                const index = this.chapters.findIndex(c => c.id === this.currentChapterId);
                if (index !== -1) {
                    this.chapters[index] = updatedChapter;
                }

                // 重新渲染章节列表
                this.renderChaptersList();

                // 重新选中当前章节
                const currentChapter = this.chapters.find(c => c.id === this.currentChapterId);
                if (currentChapter) {
                    this.selectChapter(currentChapter);
                }

                this.showStatus('chapter', '保存成功', 'success');
                showSuccess('保存成功', '章节已保存');
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showStatus('chapter', '保存失败', 'error');
                showError('保存失败', errorData.detail || '保存章节失败');
            }
        } catch (error) {
            console.error('保存章节失败:', error);
            this.showStatus('chapter', '保存失败', 'error');
            showError('保存失败', '网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    // 删除章节
    async deleteChapter() {
        if (!this.currentChapterId) {
            showError('删除失败', '请先选择一个章节');
            return;
        }

        const confirmed = await showConfirmDialog({
            title: '确认删除',
            message: '确定要删除这个章节吗？此操作无法撤销。',
            type: 'danger',
            confirmText: '删除',
            cancelText: '取消'
        });

        if (!confirmed) {
            return;
        }

        try {
            const response = await ApiService.request(`/api/script-works/${this.currentScriptWorkId}/chapters/${this.currentChapterId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                // 从本地数据中移除
                this.chapters = this.chapters.filter(c => c.id !== this.currentChapterId);
                this.currentChapterId = null;

                // 重新渲染
                this.renderChaptersList();

                // 隐藏章节编辑器
                const chapterEditorContainer = document.getElementById('chapter-editor-container');
                if (chapterEditorContainer) {
                    chapterEditorContainer.style.display = 'none';
                }

                showSuccess('删除成功', '章节已删除');
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('删除失败', errorData.detail || '删除章节失败');
            }
        } catch (error) {
            console.error('删除章节失败:', error);
            showError('删除失败', '网络错误，请稍后重试');
        }
    },

    // 显示状态
    showStatus(type, message, status) {
        const statusEl = document.getElementById(`${type}-status`);
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `save-status ${status}`;

            // 3秒后清除
            setTimeout(() => {
                this.clearStatus(type);
            }, 3000);
        }
    },

    // 清除状态
    clearStatus(type) {
        const statusEl = document.getElementById(`${type}-status`);
        if (statusEl) {
            statusEl.textContent = '';
            statusEl.className = 'save-status';
        }
    },

    // 显示编辑器
    showEditor() {
        const editorContainer = document.getElementById('script-editor-container');
        const noScriptWorkContainer = document.getElementById('no-script-work-container');

        if (editorContainer) {
            editorContainer.style.display = 'block';
        }
        if (noScriptWorkContainer) {
            noScriptWorkContainer.style.display = 'none';
        }
    },

    // 隐藏编辑器
    hideEditor() {
        const editorContainer = document.getElementById('script-editor-container');
        const noScriptWorkContainer = document.getElementById('no-script-work-container');

        if (editorContainer) {
            editorContainer.style.display = 'none';
        }

        // 只有当没有选择项目或没有脚本作品时才显示引导区域
        if (!this.currentProjectId || this.scriptWorks.length === 0) {
            if (noScriptWorkContainer) {
                noScriptWorkContainer.style.display = 'flex';
            }
        } else {
            if (noScriptWorkContainer) {
                noScriptWorkContainer.style.display = 'none';
            }
        }
    },

    // 显示无脚本作品引导
    showNoScriptWorkContainer() {
        const noScriptWorkContainer = document.getElementById('no-script-work-container');
        if (noScriptWorkContainer) {
            noScriptWorkContainer.style.display = 'flex';
        }
    },

    // 打开新建脚本作品弹窗
    openCreateScriptWorkModal() {
        if (!this.currentProjectId) {
            showError('操作失败', '请先选择一个项目');
            return;
        }

        // 重置表单
        document.getElementById('create-script-work-form')?.reset();
        this.hideCreateScriptWorkError();

        const modal = document.getElementById('create-script-work-modal');
        if (modal) {
            modal.style.display = 'block';
            document.getElementById('modal-overlay')?.classList.add('active');
        }
    },

    // 关闭新建脚本作品弹窗
    closeCreateScriptWorkModal() {
        const modal = document.getElementById('create-script-work-modal');
        if (modal) {
            modal.style.display = 'none';
            document.getElementById('modal-overlay')?.classList.remove('active');
        }
    },

    // 显示新建脚本作品错误
    showCreateScriptWorkError(message) {
        const errorEl = document.getElementById('create-script-work-error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    },

    // 隐藏新建脚本作品错误
    hideCreateScriptWorkError() {
        const errorEl = document.getElementById('create-script-work-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    },

    // 处理新建脚本作品
    async handleCreateScriptWork(e) {
        e.preventDefault();

        const title = document.getElementById('new-script-work-title')?.value.trim();
        const description = document.getElementById('new-script-work-description')?.value.trim();

        if (!title) {
            this.showCreateScriptWorkError('请输入作品名称');
            return;
        }

        if (title.length > 200) {
            this.showCreateScriptWorkError('作品名称不能超过200个字符');
            return;
        }

        const submitBtn = document.getElementById('create-script-work-submit');
        const originalText = submitBtn?.textContent;

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '创建中...';
            }

            const requestData = {
                title: title,
                project_id: this.currentProjectId
            };

            if (description) {
                requestData.description = description;
            }

            const response = await ApiService.request('/api/script-works', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const newWork = await response.json();
                this.closeCreateScriptWorkModal();
                showSuccess('创建成功', `脚本作品 "${title}" 创建成功`);

                // 重新加载脚本作品列表
                await this.loadScriptWorks(this.currentProjectId);

                // 自动选择新创建的作品
                const scriptWorkSelect = document.getElementById('script-work-select');
                if (scriptWorkSelect) {
                    scriptWorkSelect.value = newWork.id;
                    this.currentScriptWorkId = newWork.id;
                    await this.loadScriptWorkDetail(newWork.id);
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showCreateScriptWorkError(errorData.detail || '创建失败，请重试');
            }
        } catch (error) {
            console.error('创建脚本作品失败:', error);
            this.showCreateScriptWorkError('网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    // 打开新建章节弹窗
    openCreateChapterModal() {
        if (!this.currentScriptWorkId) {
            showError('操作失败', '请先选择一个脚本作品');
            return;
        }

        // 重置表单
        document.getElementById('create-chapter-form')?.reset();
        this.hideCreateChapterError();

        // 计算下一个章节号
        const maxNumber = this.chapters.length > 0 
            ? Math.max(...this.chapters.map(c => c.chapter_number))
            : 0;
        const nextNumber = maxNumber + 1;
        const numberInput = document.getElementById('new-chapter-number');
        if (numberInput) {
            numberInput.placeholder = `下一个: ${nextNumber}`;
        }

        const modal = document.getElementById('create-chapter-modal');
        if (modal) {
            modal.style.display = 'block';
            document.getElementById('modal-overlay')?.classList.add('active');
        }
    },

    // 关闭新建章节弹窗
    closeCreateChapterModal() {
        const modal = document.getElementById('create-chapter-modal');
        if (modal) {
            modal.style.display = 'none';
            document.getElementById('modal-overlay')?.classList.remove('active');
        }
    },

    // 显示新建章节错误
    showCreateChapterError(message) {
        const errorEl = document.getElementById('create-chapter-error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    },

    // 隐藏新建章节错误
    hideCreateChapterError() {
        const errorEl = document.getElementById('create-chapter-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    },

    // 处理新建章节
    async handleCreateChapter(e) {
        e.preventDefault();

        const chapterNumber = document.getElementById('new-chapter-number')?.value;
        const title = document.getElementById('new-chapter-title')?.value.trim();
        const outline = document.getElementById('new-chapter-outline')?.value.trim();

        if (!title) {
            this.showCreateChapterError('请输入章节标题');
            return;
        }

        if (title.length > 200) {
            this.showCreateChapterError('章节标题不能超过200个字符');
            return;
        }

        const submitBtn = document.getElementById('create-chapter-submit');
        const originalText = submitBtn?.textContent;

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '创建中...';
            }

            const requestData = {
                title: title
            };

            if (chapterNumber) {
                requestData.chapter_number = parseInt(chapterNumber);
            }

            if (outline) {
                requestData.outline = outline;
            }

            const response = await ApiService.request(`/api/script-works/${this.currentScriptWorkId}/chapters`, {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const newChapter = await response.json();
                this.closeCreateChapterModal();
                showSuccess('创建成功', `章节 "${title}" 创建成功`);

                // 添加到本地数据
                this.chapters.push(newChapter);

                // 重新渲染章节列表
                this.renderChaptersList();

                // 自动选择新创建的章节
                this.selectChapter(newChapter);
            } else {
                const errorData = await response.json().catch(() => ({}));
                this.showCreateChapterError(errorData.detail || '创建失败，请重试');
            }
        } catch (error) {
            console.error('创建章节失败:', error);
            this.showCreateChapterError('网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    // 当从项目页面跳转时调用
    async navigateToProject(projectId) {
        this.currentProjectId = projectId;
        
        // 加载项目列表并设置选中
        await this.loadProjects();
        
        // 设置项目选择器
        const projectSelect = document.getElementById('script-project-select');
        if (projectSelect) {
            projectSelect.value = projectId;
        }

        // 加载该项目的脚本作品
        await this.loadScriptWorks(projectId);
    }
};

// 为了在外部访问，添加到window对象
window.ScriptWorksModule = ScriptWorksModule;