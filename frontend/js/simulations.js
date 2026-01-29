/**
 * Loops Visualization System - Simulations Module
 * ================================================
 * API calls and rendering for simulations
 */

async function fetchSimulations() {
    try {
        const response = await fetch(`${API_BASE}/simulations`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Sort simulations by installed_at (newest first)
            AppState.simulations = data.simulations.sort((a, b) => {
                const dateA = a.installed_at ? new Date(a.installed_at) : new Date(0);
                const dateB = b.installed_at ? new Date(b.installed_at) : new Date(0);
                return dateB - dateA; // Newest first
            });
            
            renderQuickLaunch();
            renderSimulationsList();
            renderTerminalLaunchGrid();
            if (elements.statSimulations) {
                elements.statSimulations.textContent = AppState.simulations.length;
            }
        }
    } catch (error) {
        console.error('Failed to fetch simulations:', error);
        if (elements.quickLaunchGrid) {
            elements.quickLaunchGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Connection Error</h3>
                    <p>Could not connect to backend server</p>
                </div>
            `;
        }
    }
}

async function fetchSystemInfo() {
    try {
        const response = await fetch(`${API_BASE}/system/info`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const sys = data.system;
            if (elements.statPython) elements.statPython.textContent = sys.python_version;
            if (elements.statPlatform) elements.statPlatform.textContent = sys.platform;
            if (elements.settingBaseDir) elements.settingBaseDir.textContent = sys.base_dir;
            if (elements.settingPython) elements.settingPython.textContent = sys.python_version;
            if (elements.settingPlatform) elements.settingPlatform.textContent = sys.platform;
        }
    } catch (error) {
        console.error('Failed to fetch system info:', error);
    }
}

async function launchSimulation(simId) {
    // Always launch in embedded mode
    const output = document.getElementById('terminal-output');
    if (output) {
        output.innerHTML = '';
    }
    
    try {
        const response = await fetch(`${API_BASE}/simulations/${simId}/launch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ embedded: true })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast(`Launched ${data.message}`, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Failed to launch simulation:', error);
        showToast('Failed to launch simulation', 'error');
    }
}

function renderQuickLaunch() {
    if (!elements.quickLaunchGrid) return;
    
    if (AppState.simulations.length === 0) {
        elements.quickLaunchGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-cube"></i>
                <h3>No Simulations Found</h3>
                <p>Add simulations to the simulations folder to get started</p>
            </div>
        `;
        return;
    }
    
    // Get search query
    const searchInput = document.getElementById('dashboard-search');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    
    // Filter simulations based on search
    const filteredSims = AppState.simulations.filter(sim => {
        if (!searchQuery) return true;
        const searchText = `${sim.name} ${sim.description} ${(sim.tags || []).join(' ')} ${sim.id}`.toLowerCase();
        return searchText.includes(searchQuery);
    });
    
    if (filteredSims.length === 0) {
        elements.quickLaunchGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No Matching Simulations</h3>
                <p>Try a different search term</p>
            </div>
        `;
        return;
    }
    
    elements.quickLaunchGrid.innerHTML = filteredSims.map(sim => `
        <div class="simulation-card" style="--card-color: ${sim.color || '#6366f1'}" data-id="${sim.id}">
            <div class="simulation-icon">${sim.icon || '🔄'}</div>
            <div class="simulation-name">${sim.name}</div>
            <div class="simulation-desc">${sim.description}</div>
            <div class="simulation-actions">
                <button class="btn btn-secondary btn-info" data-id="${sim.id}">
                    <i class="fas fa-info-circle"></i>
                </button>
                <button class="btn btn-primary btn-launch" data-id="${sim.id}">
                    <i class="fas fa-rocket"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    // Add event listeners
    document.querySelectorAll('#quick-launch-grid .btn-launch').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            launchSimulation(btn.dataset.id);
        });
    });
    
    document.querySelectorAll('#quick-launch-grid .btn-info').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const sim = AppState.simulations.find(s => s.id === btn.dataset.id);
            if (sim) openModal(sim);
        });
    });
    
    document.querySelectorAll('#quick-launch-grid .simulation-card').forEach(card => {
        card.addEventListener('click', () => {
            const sim = AppState.simulations.find(s => s.id === card.dataset.id);
            if (sim) openModal(sim);
        });
    });
}

function renderSimulationsList() {
    if (!elements.simulationsList) return;
    
    if (AppState.simulations.length === 0) {
        elements.simulationsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-cube"></i>
                <h3>No Simulations Found</h3>
                <p>Add simulations to the simulations folder to get started</p>
            </div>
        `;
        return;
    }
    
    // Get search query
    const searchInput = document.getElementById('simulations-search');
    const searchQuery = searchInput ? searchInput.value.toLowerCase() : '';
    
    // Filter simulations based on search
    const filteredSims = AppState.simulations.filter(sim => {
        if (!searchQuery) return true;
        const searchText = `${sim.name} ${sim.description} ${(sim.tags || []).join(' ')} ${sim.id}`.toLowerCase();
        return searchText.includes(searchQuery);
    });
    
    if (filteredSims.length === 0) {
        elements.simulationsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No Matching Simulations</h3>
                <p>Try a different search term</p>
            </div>
        `;
        return;
    }
    
    elements.simulationsList.innerHTML = filteredSims.map(sim => `
        <div class="simulation-list-item">
            <div class="simulation-list-icon">${sim.icon || '🔄'}</div>
            <div class="simulation-list-info">
                <div class="simulation-list-name">${sim.name}</div>
                <div class="simulation-list-path">${sim.path}</div>
            </div>
            <div class="simulation-list-stats">
                <span><i class="fas fa-window-maximize"></i> ${sim.has_control_panel ? 'Control Panel' : 'Direct Run'}</span>
            </div>
            <div class="simulation-list-actions">
                <button class="btn btn-primary btn-launch" data-id="${sim.id}">
                    <i class="fas fa-rocket"></i> Launch
                </button>
            </div>
        </div>
    `).join('');
    
    elements.simulationsList.querySelectorAll('.btn-launch').forEach(btn => {
        btn.addEventListener('click', () => launchSimulation(btn.dataset.id));
    });
}

// Setup search bar event listeners
function setupSearchListeners() {
    const dashboardSearch = document.getElementById('dashboard-search');
    const simulationsSearch = document.getElementById('simulations-search');
    
    if (dashboardSearch) {
        dashboardSearch.addEventListener('input', renderQuickLaunch);
    }
    
    if (simulationsSearch) {
        simulationsSearch.addEventListener('input', renderSimulationsList);
    }
}

function renderTerminalLaunchGrid() {
    const grid = document.getElementById('terminal-launch-grid');
    if (!grid || AppState.simulations.length === 0) return;
    
    grid.innerHTML = AppState.simulations.map(sim => `
        <button class="terminal-launch-btn" data-id="${sim.id}">
            <span class="icon">${sim.icon || '🔄'}</span>
            <span class="name">${sim.name}</span>
        </button>
    `).join('');
    
    grid.querySelectorAll('.terminal-launch-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            launchEmbedded(btn.dataset.id);
        });
    });
}
