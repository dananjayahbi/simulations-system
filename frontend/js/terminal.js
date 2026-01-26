/**
 * Loops Visualization System - Terminal Module
 * =============================================
 * WebSocket communication and terminal functionality
 */

function initWebSocket() {
    try {
        AppState.socket = io('http://127.0.0.1:5000');
        
        AppState.socket.on('connect', () => {
            console.log('WebSocket connected');
        });
        
        AppState.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });
        
        AppState.socket.on('terminal_output', (data) => {
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
        AppState.currentRunningSimId = data.sim_id;
        updateTerminalStatus(true);
    } else if (data.type === 'exit') {
        AppState.currentRunningSimId = null;
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
        if (running && AppState.currentRunningSimId) {
            const sim = AppState.simulations.find(s => s.id === AppState.currentRunningSimId);
            simName.textContent = sim ? `Running: ${sim.name}` : 'Running...';
        } else {
            simName.textContent = 'Terminal Output';
        }
    }
}

async function launchEmbedded(simId) {
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
    if (!AppState.currentRunningSimId) return;
    
    try {
        const response = await fetch(`${API_BASE}/simulations/${AppState.currentRunningSimId}/stop`, {
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

function initTerminalControls() {
    const clearBtn = document.getElementById('terminal-clear');
    const stopBtn = document.getElementById('terminal-stop');
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearTerminal);
    }
    if (stopBtn) {
        stopBtn.addEventListener('click', stopEmbeddedSimulation);
    }
}
