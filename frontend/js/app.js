/**
 * Loops Visualization System - Frontend Application
 * ==================================================
 * Handles all frontend interactions for the admin dashboard
 */

// API Configuration
const API_BASE = 'http://127.0.0.1:5000/api';

// State
let simulations = [];
let selectedSimulation = null;

// DOM Elements
const elements = {
    pageTitle: document.getElementById('page-title'),
    refreshBtn: document.getElementById('refresh-btn'),
    datetime: document.getElementById('datetime'),
    quickLaunchGrid: document.getElementById('quick-launch-grid'),
    simulationsList: document.getElementById('simulations-list'),
    toastContainer: document.getElementById('toast-container'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),
    modalCancel: document.getElementById('modal-cancel'),
    modalLaunch: document.getElementById('modal-launch'),
    statSimulations: document.getElementById('stat-simulations'),
    statFrames: document.getElementById('stat-frames'),
    statPython: document.getElementById('stat-python'),
    statPlatform: document.getElementById('stat-platform'),
    settingBaseDir: document.getElementById('setting-base-dir'),
    settingPython: document.getElementById('setting-python'),
    settingPlatform: document.getElementById('setting-platform')
};

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Update section
        const section = item.dataset.section;
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(`${section}-section`).classList.add('active');
        
        // Update title
        elements.pageTitle.textContent = section.charAt(0).toUpperCase() + section.slice(1);
    });
});

// Update datetime
function updateDateTime() {
    const now = new Date();
    elements.datetime.textContent = now.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
setInterval(updateDateTime, 1000);
updateDateTime();

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} toast-icon"></i>
        <span class="toast-message">${message}</span>
    `;
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal Functions
function openModal(simulation) {
    selectedSimulation = simulation;
    elements.modalTitle.textContent = simulation.name;
    elements.modalBody.innerHTML = `
        <div class="modal-detail">
            <span class="modal-detail-label">ID</span>
            <span class="modal-detail-value">${simulation.id}</span>
        </div>
        <div class="modal-detail">
            <span class="modal-detail-label">Description</span>
            <span class="modal-detail-value">${simulation.description}</span>
        </div>
        <div class="modal-detail">
            <span class="modal-detail-label">Control Panel</span>
            <span class="modal-detail-value">${simulation.has_control_panel ? '✅ Available' : '❌ Not Available'}</span>
        </div>
        <div class="modal-detail">
            <span class="modal-detail-label">Path</span>
            <span class="modal-detail-value" style="font-size: 12px; word-break: break-all;">${simulation.path}</span>
        </div>
    `;
    elements.modal.classList.add('active');
}

function closeModal() {
    elements.modal.classList.remove('active');
    selectedSimulation = null;
}

elements.modalClose.addEventListener('click', closeModal);
elements.modalCancel.addEventListener('click', closeModal);
elements.modal.addEventListener('click', (e) => {
    if (e.target === elements.modal) closeModal();
});

elements.modalLaunch.addEventListener('click', async () => {
    if (selectedSimulation) {
        await launchSimulation(selectedSimulation.id);
        closeModal();
    }
});

// API Functions
async function fetchSimulations() {
    try {
        const response = await fetch(`${API_BASE}/simulations`);
        const data = await response.json();
        
        if (data.status === 'success') {
            simulations = data.simulations;
            renderQuickLaunch();
            renderSimulationsList();
            renderTerminalLaunchGrid();
            elements.statSimulations.textContent = simulations.length;
        }
    } catch (error) {
        console.error('Failed to fetch simulations:', error);
        elements.quickLaunchGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Connection Error</h3>
                <p>Could not connect to backend server</p>
            </div>
        `;
    }
}

async function fetchSystemInfo() {
    try {
        const response = await fetch(`${API_BASE}/system/info`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const sys = data.system;
            elements.statPython.textContent = sys.python_version;
            elements.statPlatform.textContent = sys.platform;
            elements.settingBaseDir.textContent = sys.base_dir;
            elements.settingPython.textContent = sys.python_version;
            elements.settingPlatform.textContent = sys.platform;
        }
    } catch (error) {
        console.error('Failed to fetch system info:', error);
    }
}

