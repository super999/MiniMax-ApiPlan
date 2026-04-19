const ProjectsModule = {
    async loadProjects() {
        const token = StorageService.getToken();
        if (!token) return [];

        try {
            const response = await ApiService.get('/api/projects');

            if (response.ok) {
                const projects = await response.json();
                this.renderProjects(projects);
                this.updateProjectStats(projects.length);
                return projects;
            } else if (response.status === 401) {
                StorageService.clearToken();
                AppState.reset();
                return [];
            }
        } catch (error) {
            console.error('加载项目列表失败:', error);
            this.renderProjects([]);
            return [];
        }
        return [];
    },
    
    renderProjects(projects) {
        const emptyState = document.getElementById('projects-empty-state');
        const projectsList = document.getElementById('projects-list');

        if (!emptyState || !projectsList) return;

        if (projects.length === 0) {
            emptyState.style.display = 'flex';
            projectsList.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            projectsList.style.display = 'grid';
            
            projectsList.innerHTML = '';
            projects.forEach(project => {
                const projectCard = this.createProjectCard(project);
                projectsList.appendChild(projectCard);
            });
        }
    },
    
    createProjectCard(project) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.projectId = project.id;

        const statusLabels = {
            'planning': '规划中',
            'active': '进行中',
            'completed': '已完成'
        };

        const statusClasses = {
            'planning': 'planning',
            'active': 'active',
            'completed': 'completed'
        };

        const formatDate = (dateString) => {
            if (!dateString) return '未知';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        };

        card.innerHTML = `
            <div class="project-card-header">
                <div class="project-icon">📁</div>
                <span class="project-status-badge ${statusClasses[project.status] || 'planning'}">
                    ${statusLabels[project.status] || '规划中'}
                </span>
            </div>
            <h4>${project.name}</h4>
            <p class="project-description">${project.description || '暂无描述'}</p>
            <div class="project-footer">
                <span>创建于: ${formatDate(project.created_at)}</span>
                <div class="project-actions">
                    <button class="project-action-btn" title="编辑">✏️</button>
                    <button class="project-action-btn delete" title="删除">🗑️</button>
                </div>
            </div>
        `;

        card.addEventListener('click', (e) => {
            if (e.target.closest('.project-action-btn')) {
                return;
            }
            this.handleProjectClick(project);
        });

        const editBtn = card.querySelector('.project-action-btn:not(.delete)');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleEditProject(project);
            });
        }

        const deleteBtn = card.querySelector('.project-action-btn.delete');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleDeleteProject(project);
            });
        }

        return card;
    },
    
    updateProjectStats(count) {
        const statProjects = document.getElementById('stat-projects');
        if (statProjects) {
            statProjects.textContent = count;
        }
    },
    
    handleProjectClick(project) {
        // 跳转到脚本工坊页面，并加载该项目
        if (window.ScriptWorksModule) {
            // 先导航到脚本工坊页面
            NavigationModule.navigateTo('script');
            // 然后加载项目
            setTimeout(() => {
                window.ScriptWorksModule.navigateToProject(project.id);
            }, 100);
        } else {
            console.log('点击项目:', project);
        }
    },
    
    handleEditProject(project) {
        console.log('编辑项目:', project);
    },
    
    async handleDeleteProject(project) {
        const confirmed = await showConfirmDialog({
            title: '确认删除',
            message: `确定要删除项目 "${project.name}" 吗？此操作无法撤销。`,
            type: 'danger',
            confirmText: '删除',
            cancelText: '取消'
        });

        if (!confirmed) {
            return;
        }

        const token = StorageService.getToken();
        if (!token) return;

        try {
            const response = await ApiService.delete(`/api/projects/${project.id}`);

            if (response.ok) {
                const data = await response.json();
                showSuccess('操作成功', data.message || '项目删除成功');
                this.loadProjects();
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError('操作失败', errorData.detail || '删除项目失败');
            }
        } catch (error) {
            console.error('删除项目失败:', error);
            showError('操作失败', '删除项目失败，请稍后重试');
        }
    },
    
    async handleCreateProject(e) {
        e.preventDefault();
        
        const name = document.getElementById('project-name')?.value.trim();
        const description = document.getElementById('project-description')?.value.trim();
        const status = document.getElementById('project-status')?.value;
        
        if (!name) {
            showCreateProjectError('请输入项目名称');
            return;
        }
        
        if (name.length > 100) {
            showCreateProjectError('项目名称不能超过100个字符');
            return;
        }
        
        const token = StorageService.getToken();
        if (!token) {
            closeCreateProjectModal();
            return;
        }
        
        const submitBtn = document.getElementById('create-project-btn');
        const originalText = submitBtn ? submitBtn.textContent : '';
        
        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '创建中...';
            }
            
            const requestData = {
                name: name,
                status: status || 'planning'
            };
            
            if (description) {
                requestData.description = description;
            }
            
            const response = await ApiService.post('/api/projects', requestData);
            
            const data = await response.json();
            
            if (response.ok) {
                closeCreateProjectModal();
                showSuccess('操作成功', '项目创建成功！');
                this.loadProjects();
            } else {
                showCreateProjectError(data.detail || '创建项目失败，请重试');
            }
        } catch (error) {
            console.error('创建项目失败:', error);
            showCreateProjectError('网络错误，请稍后重试');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },
    
    bindEvents() {
        const quickCreateProject = document.getElementById('quick-create-project');
        if (quickCreateProject) {
            quickCreateProject.addEventListener('click', openCreateProjectModal);
        }
        
        const headerCreateProject = document.getElementById('header-create-project');
        if (headerCreateProject) {
            headerCreateProject.addEventListener('click', openCreateProjectModal);
        }
        
        const emptyCreateProject = document.getElementById('empty-create-project');
        if (emptyCreateProject) {
            emptyCreateProject.addEventListener('click', openCreateProjectModal);
        }
        
        const closeCreateProject = document.getElementById('close-create-project');
        if (closeCreateProject) {
            closeCreateProject.addEventListener('click', closeCreateProjectModal);
        }
        
        const createProjectForm = document.getElementById('create-project-form');
        if (createProjectForm) {
            createProjectForm.addEventListener('submit', (e) => this.handleCreateProject(e));
        }
    }
};
