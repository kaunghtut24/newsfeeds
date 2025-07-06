/**
 * User Dashboard JavaScript
 * Handles user's personal news source management and dashboard functionality
 */

class UserDashboard {
    constructor() {
        this.sessionToken = localStorage.getItem('session_token');
        this.currentUser = null;
        this.init();
    }
    
    init() {
        this.loadUserInfo();
        this.loadUserSources();
        this.setupEventListeners();
    }
    
    async loadUserInfo() {
        try {
            const response = await this.apiCall('/api/user/profile');
            if (response.success) {
                this.currentUser = response.user;
                this.updateUserInfo(response.user);
            }
        } catch (error) {
            console.error('Error loading user info:', error);
        }
    }
    
    updateUserInfo(user) {
        document.getElementById('userName').textContent = user.username;
        document.getElementById('userEmail').textContent = user.email;
        document.getElementById('accountStatus').textContent = user.status;
        document.getElementById('memberSince').textContent = this.formatDate(user.created_at);
        document.getElementById('lastLogin').textContent = this.formatDate(user.last_login);

        // Show admin link if user is admin
        if (user.role === 'admin') {
            const adminLink = document.getElementById('adminLinkHeader');
            if (adminLink) {
                adminLink.style.display = 'inline-block';
            }
        }
    }
    
    async loadUserSources() {
        try {
            const response = await this.apiCall('/api/user/source-preferences');
            if (response.success) {
                // Store the dynamic limits from admin settings
                this.maxSources = response.max_allowed || 6; // Default to 6 if not provided

                this.displayUserSourcePreferences(response.source_details || [], response.count || 0);
                this.updateSourceCount(response.count || 0);
            } else {
                console.error('Failed to load user sources:', response.error);
                document.getElementById('sourcesList').innerHTML =
                    '<div class="empty-state">Error loading news sources</div>';
            }
        } catch (error) {
            console.error('Error loading user sources:', error);
            document.getElementById('sourcesList').innerHTML =
                '<div class="empty-state">Error loading news sources</div>';
        }
    }

    updateSourceCount(count) {
        const sourceCountEl = document.getElementById('sourceCount');
        if (sourceCountEl) {
            sourceCountEl.textContent = count;
        }

        // Update the max sources display in the HTML
        const maxSourcesEl = document.getElementById('maxSources');
        if (maxSourcesEl) {
            const maxSources = this.maxSources || 6; // Use dynamic limit or default
            maxSourcesEl.textContent = maxSources;
        }

        const addBtn = document.getElementById('addSourceBtn');
        if (addBtn) {
            // Use dynamic max sources from admin settings
            const maxSources = this.maxSources || 6; // Use dynamic limit or default
            if (count >= maxSources) {
                addBtn.disabled = true;
                addBtn.textContent = `📋 Limit Reached (${count}/${maxSources})`;
            } else {
                addBtn.disabled = false;
                addBtn.textContent = '📋 Select Sources';
            }
        }
    }

