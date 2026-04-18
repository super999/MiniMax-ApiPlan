const ScriptWorkshopModule = {
    currentProjectId: null,
    currentScriptWorkId: null,
    currentScriptWork: null,
    currentChapterId: null,
    isGenerating: false,

    async initialize() {
        this.bindEvents();
        this.loadProjects();
    },

    bindEvents() {
        const projectSelect = document.getElementById('script-project-select');
        if (projectSelect) {
            projectSelect.addEventListener('change', (e) => {
                this.currentProjectId = e.target.value ? parseInt(e.target.value) : null;
                this.loadScriptWorks();
            });
        }

        const createScriptBtn = document.getElementById('create-script-btn');
        if (createScriptBtn) {
            createScriptBtn.addEventListener('click', () => this.showCreateScriptModal());
        }

        const createScriptForm = document.getElementById('create-script-form');
        if (createScriptForm) {
            createScriptForm.addEventListener('submit', (e) => this.handleCreateScript(e));
        }

        const closeCreateScript = document.getElementById('close-create-script');
        if (closeCreateScript) {
            closeCreateScript.addEventListener('click', () => this.hideCreateScriptModal());
        }

        const backToListBtn = document.getElementById('back-to-list-btn');
        if (backToListBtn) {
            backToListBtn.addEventListener('click', () => this.showScriptList());
        }

        const saveOutlineBtn = document.getElementById('save-outline-btn');
        if (saveOutlineBtn) {
            saveOutlineBtn.addEventListener('click', () => this.saveOutline());
        }

        const generateOutlineBtn = document.getElementById('generate-outline-btn');
        if (generateOutlineBtn) {
            generateOutlineBtn.addEventListener('click', () => this.generateOutline());
        }

        const saveCharactersBtn = document.getElementById('save-characters-btn');
        if (saveCharactersBtn) {
            saveCharactersBtn.addEventListener('click', () => this.saveCharacters());
        }

        const generateCharactersBtn = document.getElementById('generate-characters-btn');
        if (generateCharactersBtn) {
            generateCharactersBtn.addEventListener('click', () => this.generateCharacters());
        }

        const createChapterBtn = document.getElementById('create-chapter-btn');
        if (createChapterBtn) {
            createChapterBtn.addEventListener('click', () => this.showCreateChapterModal());
        }

        const createChapterForm = document.getElementById('create-chapter-form');
        if (createChapterForm) {
            createChapterForm.addEventListener('submit', (e) => this.handleCreateChapter(e));
        }

        const closeCreateChapter = document.getElementById('close-create-chapter');
        if (closeCreateChapter) {
            closeCreateChapter.addEventListener('click', () => this.hideCreateChapterModal());
        }

        const saveChapterBtn = document.getElementById('save-chapter-btn');
        if (saveChapterBtn) {
            saveChapterBtn.addEventListener('click', () => this.saveChapter());
        }

        const generateChapterBtn = document.getElementById('generate-chapter-btn');
        if (generateChapterBtn) {
            generateChapterBtn.addEventListener('click', () => this.generateChapterContent());
        }

        const backToOverviewBtn = document.getElementById('back-to-overview-btn');
        if (backToOverviewBtn) {
            backToOverviewBtn.addEventListener('click', () => this.showOverview());
        }
    },

    async loadProjects() {
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get('/api/projects');
            if (response.ok) {
                const projects = await response.json();
                this.renderProjectSelect(projects);
            }
        } catch (error) {
            console.error('加载项目列表失败:', error);
        }
    },

    renderProjectSelect(projects) {
        const select = document.getElementById('script-project-select');
        if (!select) return;

        select.innerHTML = '<option value="">选择项目...</option>';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            select.appendChild(option);
        });
    },

    async loadScriptWorks() {
        if (!this.currentProjectId) {
            this.renderScriptWorks([]);
            return;
        }

        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get(`/api/script-works?project_id=${this.currentProjectId}`);
            if (response.ok) {
                const scriptWorks = await response.json();
                this.renderScriptWorks(scriptWorks);
            }
        } catch (error) {
            console.error('加载脚本作品列表失败:', error);
            showError('加载失败', '无法加载脚本作品列表');
        }
    },

    renderScriptWorks(scriptWorks) {
        const listContainer = document.getElementById('script-works-list');
        const emptyState = document.getElementById('script-works-empty');

        if (!listContainer || !emptyState) return;

        if (scriptWorks.length === 0) {
            listContainer.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        listContainer.style.display = 'grid';
        emptyState.style.display = 'none';

        listContainer.innerHTML = '';
        scriptWorks.forEach(work => {
            const card = this.createScriptWorkCard(work);
            listContainer.appendChild(card);
        });
    },

    createScriptWorkCard(work) {
        const card = document.createElement('div');
        card.className = 'script-work-card';
        card.dataset.id = work.id;

        const statusLabels = {
            'draft': '草稿',
            'generating': '生成中',
            'completed': '已完成',
            'failed': '失败'
        };

        card.innerHTML = `
            <div class="script-work-header">
                <h4>${work.title}</h4>
                <span class="status-badge ${work.status}">${statusLabels[work.status] || '草稿'}</span>
            </div>
            <p class="script-work-description">${work.description || '暂无描述'}</p>
            <div class="script-work-footer">
                <span class="chapter-count">${work.chapter_count || 0} 个章节</span>
                <div class="script-work-actions">
                    <button class="btn-secondary btn-sm edit-btn" title="编辑">✏️ 编辑</button>
                    <button class="btn-secondary btn-sm delete-btn" title="删除">🗑️</button>
                </div>
            </div>
        `;

        card.addEventListener('click', (e) => {
            if (e.target.closest('.edit-btn') || e.target.closest('.delete-btn')) {
                return;
            }
            this.openScriptWork(work.id);
        });

        const editBtn = card.querySelector('.edit-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openScriptWork(work.id);
            });
        }

        const deleteBtn = card.querySelector('.delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteScriptWork(work);
            });
        }

        return card;
    },

    async openScriptWork(scriptWorkId) {
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.get(`/api/script-works/${scriptWorkId}`);
            if (response.ok) {
                this.currentScriptWork = await response.json();
                this.currentScriptWorkId = scriptWorkId;
                this.showScriptEditor();
                this.renderScriptWorkDetail();
            } else {
                showError('加载失败', '无法加载脚本作品详情');
            }
        } catch (error) {
            console.error('加载脚本作品详情失败:', error);
            showError('加载失败', '无法加载脚本作品详情');
        }
    },

    renderScriptWorkDetail() {
        const work = this.currentScriptWork;
        if (!work) return;

        const titleEl = document.getElementById('editor-script-title');
        if (titleEl) {
            titleEl.textContent = work.title;
        }

        const outlineEl = document.getElementById('outline-editor');
        if (outlineEl) {
            outlineEl.value = work.outline || '';
        }

        const charactersEl = document.getElementById('characters-editor');
        if (charactersEl) {
            charactersEl.value = work.characters || '';
        }

        this.renderChapters(work.chapters || []);
    },

    renderChapters(chapters) {
        const listContainer = document.getElementById('chapters-list');
        if (!listContainer) return;

        listContainer.innerHTML = '';

        if (chapters.length === 0) {
            listContainer.innerHTML = '<p class="empty-text">暂无章节，请添加章节</p>';
            return;
        }

        chapters.sort((a, b) => a.chapter_number - b.chapter_number);

        chapters.forEach(chapter => {
            const item = this.createChapterItem(chapter);
            listContainer.appendChild(item);
        });
    },

    createChapterItem(chapter) {
        const item = document.createElement('div');
        item.className = 'chapter-item';
        item.dataset.id = chapter.id;

        const statusLabels = {
            'draft': '草稿',
            'generating': '生成中',
            'completed': '已完成',
            'failed': '失败'
        };

        item.innerHTML = `
            <div class="chapter-info">
                <span class="chapter-number">第${chapter.chapter_number}集</span>
                <span class="chapter-title">${chapter.title}</span>
            </div>
            <div class="chapter-status">
                <span class="status-badge ${chapter.status}">${statusLabels[chapter.status] || '草稿'}</span>
            </div>
            <div class="chapter-actions">
                <button class="btn-secondary btn-sm edit-chapter-btn" title="编辑">✏️</button>
                <button class="btn-secondary btn-sm delete-chapter-btn" title="删除">🗑️</button>
            </div>
        `;

        item.addEventListener('click', (e) => {
            if (e.target.closest('.edit-chapter-btn') || e.target.closest('.delete-chapter-btn')) {
                return;
            }
            this.openChapterEditor(chapter);
        });

        const editBtn = item.querySelector('.edit-chapter-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openChapterEditor(chapter);
            });
        }

        const deleteBtn = item.querySelector('.delete-chapter-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteChapter(chapter);
            });
        }

        return item;
    },

    openChapterEditor(chapter) {
        this.currentChapterId = chapter.id;

        const chapterTitleEl = document.getElementById('chapter-editor-title');
        if (chapterTitleEl) {
            chapterTitleEl.textContent = `第${chapter.chapter_number}集: ${chapter.title}`;
        }

        const chapterOutlineEl = document.getElementById('chapter-outline-editor');
        if (chapterOutlineEl) {
            chapterOutlineEl.value = chapter.outline || '';
        }

        const chapterContentEl = document.getElementById('chapter-content-editor');
        if (chapterContentEl) {
            chapterContentEl.value = chapter.content || '';
        }

        this.showChapterEditor();
    },

    showCreateScriptModal() {
        const modal = document.getElementById('create-script-modal');
        const overlay = document.getElementById('script-modal-overlay');
        if (modal) modal.style.display = 'block';
        if (overlay) overlay.style.display = 'block';
    },

    hideCreateScriptModal() {
        const modal = document.getElementById('create-script-modal');
        const overlay = document.getElementById('script-modal-overlay');
        const form = document.getElementById('create-script-form');
        if (modal) modal.style.display = 'none';
        if (overlay) overlay.style.display = 'none';
        if (form) form.reset();
    },

    async handleCreateScript(e) {
        e.preventDefault();

        const title = document.getElementById('script-title')?.value.trim();
        const description = document.getElementById('script-description')?.value.trim();

        if (!title) {
            showError('创建失败', '请输入脚本作品名称');
            return;
        }

        if (!this.currentProjectId) {
            showError('创建失败', '请先选择项目');
            return;
        }

        const token = StorageService.getToken();
        if (!token) return;

        const submitBtn = document.getElementById('create-script-submit');
        const originalText = submitBtn ? submitBtn.textContent : '';

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

            const response = await ApiService.post('/api/script-works', requestData);

            if (response.ok) {
                this.hideCreateScriptModal();
                showSuccess('创建成功', '脚本作品创建成功');
                this.loadScriptWorks();
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('创建失败', errorData.detail || '创建脚本作品失败');
            }
        } catch (error) {
            console.error('创建脚本作品失败:', error);
            showError('创建失败', '网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    async deleteScriptWork(work) {
        const confirmed = await showConfirmDialog({
            title: '确认删除',
            message: `确定要删除脚本作品 "${work.title}" 吗？此操作无法撤销。`,
            type: 'danger',
            confirmText: '删除',
            cancelText: '取消'
        });

        if (!confirmed) return;

        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.delete(`/api/script-works/${work.id}`);
            if (response.ok) {
                showSuccess('删除成功', '脚本作品已删除');
                this.loadScriptWorks();
            } else {
                showError('删除失败', '删除脚本作品失败');
            }
        } catch (error) {
            console.error('删除脚本作品失败:', error);
            showError('删除失败', '网络错误，请稍后重试');
        }
    },

    async saveOutline() {
        if (!this.currentScriptWorkId) return;

        const outlineEl = document.getElementById('outline-editor');
        if (!outlineEl) return;

        const outline = outlineEl.value;
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await fetch(`/api/script-works/${this.currentScriptWorkId}/outline`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ outline: outline })
            });

            if (response.ok) {
                if (this.currentScriptWork) {
                    this.currentScriptWork.outline = outline;
                }
                showSuccess('保存成功', '大纲已保存');
            } else {
                showError('保存失败', '保存大纲失败');
            }
        } catch (error) {
            console.error('保存大纲失败:', error);
            showError('保存失败', '网络错误，请稍后重试');
        }
    },

    async generateOutline() {
        if (this.isGenerating) {
            showError('生成中', '请等待当前生成完成');
            return;
        }

        if (!this.currentScriptWorkId) return;

        const confirmed = await showConfirmDialog({
            title: '确认生成',
            message: 'AI将根据作品标题和描述生成大纲。注意：这将覆盖当前编辑区的内容。建议先保存已编辑的内容。是否继续？',
            type: 'warning',
            confirmText: '继续生成',
            cancelText: '取消'
        });

        if (!confirmed) return;

        const token = StorageService.getToken();
        if (!token) return;

        this.isGenerating = true;
        this.setGeneratingState('outline', true);

        try {
            const response = await fetch('/api/script-generation/generate-outline', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    script_work_id: this.currentScriptWorkId
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.content) {
                    const outlineEl = document.getElementById('outline-editor');
                    if (outlineEl) {
                        outlineEl.value = data.content;
                    }
                    showSuccess('生成成功', `大纲已生成 (${data.model || 'AI模型'})`);
                } else {
                    showError('生成失败', data.error_msg || '生成大纲失败');
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('生成失败', errorData.detail || '生成大纲失败');
            }
        } catch (error) {
            console.error('生成大纲失败:', error);
            showError('生成失败', '网络错误，请稍后重试');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState('outline', false);
        }
    },

    async saveCharacters() {
        if (!this.currentScriptWorkId) return;

        const charactersEl = document.getElementById('characters-editor');
        if (!charactersEl) return;

        const characters = charactersEl.value;
        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await fetch(`/api/script-works/${this.currentScriptWorkId}/characters`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ characters: characters })
            });

            if (response.ok) {
                if (this.currentScriptWork) {
                    this.currentScriptWork.characters = characters;
                }
                showSuccess('保存成功', '人物设定已保存');
            } else {
                showError('保存失败', '保存人物设定失败');
            }
        } catch (error) {
            console.error('保存人物设定失败:', error);
            showError('保存失败', '网络错误，请稍后重试');
        }
    },

    async generateCharacters() {
        if (this.isGenerating) {
            showError('生成中', '请等待当前生成完成');
            return;
        }

        if (!this.currentScriptWorkId) return;

        const confirmed = await showConfirmDialog({
            title: '确认生成',
            message: 'AI将根据作品信息和已保存的大纲生成人物设定。注意：这将覆盖当前编辑区的内容。建议先保存已编辑的内容。是否继续？',
            type: 'warning',
            confirmText: '继续生成',
            cancelText: '取消'
        });

        if (!confirmed) return;

        const token = StorageService.getToken();
        if (!token) return;

        this.isGenerating = true;
        this.setGeneratingState('characters', true);

        try {
            const response = await fetch('/api/script-generation/generate-characters', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    script_work_id: this.currentScriptWorkId
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.content) {
                    const charactersEl = document.getElementById('characters-editor');
                    if (charactersEl) {
                        charactersEl.value = data.content;
                    }
                    showSuccess('生成成功', `人物设定已生成 (${data.model || 'AI模型'})`);
                } else {
                    showError('生成失败', data.error_msg || '生成人物设定失败');
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('生成失败', errorData.detail || '生成人物设定失败');
            }
        } catch (error) {
            console.error('生成人物设定失败:', error);
            showError('生成失败', '网络错误，请稍后重试');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState('characters', false);
        }
    },

    setGeneratingState(type, isGenerating) {
        let btnId, icon;
        if (type === 'outline') {
            btnId = 'generate-outline-btn';
        } else if (type === 'characters') {
            btnId = 'generate-characters-btn';
        } else if (type === 'chapter') {
            btnId = 'generate-chapter-btn';
        }

        const btn = document.getElementById(btnId);
        if (btn) {
            btn.disabled = isGenerating;
            if (isGenerating) {
                btn.innerHTML = '⏳ 生成中...';
            } else {
                if (type === 'outline') {
                    btn.innerHTML = '✨ AI生成大纲';
                } else if (type === 'characters') {
                    btn.innerHTML = '✨ AI生成人设';
                } else if (type === 'chapter') {
                    btn.innerHTML = '✨ AI生成内容';
                }
            }
        }
    },

    showCreateChapterModal() {
        const modal = document.getElementById('create-chapter-modal');
        const overlay = document.getElementById('chapter-modal-overlay');
        if (modal) modal.style.display = 'block';
        if (overlay) overlay.style.display = 'block';
    },

    hideCreateChapterModal() {
        const modal = document.getElementById('create-chapter-modal');
        const overlay = document.getElementById('chapter-modal-overlay');
        const form = document.getElementById('create-chapter-form');
        if (modal) modal.style.display = 'none';
        if (overlay) overlay.style.display = 'none';
        if (form) form.reset();
    },

    async handleCreateChapter(e) {
        e.preventDefault();

        const title = document.getElementById('chapter-title')?.value.trim();
        const chapterNumber = document.getElementById('chapter-number')?.value;
        const chapterOutline = document.getElementById('chapter-outline-input')?.value.trim();

        if (!title) {
            showError('创建失败', '请输入章节名称');
            return;
        }

        if (!this.currentScriptWorkId) return;

        const token = StorageService.getToken();
        if (!token) return;

        const submitBtn = document.getElementById('create-chapter-submit');
        const originalText = submitBtn ? submitBtn.textContent : '';

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

            if (chapterOutline) {
                requestData.outline = chapterOutline;
            }

            const response = await ApiService.post(`/api/script-works/${this.currentScriptWorkId}/chapters`, requestData);

            if (response.ok) {
                this.hideCreateChapterModal();
                showSuccess('创建成功', '章节创建成功');
                await this.openScriptWork(this.currentScriptWorkId);
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('创建失败', errorData.detail || '创建章节失败');
            }
        } catch (error) {
            console.error('创建章节失败:', error);
            showError('创建失败', '网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },

    async deleteChapter(chapter) {
        const confirmed = await showConfirmDialog({
            title: '确认删除',
            message: `确定要删除第${chapter.chapter_number}集 "${chapter.title}" 吗？此操作无法撤销。`,
            type: 'danger',
            confirmText: '删除',
            cancelText: '取消'
        });

        if (!confirmed) return;

        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.delete(`/api/script-works/${this.currentScriptWorkId}/chapters/${chapter.id}`);
            if (response.ok) {
                showSuccess('删除成功', '章节已删除');
                await this.openScriptWork(this.currentScriptWorkId);
            } else {
                showError('删除失败', '删除章节失败');
            }
        } catch (error) {
            console.error('删除章节失败:', error);
            showError('删除失败', '网络错误，请稍后重试');
        }
    },

    async saveChapter() {
        if (!this.currentScriptWorkId || !this.currentChapterId) return;

        const outlineEl = document.getElementById('chapter-outline-editor');
        const contentEl = document.getElementById('chapter-content-editor');
        if (!outlineEl || !contentEl) return;

        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await fetch(`/api/script-works/${this.currentScriptWorkId}/chapters/${this.currentChapterId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    outline: outlineEl.value,
                    content: contentEl.value
                })
            });

            if (response.ok) {
                showSuccess('保存成功', '章节内容已保存');
            } else {
                showError('保存失败', '保存章节内容失败');
            }
        } catch (error) {
            console.error('保存章节内容失败:', error);
            showError('保存失败', '网络错误，请稍后重试');
        }
    },

    async generateChapterContent() {
        if (this.isGenerating) {
            showError('生成中', '请等待当前生成完成');
            return;
        }

        if (!this.currentScriptWorkId || !this.currentChapterId) return;

        const confirmed = await showConfirmDialog({
            title: '确认生成',
            message: 'AI将根据大纲、人物设定和章节信息生成内容。注意：这将覆盖当前内容编辑区的内容。建议先保存已编辑的内容。是否继续？',
            type: 'warning',
            confirmText: '继续生成',
            cancelText: '取消'
        });

        if (!confirmed) return;

        const token = StorageService.getToken();
        if (!token) return;

        this.isGenerating = true;
        this.setGeneratingState('chapter', true);

        try {
            const response = await fetch('/api/script-generation/generate-chapter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    script_work_id: this.currentScriptWorkId,
                    chapter_id: this.currentChapterId
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.content) {
                    const contentEl = document.getElementById('chapter-content-editor');
                    if (contentEl) {
                        contentEl.value = data.content;
                    }
                    showSuccess('生成成功', `章节内容已生成 (${data.model || 'AI模型'})`);
                } else {
                    showError('生成失败', data.error_msg || '生成章节内容失败');
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('生成失败', errorData.detail || '生成章节内容失败');
            }
        } catch (error) {
            console.error('生成章节内容失败:', error);
            showError('生成失败', '网络错误，请稍后重试');
        } finally {
            this.isGenerating = false;
            this.setGeneratingState('chapter', false);
        }
    },

    showScriptList() {
        const listView = document.getElementById('script-list-view');
        const editorView = document.getElementById('script-editor-view');

        if (listView) listView.style.display = 'block';
        if (editorView) editorView.style.display = 'none';

        this.currentScriptWorkId = null;
        this.currentScriptWork = null;
    },

    showScriptEditor() {
        const listView = document.getElementById('script-list-view');
        const editorView = document.getElementById('script-editor-view');
        const chapterEditorView = document.getElementById('chapter-editor-view');

        if (listView) listView.style.display = 'none';
        if (editorView) editorView.style.display = 'block';
        if (chapterEditorView) chapterEditorView.style.display = 'none';

        this.switchEditorTab('outline');
    },

    showChapterEditor() {
        const editorView = document.getElementById('script-editor-view');
        const chapterEditorView = document.getElementById('chapter-editor-view');

        if (editorView) editorView.style.display = 'none';
        if (chapterEditorView) chapterEditorView.style.display = 'block';
    },

    showOverview() {
        this.showScriptEditor();
    },

    switchEditorTab(tab) {
        document.querySelectorAll('.editor-tab').forEach(tabEl => {
            tabEl.classList.remove('active');
            if (tabEl.dataset.tab === tab) {
                tabEl.classList.add('active');
            }
        });

        document.querySelectorAll('.editor-panel').forEach(panel => {
            panel.style.display = 'none';
        });

        const targetPanel = document.getElementById(`${tab}-panel`);
        if (targetPanel) {
            targetPanel.style.display = 'block';
        }
    }
};

function switchEditorTab(tab) {
    ScriptWorkshopModule.switchEditorTab(tab);
}
