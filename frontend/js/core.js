/**
 * Loops Visualization System - Core Module
 * =========================================
 * Configuration, state management, and core utilities
 */

// API Configuration
const API_BASE = 'http://127.0.0.1:5000/api';

// Global State
const AppState = {
    simulations: [],
    selectedSimulation: null,
    videos: [],
    currentVideo: null,
    currentRunningSimId: null,
    socket: null
};

// Core DOM Elements (initialized after DOM load)
const elements = {};

function initCoreElements() {
    elements.pageTitle = document.getElementById('page-title');
    elements.refreshBtn = document.getElementById('refresh-btn');
    elements.datetime = document.getElementById('datetime');
    elements.quickLaunchGrid = document.getElementById('quick-launch-grid');
    elements.simulationsList = document.getElementById('simulations-list');
    elements.toastContainer = document.getElementById('toast-container');
    elements.modal = document.getElementById('modal');
    elements.modalTitle = document.getElementById('modal-title');
    elements.modalBody = document.getElementById('modal-body');
    elements.modalClose = document.getElementById('modal-close');
    elements.modalCancel = document.getElementById('modal-cancel');
    elements.modalLaunch = document.getElementById('modal-launch');
    elements.statSimulations = document.getElementById('stat-simulations');
    elements.statFrames = document.getElementById('stat-frames');
    elements.statPython = document.getElementById('stat-python');
    elements.statPlatform = document.getElementById('stat-platform');
    elements.settingBaseDir = document.getElementById('setting-base-dir');
    elements.settingPython = document.getElementById('setting-python');
    elements.settingPlatform = document.getElementById('setting-platform');
}

// Update datetime
function updateDateTime() {
    if (!elements.datetime) return;
    const now = new Date();
    elements.datetime.textContent = now.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Toast Notifications
function showToast(message, type = 'success') {
    if (!elements.toastContainer) return;
    
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

// Format utilities
function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
