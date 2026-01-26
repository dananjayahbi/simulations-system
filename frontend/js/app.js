/**
 * Loops Visualization System - Main Application
 * ==============================================
 * Entry point that initializes all modules
 * 
 * Modules:
 * - core.js: Configuration, state, utilities
 * - navigation.js: Page navigation
 * - modal.js: Modal dialogs
 * - simulations.js: Simulation API and rendering
 * - terminal.js: WebSocket terminal
 * - videos.js: Video outputs and player
 */

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize core elements
    initCoreElements();
    
    // Initialize datetime
    setInterval(updateDateTime, 1000);
    updateDateTime();
    
    // Initialize modules
    initNavigation();
    initRefreshButton();
    initModal();
    initTerminalControls();
    initVideoElements();
    
    // Fetch initial data
    fetchSimulations();
    fetchSystemInfo();
    
    // Initialize WebSocket
    initWebSocket();
    
    console.log('Loops Dashboard initialized');
});