async function launchSimulation(simId) {
    // Always launch in embedded mode
    const output = document.getElementById('terminal-output');
    if (output) {
        // Clear previous output
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

// Render Functions
function renderQuickLaunch() {
    if (simulations.length === 0) {
        elements.quickLaunchGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-cube"></i>
                <h3>No Simulations Found</h3>
                <p>Add simulations to the simulations folder to get started</p>
            </div>
        `;
        return;
    }
    
    elements.quickLaunchGrid.innerHTML = simulations.map(sim => `
        <div class="simulation-card" style="--card-color: ${sim.color || '#6366f1'}" data-id="${sim.id}">
            <div class="simulation-icon">${sim.icon || '🔄'}</div>
            <div class="simulation-name">${sim.name}</div>
            <div class="simulation-desc">${sim.description}</div>
            <div class="simulation-actions">
                <button class="btn btn-secondary btn-info" data-id="${sim.id}">
                    <i class="fas fa-info-circle"></i> Info
                </button>
                <button class="btn btn-primary btn-launch" data-id="${sim.id}">
                    <i class="fas fa-rocket"></i> Launch
                </button>
            </div>
        </div>
    `).join('');
    
    // Add event listeners
    document.querySelectorAll('.btn-launch').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            launchSimulation(btn.dataset.id);
        });
    });
    
    document.querySelectorAll('.btn-info').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const sim = simulations.find(s => s.id === btn.dataset.id);
            if (sim) openModal(sim);
        });
    });
    
    document.querySelectorAll('.simulation-card').forEach(card => {
        card.addEventListener('click', () => {
            const sim = simulations.find(s => s.id === card.dataset.id);
            if (sim) openModal(sim);
        });
    });
}

function renderSimulationsList() {
    if (simulations.length === 0) {
        elements.simulationsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-cube"></i>
                <h3>No Simulations Found</h3>
                <p>Add simulations to the simulations folder to get started</p>
            </div>
        `;
        return;
    }
    
    elements.simulationsList.innerHTML = simulations.map(sim => `
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
    
    // Add event listeners for list view
    elements.simulationsList.querySelectorAll('.btn-launch').forEach(btn => {
        btn.addEventListener('click', () => launchSimulation(btn.dataset.id));
    });
}

// Render terminal quick launch buttons
function renderTerminalLaunchGrid() {
    const grid = document.getElementById('terminal-launch-grid');
    if (!grid || simulations.length === 0) return;
    
    grid.innerHTML = simulations.map(sim => `
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

// Refresh button
elements.refreshBtn.addEventListener('click', () => {
    elements.refreshBtn.querySelector('i').classList.add('fa-spin');
    Promise.all([fetchSimulations(), fetchSystemInfo()]).then(() => {
        setTimeout(() => {
            elements.refreshBtn.querySelector('i').classList.remove('fa-spin');
        }, 500);
        showToast('Refreshed successfully');
    });
});

// ============================================
// EMBEDDED TERMINAL (WebSocket)
// ============================================
let socket = null;
let currentRunningSimId = null;

function initWebSocket() {
    try {
        socket = io('http://127.0.0.1:5000');
        
        socket.on('connect', () => {
            console.log('WebSocket connected');
        });
        
        socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });
        
        socket.on('terminal_output', (data) => {
            appendTerminalOutput(data);
        });
    } catch (error) {
        console.error('WebSocket init failed:', error);
    }
}

function appendTerminalOutput(data) {
    const output = document.getElementById('terminal-output');
    if (!output) return;
    
    // Clear welcome message if present
    const welcome = output.querySelector('.terminal-welcome');
    if (welcome) welcome.remove();
    
    const line = document.createElement('div');
    line.className = `terminal-line ${data.type}`;
    line.textContent = data.data;
    output.appendChild(line);
    
    // Auto scroll to bottom
    output.scrollTop = output.scrollHeight;
    
    // Update running status
    if (data.type === 'start') {
        currentRunningSimId = data.sim_id;
        updateTerminalStatus(true);
    } else if (data.type === 'exit') {
        currentRunningSimId = null;
        updateTerminalStatus(false);
    }
}

function updateTerminalStatus(running) {
    const stopBtn = document.getElementById('terminal-stop');
    const simName = document.getElementById('terminal-sim-name');
    
    if (stopBtn) {
        stopBtn.disabled = !running;
    }
    
    if (simName) {
        if (running && currentRunningSimId) {
            const sim = simulations.find(s => s.id === currentRunningSimId);
            simName.textContent = sim ? `Running: ${sim.name}` : 'Running...';
        } else {
            simName.textContent = 'Terminal Output';
        }
    }
}

async function launchEmbedded(simId) {
    const output = document.getElementById('terminal-output');
    if (output) {
        // Clear previous output
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
            showToast(`Started ${data.message} in embedded mode`, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        console.error('Failed to launch embedded:', error);
        showToast('Failed to launch simulation', 'error');
    }
}

async function stopEmbeddedSimulation() {
    if (!currentRunningSimId) return;
    
    try {
        const response = await fetch(`${API_BASE}/simulations/${currentRunningSimId}/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Simulation stopped', 'success');
        }
    } catch (error) {
        console.error('Failed to stop:', error);
    }
}

function clearTerminal() {
    const output = document.getElementById('terminal-output');
    if (output) {
        output.innerHTML = `
            <div class="terminal-welcome">
                <p>👋 Welcome to Loops Terminal</p>
                <p class="terminal-hint">Launch a simulation to see output here</p>
            </div>
        `;
    }
}

// Terminal controls
document.addEventListener('DOMContentLoaded', () => {
    const clearBtn = document.getElementById('terminal-clear');
    const stopBtn = document.getElementById('terminal-stop');
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearTerminal);
    }
    if (stopBtn) {
        stopBtn.addEventListener('click', stopEmbeddedSimulation);
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchSimulations();
    fetchSystemInfo();
    initWebSocket();
});
