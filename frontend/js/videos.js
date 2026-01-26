/**
 * Loops Visualization System - Video/Outputs Module
 * ==================================================
 * Handles video listing, playback, and outputs page
 */

// Video-specific DOM elements
const videoElements = {
    outputsGrid: null,
    videoModal: null,
    videoPlayer: null,
    videoSource: null,
    videoModalTitle: null,
    videoInfo: null,
    videoModalClose: null,
    videoModalCloseBtn: null,
    videoOpenFolder: null,
    refreshOutputs: null
};

function initVideoElements() {
    videoElements.outputsGrid = document.getElementById('outputs-grid');
    videoElements.videoModal = document.getElementById('video-modal');
    videoElements.videoPlayer = document.getElementById('video-player');
    videoElements.videoSource = document.getElementById('video-source');
    videoElements.videoModalTitle = document.getElementById('video-modal-title');
    videoElements.videoInfo = document.getElementById('video-info');
    videoElements.videoModalClose = document.getElementById('video-modal-close');
    videoElements.videoModalCloseBtn = document.getElementById('video-modal-close-btn');
    videoElements.videoOpenFolder = document.getElementById('video-open-folder');
    videoElements.refreshOutputs = document.getElementById('refresh-outputs');
    
    // Video modal event listeners
    if (videoElements.videoModalClose) {
        videoElements.videoModalClose.addEventListener('click', closeVideoModal);
    }
    if (videoElements.videoModalCloseBtn) {
        videoElements.videoModalCloseBtn.addEventListener('click', closeVideoModal);
    }
    if (videoElements.videoModal) {
        videoElements.videoModal.addEventListener('click', (e) => {
            if (e.target === videoElements.videoModal) closeVideoModal();
        });
    }
    if (videoElements.videoOpenFolder) {
        videoElements.videoOpenFolder.addEventListener('click', openVideoFolder);
    }
    if (videoElements.refreshOutputs) {
        videoElements.refreshOutputs.addEventListener('click', fetchVideos);
    }
}

async function fetchVideos() {
    if (!videoElements.outputsGrid) return;
    
    videoElements.outputsGrid.innerHTML = `
        <div class="loading-placeholder">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading videos...</span>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE}/video/list`);
        const data = await response.json();
        
        if (data.status === 'success') {
            AppState.videos = data.videos || [];
            renderVideosGrid();
        } else {
            showVideoError('Failed to load videos');
        }
    } catch (error) {
        console.error('Failed to fetch videos:', error);
        showVideoError('Could not connect to server');
    }
}

function showVideoError(message) {
    if (!videoElements.outputsGrid) return;
    
    videoElements.outputsGrid.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Error</h3>
            <p>${message}</p>
        </div>
    `;
}

function renderVideosGrid() {
    if (!videoElements.outputsGrid) return;
    
    if (AppState.videos.length === 0) {
        videoElements.outputsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-film"></i>
                <h3>No Videos Found</h3>
                <p>Generate videos from your simulations to see them here</p>
            </div>
        `;
        return;
    }
    
    videoElements.outputsGrid.innerHTML = AppState.videos.map((video, index) => `
        <div class="video-card" data-index="${index}">
            <div class="video-thumbnail">
                <i class="fas fa-video"></i>
                <div class="play-overlay">
                    <i class="fas fa-play-circle"></i>
                </div>
            </div>
            <div class="video-card-body">
                <div class="video-card-title" title="${video.name}">${video.name}</div>
                <div class="video-card-meta">
                    <span><i class="fas fa-hdd"></i> ${formatFileSize(video.size_bytes)}</span>
                    <span><i class="fas fa-clock"></i> ${formatDate(video.created)}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    // Add click event listeners
    document.querySelectorAll('.video-card').forEach(card => {
        card.addEventListener('click', () => {
            const index = parseInt(card.dataset.index);
            openVideoPlayer(AppState.videos[index]);
        });
    });
}

function openVideoPlayer(video) {
    AppState.currentVideo = video;
    
    if (!videoElements.videoModal || !videoElements.videoPlayer) return;
    
    // Set video source - using API endpoint to stream video
    const videoUrl = `${API_BASE}/video/stream/${encodeURIComponent(video.name)}`;
    videoElements.videoSource.src = videoUrl;
    videoElements.videoPlayer.load();
    
    // Set title
    if (videoElements.videoModalTitle) {
        videoElements.videoModalTitle.textContent = video.name;
    }
    
    // Set video info
    if (videoElements.videoInfo) {
        videoElements.videoInfo.innerHTML = `
            <div class="video-info-row">
                <span class="video-info-label">File Name</span>
                <span class="video-info-value">${video.name}</span>
            </div>
            <div class="video-info-row">
                <span class="video-info-label">Size</span>
                <span class="video-info-value">${formatFileSize(video.size_bytes)}</span>
            </div>
            <div class="video-info-row">
                <span class="video-info-label">Created</span>
                <span class="video-info-value">${formatDate(video.created)}</span>
            </div>
            <div class="video-info-row">
                <span class="video-info-label">Path</span>
                <span class="video-info-value" style="font-size: 11px; word-break: break-all;">${video.path}</span>
            </div>
        `;
    }
    
    // Show modal
    videoElements.videoModal.classList.add('active');
}

function closeVideoModal() {
    if (!videoElements.videoModal || !videoElements.videoPlayer) return;
    
    videoElements.videoPlayer.pause();
    videoElements.videoModal.classList.remove('active');
    AppState.currentVideo = null;
}

async function openVideoFolder() {
    if (!AppState.currentVideo) return;
    
    try {
        const response = await fetch(`${API_BASE}/video/open-folder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_name: AppState.currentVideo.name })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Opened video folder', 'success');
        } else {
            showToast(data.message || 'Failed to open folder', 'error');
        }
    } catch (error) {
        console.error('Failed to open folder:', error);
        showToast('Failed to open folder', 'error');
    }
}
