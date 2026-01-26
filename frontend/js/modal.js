/**
 * Loops Visualization System - Modal Module
 * ==========================================
 * Handles modal dialogs for simulations
 */

function initModal() {
    if (elements.modalClose) {
        elements.modalClose.addEventListener('click', closeModal);
    }
    if (elements.modalCancel) {
        elements.modalCancel.addEventListener('click', closeModal);
    }
    if (elements.modal) {
        elements.modal.addEventListener('click', (e) => {
            if (e.target === elements.modal) closeModal();
        });
    }
    if (elements.modalLaunch) {
        elements.modalLaunch.addEventListener('click', async () => {
            if (AppState.selectedSimulation) {
                await launchSimulation(AppState.selectedSimulation.id);
                closeModal();
            }
        });
    }
}

function openModal(simulation) {
    AppState.selectedSimulation = simulation;
    
    if (elements.modalTitle) {
        elements.modalTitle.textContent = simulation.name;
    }
    
    if (elements.modalBody) {
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
    }
    
    if (elements.modal) {
        elements.modal.classList.add('active');
    }
}

function closeModal() {
    if (elements.modal) {
        elements.modal.classList.remove('active');
    }
    AppState.selectedSimulation = null;
}
