/**
 * Admin Settings Management JavaScript
 * Handles all admin settings functionality
 */

class AdminSettings {
    constructor() {
        this.currentSettings = null;
        this.validationResults = {}; // Store validation results temporarily
        this.init();
    }
    
    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        await this.loadPendingSources();
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/admin/settings');
            const result = await response.json();
            
            if (result.success) {
                this.currentSettings = result.settings;
                this.displayCurrentSettings();
                this.populateSettingsForms();
            } else {
                this.showAlert('Failed to load settings: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showAlert('Error loading settings', 'error');
        }
    }
    
    displayCurrentSettings() {
        if (!this.currentSettings) return;
        
        // Display current user limits
        const userLimitsContainer = document.getElementById('currentUserLimits');
        const userLimits = this.currentSettings.user_limits;
        
        userLimitsContainer.innerHTML = `
            <h4>Current User Limits:</h4>
            <div class="value-item">
                <span class="value-label">Max Sources Per User:</span>
                <span class="value-data">${userLimits.max_sources_per_user}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Max Custom Sources:</span>
                <span class="value-data">${userLimits.max_custom_sources_per_user}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Max Articles Per Source:</span>
                <span class="value-data">${userLimits.max_articles_per_source}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Fetch Interval:</span>
                <span class="value-data">${userLimits.fetch_interval_minutes} minutes</span>
            </div>
            <div class="value-item">
                <span class="value-label">Max Requests Per Hour:</span>
                <span class="value-data">${userLimits.max_fetch_requests_per_hour}</span>
            </div>
        `;
        
        // Display current system settings
        const systemSettingsContainer = document.getElementById('currentSystemSettings');
        const systemSettings = this.currentSettings.system_settings;
        
        systemSettingsContainer.innerHTML = `
            <h4>Current System Settings:</h4>
            <div class="value-item">
                <span class="value-label">Auto-add User Sources:</span>
                <span class="value-data">${systemSettings.auto_add_user_sources_to_global ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Require Admin Approval:</span>
                <span class="value-data">${systemSettings.require_admin_approval_for_custom_sources ? 'Yes' : 'No'}</span>
            </div>
            <div class="value-item">
                <span class="value-label">User Fetch Scheduling:</span>
                <span class="value-data">${systemSettings.enable_user_fetch_scheduling ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Max Global Sources:</span>
                <span class="value-data">${systemSettings.max_global_sources}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Quality Scoring:</span>
                <span class="value-data">${systemSettings.enable_source_quality_scoring ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div class="value-item">
                <span class="value-label">Default User Source:</span>
                <span class="value-data">${systemSettings.default_user_source || 'BBC News'}</span>
            </div>
        `;
    }
    
    populateSettingsForms() {
        if (!this.currentSettings) return;
        
        // Populate user limits form
        const userLimits = this.currentSettings.user_limits;
        document.getElementById('maxSourcesPerUser').value = userLimits.max_sources_per_user;
        document.getElementById('maxCustomSourcesPerUser').value = userLimits.max_custom_sources_per_user;
        document.getElementById('maxArticlesPerSource').value = userLimits.max_articles_per_source;
        document.getElementById('fetchIntervalMinutes').value = userLimits.fetch_interval_minutes;
        document.getElementById('maxFetchRequestsPerHour').value = userLimits.max_fetch_requests_per_hour;
        
        // Populate system settings form
        const systemSettings = this.currentSettings.system_settings;
        document.getElementById('autoAddUserSources').checked = systemSettings.auto_add_user_sources_to_global;
        document.getElementById('requireAdminApproval').checked = systemSettings.require_admin_approval_for_custom_sources;
        document.getElementById('enableUserFetchScheduling').checked = systemSettings.enable_user_fetch_scheduling;
        document.getElementById('maxGlobalSources').value = systemSettings.max_global_sources;
        document.getElementById('enableSourceQualityScoring').checked = systemSettings.enable_source_quality_scoring;
        document.getElementById('defaultUserSource').value = systemSettings.default_user_source || 'BBC News';
    }
    
    setupEventListeners() {
        // User limits form
        document.getElementById('userLimitsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.updateUserLimits();
        });
        
