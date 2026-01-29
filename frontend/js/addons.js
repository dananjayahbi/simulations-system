/**
 * Add-ons Management Module
 * ===========================
 * Handles uploading, installing, and managing simulation add-ons
 */

class AddonsManager {
    constructor() {
        this.addons = [];
        this.selectedFile = null;
        this.uploadModal = null;
        
        this.init();
    }
    
    init() {
        console.log('🔌 Initializing Add-ons Manager...');
        this.setupEventListeners();
        this.loadAddons();
    }
    
    setupEventListeners() {
        // Upload button
        const uploadBtn = document.getElementById('upload-addon-btn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.openUploadModal());
        }
        
        // Scan button
        const scanBtn = document.getElementById('scan-addons-btn');
        if (scanBtn) {
            scanBtn.addEventListener('click', () => this.scanAddons());
        }
        
        // Search bar
        const searchBar = document.getElementById('addons-search');
        if (searchBar) {
            searchBar.addEventListener('input', () => this.renderAddons());
        }
        
        // Upload modal elements
        this.uploadModal = document.getElementById('upload-modal');
        
        const closeBtn = document.getElementById('upload-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeUploadModal());
        }
        
        // Close modal on background click
        if (this.uploadModal) {
            this.uploadModal.addEventListener('click', (e) => {
                if (e.target === this.uploadModal) {
                    this.closeUploadModal();
                }
            });
        }
        
        // File drop zone
        const dropZone = document.getElementById('upload-drop-zone');
        const fileInput = document.getElementById('upload-file-input');
        
        if (dropZone && fileInput) {
            // Click to select file
            dropZone.addEventListener('click', () => fileInput.click());
            
            // Drag and drop
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
            
            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('drag-over');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelect(files[0]);
                }
            });
            
            // File input change
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }
        
        // Upload buttons
        const cancelBtn = document.getElementById('upload-cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeUploadModal());
        }
        
        const installBtn = document.getElementById('upload-install-btn');
        if (installBtn) {
            installBtn.addEventListener('click', () => this.installAddon());
        }
    }
    
    async loadAddons() {
        const container = document.getElementById('addons-container');
        if (!container) return;
        
        // Show loading
        container.innerHTML = `
            <div class="addons-loading">
                <div class="addons-loading-spinner"></div>
                <p>Loading add-ons...</p>
            </div>
        `;
        
        try {
            const response = await fetch('/api/addon/list');
            const data = await response.json();
            
            if (data.status === 'success') {
                // Sort add-ons by installed_at (newest first)
                this.addons = data.addons.sort((a, b) => {
                    const dateA = a.installed_at ? new Date(a.installed_at) : new Date(0);
                    const dateB = b.installed_at ? new Date(b.installed_at) : new Date(0);
                    return dateB - dateA; // Newest first
                });
                this.renderAddons();
            } else {
                this.showError('Failed to load add-ons: ' + data.message);
            }
        } catch (error) {
            console.error('Error loading add-ons:', error);
            this.showError('Failed to load add-ons: ' + error.message);
        }
    }
    
    renderAddons() {
        const container = document.getElementById('addons-container');
        if (!container) return;
        
        // Get search query
        const searchInput = document.getElementById('addons-search');
        const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
        
        // Filter add-ons based on search
        const filteredAddons = this.addons.filter(addon => {
            if (!searchQuery) return true;
            const searchText = `${addon.name} ${addon.description} ${(addon.tags || []).join(' ')} ${addon.id} ${addon.author}`.toLowerCase();
            return searchText.includes(searchQuery);
        });
        
        if (filteredAddons.length === 0) {
            if (searchQuery) {
                container.innerHTML = `
                    <div class="addons-empty">
                        <div class="addons-empty-icon">🔍</div>
                        <div class="addons-empty-text">No Matching Add-ons</div>
                        <div class="addons-empty-hint">Try a different search term</div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="addons-empty">
                        <div class="addons-empty-icon">📦</div>
                        <div class="addons-empty-text">No add-ons installed</div>
                        <div class="addons-empty-hint">Upload a simulation add-on to get started</div>
                    </div>
                `;
            }
            return;
        }
        
        const grid = document.createElement('div');
        grid.className = 'addons-grid';
        
        filteredAddons.forEach(addon => {
            const card = this.createAddonCard(addon);
            grid.appendChild(card);
        });
        
        container.innerHTML = '';
        container.appendChild(grid);
    }
    
    createAddonCard(addon) {
        const card = document.createElement('div');
        card.className = 'addon-card';
        
        const statusClass = addon.enabled ? 'enabled' : 'disabled';
        const statusText = addon.enabled ? 'Enabled' : 'Disabled';
        const builtinBadge = addon.builtin ? `<span class="addon-status builtin">
            <span class="addon-status-dot"></span>
            Built-in
        </span>` : '';
        
        const tags = addon.tags ? addon.tags.map(tag => 
            `<span class="addon-tag">${tag}</span>`
        ).join('') : '';
        
        card.innerHTML = `
            <div class="addon-card-header">
                <div class="addon-icon" style="background: ${addon.color || '#6366f1'}">
                    ${addon.icon || '🎮'}
                </div>
                <div class="addon-info">
                    <div class="addon-name">${addon.name}</div>
                    <div class="addon-version">v${addon.version}</div>
                </div>
            </div>
            
            <div class="addon-description">
                ${addon.description || 'No description available'}
            </div>
            
            ${tags ? `<div class="addon-tags">${tags}</div>` : ''}
            
            <div class="addon-meta">
                <div class="addon-meta-item">
                    <span>👤</span>
                    <span>${addon.author || 'Unknown'}</span>
                </div>
                <span class="addon-status ${statusClass}">
                    <span class="addon-status-dot"></span>
                    ${statusText}
                </span>
                ${builtinBadge}
            </div>
            
            <div class="addon-actions">
                ${this.getAddonActions(addon)}
            </div>
        `;
        
        // Attach event listeners
        this.attachCardEventListeners(card, addon);
        
        return card;
    }
    
    getAddonActions(addon) {
        const actions = [];
        
        if (addon.enabled) {
            actions.push(`<button class="addon-action-btn primary" data-action="launch" data-id="${addon.id}">
                🚀 Launch
            </button>`);
            
            if (!addon.builtin) {
                actions.push(`<button class="addon-action-btn secondary" data-action="disable" data-id="${addon.id}">
                    ⏸️ Disable
                </button>`);
            }
        } else {
            actions.push(`<button class="addon-action-btn primary" data-action="enable" data-id="${addon.id}">
                ▶️ Enable
            </button>`);
        }
        
        actions.push(`<button class="addon-action-btn secondary" data-action="export" data-id="${addon.id}">
            📥 Export
        </button>`);
        
        if (!addon.builtin) {
            actions.push(`<button class="addon-action-btn danger" data-action="remove" data-id="${addon.id}">
                🗑️ Remove
            </button>`);
        }
        
        return actions.join('');
    }
    
    attachCardEventListeners(card, addon) {
        const buttons = card.querySelectorAll('[data-action]');
        
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const action = button.dataset.action;
                const addonId = button.dataset.id;
                
                switch (action) {
                    case 'launch':
                        this.launchAddon(addonId);
                        break;
                    case 'enable':
                        this.enableAddon(addonId);
                        break;
                    case 'disable':
                        this.disableAddon(addonId);
                        break;
                    case 'export':
                        this.exportAddon(addonId);
                        break;
                    case 'remove':
                        this.removeAddon(addonId);
                        break;
                }
            });
        });
    }
    
    openUploadModal() {
        if (this.uploadModal) {
            this.uploadModal.classList.add('active');
            this.resetUploadForm();
        }
    }
    
    closeUploadModal() {
        if (this.uploadModal) {
            this.uploadModal.classList.remove('active');
            this.resetUploadForm();
        }
    }
    
    resetUploadForm() {
        this.selectedFile = null;
        
        const fileInput = document.getElementById('upload-file-input');
        if (fileInput) fileInput.value = '';
        
        const fileInfo = document.getElementById('upload-file-info');
        if (fileInfo) fileInfo.classList.remove('active');
        
        const installBtn = document.getElementById('upload-install-btn');
        if (installBtn) installBtn.disabled = true;
        
        const progress = document.getElementById('upload-progress');
        if (progress) progress.classList.remove('active');
    }
    
    handleFileSelect(file) {
        if (!file.name.endsWith('.zip')) {
            this.showNotification('Please select a ZIP file', 'error');
            return;
        }
        
        this.selectedFile = file;
        
        // Show file info
        const fileInfo = document.getElementById('upload-file-info');
        const fileName = document.getElementById('upload-file-name');
        const fileSize = document.getElementById('upload-file-size');
        const installBtn = document.getElementById('upload-install-btn');
        
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
        if (fileInfo) fileInfo.classList.add('active');
        if (installBtn) installBtn.disabled = false;
    }
    
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
    
    async installAddon() {
        if (!this.selectedFile) return;
        
        const installBtn = document.getElementById('upload-install-btn');
        const cancelBtn = document.getElementById('upload-cancel-btn');
        const progress = document.getElementById('upload-progress');
        const progressFill = document.getElementById('upload-progress-fill');
        const progressText = document.getElementById('upload-progress-text');
        
        // Disable buttons
        if (installBtn) installBtn.disabled = true;
        if (cancelBtn) cancelBtn.disabled = true;
        
        // Show progress
        if (progress) progress.classList.add('active');
        if (progressText) progressText.textContent = 'Uploading...';
        
        // Simulate progress
        let progressValue = 0;
        const progressInterval = setInterval(() => {
            progressValue += 5;
            if (progressValue <= 90 && progressFill) {
                progressFill.style.width = progressValue + '%';
            }
        }, 100);
        
        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            
            const response = await fetch('/api/addon/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            clearInterval(progressInterval);
            if (progressFill) progressFill.style.width = '100%';
            
            if (data.status === 'success') {
                if (progressText) progressText.textContent = 'Installation complete!';
                this.showNotification('Add-on installed successfully!', 'success');
                
                // Wait a moment then close
                setTimeout(() => {
                    this.closeUploadModal();
                    this.loadAddons();
                }, 1500);
            } else {
                throw new Error(data.message || 'Installation failed');
            }
        } catch (error) {
            clearInterval(progressInterval);
            console.error('Error installing add-on:', error);
            this.showNotification('Installation failed: ' + error.message, 'error');
            
            // Re-enable buttons
            if (installBtn) installBtn.disabled = false;
            if (cancelBtn) cancelBtn.disabled = false;
            if (progress) progress.classList.remove('active');
        }
    }
    
    async launchAddon(addonId) {
        // Clear terminal
        const output = document.getElementById('terminal-output');
        if (output) {
            output.innerHTML = '';
        }
        
        // Show loading modal
        this.showLoadingModal('Launching Simulation', 'Initializing...');
        
        try {
            const response = await fetch(`/api/simulations/${addonId}/launch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ embedded: true })
            });
            
            const data = await response.json();
            
            // Close loading modal
            this.closeLoadingModal();
            
            if (data.status === 'success') {
                this.showNotification(`Launched ${data.message} in embedded mode`, 'success');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error launching add-on:', error);
            this.closeLoadingModal();
            this.showNotification('Failed to launch: ' + error.message, 'error');
        }
    }
    
    async enableAddon(addonId) {
        try {
            const response = await fetch(`/api/addon/${addonId}/enable`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Add-on enabled', 'success');
                this.loadAddons();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error enabling add-on:', error);
            this.showNotification('Failed to enable: ' + error.message, 'error');
        }
    }
    
    async disableAddon(addonId) {
        try {
            const response = await fetch(`/api/addon/${addonId}/disable`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Add-on disabled', 'success');
                this.loadAddons();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error disabling add-on:', error);
            this.showNotification('Failed to disable: ' + error.message, 'error');
        }
    }
    
    async exportAddon(addonId) {
        try {
            // Download the exported ZIP file
            window.location.href = `/api/addon/${addonId}/export`;
            this.showNotification('Exporting add-on...', 'success');
        } catch (error) {
            console.error('Error exporting add-on:', error);
            this.showNotification('Failed to export: ' + error.message, 'error');
        }
    }
    
    async removeAddon(addonId) {
        const addon = this.addons.find(a => a.id === addonId);
        const addonName = addon ? addon.name : addonId;
        
        // Show confirmation modal
        this.showConfirmModal(
            'Remove Add-on',
            `Are you sure you want to remove "${addonName}"?<br><br>This will delete:<br>• Simulation files<br>• Generated frames<br>• Generated videos<br><br><strong>This action cannot be undone.</strong>`,
            async () => {
                // Show loading modal
                this.showLoadingModal('Removing Add-on', 'Deleting files...');
                
                try {
                    const response = await fetch(`/api/addon/${addonId}`, {
                        method: 'DELETE'
                    });
                    
                    const data = await response.json();
                    
                    this.closeLoadingModal();
                    
                    if (data.status === 'success') {
                        this.showNotification('Add-on removed successfully', 'success');
                        this.loadAddons();
                    } else {
                        throw new Error(data.message);
                    }
                } catch (error) {
                    console.error('Error removing add-on:', error);
                    this.closeLoadingModal();
                    this.showNotification('Failed to remove: ' + error.message, 'error');
                }
            }
        );
    }
    
    async scanAddons() {
        this.showNotification('Scanning for add-ons...', 'info');
        
        try {
            // The scan happens automatically when the addon manager initializes
            // We just need to reload the add-ons list
            await this.loadAddons();
            this.showNotification('Add-ons scanned successfully', 'success');
        } catch (error) {
            console.error('Error scanning add-ons:', error);
            this.showNotification('Failed to scan: ' + error.message, 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // Use the existing toast system
        if (window.showToast) {
            window.showToast(message, type === 'info' ? 'success' : type);
        } else if (typeof showToast === 'function') {
            showToast(message, type === 'info' ? 'success' : type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
    
    showError(message) {
        const container = document.getElementById('addons-container');
        if (container) {
            container.innerHTML = `
                <div class="addons-empty">
                    <div class="addons-empty-icon">⚠️</div>
                    <div class="addons-empty-text">Error</div>
                    <div class="addons-empty-hint">${message}</div>
                </div>
            `;
        }
    }
    
    showLoadingModal(title, message) {
        // Remove existing modal if present
        this.closeLoadingModal();
        
        const modal = document.createElement('div');
        modal.id = 'addon-loading-modal';
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 400px; text-align: center;">
                <div class="modal-body" style="padding: 40px 30px;">
                    <div class="loading-spinner" style="margin: 0 auto 20px;"></div>
                    <h3 style="margin: 0 0 10px; font-size: 18px;">${title}</h3>
                    <p style="margin: 0; color: var(--text-muted); font-size: 14px;">${message}</p>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    closeLoadingModal() {
        const modal = document.getElementById('addon-loading-modal');
        if (modal) {
            modal.remove();
        }
    }
    
    showConfirmModal(title, message, onConfirm) {
        // Remove existing modal if present
        const existingModal = document.getElementById('addon-confirm-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'addon-confirm-modal';
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" id="addon-confirm-close">&times;</button>
                </div>
                <div class="modal-body" style="padding: 24px;">
                    <p style="margin: 0; line-height: 1.6;">${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="addon-confirm-cancel">Cancel</button>
                    <button class="btn btn-danger" id="addon-confirm-ok">Remove</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Event listeners
        const closeModal = () => modal.remove();
        
        modal.querySelector('#addon-confirm-close').addEventListener('click', closeModal);
        modal.querySelector('#addon-confirm-cancel').addEventListener('click', closeModal);
        modal.querySelector('#addon-confirm-ok').addEventListener('click', () => {
            closeModal();
            onConfirm();
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.addonsManager = new AddonsManager();
    });
} else {
    window.addonsManager = new AddonsManager();
}
