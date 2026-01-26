/**
 * Loops Visualization System - Navigation Module
 * ===============================================
 * Handles page navigation and section switching
 */

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            // Update active nav
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Update section
            const section = item.dataset.section;
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            const targetSection = document.getElementById(`${section}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Update title
            if (elements.pageTitle) {
                elements.pageTitle.textContent = section.charAt(0).toUpperCase() + section.slice(1);
            }
            
            // Trigger section-specific actions
            if (section === 'outputs') {
                fetchVideos();
            }
        });
    });
}

function initRefreshButton() {
    if (!elements.refreshBtn) return;
    
    elements.refreshBtn.addEventListener('click', () => {
        const icon = elements.refreshBtn.querySelector('i');
        if (icon) icon.classList.add('fa-spin');
        
        Promise.all([fetchSimulations(), fetchSystemInfo()]).then(() => {
            setTimeout(() => {
                if (icon) icon.classList.remove('fa-spin');
            }, 500);
            showToast('Refreshed successfully');
        });
    });
}