    displayUserSourcePreferences(sourceDetails, count) {
        const container = document.getElementById('sourcesList');

        if (!sourceDetails || sourceDetails.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No news sources selected yet.</p>
                    <p>Click "Select Sources" to choose from available sources.</p>
                </div>
            `;
            return;
        }

        const sourcesHtml = sourceDetails.map(source => `
            <div class="source-item">
                <div class="source-info">
                    <h4>${source.name}</h4>
                    <p class="source-url">${source.url}</p>
                    <span class="source-category">${source.category}</span>
                </div>
                <div class="source-actions">
                    <button onclick="userDashboard.removeSourcePreference('${source.name}')"
                            class="btn btn-danger btn-sm">
                        🗑️ Remove
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = sourcesHtml;
    }

    async showSourceSelector() {
        try {
            // Get available global sources
            const response = await this.apiCall('/api/sources');
            if (response.success) {
                this.displaySourceSelector(response.sources);
            } else {
                this.showAlert('Failed to load available sources', 'error');
            }
        } catch (error) {
            console.error('Error loading sources:', error);
            this.showAlert('Error loading available sources', 'error');
        }
    }

    displaySourceSelector(sources) {
        // Create modal for source selection
        const modalHtml = `
            <div class="modal-overlay" id="sourceSelectorModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>📋 Select News Sources</h3>
                        <button onclick="userDashboard.closeSourceSelector()" class="modal-close">×</button>
                    </div>
                    <div class="modal-body">
                        <p>Choose from available news sources (up to 3 sources):</p>
                        <div class="source-selector-list">
                            ${sources.map(source => `
                                <div class="source-selector-item ${source.user_selected ? 'selected' : ''}">
                                    <div class="source-info">
                                        <h4>${source.name}</h4>
                                        <p class="source-description">${source.description}</p>
                                        <span class="source-category">${source.category}</span>
                                    </div>
                                    <div class="source-actions">
                                        ${source.user_selected ?
                                            `<button onclick="userDashboard.removeSourcePreference('${source.name}')"
                                                    class="btn btn-danger btn-sm">Remove</button>` :
                                            `<button onclick="userDashboard.addSourcePreference('${source.name}')"
                                                    class="btn btn-success btn-sm">Add</button>`
                                        }
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button onclick="userDashboard.closeSourceSelector()" class="btn btn-secondary">Close</button>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    closeSourceSelector() {
        const modal = document.getElementById('sourceSelectorModal');
        if (modal) {
            modal.remove();
        }
    }

    async addSourcePreference(sourceName) {
        try {
            const response = await this.apiCall('/api/user/source-preferences', 'POST', {
                source_name: sourceName
            });

            if (response.success) {
                this.showAlert(`Added ${sourceName} to your sources!`, 'success');
                await this.loadUserSources();
                this.closeSourceSelector();
            } else {
                this.showAlert('Failed to add source: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error adding source preference:', error);
            this.showAlert('Error adding source', 'error');
        }
    }

    async removeSourcePreference(sourceName) {
        try {
            const response = await this.apiCall(`/api/user/source-preferences/${sourceName}`, 'DELETE');

            if (response.success) {
                this.showAlert(`Removed ${sourceName} from your sources!`, 'success');
                await this.loadUserSources();
                // Refresh source selector if open
                const modal = document.getElementById('sourceSelectorModal');
                if (modal) {
                    this.closeSourceSelector();
                    await this.showSourceSelector();
                }
            } else {
                this.showAlert('Failed to remove source: ' + response.error, 'error');
            }
        } catch (error) {
            console.error('Error removing source preference:', error);
            this.showAlert('Error removing source', 'error');
        }
    }
    
    displaySources(sources) {
        const container = document.getElementById('sourcesList');
        
        if (!sources || sources.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📰</div>
                    <h3>No news sources yet</h3>
                    <p>Add your first news source to get started with personalized news</p>
                    <button class="btn btn-success" onclick="userDashboard.showAddSourceModal()">
                        Add Your First Source
                    </button>
                </div>
            `;
            return;
        }
        
        const sourcesHtml = `
            <ul class="sources-list">
                ${sources.map(source => `
                    <li class="source-item">
                        <div class="source-info">
                            <div class="source-name">${source.name}</div>
                            <div class="source-url">${source.url}</div>
                            <span class="source-category">${source.category}</span>
                        </div>
                        <div class="source-actions">
                            <button class="btn btn-secondary btn-sm" 
                                    onclick="userDashboard.editSource('${source.source_id}')">
                                Edit
                            </button>
                            <button class="btn btn-danger btn-sm" 
                                    onclick="userDashboard.deleteSource('${source.source_id}')">
                                Delete
                            </button>
                        </div>
                    </li>
                `).join('')}
            </ul>
        `;
        
        container.innerHTML = sourcesHtml;
    }
    
    showAddSourceModal() {
        document.getElementById('addSourceModal').style.display = 'block';
        document.getElementById('addSourceForm').reset();
    }
    
    hideAddSourceModal() {
        document.getElementById('addSourceModal').style.display = 'none';
    }
    
    showEditSourceModal() {
        document.getElementById('editSourceModal').style.display = 'block';
    }
    
    hideEditSourceModal() {
        document.getElementById('editSourceModal').style.display = 'none';
    }
    
    async editSource(sourceId) {
        try {
            const response = await this.apiCall(`/api/user/sources/${sourceId}`);
            if (response.success) {
                const source = response.source;
                document.getElementById('editSourceId').value = source.source_id;
                document.getElementById('editSourceName').value = source.name;
                document.getElementById('editSourceUrl').value = source.url;
                document.getElementById('editSourceCategory').value = source.category;
                this.showEditSourceModal();
            }
        } catch (error) {
            this.showAlert('Error loading source details', 'error');
        }
    }
    
    async deleteSource(sourceId) {
        if (!confirm('Are you sure you want to delete this news source?')) return;
        
        try {
            const response = await this.apiCall(`/api/user/sources/${sourceId}`, 'DELETE');
            if (response.success) {
                this.showAlert('News source deleted successfully', 'success');
                this.loadUserSources();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error deleting news source', 'error');
        }
    }
    
    async refreshNewsFeed() {
        const container = document.getElementById('newsFeed');
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                Refreshing your news feed...
            </div>
        `;
        
        try {
            const response = await this.apiCall('/api/user/news-feed');
            if (response.success) {
                this.displayNewsFeed(response.articles);
            } else {
                container.innerHTML = '<div class="empty-state">Error loading news feed</div>';
            }
        } catch (error) {
            container.innerHTML = '<div class="empty-state">Error loading news feed</div>';
        }
    }
    
    displayNewsFeed(articles) {
        const container = document.getElementById('newsFeed');
        
        if (!articles || articles.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📰</div>
                    <h3>No news articles yet</h3>
                    <p>Add news sources to see your personalized feed here</p>
                </div>
            `;
            return;
        }
        
        const articlesHtml = articles.slice(0, 10).map(article => `
            <div style="padding: 15px 0; border-bottom: 1px solid #e1e5e9;">
                <h4 style="margin: 0 0 8px 0; color: #333;">
                    <a href="${article.url}" target="_blank" style="text-decoration: none; color: inherit;">
                        ${article.title}
                    </a>
                </h4>
                <p style="margin: 0 0 8px 0; color: #666; font-size: 14px; line-height: 1.4;">
                    ${article.summary || article.description || 'No summary available'}
                </p>
                <div style="font-size: 12px; color: #888;">
                    <span>${article.source}</span> • 
                    <span>${this.formatDate(article.published_date)}</span>
                    ${article.category ? ` • <span class="source-category">${article.category}</span>` : ''}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = articlesHtml;
    }
    
    setupEventListeners() {
        // Add source form
        document.getElementById('addSourceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleAddSource(e);
        });
        
        // Edit source form
        document.getElementById('editSourceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleEditSource(e);
        });
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
        
        // News feed functionality moved to main application
    }
    
    async handleAddSource(e) {
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            url: formData.get('url'),
            category: formData.get('category'),
            is_custom: true  // Mark as custom source for auto-add to global
        };

        try {
            // Use enhanced sources API for custom source addition
            const response = await this.apiCall('/api/user/enhanced-sources', 'POST', data);
            if (response.success) {
                this.showAlert('✅ Custom news source added successfully! It will be available globally for other users too.', 'success');

                setTimeout(() => {
                    this.showAlert('💡 Tip: Visit the main application and click "Fetch News" to get articles from your new source!', 'info');
                }, 2000);

                this.hideAddSourceModal();
                this.loadUserSources();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error adding custom news source', 'error');
        }
    }
    
    async handleEditSource(e) {
        const formData = new FormData(e.target);
        const sourceId = formData.get('sourceId');
        const data = {
            name: formData.get('name'),
            url: formData.get('url'),
            category: formData.get('category')
        };
        
        try {
            const response = await this.apiCall(`/api/user/sources/${sourceId}`, 'PUT', data);
            if (response.success) {
                this.showAlert('News source updated successfully', 'success');
                this.hideEditSourceModal();
                this.loadUserSources();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error updating news source', 'error');
        }
    }
    
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.sessionToken}`
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        return await response.json();
    }
    
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alertHtml = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        alertContainer.innerHTML = alertHtml;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Never';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}

// Initialize user dashboard when page loads
let userDashboard;
document.addEventListener('DOMContentLoaded', () => {
    userDashboard = new UserDashboard();
});
