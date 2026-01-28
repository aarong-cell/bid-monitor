// Application State
let filteredOpportunities = [];
let activeFilters = {
    location: ['cleveland', 'cuyahoga', 'ohio'],
    type: ['municipal', 'county', 'state'],
    deadline: ['urgent', 'soon', 'later'],
    keywords: ['stormwater', 'vac-truck', 'cleaning', 'sewer'],
    search: ''
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    renderOpportunities();
    updateStatistics();
});

// Initialize Application
function initializeApp() {
    filteredOpportunities = window.bidOpportunities;
    updateLastUpdated();
    
    // Auto-refresh every 5 minutes
    setInterval(() => {
        updateLastUpdated();
        simulateRefresh();
    }, 300000);
}

// Setup Event Listeners
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    // Filter checkboxes
    const filterCheckboxes = document.querySelectorAll('.filter-checkbox');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleFilterChange);
    });
    
    // Keyword tags
    const keywordTags = document.querySelectorAll('.keyword-tag');
    keywordTags.forEach(tag => {
        tag.addEventListener('click', handleKeywordToggle);
    });
    
    // Clear filters button
    document.getElementById('clearFilters').addEventListener('click', clearAllFilters);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', handleRefresh);
    
    // Export button
    document.getElementById('exportBtn').addEventListener('click', exportToCSV);
    
    // Email toggle
    document.getElementById('emailToggle').addEventListener('change', handleEmailToggle);
    
    // Notification button
    document.getElementById('notificationBtn').addEventListener('click', toggleNotificationPanel);
    
    // Close notifications
    document.getElementById('closeNotifications').addEventListener('click', toggleNotificationPanel);
}

// Handle Search
function handleSearch(e) {
    activeFilters.search = e.target.value.toLowerCase();
    applyFilters();
}

// Handle Filter Change
function handleFilterChange(e) {
    const filterType = e.target.dataset.filter;
    const value = e.target.value;
    const isChecked = e.target.checked;
    
    if (isChecked) {
        if (!activeFilters[filterType].includes(value)) {
            activeFilters[filterType].push(value);
        }
    } else {
        activeFilters[filterType] = activeFilters[filterType].filter(v => v !== value);
    }
    
    applyFilters();
}

// Handle Keyword Toggle
function handleKeywordToggle(e) {
    const tag = e.currentTarget;
    const keyword = tag.dataset.keyword;
    
    tag.classList.toggle('active');
    
    if (tag.classList.contains('active')) {
        if (!activeFilters.keywords.includes(keyword)) {
            activeFilters.keywords.push(keyword);
        }
    } else {
        activeFilters.keywords = activeFilters.keywords.filter(k => k !== keyword);
    }
    
    applyFilters();
}

// Clear All Filters
function clearAllFilters() {
    // Reset active filters
    activeFilters = {
        location: [],
        type: [],
        deadline: [],
        keywords: [],
        search: ''
    };
    
    // Uncheck all checkboxes
    document.querySelectorAll('.filter-checkbox').forEach(cb => cb.checked = false);
    
    // Deactivate all keyword tags
    document.querySelectorAll('.keyword-tag').forEach(tag => tag.classList.remove('active'));
    
    // Clear search
    document.getElementById('searchInput').value = '';
    
    applyFilters();
}

// Apply Filters
function applyFilters() {
    filteredOpportunities = window.bidOpportunities.filter(opp => {
        // Search filter
        if (activeFilters.search) {
            const searchText = `${opp.title} ${opp.description} ${opp.location}`.toLowerCase();
            if (!searchText.includes(activeFilters.search)) {
                return false;
            }
        }
        
        // Location filter
        if (activeFilters.location.length > 0) {
            const locationMatch = activeFilters.location.some(loc => {
                if (loc === 'cleveland') return opp.location.toLowerCase().includes('cleveland');
                if (loc === 'cuyahoga') return opp.location.toLowerCase().includes('cuyahoga');
                if (loc === 'ohio') return opp.type === 'state' || opp.location.toLowerCase().includes('ohio');
                return false;
            });
            if (!locationMatch) return false;
        }
        
        // Type filter
        if (activeFilters.type.length > 0) {
            if (!activeFilters.type.includes(opp.type)) {
                return false;
            }
        }
        
        // Deadline filter
        if (activeFilters.deadline.length > 0) {
            const deadlineMatch = activeFilters.deadline.some(dl => {
                if (dl === 'urgent') return opp.daysUntilDeadline <= 7;
                if (dl === 'soon') return opp.daysUntilDeadline <= 14;
                if (dl === 'later') return opp.daysUntilDeadline > 14;
                return false;
            });
            if (!deadlineMatch) return false;
        }
        
        // Keywords filter
        if (activeFilters.keywords.length > 0) {
            const keywordMatch = activeFilters.keywords.some(keyword => 
                opp.tags.includes(keyword)
            );
            if (!keywordMatch) return false;
        }
        
        return true;
    });
    
    renderOpportunities();
    updateStatistics();
}

