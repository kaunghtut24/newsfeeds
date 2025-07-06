/**
 * Admin Dashboard JavaScript
 * Handles user management, approvals, and admin operations
 */

class AdminDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.sessionToken = localStorage.getItem('session_token');
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.loadDashboardData();
        this.setupEventListeners();
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                if (section) {
                    this.showSection(section);
                }
            });
        });
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Show selected section
        const targetSection = document.getElementById(sectionName + 'Section');
        if (targetSection) {
            targetSection.style.display = 'block';
        }
        
        // Add active class to current nav link
        const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        switch (sectionName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'pending':
                this.loadPendingUsers();
                break;
            case 'audit':
                this.loadAuditLog();
                break;
        }
    }
    
    async loadDashboardData() {
        try {
            const response = await this.apiCall('/api/admin/stats');
            if (response.success) {
                this.updateStats(response.stats);
            }
            
            const activityResponse = await this.apiCall('/api/admin/recent-activity');
            if (activityResponse.success) {
                this.updateRecentActivity(activityResponse.activities);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    updateStats(stats) {
        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('activeUsers').textContent = stats.active_users || 0;
        document.getElementById('pendingUsers').textContent = stats.pending_users || 0;
        document.getElementById('inactiveUsers').textContent = stats.inactive_users || 0;
    }
    
    updateRecentActivity(activities) {
        const container = document.getElementById('recentActivity');
        
        if (!activities || activities.length === 0) {
            container.innerHTML = '<div class="empty-state">No recent activity</div>';
            return;
        }
        
        const activityHtml = activities.map(activity => `
            <div class="activity-item" style="padding: 10px 0; border-bottom: 1px solid #e1e5e9;">
                <div style="font-weight: 500;">${this.formatActivityAction(activity.action)}</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">
                    ${this.formatDate(activity.timestamp)} by ${activity.user_id}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = activityHtml;
    }
    
    async loadUsers() {
        try {
            const response = await this.apiCall('/api/admin/users');
            if (response.success) {
                this.displayUsersTable(response.users);
            }
        } catch (error) {
            console.error('Error loading users:', error);
            document.getElementById('usersTable').innerHTML = 
                '<div class="empty-state">Error loading users</div>';
        }
    }
    
    async loadPendingUsers() {
        try {
            const response = await this.apiCall('/api/admin/pending-users');
            if (response.success) {
                this.displayPendingTable(response.users);
            }
        } catch (error) {
            console.error('Error loading pending users:', error);
            document.getElementById('pendingTable').innerHTML = 
                '<div class="empty-state">Error loading pending users</div>';
        }
    }
    
    displayUsersTable(users) {
        const container = document.getElementById('usersTable');
        
        if (!users || users.length === 0) {
            container.innerHTML = '<div class="empty-state">No users found</div>';
            return;
        }
        
        const tableHtml = `
            <table class="user-table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.role}</td>
                            <td><span class="status-badge status-${user.status}">${user.status}</span></td>
                            <td>${this.formatDate(user.created_at)}</td>
                            <td>
                                <div class="action-buttons">
                                    ${this.getUserActionButtons(user)}
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = tableHtml;
        this.setupUserActionHandlers();
    }
    
    displayPendingTable(users) {
        const container = document.getElementById('pendingTable');
        
        if (!users || users.length === 0) {
            container.innerHTML = '<div class="empty-state">No pending approvals</div>';
            return;
        }
        
        const tableHtml = `
            <table class="user-table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Registered</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${this.formatDate(user.created_at)}</td>
                            <td>
                                <div class="action-buttons">
                                    <button class="btn btn-approve" onclick="adminDashboard.approveUser('${user.user_id}')">
                                        Approve
                                    </button>
                                    <button class="btn btn-reject" onclick="adminDashboard.rejectUser('${user.user_id}')">
                                        Reject
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = tableHtml;
    }
    
    getUserActionButtons(user) {
        if (user.role === 'admin') {
            return '<span style="color: #666; font-size: 12px;">Admin user</span>';
        }
        
        let buttons = [];
        
        if (user.status === 'active') {
            buttons.push(`<button class="btn btn-deactivate" onclick="adminDashboard.deactivateUser('${user.user_id}')">Deactivate</button>`);
        } else if (user.status === 'inactive') {
            buttons.push(`<button class="btn btn-activate" onclick="adminDashboard.activateUser('${user.user_id}')">Activate</button>`);
        }
        
        buttons.push(`<button class="btn btn-delete" onclick="adminDashboard.deleteUser('${user.user_id}')">Delete</button>`);
        
        return buttons.join('');
    }
    
    async approveUser(userId) {
        if (!confirm('Are you sure you want to approve this user?')) return;
        
        try {
            const response = await this.apiCall(`/api/admin/users/${userId}/approve`, 'POST');
            if (response.success) {
                this.showAlert('User approved successfully', 'success');
                this.loadPendingUsers();
                this.loadDashboardData();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error approving user', 'error');
        }
    }
    
    async rejectUser(userId) {
        if (!confirm('Are you sure you want to reject this user?')) return;
        
        try {
            const response = await this.apiCall(`/api/admin/users/${userId}/reject`, 'POST');
            if (response.success) {
                this.showAlert('User rejected successfully', 'success');
                this.loadPendingUsers();
                this.loadDashboardData();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error rejecting user', 'error');
        }
    }
    
    async deactivateUser(userId) {
        if (!confirm('Are you sure you want to deactivate this user?')) return;
        
        try {
            const response = await this.apiCall(`/api/admin/users/${userId}/deactivate`, 'POST');
            if (response.success) {
                this.showAlert('User deactivated successfully', 'success');
                this.loadUsers();
                this.loadDashboardData();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error deactivating user', 'error');
        }
    }
    
    async activateUser(userId) {
        if (!confirm('Are you sure you want to activate this user?')) return;
        
        try {
            const response = await this.apiCall(`/api/admin/users/${userId}/activate`, 'POST');
            if (response.success) {
                this.showAlert('User activated successfully', 'success');
                this.loadUsers();
                this.loadDashboardData();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error activating user', 'error');
        }
    }
    
    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
        
        try {
            const response = await this.apiCall(`/api/admin/users/${userId}`, 'DELETE');
            if (response.success) {
                this.showAlert('User deleted successfully', 'success');
                this.loadUsers();
                this.loadDashboardData();
            } else {
                this.showAlert(response.error, 'error');
            }
        } catch (error) {
            this.showAlert('Error deleting user', 'error');
        }
    }
    
    async loadAuditLog() {
        try {
            const response = await this.apiCall('/api/admin/audit-log');
            if (response.success) {
                this.displayAuditLog(response.logs);
            }
        } catch (error) {
            console.error('Error loading audit log:', error);
            document.getElementById('auditLog').innerHTML = 
                '<div class="empty-state">Error loading audit log</div>';
        }
    }
    
    displayAuditLog(logs) {
        const container = document.getElementById('auditLog');
        
        if (!logs || logs.length === 0) {
            container.innerHTML = '<div class="empty-state">No audit log entries</div>';
            return;
        }
        
        const logHtml = logs.map(log => `
            <div class="audit-entry" style="padding: 15px; border-bottom: 1px solid #e1e5e9;">
                <div style="font-weight: 500; margin-bottom: 5px;">
                    ${this.formatActivityAction(log.action)}
                </div>
                <div style="font-size: 12px; color: #666;">
                    ${this.formatDate(log.timestamp)} by ${log.user_id}
                    ${log.target_user_id ? ` → ${log.target_user_id}` : ''}
                </div>
                ${log.details ? `<div style="font-size: 12px; color: #888; margin-top: 5px;">${JSON.stringify(log.details)}</div>` : ''}
            </div>
        `).join('');
        
        container.innerHTML = logHtml;
    }
    
    setupEventListeners() {
        // Auto-refresh dashboard every 30 seconds
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000);
    }
    
    setupUserActionHandlers() {
        // Event handlers are set up via onclick attributes in the HTML
        // This method can be used for additional event setup if needed
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
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    formatActivityAction(action) {
        const actionMap = {
            'user_registered': '👤 User registered',
            'user_login': '🔑 User logged in',
            'user_approved': '✅ User approved',
            'user_rejected': '❌ User rejected',
            'user_activated': '🟢 User activated',
            'user_deactivated': '🔴 User deactivated',
            'user_deleted': '🗑️ User deleted',
            'source_added': '📰 News source added',
            'source_updated': '📝 News source updated',
            'source_deleted': '🗑️ News source deleted'
        };
        
        return actionMap[action] || action;
    }
}

// Initialize admin dashboard when page loads
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});