        // System settings form
        document.getElementById('systemSettingsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.updateSystemSettings();
        });
    }
    
    async updateUserLimits() {
        try {
            const formData = new FormData(document.getElementById('userLimitsForm'));
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = parseInt(value);
            }
            
            const response = await fetch('/api/admin/settings/user-limits', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('User limits updated successfully!', 'success');
                await this.loadSettings(); // Reload to show updated values
            } else {
                this.showAlert('Failed to update user limits: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error updating user limits:', error);
            this.showAlert('Error updating user limits', 'error');
        }
    }
    
    async updateSystemSettings() {
        try {
            const formData = new FormData(document.getElementById('systemSettingsForm'));
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (value === 'on') {
                    data[key] = true;
                } else if (!isNaN(value)) {
                    data[key] = parseInt(value);
                } else {
                    data[key] = value;
                }
            }
            
            // Handle unchecked checkboxes
            const checkboxes = ['auto_add_user_sources_to_global', 'require_admin_approval_for_custom_sources',
                              'enable_user_fetch_scheduling', 'enable_source_quality_scoring'];
            
            checkboxes.forEach(checkbox => {
                if (!(checkbox in data)) {
                    data[checkbox] = false;
                }
            });
            
            const response = await fetch('/api/admin/settings/system', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('System settings updated successfully!', 'success');
                await this.loadSettings(); // Reload to show updated values
            } else {
                this.showAlert('Failed to update system settings: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error updating system settings:', error);
            this.showAlert('Error updating system settings', 'error');
        }
    }
    
    async loadPendingSources() {
        try {
            const response = await fetch('/api/admin/pending-sources');
            const result = await response.json();

            if (result.success) {
                this.displayPendingSources(result.pending_sources);
                this.updateReviewStats(result.pending_sources);
            } else {
                this.showAlert('Failed to load pending sources: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error loading pending sources:', error);
            this.showAlert('Error loading pending sources', 'error');
        }
    }

    updateReviewStats(sources) {
        const pendingCount = sources.length;
        const today = new Date().toDateString();

        // Count approved/rejected today (would need additional API endpoint for this)
        // For now, just show pending count
        document.getElementById('pendingCount').textContent = pendingCount;
        document.getElementById('approvedCount').textContent = '0'; // Placeholder
        document.getElementById('rejectedCount').textContent = '0'; // Placeholder
    }
    
    displayPendingSources(sources) {
        const container = document.getElementById('pendingSourcesList');

        if (!sources || sources.length === 0) {
            container.innerHTML = `
                <div class="loading-state">
                    <p>✅ No pending sources to review</p>
                    <p style="font-size: 14px; color: #6c757d;">All user submissions have been processed.</p>
                </div>
            `;
            return;
        }

        const sourcesHtml = sources.map(source => {
            const submittedBy = source.submitted_by || {};
            // Use stored validation result if available, otherwise use source's validation result
            const validationResult = (this.validationResults && this.validationResults[source.source_id]) || source.validation_result || {};

            return `
                <div class="source-review-item pending" data-source-id="${source.source_id}">
                    <div class="source-header">
                        <div class="source-info">
                            <div class="source-title">${source.name}</div>
                            <a href="${source.url}" target="_blank" class="source-url">${source.url}</a>
                            <div class="source-meta">
                                <span>📂 ${source.category}</span>
                                <span>👤 ${submittedBy.username || 'Unknown User'}</span>
                                <span>📅 ${new Date(source.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>
                    </div>

                    ${this.renderValidationResults(validationResult)}

                    <div class="review-actions-item">
                        <button onclick="adminSettings.validateSource('${source.source_id}')" class="btn btn-info">
                            🧪 Test Source
                        </button>
                        <button onclick="adminSettings.showApprovalDialog('${source.source_id}')" class="btn btn-success">
                            ✅ Approve
                        </button>
                        <button onclick="adminSettings.showRejectionDialog('${source.source_id}')" class="btn btn-danger">
                            ❌ Reject
                        </button>
                        <button onclick="adminSettings.previewSource('${source.url}')" class="btn btn-secondary">
                            👁️ Preview
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = sourcesHtml;
    }

    renderValidationResults(validationResult) {
        if (!validationResult || !validationResult.test_results) {
            return `
                <div class="validation-results">
                    <p><strong>⚠️ Not yet validated</strong> - Click "Test Source" to run validation tests</p>
                </div>
            `;
        }

        const score = validationResult.score || 0;
        const scoreClass = score >= 80 ? 'score-excellent' :
                          score >= 60 ? 'score-good' :
                          score >= 40 ? 'score-fair' : 'score-poor';

        const testResults = Object.entries(validationResult.test_results || {}).map(([testName, result]) => {
            const icon = result.passed ? '✅' : '❌';
            const className = result.passed ? 'test-pass' : 'test-fail';
            return `<div class="test-item ${className}">${icon} ${testName.replace('_', ' ')}</div>`;
        }).join('');

        return `
            <div class="validation-results">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <strong>🔍 Validation Results</strong>
                    <span class="validation-score ${scoreClass}">Score: ${score}/100</span>
                </div>
                <div class="test-results">
                    ${testResults}
                </div>
                ${validationResult.errors && validationResult.errors.length > 0 ?
                    `<div style="color: #dc3545; margin-top: 10px;"><strong>Errors:</strong> ${validationResult.errors.join(', ')}</div>` : ''}
                ${validationResult.warnings && validationResult.warnings.length > 0 ?
                    `<div style="color: #ffc107; margin-top: 5px;"><strong>Warnings:</strong> ${validationResult.warnings.join(', ')}</div>` : ''}
            </div>
        `;
    }

    async validateSource(sourceId) {
        try {
            // Get source details first
            const sourceElement = document.querySelector(`[data-source-id="${sourceId}"]`);
            if (!sourceElement) {
                this.showAlert('❌ Source element not found', 'error');
                return;
            }

            const urlElement = sourceElement.querySelector('.source-url');
            const nameElement = sourceElement.querySelector('.source-title');

            if (!urlElement || !nameElement) {
                this.showAlert('❌ Source details not found', 'error');
                return;
            }

            const url = urlElement.href || urlElement.textContent;
            const name = nameElement.textContent;

            this.showAlert('🧪 Running validation tests...', 'info');

            const response = await fetch('/api/admin/validate-source', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, name })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('✅ Validation completed!', 'success');
                // Store validation result and refresh display
                this.storeValidationResult(sourceId, result.validation_result);
                await this.loadPendingSources();
            } else {
                this.showAlert('❌ Validation failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error validating source:', error);
            this.showAlert('Error validating source: ' + error.message, 'error');
        }
    }

    storeValidationResult(sourceId, validationResult) {
        // Store validation result temporarily for display
        if (!this.validationResults) {
            this.validationResults = {};
        }
        this.validationResults[sourceId] = validationResult;
    }

    showApprovalDialog(sourceId) {
        const modal = this.createModal('Approve Source', `
            <div style="margin-bottom: 20px;">
                <label for="sourceTags">Add tags (optional):</label>
                <div style="margin-top: 10px;">
                    <label><input type="checkbox" value="default"> 📌 Default (pre-added for all users)</label><br>
                    <label><input type="checkbox" value="optional"> 🆕 Optional (users can opt-in)</label><br>
                    <label><input type="checkbox" value="premium"> ⭐ Premium</label><br>
                    <label><input type="checkbox" value="experimental"> 🧪 Experimental</label>
                </div>
            </div>
        `, [
            {
                text: '✅ Approve',
                class: 'btn-success',
                onclick: () => {
                    const selectedTags = Array.from(modal.querySelectorAll('input[type="checkbox"]:checked'))
                        .map(cb => cb.value);
                    this.approveCustomSource(sourceId, selectedTags);
                    this.closeModal(modal);
                }
            },
            {
                text: 'Cancel',
                class: 'btn-secondary',
                onclick: () => this.closeModal(modal)
            }
        ]);
    }

    showRejectionDialog(sourceId) {
        const modal = this.createModal('Reject Source', `
            <div style="margin-bottom: 20px;">
                <label for="rejectionReason">Reason for rejection (required):</label>
                <textarea id="rejectionReason" style="width: 100%; height: 100px; margin-top: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 4px;"
                    placeholder="Please provide a clear reason for rejection..."></textarea>
            </div>
        `, [
            {
                text: '❌ Reject',
                class: 'btn-danger',
                onclick: () => {
                    const reason = modal.querySelector('#rejectionReason').value.trim();
                    if (!reason) {
                        alert('Please provide a reason for rejection');
                        return;
                    }
                    this.rejectCustomSource(sourceId, reason);
                    this.closeModal(modal);
                }
            },
            {
                text: 'Cancel',
                class: 'btn-secondary',
                onclick: () => this.closeModal(modal)
            }
        ]);
    }

    previewSource(url) {
        // Clean the URL if it has extra characters
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://')) {
            window.open(cleanUrl, '_blank');
        } else {
            this.showAlert('❌ Invalid URL for preview', 'error');
        }
    }

    createModal(title, content, buttons) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 1000; display: flex;
            align-items: center; justify-content: center;
        `;

        const buttonsHtml = buttons.map((btn, index) =>
            `<button class="btn ${btn.class}" data-button-index="${index}">${btn.text}</button>`
        ).join(' ');

        modal.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 8px; max-width: 500px; width: 90%;">
                <h3 style="margin-top: 0;">${title}</h3>
                ${content}
                <div style="text-align: right; margin-top: 20px;">
                    ${buttonsHtml}
                </div>
            </div>
        `;

        // Add event listeners
        buttons.forEach((btn, index) => {
            modal.querySelector(`[data-button-index="${index}"]`).onclick = btn.onclick;
        });

        document.body.appendChild(modal);
        return modal;
    }

    closeModal(modal) {
        document.body.removeChild(modal);
    }

    async approveCustomSource(sourceId, tags = []) {
        try {
            const response = await fetch(`/api/admin/custom-sources/${sourceId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tags })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('✅ Source approved successfully!', 'success');
                await this.loadPendingSources(); // Reload pending sources
            } else {
                this.showAlert('Failed to approve source: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error approving source:', error);
            this.showAlert('Error approving source', 'error');
        }
    }
    
    async rejectCustomSource(sourceId, reason) {
        try {
            const response = await fetch(`/api/admin/custom-sources/${sourceId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ reason })
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('❌ Source rejected successfully!', 'success');
                await this.loadPendingSources(); // Reload pending sources
            } else {
                this.showAlert('Failed to reject source: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error rejecting source:', error);
            this.showAlert('Error rejecting source', 'error');
        }
    }
    
    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        
        const alertHtml = `
            <div class="alert ${alertClass}">
                ${message}
            </div>
        `;
        
        alertContainer.innerHTML = alertHtml;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
}

// Global functions for button clicks
async function resetAllSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/admin/settings/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            adminSettings.showAlert('All settings reset to defaults successfully!', 'success');
            await adminSettings.loadSettings();
        } else {
            adminSettings.showAlert('Failed to reset settings: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        adminSettings.showAlert('Error resetting settings', 'error');
    }
}

function exportSettings() {
    if (adminSettings.currentSettings) {
        const dataStr = JSON.stringify(adminSettings.currentSettings, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `admin-settings-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        adminSettings.showAlert('Settings exported successfully!', 'success');
    }
}

function viewSystemStats() {
    window.open('/admin', '_blank');
}

async function loadPendingSources() {
    await adminSettings.loadPendingSources();
}

async function validateAllPending() {
    if (!confirm('This will run validation tests on all pending sources. Continue?')) {
        return;
    }

    adminSettings.showAlert('🧪 Running validation tests on all pending sources...', 'info');

    // Get all pending source IDs
    const pendingSources = document.querySelectorAll('.source-review-item[data-source-id]');

    for (const sourceElement of pendingSources) {
        const sourceId = sourceElement.getAttribute('data-source-id');
        await adminSettings.validateSource(sourceId);
        // Add small delay to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    adminSettings.showAlert('✅ Validation completed for all pending sources!', 'success');
}

function showBulkActions() {
    const modal = adminSettings.createModal('Bulk Actions', `
        <div style="margin-bottom: 20px;">
            <p>Select an action to perform on all pending sources:</p>
            <div style="margin-top: 15px;">
                <button onclick="bulkApproveAll()" class="btn btn-success" style="margin-right: 10px;">
                    ✅ Approve All Valid Sources (Score ≥ 70)
                </button>
                <button onclick="bulkRejectAll()" class="btn btn-danger">
                    ❌ Reject All Invalid Sources (Score < 40)
                </button>
            </div>
        </div>
    `, [
        {
            text: 'Close',
            class: 'btn-secondary',
            onclick: () => adminSettings.closeModal(modal)
        }
    ]);
}

async function bulkApproveAll() {
    if (!confirm('This will approve all sources with validation score ≥ 70. Continue?')) {
        return;
    }

    adminSettings.showAlert('Processing bulk approval...', 'info');
    // Implementation would require additional logic to check validation scores
    // For now, just show a message
    adminSettings.showAlert('Bulk approval feature coming soon!', 'info');
}

async function bulkRejectAll() {
    if (!confirm('This will reject all sources with validation score < 40. Continue?')) {
        return;
    }

    adminSettings.showAlert('Processing bulk rejection...', 'info');
    // Implementation would require additional logic to check validation scores
    // For now, just show a message
    adminSettings.showAlert('Bulk rejection feature coming soon!', 'info');
}

// Initialize when page loads
let adminSettings;
document.addEventListener('DOMContentLoaded', () => {
    adminSettings = new AdminSettings();
});