// Render Opportunities
function renderOpportunities() {
    const container = document.getElementById('opportunitiesContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (filteredOpportunities.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    container.style.display = 'grid';
    emptyState.style.display = 'none';
    
    container.innerHTML = filteredOpportunities.map(opp => {
        const isUrgent = opp.daysUntilDeadline <= 7;
        const deadlineClass = isUrgent ? 'deadline-meta' : 'deadline-meta normal';
        
        return `
            <div class="opportunity-card" data-id="${opp.id}">
                <div class="opportunity-header">
                    <h3 class="opportunity-title">${opp.title}</h3>
                    <button class="favorite-btn" onclick="toggleFavorite(${opp.id})">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
                
                <div class="opportunity-meta">
                    <span class="meta-badge type-badge ${opp.type}">
                        ${getTypeIcon(opp.type)} ${capitalize(opp.type)}
                    </span>
                    <span class="meta-badge location-meta">
                        <i class="fas fa-map-marker-alt"></i> ${opp.location}
                    </span>
                    <span class="meta-badge ${deadlineClass}">
                        <i class="fas fa-calendar-alt"></i> Due: ${formatDate(opp.deadline)}
                    </span>
                </div>
                
                <p class="opportunity-description">${opp.description}</p>
                
                <div class="opportunity-tags">
                    ${opp.tags.map(tag => `
                        <span class="tag">
                            <i class="${getTagIcon(tag)}"></i> ${capitalize(tag)}
                        </span>
                    `).join('')}
                </div>
                
                <div class="opportunity-footer">
                    <div>
                        <div class="source-info">
                            <strong>Source:</strong> ${opp.source}
                        </div>
                        <div class="bid-number">${opp.bidNumber}</div>
                    </div>
                </div>
                
                <div class="opportunity-actions">
                    <button class="btn-view" onclick="viewOpportunity('${opp.url}')">
                        View Opportunity <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Update Statistics
function updateStatistics() {
    const total = filteredOpportunities.length;
    const municipal = filteredOpportunities.filter(o => o.type === 'municipal').length;
    const county = filteredOpportunities.filter(o => o.type === 'county').length;
    const state = filteredOpportunities.filter(o => o.type === 'state').length;
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('municipalCount').textContent = municipal;
    document.getElementById('countyCount').textContent = county;
    document.getElementById('stateCount').textContent = state;
}

// Toggle Favorite
function toggleFavorite(id) {
    const btn = event.currentTarget;
    const icon = btn.querySelector('i');
    
    if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        icon.classList.remove('fas');
        icon.classList.add('far');
        showToast('Removed from favorites', 'info');
    } else {
        btn.classList.add('active');
        icon.classList.remove('far');
        icon.classList.add('fas');
        showToast('Added to favorites', 'success');
    }
}

// View Opportunity
function viewOpportunity(url) {
    window.open(url, '_blank');
}

// Handle Refresh
function handleRefresh() {
    const btn = document.getElementById('refreshBtn');
    const icon = btn.querySelector('i');
    
    icon.classList.add('rotating');
    
    // Simulate refresh
    setTimeout(() => {
        icon.classList.remove('rotating');
        updateLastUpdated();
        showToast('Data refreshed successfully', 'success');
    }, 1500);
}

// Simulate Refresh (for auto-refresh)
function simulateRefresh() {
    console.log('Auto-refreshing data...');
    // In a real application, this would fetch new data from an API
}

// Export to CSV
function exportToCSV() {
    const headers = ['Title', 'Location', 'Type', 'Source', 'Bid Number', 'Posted Date', 'Deadline', 'URL'];
    const rows = filteredOpportunities.map(opp => [
        opp.title,
        opp.location,
        capitalize(opp.type),
        opp.source,
        opp.bidNumber,
        opp.postedDate,
        opp.deadline,
        opp.url
    ]);
    
    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bid-opportunities-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showToast('CSV exported successfully', 'success');
}

// Handle Email Toggle
function handleEmailToggle(e) {
    const isEnabled = e.target.checked;
    const message = isEnabled ? 'Email notifications enabled' : 'Email notifications disabled';
    const type = isEnabled ? 'success' : 'info';
    showToast(message, type);
}

// Toggle Notification Panel
function toggleNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    panel.classList.toggle('active');
}

// Update Last Updated Timestamp
function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit'
    });
    document.getElementById('lastUpdated').textContent = timeString;
}

// Show Toast Notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    const icon = type === 'success' ? 'fa-check-circle' : 
                 type === 'error' ? 'fa-exclamation-circle' : 
                 'fa-info-circle';
    const color = type === 'success' ? '#10b981' : 
                  type === 'error' ? '#ef4444' : 
                  '#3b82f6';
    
    toast.innerHTML = `
        <i class="fas ${icon}" style="color: ${color}; font-size: 1.25rem;"></i>
        <span style="color: #1e293b; font-weight: 500;">${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Utility Functions
function capitalize(str) {
    return str.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
}

function getTypeIcon(type) {
    switch(type) {
        case 'municipal': return '<i class="fas fa-building"></i>';
        case 'county': return '<i class="fas fa-map"></i>';
        case 'state': return '<i class="fas fa-landmark"></i>';
        default: return '<i class="fas fa-file"></i>';
    }
}

function getTagIcon(tag) {
    switch(tag.toLowerCase()) {
        case 'stormwater': return 'fas fa-droplet';
        case 'vac-truck': return 'fas fa-truck';
        case 'cleaning': return 'fas fa-broom';
        case 'sewer': return 'fas fa-water';
        case 'cctv': return 'fas fa-video';
        case 'emergency': return 'fas fa-exclamation-triangle';
        case 'compliance': return 'fas fa-clipboard-check';
        case 'sweeping': return 'fas fa-wind';
        default: return 'fas fa-tag';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
