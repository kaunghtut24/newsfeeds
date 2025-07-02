/**
 * News Feed Application - Modern JavaScript
 * Enhanced with modern UI components and interactions
 */

class NewsFeedApp {
    constructor() {
        this.currentConfig = {};
        this.allNewsData = [];
        this.currentPage = 1;
        this.itemsPerPage = 8;
        this.isProcessing = false;
        this.debugMode = true; // Enable debug logging

        this.debug('🚀 NewsFeedApp constructor called');
        this.init();
    }

    debug(message, data = null) {
        if (this.debugMode) {
            console.log(`[NewsFeedApp Debug] ${message}`, data || '');
        }
    }

    init() {
        this.debug('🔧 Initializing NewsFeedApp');
        this.setupThemeToggle();
        this.setupEventListeners();
        this.loadInitialData();
        this.setupToastNotifications();
        this.setupLoadingStates();
        this.setupAIFeatures();
        this.debug('✅ NewsFeedApp initialization complete');
    }

    // Theme Management
    setupThemeToggle() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                this.setTheme(newTheme);
            });
        }
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
        }
    }

    // Toast Notifications
    setupToastNotifications() {
        if (!document.getElementById('toastContainer')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
    }

    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icon}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        document.getElementById('toastContainer').appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    }

    getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    // Loading States
    setupLoadingStates() {
        this.debug('🔄 Setting up loading states');

        // Clean up any existing overlays first
        this.cleanupExistingOverlays();

        this.loadingOverlay = this.createLoadingOverlay();
        this.debug('✅ Loading overlay created', this.loadingOverlay);

        // Ensure overlay starts hidden
        this.hideLoading();
    }

    cleanupExistingOverlays() {
        this.debug('🧹 Cleaning up existing loading overlays');
        const existingOverlays = document.querySelectorAll('.loading-overlay');
        existingOverlays.forEach((overlay, index) => {
            this.debug(`Removing existing overlay ${index + 1}`);
            overlay.remove();
        });
    }

    createLoadingOverlay() {
        this.debug('🏗️ Creating loading overlay');

        // Check if overlay already exists
        const existingOverlay = document.querySelector('.loading-overlay');
        if (existingOverlay) {
            this.debug('⚠️ Loading overlay already exists, removing old one');
            existingOverlay.remove();
        }

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay hidden';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <p class="loading-text">Processing...</p>
            </div>
        `;
        document.body.appendChild(overlay);
        this.debug('✅ Loading overlay created and appended to body');
        return overlay;
    }

    showLoading(text = 'Processing...') {
        this.debug('🔄 showLoading called', { text, overlay: this.loadingOverlay });

        if (!this.loadingOverlay) {
            this.debug('⚠️ No loading overlay found, creating new one');
            this.loadingOverlay = this.createLoadingOverlay();
        }

        const loadingText = this.loadingOverlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = text;
        }

        this.loadingOverlay.classList.remove('hidden');
        this.loadingOverlay.style.display = 'flex'; // Force show

        this.debug('✅ Loading overlay shown', {
            classes: this.loadingOverlay.className,
            display: this.loadingOverlay.style.display,
            visible: !this.loadingOverlay.classList.contains('hidden')
        });
    }

    hideLoading() {
        this.debug('🚫 hideLoading called', { overlay: this.loadingOverlay });

        if (!this.loadingOverlay) {
            this.debug('⚠️ No loading overlay to hide');
            return;
        }

        this.loadingOverlay.classList.add('hidden');
        this.loadingOverlay.style.display = 'none'; // Force hide

        this.debug('✅ Loading overlay hidden', {
            classes: this.loadingOverlay.className,
            display: this.loadingOverlay.style.display,
            hidden: this.loadingOverlay.classList.contains('hidden')
        });
    }

    forceHideAllLoading() {
        this.debug('🚨 forceHideAllLoading called - aggressive cleanup');

        // Aggressively hide all loading states
        const loadingElements = [
            '.loading-overlay',
            '.skeleton-loader',
            '.loading-spinner'
        ];

        let hiddenCount = 0;
        loadingElements.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            this.debug(`Found ${elements.length} elements for selector: ${selector}`);

            elements.forEach(element => {
                element.classList.add('hidden');
                element.style.display = 'none';
                element.style.visibility = 'hidden';
                hiddenCount++;
            });
        });

        // Clear loading text
        const loadingTexts = document.querySelectorAll('.loading-text');
        loadingTexts.forEach(text => {
            text.textContent = '';
        });

        // Clear processing state
        this.isProcessing = false;

        this.debug(`✅ forceHideAllLoading complete - hidden ${hiddenCount} elements`);
    }

    // Comprehensive UI state management
    ensureUIAccessible() {
        this.debug('🔓 Ensuring UI is accessible');

        // Force hide all loading states
        this.forceHideAllLoading();

        // Ensure main content is visible
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.display = 'block';
            mainContent.style.visibility = 'visible';
            mainContent.style.opacity = '1';
            this.debug('✅ Main content forced visible');
        }

        // Clear any processing states
        this.isProcessing = false;

        // Re-enable all interactive elements
        const buttons = document.querySelectorAll('button:disabled');
        buttons.forEach(button => {
            button.disabled = false;
        });

        this.debug('✅ UI accessibility ensured');
    }

    // Emergency UI reset function - can be called from browser console
    emergencyUIReset() {
        console.log('🚨 Emergency UI Reset - Clearing all loading states');

        // Force hide all loading overlays
        const allLoadingElements = document.querySelectorAll('.loading-overlay, .skeleton-loader, .loading-spinner');
        allLoadingElements.forEach(element => {
            element.classList.add('hidden');
            element.style.display = 'none !important';
            element.remove(); // Remove completely if possible
        });

        // Clear all processing states
        this.isProcessing = false;

        // Hide all reset buttons
        this.hideResetButton();
        const statusResetBtn = document.getElementById('statusResetBtn');
        if (statusResetBtn) {
            statusResetBtn.style.display = 'none';
        }

        // Clear status display
        const statusElement = document.getElementById('statusDisplay');
        if (statusElement) {
            statusElement.classList.add('hidden');
        }

        // Re-enable all buttons
        const fetchBtn = document.getElementById('fetchBtn');
        if (fetchBtn) {
            fetchBtn.disabled = false;
            fetchBtn.textContent = '🚀 Fetch & Summarize News';
        }

        console.log('✅ Emergency UI Reset Complete - Application should be accessible now');
        return 'UI Reset Complete';
    }

    // Event Listeners
    setupEventListeners() {
        // Fetch news button
        const fetchBtn = document.getElementById('fetchBtn');
        if (fetchBtn) {
            fetchBtn.addEventListener('click', () => this.fetchNews());
        }

        // Load news button
        const loadBtn = document.getElementById('loadBtn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadNews());
        }

        // Reset processing button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetProcessing());
        }

        // Status reset button
        const statusResetBtn = document.getElementById('statusResetBtn');
        if (statusResetBtn) {
            statusResetBtn.addEventListener('click', () => this.resetProcessing());
        }

        // Category filter
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.displayFilteredNews());
        }

        // Search functionality
        this.setupAdvancedSearch();

        // Pagination buttons
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        if (prevBtn) prevBtn.addEventListener('click', () => this.changePage(-1));
        if (nextBtn) nextBtn.addEventListener('click', () => this.changePage(1));
    }

    // Initial Data Loading
    async loadInitialData() {
        try {
            await this.loadConfig();
            await this.loadNews();
            await this.loadSources();
        } catch (error) {
            this.showToast('Failed to load initial data', 'error');
            console.error('Initial data loading error:', error);
        }
    }

    // News Operations
    async fetchNews() {
        this.debug('📰 fetchNews called', { isProcessing: this.isProcessing });

        if (this.isProcessing) {
            this.showToast('News processing is already in progress', 'warning');
            return;
        }

        const fetchBtn = document.getElementById('fetchBtn');
        const originalText = fetchBtn?.textContent || 'Fetch News';

        try {
            this.isProcessing = true;
            this.debug('🔄 Starting news fetch process');

            if (fetchBtn) {
                fetchBtn.disabled = true;
                fetchBtn.innerHTML = '<div class="spinner"></div> Processing...';
            }

            this.showLoading('Fetching and summarizing news...');

            const response = await fetch('/api/fetch-news', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            this.debug('📡 Fetch news API response', data);

            if (data.success) {
                this.showToast('News processing started successfully', 'success');
                this.pollStatus();
            } else {
                throw new Error(data.message || 'Failed to start news processing');
            }
        } catch (error) {
            this.debug('❌ Fetch news error', error);
            this.showToast(`Error: ${error.message}`, 'error');
            console.error('Fetch news error:', error);
        } finally {
            this.debug('🏁 Fetch news finally block');
            this.hideLoading();
            if (fetchBtn) {
                fetchBtn.disabled = false;
                fetchBtn.textContent = originalText;
            }
        }
    }

    async pollStatus() {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                this.updateStatusDisplay(data.status, data.is_processing);

                if (data.is_processing) {
                    this.showResetButton(); // Show reset button when processing
                } else {
                    clearInterval(pollInterval);
                    this.isProcessing = false;
                    this.hideResetButton(); // Hide reset button when done
                    this.showToast('News processing completed!', 'success');
                    await this.loadNews(); // Auto-reload news
                }
            } catch (error) {
                clearInterval(pollInterval);
                this.isProcessing = false;
                this.hideResetButton();
                this.showToast('Error checking status', 'error');
                console.error('Status polling error:', error);
            }
        }, 2000);
    }

    updateStatusDisplay(status, isProcessing) {
        const statusElement = document.getElementById('statusDisplay');
        const statusText = document.getElementById('statusText');
        const statusResetBtn = document.getElementById('statusResetBtn');

        if (statusElement && statusText) {
            statusText.textContent = status;
            statusElement.className = `alert ${isProcessing ? 'alert-info' : 'alert-success'}`;
            statusElement.classList.remove('hidden');

            // Show reset button if processing for more than 30 seconds or if stuck
            if (statusResetBtn) {
                if (isProcessing && (status.includes('Running for') || status.includes('Processing'))) {
                    // Extract duration if available
                    const durationMatch = status.match(/(\d+)m\s*(\d+)s/);
                    if (durationMatch) {
                        const minutes = parseInt(durationMatch[1]);
                        const seconds = parseInt(durationMatch[2]);
                        const totalSeconds = minutes * 60 + seconds;

                        // Show reset button after 30 seconds
                        if (totalSeconds > 30) {
                            statusResetBtn.style.display = 'inline-block';
                        }
                    } else {
                        // Show reset button for any processing status without duration
                        statusResetBtn.style.display = 'inline-block';
                    }
                } else {
                    statusResetBtn.style.display = 'none';
                }
            }
        }
    }

    showResetButton() {
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.style.display = 'inline-block';
        }
    }

    hideResetButton() {
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.style.display = 'none';
        }
    }

    async resetProcessing() {
        this.debug('🔄 resetProcessing called');

        try {
            this.showToast('🔄 Resetting processing...', 'info');

            const response = await fetch('/api/reset-processing', {
                method: 'POST'
            });

            const data = await response.json();
            this.debug('📡 Reset processing API response', data);

            if (data.success) {
                this.showToast('✅ Processing has been reset successfully! You can now use the application normally.', 'success');

                this.debug('🧹 Starting comprehensive UI cleanup');

                // Use comprehensive UI accessibility function
                this.ensureUIAccessible();
                this.hideResetButton();

                // Clear any status display
                const statusElement = document.getElementById('statusDisplay');
                const statusResetBtn = document.getElementById('statusResetBtn');
                if (statusElement) {
                    statusElement.classList.add('hidden');
                    this.debug('✅ Status element hidden');
                }
                if (statusResetBtn) {
                    statusResetBtn.style.display = 'none';
                    this.debug('✅ Status reset button hidden');
                }

                // Force hide loading overlay
                const loadingOverlay = document.querySelector('.loading-overlay');
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                    loadingOverlay.style.display = 'none';
                    this.debug('✅ Loading overlay force hidden');
                }

                // Re-enable fetch button
                const fetchBtn = document.getElementById('fetchBtn');
                if (fetchBtn) {
                    fetchBtn.disabled = false;
                    fetchBtn.textContent = '🚀 Fetch & Summarize News';
                    this.debug('✅ Fetch button re-enabled');
                }

                // Clear any polling intervals
                if (this.statusPollInterval) {
                    clearInterval(this.statusPollInterval);
                    this.statusPollInterval = null;
                    this.debug('✅ Status polling cleared');
                }

                this.debug('🔄 Refreshing page content');
                // Refresh the page content
                this.loadNews();
                this.loadInsights();

                this.debug('✅ Reset processing complete');

            } else {
                this.debug('❌ Reset processing failed', data);
                this.showToast('❌ Failed to reset processing', 'error');
            }
        } catch (error) {
            this.debug('❌ Reset processing error', error);
            this.showToast(`❌ Error resetting processing: ${error.message}`, 'error');
        }
    }

    async loadNews() {
        const newsList = document.getElementById('newsList');
        if (newsList) {
            newsList.innerHTML = this.createSkeletonLoader();
        }
        
        try {
            const response = await fetch('/api/news');
            const data = await response.json();
            
            if (data.success && data.news.length > 0) {
                this.allNewsData = data.news;
                this.populateCategories(this.allNewsData);
                this.currentPage = 1;
                this.displayFilteredNews();
                this.showToast(`Loaded ${data.news.length} news articles`, 'success');
            } else {
                if (newsList) {
                    newsList.innerHTML = this.createEmptyState();
                }
                this.showToast('No news available. Please fetch news first.', 'info');
            }
        } catch (error) {
            if (newsList) {
                newsList.innerHTML = this.createErrorState(error.message);
            }
            this.showToast(`Error loading news: ${error.message}`, 'error');
            console.error('Load news error:', error);
        }
    }

    // Search functionality
    searchNews(query) {
        if (!query.trim()) {
            this.displayFilteredNews();
            return;
        }

        const filteredNews = this.allNewsData.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) ||
            (item.summary && item.summary.toLowerCase().includes(query.toLowerCase())) ||
            item.source.toLowerCase().includes(query.toLowerCase())
        );

        this.displayNews(filteredNews);
        this.showToast(`Found ${filteredNews.length} articles matching "${query}"`, 'info');
    }

    // Display and filtering
    displayFilteredNews() {
        const categoryFilter = document.getElementById('categoryFilter');
        const selectedCategory = categoryFilter?.value || 'all';

        let filteredNews = this.allNewsData;
        if (selectedCategory !== 'all') {
            filteredNews = this.allNewsData.filter(item => item.category === selectedCategory);
        }

        this.displayNews(filteredNews);
    }

    displayNews(newsItems) {
        const totalPages = Math.ceil(newsItems.length / this.itemsPerPage);
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const newsToDisplay = newsItems.slice(startIndex, endIndex);

        const newsList = document.getElementById('newsList');
        if (!newsList) return;

        if (newsToDisplay.length === 0) {
            newsList.innerHTML = this.createEmptyState();
            this.updatePaginationButtons(0, 0);
            return;
        }

        // Group by category for better organization
        const categorizedNews = this.groupNewsByCategory(newsToDisplay);
        newsList.innerHTML = this.renderCategorizedNews(categorizedNews);
        this.updatePaginationButtons(this.currentPage, totalPages);
    }

    groupNewsByCategory(newsItems) {
        const grouped = {};
        newsItems.forEach(item => {
            const category = item.category || 'Uncategorized';
            if (!grouped[category]) {
                grouped[category] = [];
            }
            grouped[category].push(item);
        });
        return grouped;
    }

    renderCategorizedNews(categorizedNews) {
        let html = '';
        for (const [category, items] of Object.entries(categorizedNews)) {
            html += `
                <div class="category-section mb-6">
                    <h3 class="category-title">${category}</h3>
                    <div class="news-grid">
                        ${items.map(item => this.renderNewsItem(item)).join('')}
                    </div>
                </div>
            `;
        }
        return html;
    }

    renderNewsItem(item) {
        const timeAgo = this.getTimeAgo(item.timestamp);
        const sentiment = this.getSentimentBadge(item.sentiment);
        const categoryClass = this.getCategoryClass(item.category);
        const itemId = this.generateItemId(item);

        return `
            <article class="news-item card p-6 hover:shadow-lg transition-shadow">
                <div class="news-header mb-4">
                    <h4 class="news-title font-semibold text-lg mb-2">${item.title}</h4>
                    <div class="news-meta flex items-center gap-4 text-sm text-secondary">
                        <span class="source-badge">${item.source}</span>
                        <span class="category-badge ${categoryClass}">${item.category || 'General'}</span>
                        <span class="time-badge">${timeAgo}</span>
                        ${sentiment}
                        <a href="${item.link}" target="_blank" class="read-more-link">
                            Read Full Article →
                        </a>
                    </div>
                </div>
                <div class="news-summary bg-tertiary p-4 rounded-lg">
                    <p class="text-sm leading-relaxed">${item.summary || 'No summary available'}</p>
                </div>
                <div class="news-actions mt-4">
                    <button class="btn btn-sm btn-secondary explain-article-btn"
                            onclick="app.explainArticle('${itemId}')"
                            data-item-id="${itemId}">
                        🤖 Explain Article
                    </button>
                    <button class="btn btn-sm btn-outline categorize-article-btn"
                            onclick="app.categorizeArticle('${itemId}')"
                            data-item-id="${itemId}">
                        🎯 Categorize
                    </button>
                </div>
                <div class="article-explanation" id="explanation-${itemId}" style="display: none;">
                    <!-- AI explanation will be inserted here -->
                </div>
            </article>
        `;
    }

    generateItemId(item) {
        // Generate a unique ID for the item based on title and source
        return btoa(encodeURIComponent(item.title + item.source)).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
    }

    getSentimentBadge(sentiment) {
        if (!sentiment) return '';

        const badges = {
            positive: '<span class="sentiment-badge sentiment-positive">😊 Positive</span>',
            negative: '<span class="sentiment-badge sentiment-negative">😔 Negative</span>',
            neutral: '<span class="sentiment-badge sentiment-neutral">😐 Neutral</span>'
        };

        return badges[sentiment.toLowerCase()] || '';
    }

    getCategoryClass(category) {
        if (!category) return 'general';

        // Convert category name to CSS class
        return category.toLowerCase()
            .replace(/\s+/g, '-')
            .replace(/&/g, '')
            .replace(/[^a-z0-9-]/g, '');
    }

    getTimeAgo(timestamp) {
        if (!timestamp) return 'Unknown time';
        
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    // Pagination
    changePage(direction) {
        this.currentPage += direction;
        this.displayFilteredNews();
        
        // Smooth scroll to top of news list
        const newsList = document.getElementById('newsList');
        if (newsList) {
            newsList.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    updatePaginationButtons(currentPage, totalPages) {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageInfo = document.getElementById('pageInfo');
        
        if (prevBtn) prevBtn.disabled = currentPage <= 1;
        if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
        if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }

    // Categories
    populateCategories(newsItems) {
        const categoryFilter = document.getElementById('categoryFilter');
        if (!categoryFilter) return;
        
        categoryFilter.innerHTML = '<option value="all">All Categories</option>';
        const categories = new Set();
        
        newsItems.forEach(item => {
            if (item.category) {
                categories.add(item.category);
            }
        });
        
        Array.from(categories).sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }

    // Source Management
    async loadSources() {
        try {
            const response = await fetch('/api/sources');
            const data = await response.json();

            if (data.success) {
                this.displaySourcesSelection(data.sources);
                this.debug('✅ Sources loaded successfully', data);
            } else {
                console.error('Failed to load sources:', data.error);
            }
        } catch (error) {
            console.error('Error loading sources:', error);
        }
    }

    displaySourcesSelection(sources) {
        const container = document.getElementById('sourcesList');
        if (!container) return;

        container.innerHTML = '';

        if (!sources || sources.length === 0) {
            container.innerHTML = '<p class="text-sm text-secondary">No sources configured</p>';
            return;
        }

        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-checkbox-item';

            sourceItem.innerHTML = `
                <input type="checkbox"
                       id="source-${source.name}"
                       ${source.enabled ? 'checked' : ''}
                       onchange="app.toggleSource('${source.name}', this.checked)">
                <label for="source-${source.name}">
                    <div>${source.name}</div>
                    <div class="source-info">${source.type.toUpperCase()} • ${source.category}</div>
                </label>
                <div class="source-actions">
                    <button onclick="app.editSource('${source.name}', '${source.url}')"
                            class="btn btn-secondary btn-xs" title="Edit Source">
                        ✏️
                    </button>
                    <button onclick="app.deleteSource('${source.name}')"
                            class="btn btn-danger btn-xs" title="Delete Source">
                        🗑️
                    </button>
                </div>
            `;

            container.appendChild(sourceItem);
        });

        // Update toggle all button text
        const enabledCount = sources.filter(s => s.enabled).length;
        const toggleAllBtn = document.getElementById('toggleAllBtn');
        if (toggleAllBtn) {
            toggleAllBtn.textContent = enabledCount === sources.length ? 'Disable All' : 'Enable All';
        }
    }

    async toggleSource(sourceName, enabled) {
        try {
            const response = await fetch('/api/sources/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source_name: sourceName,
                    enabled: enabled
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(
                    `${sourceName} ${enabled ? 'enabled' : 'disabled'}`,
                    'success'
                );

                // Reload sources to update UI
                await this.loadSources();
            } else {
                this.showToast(`Failed to toggle source: ${data.error}`, 'error');

                // Revert checkbox state
                const checkbox = document.getElementById(`source-${sourceName}`);
                if (checkbox) {
                    checkbox.checked = !enabled;
                }
            }
        } catch (error) {
            console.error('Error toggling source:', error);
            this.showToast('Error toggling source', 'error');

            // Revert checkbox state
            const checkbox = document.getElementById(`source-${sourceName}`);
            if (checkbox) {
                checkbox.checked = !enabled;
            }
        }
    }

    async toggleAllSources() {
        try {
            const response = await fetch('/api/sources');
            const data = await response.json();

            if (!data.success) {
                this.showToast('Failed to load sources', 'error');
                return;
            }

            const sources = data.sources;
            const enabledCount = sources.filter(s => s.enabled).length;
            const shouldEnable = enabledCount < sources.length;

            // Toggle all sources
            const promises = sources.map(source =>
                this.toggleSourceSilent(source.name, shouldEnable)
            );

            await Promise.all(promises);

            this.showToast(
                `All sources ${shouldEnable ? 'enabled' : 'disabled'}`,
                'success'
            );

            // Reload sources to update UI
            await this.loadSources();

        } catch (error) {
            console.error('Error toggling all sources:', error);
            this.showToast('Error toggling all sources', 'error');
        }
    }

    async toggleSourceSilent(sourceName, enabled) {
        try {
            const response = await fetch('/api/sources/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source_name: sourceName,
                    enabled: enabled
                })
            });

            return await response.json();
        } catch (error) {
            console.error(`Error toggling source ${sourceName}:`, error);
            return { success: false, error: error.message };
        }
    }

    async editSource(sourceName, currentUrl) {
        try {
            const newName = prompt(`Edit source name:`, sourceName);
            if (!newName || newName === sourceName) {
                const newUrl = prompt(`Edit source URL:`, currentUrl);
                if (!newUrl || newUrl === currentUrl) {
                    return; // User cancelled or no changes
                }

                // Only URL changed
                const response = await fetch('/api/sources/edit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        old_name: sourceName,
                        new_name: sourceName,
                        new_url: newUrl
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.showToast(`Source "${sourceName}" updated successfully`, 'success');
                    await this.loadSources();
                } else {
                    this.showToast(`Failed to update source: ${data.error}`, 'error');
                }
            } else {
                // Name changed, also ask for URL
                const newUrl = prompt(`Edit source URL:`, currentUrl);
                if (!newUrl) {
                    return; // User cancelled
                }

                const response = await fetch('/api/sources/edit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        old_name: sourceName,
                        new_name: newName,
                        new_url: newUrl
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.showToast(`Source updated to "${newName}"`, 'success');
                    await this.loadSources();
                } else {
                    this.showToast(`Failed to update source: ${data.error}`, 'error');
                }
            }
        } catch (error) {
            console.error('Error editing source:', error);
            this.showToast('Error editing source', 'error');
        }
    }

    async deleteSource(sourceName) {
        try {
            const confirmed = confirm(`Are you sure you want to delete the source "${sourceName}"?`);
            if (!confirmed) {
                return;
            }

            const response = await fetch('/api/sources/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source_name: sourceName
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(`Source "${sourceName}" deleted successfully`, 'success');
                await this.loadSources();
            } else {
                this.showToast(`Failed to delete source: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error deleting source:', error);
            this.showToast('Error deleting source', 'error');
        }
    }

    // Configuration
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            this.currentConfig = await response.json();
            this.displaySources();
            this.populateOllamaModels();
            this.loadLLMProviders();
        } catch (error) {
            console.error('Error loading config:', error);
            this.showToast('Error loading configuration', 'error');
        }
    }

    // LLM Provider Management
    async loadLLMProviders() {
        try {
            const response = await fetch('/api/llm-providers');
            const data = await response.json();

            if (data.success && data.providers) {
                this.displayLLMProviders(data);
                this.updateCostTracking(data.budget || {});
                this.populateProviderSelectors(data.available_providers || [], data.available_models || {});
            } else {
                console.warn('LLM providers response:', data);
                // Don't show error toast for missing providers - it's not critical
                console.log('LLM providers not available or not configured');
            }
        } catch (error) {
            console.error('Error loading LLM providers:', error);
            // Don't show error toast - LLM providers are optional
            console.log('LLM providers functionality not available');
        }
    }

    displayLLMProviders(data) {
        const container = document.getElementById('llmProvidersList');
        if (!container) return;

        container.innerHTML = '';

        for (const [name, provider] of Object.entries(data.providers)) {
            const card = document.createElement('div');
            card.className = 'llm-provider-card';

            const statusClass = provider.enabled && provider.available_models.length > 0 ? 'online' : 'offline';
            const statusText = provider.enabled ? (provider.available_models.length > 0 ? 'Online' : 'No Models') : 'Disabled';

            card.innerHTML = `
                <div class="llm-provider-header">
                    <span class="llm-provider-name">${name.toUpperCase()}</span>
                    <div class="llm-provider-status">
                        <span class="status-indicator ${statusClass}"></span>
                        <span>${statusText}</span>
                    </div>
                </div>
                <div class="llm-provider-stats">
                    <span>Requests: ${provider.request_count}</span>
                    <span>Success: ${(provider.success_rate * 100).toFixed(1)}%</span>
                    <span>Cost: $${provider.total_cost.toFixed(4)}</span>
                </div>
                <div class="llm-provider-actions">
                    <button onclick="app.toggleProvider('${name}', ${!provider.enabled})"
                            class="btn btn-sm ${provider.enabled ? 'btn-secondary' : 'btn-primary'}">
                        ${provider.enabled ? 'Disable' : 'Enable'}
                    </button>
                    ${provider.available_models.length > 0 ?
                        `<select class="form-select" style="font-size: 0.75rem; padding: 0.25rem;">
                            ${provider.available_models.map(model =>
                                `<option value="${model}">${model}</option>`
                            ).join('')}
                        </select>` : ''
                    }
                </div>
            `;

            container.appendChild(card);
        }
    }

    updateCostTracking(budget) {
        const dailyCost = document.getElementById('dailyCost');
        const monthlyCost = document.getElementById('monthlyCost');
        const dailyLimit = document.getElementById('dailyLimit');
        const monthlyLimit = document.getElementById('monthlyLimit');
        const budgetProgress = document.getElementById('budgetProgress');

        // Provide default values if budget properties are undefined
        const currentDaily = budget.current_daily || 0;
        const currentMonthly = budget.current_monthly || 0;
        const dailyLimitValue = budget.daily_limit || 10;
        const monthlyLimitValue = budget.monthly_limit || 200;

        if (dailyCost) dailyCost.textContent = `$${currentDaily.toFixed(2)}`;
        if (monthlyCost) monthlyCost.textContent = `$${currentMonthly.toFixed(2)}`;
        if (dailyLimit) dailyLimit.textContent = `$${dailyLimitValue.toFixed(2)}`;
        if (monthlyLimit) monthlyLimit.textContent = `$${monthlyLimitValue.toFixed(2)}`;

        if (budgetProgress && dailyLimitValue > 0) {
            const dailyPercent = (currentDaily / dailyLimitValue) * 100;
            budgetProgress.style.width = `${Math.min(dailyPercent, 100)}%`;
        }
    }

    populateProviderSelectors(providers, models) {
        const providerSelect = document.getElementById('preferredProvider');
        const modelSelect = document.getElementById('preferredModel');

        if (providerSelect) {
            providerSelect.innerHTML = '<option value="">Auto (Best Available)</option>';
            providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider;
                option.textContent = provider.toUpperCase();
                providerSelect.appendChild(option);
            });
        }

        if (modelSelect) {
            modelSelect.innerHTML = '<option value="">Auto (Default)</option>';
            for (const [provider, providerModels] of Object.entries(models)) {
                providerModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = `${provider.toUpperCase()}: ${model}`;
                    modelSelect.appendChild(option);
                });
            }
        }
    }

    async toggleProvider(providerName, enable) {
        try {
            const action = enable ? 'enable' : 'disable';
            const response = await fetch(`/api/llm-providers/${providerName}/${action}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(data.message, 'success');
                this.loadLLMProviders(); // Refresh the display
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast(`Error toggling provider: ${error.message}`, 'error');
        }
    }

    async refreshLLMProviders() {
        this.showToast('Refreshing LLM providers...', 'info');
        await this.loadLLMProviders();
        this.showToast('LLM providers refreshed', 'success');
    }

    async healthCheckProviders() {
        try {
            this.showToast('Performing health check...', 'info');

            const response = await fetch('/api/llm-providers/health-check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                const results = data.health_results;
                const healthyCount = Object.values(results).filter(Boolean).length;
                const totalCount = Object.keys(results).length;

                this.showToast(
                    `Health check complete: ${healthyCount}/${totalCount} providers healthy`,
                    healthyCount === totalCount ? 'success' : 'warning'
                );

                // Show detailed results
                console.log('Health check results:', results);

                this.loadLLMProviders(); // Refresh the display
            } else {
                this.showToast(`Health check failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Health check error:', error);

            // Provide more specific error messages
            if (error.message.includes('Unexpected token')) {
                this.showToast('Health check error: Server returned invalid response (check server logs)', 'error');
            } else if (error.message.includes('HTTP 404')) {
                this.showToast('Health check error: Endpoint not found (server may need restart)', 'error');
            } else if (error.message.includes('Failed to fetch')) {
                this.showToast('Health check error: Cannot connect to server', 'error');
            } else {
                this.showToast(`Health check error: ${error.message}`, 'error');
            }
        }
    }

    // Advanced Search Functionality
    setupAdvancedSearch() {
        // Advanced search toggle
        const advancedToggle = document.getElementById('advancedSearchToggle');
        const advancedPanel = document.getElementById('advancedSearchPanel');

        if (advancedToggle && advancedPanel) {
            advancedToggle.addEventListener('click', () => {
                advancedPanel.classList.toggle('hidden');
                advancedToggle.textContent = advancedPanel.classList.contains('hidden') ?
                    '⚙️ Advanced' : '⚙️ Simple';
            });
        }

        // Search input with suggestions
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            let suggestionTimeout;

            searchInput.addEventListener('input', (e) => {
                const query = e.target.value;

                // Clear previous timeouts
                clearTimeout(searchTimeout);
                clearTimeout(suggestionTimeout);

                // Show suggestions after short delay
                if (query.length >= 2) {
                    suggestionTimeout = setTimeout(() => {
                        this.showSearchSuggestions(query);
                    }, 200);
                } else {
                    this.hideSearchSuggestions();
                }

                // Perform search after longer delay
                searchTimeout = setTimeout(() => {
                    if (query.trim()) {
                        this.performAdvancedSearch();
                    } else {
                        this.displayFilteredNews(); // Show all news
                    }
                }, 500);
            });

            // Hide suggestions when clicking outside
            document.addEventListener('click', (e) => {
                if (!searchInput.contains(e.target)) {
                    this.hideSearchSuggestions();
                }
            });
        }

        // Search button
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performAdvancedSearch();
            });
        }

        // Clear search button
        const clearSearchBtn = document.getElementById('clearSearchBtn');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Save search button
        const saveSearchBtn = document.getElementById('saveSearchBtn');
        if (saveSearchBtn) {
            saveSearchBtn.addEventListener('click', () => {
                this.saveCurrentSearch();
            });
        }

        // Load saved searches
        this.loadSavedSearches();
        this.populateSearchFilters();

        // Setup insights dashboard
        this.setupInsightsDashboard();
    }

    // Insights Dashboard
    setupInsightsDashboard() {
        const refreshBtn = document.getElementById('refreshInsightsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadInsights();
            });
        }

        // Load insights on startup
        this.loadInsights();
    }

    async loadInsights() {
        try {
            // Load trending analysis
            const trendingResponse = await fetch('/api/trending-analysis');
            const trendingData = await trendingResponse.json();

            // Load content insights
            const insightsResponse = await fetch('/api/content-insights');
            const insightsData = await insightsResponse.json();

            if (trendingData.success && insightsData.success) {
                this.displayTrendingTopics(trendingData.trending_analysis.trending_topics);
                this.displaySentimentOverview(insightsData.insights.sentiment_distribution);
                this.displayContentStats(insightsData.insights);
                this.displayActiveSources(trendingData.trending_analysis.trending_sources);
            }
        } catch (error) {
            console.error('Error loading insights:', error);
        }
    }

    displayTrendingTopics(topics) {
        const container = document.getElementById('trendingTopics');
        if (!container) return;

        if (!topics || topics.length === 0) {
            container.innerHTML = '<p class="text-sm text-secondary">No trending topics found</p>';
            return;
        }

        container.innerHTML = '';
        topics.slice(0, 5).forEach(topic => {
            const item = document.createElement('div');
            item.className = 'trending-item';

            const score = (topic.trend_score * 100).toFixed(0);

            item.innerHTML = `
                <span class="trending-keyword">${topic.keyword}</span>
                <span class="trending-score">${topic.count} articles</span>
            `;

            container.appendChild(item);
        });
    }

    displaySentimentOverview(sentimentData) {
        const container = document.getElementById('sentimentOverview');
        if (!container) return;

        const sentiments = [
            { name: 'Positive', value: sentimentData.positive_percentage, class: 'positive' },
            { name: 'Negative', value: sentimentData.negative_percentage, class: 'negative' },
            { name: 'Neutral', value: sentimentData.neutral_percentage, class: 'neutral' }
        ];

        container.innerHTML = '';
        sentiments.forEach(sentiment => {
            const bar = document.createElement('div');
            bar.className = 'sentiment-bar';

            bar.innerHTML = `
                <span class="sentiment-label">${sentiment.name}</span>
                <div class="sentiment-progress">
                    <div class="sentiment-fill ${sentiment.class}" style="width: ${sentiment.value}%"></div>
                </div>
                <span class="sentiment-percentage">${sentiment.value.toFixed(1)}%</span>
            `;

            container.appendChild(bar);
        });
    }

    displayContentStats(insights) {
        const container = document.getElementById('contentStats');
        if (!container) return;

        const stats = [
            { value: insights.total_articles, label: 'Total Articles' },
            { value: insights.diversity.unique_sources, label: 'Sources' },
            { value: insights.reading_metrics.average_reading_time.toFixed(1) + 'm', label: 'Avg Read Time' },
            { value: (insights.content_quality.average_score * 100).toFixed(0) + '%', label: 'Quality Score' }
        ];

        container.innerHTML = '';
        stats.forEach(stat => {
            const item = document.createElement('div');
            item.className = 'stat-item';

            item.innerHTML = `
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
            `;

            container.appendChild(item);
        });
    }

    displayActiveSources(sources) {
        const container = document.getElementById('activeSources');
        if (!container) return;

        if (!sources || sources.length === 0) {
            container.innerHTML = '<p class="text-sm text-secondary">No active sources</p>';
            return;
        }

        container.innerHTML = '';
        sources.slice(0, 5).forEach(source => {
            const item = document.createElement('div');
            item.className = 'source-item-insight';

            item.innerHTML = `
                <span class="source-name">${source.source}</span>
                <span class="source-count">${source.article_count}</span>
            `;

            container.appendChild(item);
        });
    }

    async showSearchSuggestions(query) {
        try {
            const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();

            if (data.success && data.suggestions.length > 0) {
                this.displaySearchSuggestions(data.suggestions);
            } else {
                this.hideSearchSuggestions();
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    displaySearchSuggestions(suggestions) {
        const container = document.getElementById('searchSuggestions');
        if (!container) return;

        container.innerHTML = '';
        container.classList.remove('hidden');

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'search-suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                document.getElementById('searchInput').value = suggestion;
                this.hideSearchSuggestions();
                this.performAdvancedSearch();
            });
            container.appendChild(item);
        });
    }

    hideSearchSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (container) {
            container.classList.add('hidden');
        }
    }

    async performAdvancedSearch() {
        const searchQuery = this.buildSearchQuery();

        try {
            this.showLoading('Searching...');

            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchQuery)
            });

            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results);
                this.showToast(`Found ${data.total_results} articles`, 'success');
            } else {
                this.showToast(`Search failed: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Search error: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    buildSearchQuery() {
        const searchInput = document.getElementById('searchInput');
        const searchSources = document.getElementById('searchSources');
        const searchCategories = document.getElementById('searchCategories');
        const searchDateFrom = document.getElementById('searchDateFrom');
        const searchDateTo = document.getElementById('searchDateTo');
        const searchSentiment = document.getElementById('searchSentiment');
        const searchSortBy = document.getElementById('searchSortBy');

        return {
            text: searchInput?.value || '',
            sources: searchSources ? Array.from(searchSources.selectedOptions).map(o => o.value) : [],
            categories: searchCategories ? Array.from(searchCategories.selectedOptions).map(o => o.value) : [],
            date_from: searchDateFrom?.value || null,
            date_to: searchDateTo?.value || null,
            sentiment: searchSentiment?.value || null,
            sort_by: searchSortBy?.value || 'relevance',
            sort_order: 'desc',
            limit: 50
        };
    }

    displaySearchResults(results) {
        const newsList = document.getElementById('newsList');
        if (!newsList) return;

        if (results.length === 0) {
            newsList.innerHTML = this.createEmptySearchState();
            return;
        }

        let html = '<div class="search-results-header mb-4">';
        html += `<h3>Search Results (${results.length} found)</h3>`;
        html += '</div>';

        results.forEach(result => {
            html += this.renderSearchResult(result);
        });

        newsList.innerHTML = html;
        this.updatePaginationButtons(0, 0); // Hide pagination for search results
    }

    renderSearchResult(result) {
        // Handle both direct article objects and wrapped results
        const article = result.article || result;
        const score = result.relevance_score ? (result.relevance_score * 100).toFixed(0) : '100';
        const timeAgo = this.getTimeAgo(article.timestamp || article.published_date);

        return `
            <div class="search-result-item">
                <div class="search-result-header">
                    <h4 class="search-result-title">${article.title}</h4>
                    <div class="search-result-score">Score: ${score}%</div>
                </div>

                <div class="search-result-meta">
                    <span class="source-badge">${article.source}</span>
                    <span class="category-badge ${this.getCategoryClass(article.category)}">${article.category || 'Uncategorized'}</span>
                    <span class="time-badge">${timeAgo}</span>
                    <a href="${article.link}" target="_blank" class="read-more-link">
                        Read Full Article →
                    </a>
                </div>

                <div class="search-result-content">
                    ${article.summary || article.description || 'No summary available'}
                </div>

                ${article.source ? `
                    <div class="search-result-matched-fields">
                        <strong>Source:</strong>
                        <span class="matched-field-tag">${article.source}</span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    createEmptySearchState() {
        return `
            <div class="empty-state text-center py-12">
                <div class="empty-icon text-6xl mb-4">🔍</div>
                <h3 class="text-xl font-semibold mb-2">No Results Found</h3>
                <p class="text-secondary mb-6">Try adjusting your search terms or filters</p>
                <button onclick="app.clearSearch()" class="btn btn-secondary">
                    Clear Search
                </button>
            </div>
        `;
    }

    clearSearch() {
        // Clear search inputs
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.value = '';

        const searchSources = document.getElementById('searchSources');
        if (searchSources) searchSources.selectedIndex = -1;

        const searchCategories = document.getElementById('searchCategories');
        if (searchCategories) searchCategories.selectedIndex = -1;

        const searchDateFrom = document.getElementById('searchDateFrom');
        if (searchDateFrom) searchDateFrom.value = '';

        const searchDateTo = document.getElementById('searchDateTo');
        if (searchDateTo) searchDateTo.value = '';

        const searchSentiment = document.getElementById('searchSentiment');
        if (searchSentiment) searchSentiment.value = '';

        // Hide suggestions
        this.hideSearchSuggestions();

        // Show all news
        this.displayFilteredNews();
        this.showToast('Search cleared', 'info');
    }

    populateSearchFilters() {
        // Populate sources and categories from current news data
        if (this.allNewsData && this.allNewsData.length > 0) {
            this.populateSearchSources();
            this.populateSearchCategories();
        }
    }

    populateSearchSources() {
        const searchSources = document.getElementById('searchSources');
        if (!searchSources) return;

        const sources = new Set();
        this.allNewsData.forEach(item => {
            if (item.source) sources.add(item.source);
        });

        searchSources.innerHTML = '';
        Array.from(sources).sort().forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            searchSources.appendChild(option);
        });
    }

    populateSearchCategories() {
        const searchCategories = document.getElementById('searchCategories');
        if (!searchCategories) return;

        const categories = new Set();
        this.allNewsData.forEach(item => {
            if (item.category) categories.add(item.category);
        });

        searchCategories.innerHTML = '';
        Array.from(categories).sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            searchCategories.appendChild(option);
        });
    }

    async saveCurrentSearch() {
        const searchQuery = this.buildSearchQuery();

        // Check if there's actually a search to save
        if (!searchQuery.text && searchQuery.sources.length === 0 &&
            searchQuery.categories.length === 0 && !searchQuery.sentiment) {
            this.showToast('No search criteria to save', 'warning');
            return;
        }

        const name = prompt('Enter a name for this search:');
        if (!name) return;

        try {
            const response = await fetch('/api/saved-searches', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    query: searchQuery,
                    tags: []
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(`Search "${name}" saved successfully`, 'success');
                this.loadSavedSearches();
            } else {
                this.showToast(`Failed to save search: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Error saving search: ${error.message}`, 'error');
        }
    }

    async loadSavedSearches() {
        try {
            const response = await fetch('/api/saved-searches');
            const data = await response.json();

            if (data.success) {
                this.displaySavedSearches(data.searches);
            }
        } catch (error) {
            console.error('Error loading saved searches:', error);
        }
    }

    displaySavedSearches(searches) {
        const container = document.getElementById('savedSearchesList');
        if (!container) return;

        if (searches.length === 0) {
            container.innerHTML = '<p class="text-sm text-secondary">No saved searches</p>';
            return;
        }

        container.innerHTML = '';
        searches.slice(0, 5).forEach(search => { // Show only first 5
            const item = document.createElement('div');
            item.className = 'saved-search-item';

            const useCount = search.use_count > 0 ? ` (${search.use_count} uses)` : '';

            item.innerHTML = `
                <div class="saved-search-info">
                    <div class="saved-search-name">${search.name}</div>
                    <div class="saved-search-meta">
                        ${search.query.text ? `"${search.query.text}"` : 'Advanced filters'}${useCount}
                    </div>
                </div>
                <div class="saved-search-actions">
                    <button onclick="app.useSavedSearch('${search.id}')" class="btn btn-sm btn-primary">
                        Use
                    </button>
                </div>
            `;

            container.appendChild(item);
        });
    }

    async useSavedSearch(searchId) {
        try {
            const response = await fetch(`/api/saved-searches/${searchId}/use`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results);
                this.showToast(`Loaded saved search with ${data.total_results} results`, 'success');
            } else {
                this.showToast(`Failed to load saved search: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Error loading saved search: ${error.message}`, 'error');
        }
    }

    displaySources() {
        const sourcesList = document.getElementById('sourcesList');
        if (!sourcesList) return;

        sourcesList.innerHTML = '';
        for (const [name, url] of Object.entries(this.currentConfig.news_sources || {})) {
            const div = document.createElement('div');
            div.className = 'source-item';
            div.innerHTML = `
                <span title="${url}">${name}</span>
                <div class="flex gap-2">
                    <button onclick="editSource('${name}', '${url}')" class="btn btn-sm btn-secondary">
                        ✏️
                    </button>
                    <button onclick="deleteSource('${name}')" class="btn btn-sm btn-secondary">
                        🗑️
                    </button>
                </div>
            `;
            sourcesList.appendChild(div);
        }
    }

    async addSource(name, url) {
        if (!name || !url) {
            this.showToast('Please enter both source name and URL', 'warning');
            return;
        }

        try {
            this.currentConfig.news_sources = this.currentConfig.news_sources || {};
            this.currentConfig.news_sources[name] = url;
            await this.saveConfig();

            // Clear input fields
            document.getElementById('sourceName').value = '';
            document.getElementById('sourceUrl').value = '';

            this.showToast(`Added source: ${name}`, 'success');
        } catch (error) {
            this.showToast(`Error adding source: ${error.message}`, 'error');
        }
    }

    async deleteSource(name) {
        try {
            delete this.currentConfig.news_sources[name];
            await this.saveConfig();
            this.showToast(`Deleted source: ${name}`, 'success');
        } catch (error) {
            this.showToast(`Error deleting source: ${error.message}`, 'error');
        }
    }

    async populateOllamaModels() {
        const ollamaModelSelect = document.getElementById('ollamaModelSelect');
        const currentModelInfo = document.getElementById('currentModelInfo');
        if (!ollamaModelSelect) return;

        ollamaModelSelect.innerHTML = '<option value="">Loading models...</option>';

        try {
            const response = await fetch('/api/ollama-status');
            const data = await response.json();

            ollamaModelSelect.innerHTML = '';

            if (data.available && data.models && data.models.length > 0) {
                // Add a default option
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = '-- Select a model --';
                ollamaModelSelect.appendChild(defaultOption);

                // Add available models
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    ollamaModelSelect.appendChild(option);
                });

                // Set current selected model
                if (this.currentConfig.ollama_model) {
                    ollamaModelSelect.value = this.currentConfig.ollama_model;
                }

                // Update current model info
                if (currentModelInfo) {
                    const currentModel = this.currentConfig.ollama_model || 'None selected';
                    currentModelInfo.textContent = `Current: ${currentModel}`;
                }

                ollamaModelSelect.disabled = false;
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Ollama not available';
                ollamaModelSelect.appendChild(option);
                ollamaModelSelect.disabled = true;

                if (currentModelInfo) {
                    currentModelInfo.textContent = 'Ollama service not available';
                }
            }
        } catch (error) {
            console.error('Error fetching Ollama models:', error);
            ollamaModelSelect.innerHTML = '<option value="">Error loading models</option>';
            ollamaModelSelect.disabled = true;

            if (currentModelInfo) {
                currentModelInfo.textContent = 'Error loading models';
            }
        }
    }

    async saveOllamaModel() {
        const selectedModel = document.getElementById('ollamaModelSelect')?.value;
        if (!selectedModel) {
            this.showToast('Please select an Ollama model', 'warning');
            return;
        }

        try {
            // Use the new API endpoint for updating Ollama model
            const response = await fetch('/api/ollama-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ model: selectedModel })
            });

            const result = await response.json();

            if (result.success) {
                this.currentConfig.ollama_model = selectedModel;
                this.showToast(result.message, 'success');
            } else {
                this.showToast(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Error saving model: ${error.message}`, 'error');
        }
    }

    async saveConfig() {
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentConfig)
            });

            const data = await response.json();

            if (data.success) {
                this.displaySources(); // Refresh the sources display
                return true;
            } else {
                throw new Error(data.message || 'Failed to save configuration');
            }
        } catch (error) {
            console.error('Error saving config:', error);
            this.showToast(`Error saving configuration: ${error.message}`, 'error');
            return false;
        }
    }

    // UI State Templates
    createSkeletonLoader() {
        return Array(4).fill().map(() => `
            <div class="skeleton-item card p-6 mb-4">
                <div class="skeleton-line skeleton-title mb-3"></div>
                <div class="skeleton-line skeleton-meta mb-4"></div>
                <div class="skeleton-line skeleton-text mb-2"></div>
                <div class="skeleton-line skeleton-text mb-2"></div>
                <div class="skeleton-line skeleton-text-short"></div>
            </div>
        `).join('');
    }

    createEmptyState() {
        return `
            <div class="empty-state text-center py-12">
                <div class="empty-icon text-6xl mb-4">📰</div>
                <h3 class="text-xl font-semibold mb-2">No News Available</h3>
                <p class="text-secondary mb-6">Click "Fetch & Summarize News" to get the latest articles</p>
                <button onclick="app.fetchNews()" class="btn btn-primary">
                    Fetch News Now
                </button>
            </div>
        `;
    }

    createErrorState(error) {
        return `
            <div class="error-state text-center py-12">
                <div class="error-icon text-6xl mb-4">⚠️</div>
                <h3 class="text-xl font-semibold mb-2">Error Loading News</h3>
                <p class="text-secondary mb-6">${error}</p>
                <button onclick="app.loadNews()" class="btn btn-secondary">
                    Try Again
                </button>
            </div>
        `;
    }

    // ===== AI FEATURES FUNCTIONALITY =====
    setupAIFeatures() {
        this.debug('🤖 Setting up AI Features');

        // Initialize AI features state
        this.aiFeatures = {
            isVisible: false,
            currentTab: 'chat',
            chatHistory: [],
            isProcessing: false
        };

        // Setup event listeners for AI features
        this.setupAIEventListeners();

        // Load AI features status
        this.loadAIFeaturesStatus();

        this.debug('✅ AI Features setup complete');
    }

    setupAIEventListeners() {
        // Toggle AI Features Dashboard
        const toggleBtn = document.getElementById('toggleAiFeaturesBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleAIFeatures());
        }

        // AI Tab switching
        const tabBtns = document.querySelectorAll('.ai-tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchAITab(tab);
            });
        });

        // AI Chat functionality
        this.setupAIChatListeners();

        // Other AI feature listeners
        this.setupAIFeatureButtons();
    }

    setupAIChatListeners() {
        const chatInput = document.getElementById('aiChatInput');
        const sendBtn = document.getElementById('aiChatSendBtn');
        const suggestions = document.querySelectorAll('.suggestion-btn');

        if (chatInput && sendBtn) {
            // Enable/disable send button based on input
            chatInput.addEventListener('input', (e) => {
                sendBtn.disabled = !e.target.value.trim();
            });

            // Send message on Enter key
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
                    e.preventDefault();
                    this.sendAIChatMessage();
                }
            });

            // Send button click
            sendBtn.addEventListener('click', () => this.sendAIChatMessage());
        }

        // Suggestion buttons
        suggestions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestion = e.target.textContent;
                if (chatInput) {
                    chatInput.value = suggestion;
                    sendBtn.disabled = false;
                    this.sendAIChatMessage();
                }
            });
        });
    }

    setupAIFeatureButtons() {
        // Smart Categorization
        const categorizationBtn = document.getElementById('runCategorizationBtn');
        if (categorizationBtn) {
            categorizationBtn.addEventListener('click', () => this.runSmartCategorization());
        }

        // Content Recommendations
        const recommendationsBtn = document.getElementById('refreshRecommendationsBtn');
        if (recommendationsBtn) {
            recommendationsBtn.addEventListener('click', () => this.loadContentRecommendations());
        }

        // Daily Briefing
        const dailyBriefingBtn = document.getElementById('generateDailyBriefingBtn');
        if (dailyBriefingBtn) {
            dailyBriefingBtn.addEventListener('click', () => this.generateDailyBriefing());
        }

        // Topic Deep Dive
        const topicDeepDiveBtn = document.getElementById('generateTopicDeepDiveBtn');
        const runDeepDiveBtn = document.getElementById('runDeepDiveBtn');

        if (topicDeepDiveBtn) {
            topicDeepDiveBtn.addEventListener('click', () => this.toggleTopicDeepDiveInput());
        }

        if (runDeepDiveBtn) {
            runDeepDiveBtn.addEventListener('click', () => this.runTopicDeepDive());
        }

        // Relationship Analysis
        const relationshipsBtn = document.getElementById('analyzeRelationshipsBtn');
        if (relationshipsBtn) {
            relationshipsBtn.addEventListener('click', () => this.analyzeContentRelationships());
        }
    }

    toggleAIFeatures() {
        const section = document.getElementById('aiFeaturesSection');
        const btn = document.getElementById('toggleAiFeaturesBtn');

        if (section && btn) {
            this.aiFeatures.isVisible = !this.aiFeatures.isVisible;

            if (this.aiFeatures.isVisible) {
                section.style.display = 'block';
                btn.textContent = '🤖 Hide AI Features';
                btn.classList.add('active');

                // Load initial data for current tab
                this.loadAITabData(this.aiFeatures.currentTab);
            } else {
                section.style.display = 'none';
                btn.textContent = '🤖 AI Features';
                btn.classList.remove('active');
            }
        }
    }

    switchAITab(tabName) {
        // Update active tab button
        document.querySelectorAll('.ai-tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active tab content
        document.querySelectorAll('.ai-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`).classList.add('active');

        // Update current tab state
        this.aiFeatures.currentTab = tabName;

        // Load data for the new tab
        this.loadAITabData(tabName);
    }

    loadAITabData(tabName) {
        switch (tabName) {
            case 'chat':
                // Chat is always ready
                break;
            case 'categorization':
                // Load categorization if not already loaded
                break;
            case 'recommendations':
                this.loadContentRecommendations();
                break;
            case 'briefing':
                // Briefing is generated on demand
                break;
            case 'relationships':
                // Relationships are analyzed on demand
                break;
        }
    }

    async loadAIFeaturesStatus() {
        try {
            const response = await fetch('/api/ai-features/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.debug('AI Features Status:', data);
                // You could update UI based on which features are available
                this.aiFeatures.status = data;
            } else {
                console.warn('AI Features status check failed:', data.error);
            }
        } catch (error) {
            console.error('Error loading AI features status:', error);
            // Don't show error to user as this is not critical
        }
    }

    // AI Chat Methods (enhanced versions are at the end of the class)

    formatMessageContent(content) {
        // Basic formatting for AI responses
        if (!content || typeof content !== 'string') {
            return String(content || '');
        }

        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    formatMarkdownContent(content) {
        // Enhanced markdown formatting for briefings
        if (!content || typeof content !== 'string') {
            return String(content || '');
        }

        let formatted = content
            // Escape HTML entities first
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')

            // Headers (process from most specific to least specific)
            .replace(/^### (.*$)/gm, '<h3 class="briefing-h3">$1</h3>')
            .replace(/^## (.*$)/gm, '<h2 class="briefing-h2">$1</h2>')
            .replace(/^# (.*$)/gm, '<h1 class="briefing-h1">$1</h1>')

            // Bold and italic
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')

            // Lists - handle bullet points and numbered lists
            .replace(/^[•\-\*] (.*$)/gm, '<li class="briefing-bullet">$1</li>')
            .replace(/^\d+\. (.*$)/gm, '<li class="briefing-numbered">$1</li>');

        // Wrap consecutive list items in proper list tags
        formatted = formatted.replace(
            /(<li class="briefing-bullet">.*?<\/li>)(\s*<li class="briefing-bullet">.*?<\/li>)*/gs,
            (match) => `<ul class="briefing-list">${match}</ul>`
        );

        formatted = formatted.replace(
            /(<li class="briefing-numbered">.*?<\/li>)(\s*<li class="briefing-numbered">.*?<\/li>)*/gs,
            (match) => `<ol class="briefing-list">${match}</ol>`
        );

        // Handle paragraphs and line breaks
        formatted = formatted
            // Split into lines and process
            .split('\n')
            .map(line => {
                line = line.trim();
                if (!line) return '';

                // Skip lines that are already HTML elements
                if (line.match(/^<(h[1-6]|ul|ol|li)/)) {
                    return line;
                }

                // Wrap regular text in paragraph tags
                return `<p class="briefing-paragraph">${line}</p>`;
            })
            .filter(line => line) // Remove empty lines
            .join('\n');

        return formatted;
    }

    // Smart Categorization Methods
    async runSmartCategorization() {
        const btn = document.getElementById('runCategorizationBtn');
        const resultsContainer = document.getElementById('categorizationResults');

        if (!btn || !resultsContainer) return;

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Analyzing...';

        try {
            // Get all articles for categorization
            const articles = this.allNewsData;
            if (!articles || articles.length === 0) {
                resultsContainer.innerHTML = '<p class="text-secondary">No articles available for categorization. Please load news first.</p>';
                return;
            }

            const results = [];

            // Process articles in batches to avoid overwhelming the UI
            for (let i = 0; i < Math.min(articles.length, 10); i++) {
                const article = articles[i];

                const response = await fetch('/api/ai-features/smart-categorization', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ article: article })
                });

                const data = await response.json();
                if (data.success) {
                    results.push({
                        title: article.title,
                        categories: data.categories
                    });
                }
            }

            this.displayCategorizationResults(results);

        } catch (error) {
            console.error('Smart categorization error:', error);
            resultsContainer.innerHTML = '<p class="text-error">Error running categorization analysis.</p>';
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🔄 Analyze All Articles';
        }
    }

    displayCategorizationResults(results) {
        const container = document.getElementById('categorizationResults');
        if (!container || !results.length) return;

        let html = '<div class="categorization-results-list">';

        results.forEach(result => {
            html += `
                <div class="categorization-item">
                    <h5 class="categorization-title">${result.title}</h5>
                    <div class="categorization-tags">
            `;

            let hasCategories = false;

            if (result.categories && result.categories.topics && result.categories.topics.length > 0) {
                result.categories.topics.forEach(topic => {
                    html += `<span class="category-tag topic-tag">${topic.name} (${Math.round(topic.confidence * 100)}%)</span>`;
                    hasCategories = true;
                });
            }

            if (result.categories && result.categories.industries && result.categories.industries.length > 0) {
                result.categories.industries.forEach(industry => {
                    html += `<span class="category-tag industry-tag">${industry.name} (${Math.round(industry.confidence * 100)}%)</span>`;
                    hasCategories = true;
                });
            }

            if (!hasCategories) {
                html += `<span class="category-tag neutral-tag">No categories detected</span>`;
            }

            html += `
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    // Content Recommendations Methods
    async loadContentRecommendations() {
        const container = document.getElementById('recommendationsResults');
        if (!container) return;

        container.innerHTML = '<p class="text-secondary">Loading recommendations...</p>';

        try {
            const response = await fetch('/api/ai-features/recommendations');
            const data = await response.json();

            if (data.success && data.recommendations) {
                this.displayRecommendations(data.recommendations);
            } else {
                container.innerHTML = '<p class="text-secondary">No recommendations available at this time.</p>';
            }

        } catch (error) {
            console.error('Recommendations error:', error);
            container.innerHTML = '<p class="text-error">Error loading recommendations.</p>';
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendationsResults');
        if (!container) return;

        let html = '<div class="recommendations-list">';

        recommendations.forEach(rec => {
            // Extract data from the correct structure
            const article = rec.article || rec;
            const title = article.title || 'No title available';
            const source = article.source || 'Unknown source';
            const score = rec.score || 0;
            const reasons = rec.reasons || ['Recommended for you'];
            const reason = Array.isArray(reasons) ? reasons.join(', ') : reasons;
            const summary = article.summary || article.description || '';
            const link = article.link || '#';

            html += `
                <div class="recommendation-item">
                    <h5 class="recommendation-title">
                        <a href="${link}" target="_blank" rel="noopener noreferrer">${title}</a>
                    </h5>
                    <p class="recommendation-summary">${summary.substring(0, 150)}${summary.length > 150 ? '...' : ''}</p>
                    <p class="recommendation-reason">💡 ${reason}</p>
                    <div class="recommendation-meta">
                        <span class="recommendation-score">Score: ${Math.round(score * 100)}%</span>
                        <span class="recommendation-source">📰 ${source}</span>
                        <span class="recommendation-category">${article.category || 'General'}</span>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;
    }

    // Smart Briefing Methods
    async generateDailyBriefing() {
        const btn = document.getElementById('generateDailyBriefingBtn');
        const container = document.getElementById('briefingResults');

        if (!btn || !container) return;

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Generating...';
        container.innerHTML = '<p class="text-secondary">Generating daily briefing...</p>';

        try {
            const response = await fetch('/api/ai-features/daily-briefing');
            const data = await response.json();

            if (data.success && data.briefing) {
                this.displayBriefing(data.briefing, 'Daily Briefing');
            } else {
                container.innerHTML = '<p class="text-error">Error generating daily briefing.</p>';
            }

        } catch (error) {
            console.error('Daily briefing error:', error);
            container.innerHTML = '<p class="text-error">Error generating daily briefing.</p>';
        } finally {
            btn.disabled = false;
            btn.innerHTML = '📅 Daily Briefing';
        }
    }

    toggleTopicDeepDiveInput() {
        const inputSection = document.getElementById('topicDeepDiveInput');
        const btn = document.getElementById('generateTopicDeepDiveBtn');

        if (inputSection && btn) {
            const isVisible = inputSection.style.display !== 'none';
            inputSection.style.display = isVisible ? 'none' : 'block';
            btn.textContent = isVisible ? '🔍 Topic Deep Dive' : '❌ Cancel';

            if (!isVisible) {
                document.getElementById('deepDiveTopic')?.focus();
            }
        }
    }

    async runTopicDeepDive() {
        const topicInput = document.getElementById('deepDiveTopic');
        const btn = document.getElementById('runDeepDiveBtn');
        const container = document.getElementById('briefingResults');

        if (!topicInput || !btn || !container) return;

        const topic = topicInput.value.trim();
        if (!topic) {
            this.showToast('Please enter a topic for deep dive analysis', 'warning');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Analyzing...';
        container.innerHTML = '<p class="text-secondary">Analyzing topic...</p>';

        try {
            const response = await fetch(`/api/ai-features/topic-deep-dive?topic=${encodeURIComponent(topic)}`);
            const data = await response.json();

            if (data.success && data.deep_dive) {
                this.displayBriefing(data.deep_dive, `Deep Dive: ${topic}`);
                this.toggleTopicDeepDiveInput(); // Hide input section
                topicInput.value = '';
            } else {
                container.innerHTML = '<p class="text-error">Error generating topic deep dive.</p>';
            }

        } catch (error) {
            console.error('Topic deep dive error:', error);
            container.innerHTML = '<p class="text-error">Error generating topic deep dive.</p>';
        } finally {
            btn.disabled = false;
            btn.innerHTML = 'Analyze';
        }
    }

    displayBriefing(briefing, title) {
        const container = document.getElementById('briefingResults');
        if (!container) return;

        let html = `
            <div class="briefing-content">
                <h4 class="briefing-title">${title}</h4>
                <div class="briefing-body">
        `;

        if (typeof briefing === 'string') {
            // Format as markdown if it contains markdown syntax
            if (briefing.includes('#') || briefing.includes('**') || briefing.includes('•')) {
                html += `<div class="briefing-markdown">${this.formatMarkdownContent(briefing)}</div>`;
            } else {
                html += `<p class="briefing-paragraph">${briefing}</p>`;
            }
        } else if (briefing.content) {
            // Format the content as markdown
            if (typeof briefing.content === 'string' &&
                (briefing.content.includes('#') || briefing.content.includes('**') || briefing.content.includes('•'))) {
                html += `<div class="briefing-markdown">${this.formatMarkdownContent(briefing.content)}</div>`;
            } else {
                html += `<div class="briefing-text">${briefing.content}</div>`;
            }
        } else {
            // Handle structured briefing data
            if (briefing.analysis) {
                html += `<div class="briefing-section">
                    <h5>Analysis</h5>
                    <div class="briefing-markdown">${this.formatMarkdownContent(briefing.analysis)}</div>
                </div>`;
            }

            if (briefing.key_points) {
                html += `<div class="briefing-section">
                    <h5>Key Points</h5>
                    <ul class="briefing-list">`;
                briefing.key_points.forEach(point => {
                    html += `<li class="briefing-bullet">${point}</li>`;
                });
                html += `</ul></div>`;
            }

            if (briefing.recommendations) {
                html += `<div class="briefing-section">
                    <h5>Recommendations</h5>
                    <div class="briefing-markdown">${this.formatMarkdownContent(briefing.recommendations)}</div>
                </div>`;
            }
        }

        // Add metadata if available
        if (briefing.metadata) {
            html += `
                <div class="briefing-metadata">
                    <div class="metadata-grid">
                        ${briefing.metadata.articles_analyzed ? `<span class="metadata-item">📰 ${briefing.metadata.articles_analyzed} articles analyzed</span>` : ''}
                        ${briefing.metadata.topics_covered ? `<span class="metadata-item">🏷️ ${briefing.metadata.topics_covered} topics covered</span>` : ''}
                        ${briefing.date ? `<span class="metadata-item">📅 ${briefing.date}</span>` : ''}
                    </div>
                </div>
            `;
        }

        html += `
                </div>
                <div class="briefing-meta">
                    <small class="text-secondary">Generated at ${new Date().toLocaleString()}</small>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    // Content Relationships Methods
    async analyzeContentRelationships() {
        const btn = document.getElementById('analyzeRelationshipsBtn');
        const container = document.getElementById('relationshipsResults');

        if (!btn || !container) return;

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Analyzing...';
        container.innerHTML = '<p class="text-secondary">Analyzing content relationships...</p>';

        try {
            const articles = this.allNewsData;
            if (!articles || articles.length === 0) {
                container.innerHTML = '<p class="text-secondary">No articles available for relationship analysis. Please load news first.</p>';
                return;
            }

            const response = await fetch('/api/ai-features/relationship-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ articles: articles.slice(0, 20) }) // Limit for performance
            });

            const data = await response.json();

            if (data.success && data.relationships) {
                this.displayRelationships(data.relationships);
            } else {
                container.innerHTML = '<p class="text-error">Error analyzing content relationships.</p>';
            }

        } catch (error) {
            console.error('Relationship analysis error:', error);
            container.innerHTML = '<p class="text-error">Error analyzing content relationships.</p>';
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🔄 Analyze Relationships';
        }
    }

    displayRelationships(relationships) {
        const container = document.getElementById('relationshipsResults');
        if (!container) return;

        let html = '<div class="relationships-content">';

        if (relationships.similar_articles && relationships.similar_articles.length > 0) {
            html += `
                <div class="relationship-section">
                    <h5>📎 Similar Articles</h5>
                    <div class="relationship-items">
            `;

            relationships.similar_articles.forEach(group => {
                html += `
                    <div class="relationship-group">
                        <div class="relationship-score">Similarity: ${Math.round(group.similarity_score * 100)}%</div>
                        <div class="relationship-articles">
                `;

                group.articles.forEach(article => {
                    html += `<div class="relationship-article">${article.title}</div>`;
                });

                html += `
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        if (relationships.follow_ups && relationships.follow_ups.length > 0) {
            html += `
                <div class="relationship-section">
                    <h5>🔄 Follow-up Stories</h5>
                    <div class="relationship-items">
            `;

            relationships.follow_ups.forEach(followUp => {
                html += `
                    <div class="relationship-group">
                        <div class="relationship-original">Original: ${followUp.original_article.title}</div>
                        <div class="relationship-followup">Follow-up: ${followUp.follow_up_article.title}</div>
                        <div class="relationship-score">Confidence: ${Math.round(followUp.confidence * 100)}%</div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    // Individual Article AI Features
    async explainArticle(itemId) {
        const btn = document.querySelector(`[data-item-id="${itemId}"].explain-article-btn`);
        const explanationDiv = document.getElementById(`explanation-${itemId}`);

        if (!btn || !explanationDiv) return;

        // Find the article data
        const article = this.findArticleById(itemId);
        if (!article) {
            this.showToast('Article not found', 'error');
            return;
        }

        // Toggle explanation visibility
        if (explanationDiv.style.display !== 'none') {
            explanationDiv.style.display = 'none';
            btn.textContent = '🤖 Explain Article';
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Explaining...';
        explanationDiv.style.display = 'block';
        explanationDiv.innerHTML = '<p class="text-secondary">Generating explanation...</p>';

        try {
            const response = await fetch('/api/ai-features/explain-article', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    article: article,
                    detail_level: 'medium'
                })
            });

            const data = await response.json();

            if (data.success) {
                // Handle the structured explanation response from AI assistant
                let explanationText = '';
                let keyInfo = '';
                let followUps = [];

                if (data.explanation && typeof data.explanation === 'object') {
                    // Extract main explanation text
                    if (data.explanation.explanation && data.explanation.explanation.main_explanation) {
                        explanationText = data.explanation.explanation.main_explanation;
                    } else if (data.explanation.explanation) {
                        explanationText = data.explanation.explanation;
                    } else if (typeof data.explanation === 'string') {
                        explanationText = data.explanation;
                    }

                    // Extract key information
                    if (data.explanation.key_information) {
                        const keyInfoObj = data.explanation.key_information;
                        let keyInfoParts = [];

                        if (keyInfoObj.main_topics && keyInfoObj.main_topics.length > 0) {
                            keyInfoParts.push(`<strong>Topics:</strong> ${keyInfoObj.main_topics.join(', ')}`);
                        }

                        if (keyInfoObj.sentiment && keyInfoObj.sentiment !== 'neutral') {
                            keyInfoParts.push(`<strong>Sentiment:</strong> ${keyInfoObj.sentiment}`);
                        }

                        if (keyInfoParts.length > 0) {
                            keyInfo = `<div class="explanation-key-info">${keyInfoParts.join('<br>')}</div>`;
                        }
                    }

                    // Extract follow-up questions
                    if (data.explanation.follow_up_questions && data.explanation.follow_up_questions.length > 0) {
                        followUps = data.explanation.follow_up_questions.slice(0, 3);
                    }
                } else if (typeof data.explanation === 'string') {
                    explanationText = data.explanation;
                }

                if (!explanationText) {
                    explanationText = 'No explanation available';
                }

                let followUpHtml = '';
                if (followUps.length > 0) {
                    followUpHtml = `
                        <div class="explanation-follow-ups">
                            <h6>💡 Follow-up Questions:</h6>
                            <div class="follow-up-questions">
                                ${followUps.map((q, index) => `
                                    <button class="follow-up-question-btn"
                                            onclick="app.askFollowUpQuestion('${itemId}', '${q.replace(/'/g, "\\'")}')">
                                        ${q}
                                    </button>
                                `).join('')}
                            </div>
                            <div class="follow-up-actions">
                                <button class="btn btn-sm btn-primary"
                                        onclick="app.openArticleChatContext('${itemId}')">
                                    💬 Chat about this article
                                </button>
                            </div>
                        </div>
                    `;
                }

                explanationDiv.innerHTML = `
                    <div class="article-explanation-content">
                        <h5>🤖 AI Explanation</h5>
                        <div class="explanation-text">${this.formatMessageContent(explanationText)}</div>
                        ${keyInfo}
                        ${followUpHtml}
                    </div>
                `;
                btn.textContent = '❌ Hide Explanation';
            } else {
                explanationDiv.innerHTML = `<p class="text-error">Error: ${data.error}</p>`;
                btn.textContent = '🤖 Explain Article';
            }

        } catch (error) {
            console.error('Article explanation error:', error);
            explanationDiv.innerHTML = '<p class="text-error">Error generating explanation.</p>';
            btn.textContent = '🤖 Explain Article';
        } finally {
            btn.disabled = false;
        }
    }

    async categorizeArticle(itemId) {
        const btn = document.querySelector(`[data-item-id="${itemId}"].categorize-article-btn`);

        if (!btn) return;

        // Find the article data
        const article = this.findArticleById(itemId);
        if (!article) {
            this.showToast('Article not found', 'error');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Categorizing...';

        try {
            const response = await fetch('/api/ai-features/smart-categorization', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ article: article })
            });

            const data = await response.json();

            if (data.success) {
                // Show categorization results in a toast or modal
                let categoryText = 'Categories: ';
                let hasCategories = false;

                if (data.categories && data.categories.topics && data.categories.topics.length > 0) {
                    categoryText += data.categories.topics.map(t => `${t.name} (${Math.round(t.confidence * 100)}%)`).join(', ');
                    hasCategories = true;
                }

                if (data.categories && data.categories.industries && data.categories.industries.length > 0) {
                    if (hasCategories) categoryText += ', ';
                    categoryText += data.categories.industries.map(i => `${i.name} (${Math.round(i.confidence * 100)}%)`).join(', ');
                    hasCategories = true;
                }

                if (!hasCategories) {
                    categoryText = 'No specific categories detected';
                }

                this.showToast(categoryText, 'success', 5000);
                btn.textContent = '✅ Categorized';

                // Optionally update the article's category badge
                setTimeout(() => {
                    btn.textContent = '🎯 Categorize';
                }, 3000);
            } else {
                this.showToast(`Categorization error: ${data.error}`, 'error');
                btn.textContent = '🎯 Categorize';
            }

        } catch (error) {
            console.error('Article categorization error:', error);
            this.showToast('Error categorizing article', 'error');
            btn.textContent = '🎯 Categorize';
        } finally {
            btn.disabled = false;
        }
    }

    findArticleById(itemId) {
        // Find article in the current news data
        for (const article of this.allNewsData) {
            if (this.generateItemId(article) === itemId) {
                return article;
            }
        }
        return null;
    }

    // Article-specific chat functionality
    async askFollowUpQuestion(itemId, question) {
        // Find the article
        const article = this.findArticleById(itemId);
        if (!article) {
            this.showToast('Article not found', 'error');
            return;
        }

        // Open AI Features if not already open
        if (!this.aiFeatures.isVisible) {
            this.toggleAIFeatures();
        }

        // Switch to chat tab
        this.switchAITab('chat');

        // Add context message about the article
        const contextMessage = `I'm asking about the article: "${article.title}" from ${article.source}`;
        this.addChatMessage(contextMessage, 'user');

        // Add the follow-up question
        const chatInput = document.getElementById('aiChatInput');
        if (chatInput) {
            chatInput.value = question;

            // Trigger the send
            await this.sendAIChatMessage();
        }

        // Scroll to AI features section
        document.getElementById('aiFeaturesSection')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    async openArticleChatContext(itemId) {
        // Find the article
        const article = this.findArticleById(itemId);
        if (!article) {
            this.showToast('Article not found', 'error');
            return;
        }

        // Open AI Features if not already open
        if (!this.aiFeatures.isVisible) {
            this.toggleAIFeatures();
        }

        // Switch to chat tab
        this.switchAITab('chat');

        // Set up article context in chat
        const contextMessage = `Let's discuss this article: "${article.title}" from ${article.source}. ${article.summary ? 'Summary: ' + article.summary.substring(0, 200) + '...' : ''}`;

        // Add context to chat input
        const chatInput = document.getElementById('aiChatInput');
        if (chatInput) {
            chatInput.value = `Tell me more about: ${article.title}`;
            chatInput.focus();
        }

        // Add a system message to provide context
        this.addChatMessage(`📰 Article Context: "${article.title}" from ${article.source}`, 'system');

        // Scroll to AI features section
        document.getElementById('aiFeaturesSection')?.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

        this.showToast('Chat context set for this article. Ask your questions!', 'success');
    }

    // Enhanced chat message method to handle system messages
    addChatMessage(content, sender, isError = false) {
        const messagesContainer = document.getElementById('aiChatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');

        if (sender === 'system') {
            messageDiv.className = 'ai-message system-context-message';
            messageDiv.innerHTML = `
                <div class="message-avatar">📰</div>
                <div class="message-content system-context">
                    <p>${this.formatMessageContent(content)}</p>
                </div>
            `;
        } else {
            messageDiv.className = `ai-message ${sender === 'user' ? 'user-message' : 'system-message'}`;
            const avatar = sender === 'user' ? '👤' : (isError ? '⚠️' : '🤖');

            messageDiv.innerHTML = `
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">
                    <p>${this.formatMessageContent(content)}</p>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addFollowUpSuggestions(suggestions) {
        const messagesContainer = document.getElementById('aiChatMessages');
        if (!messagesContainer || !suggestions.length) return;

        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'ai-message suggestions-message';

        let suggestionsHtml = `
            <div class="message-avatar">💡</div>
            <div class="message-content suggestions-content">
                <p><strong>Follow-up suggestions:</strong></p>
                <div class="chat-follow-up-suggestions">
        `;

        suggestions.forEach(suggestion => {
            suggestionsHtml += `
                <button class="chat-suggestion-btn" onclick="app.useChatSuggestion('${suggestion.replace(/'/g, "\\'")}')">
                    ${suggestion}
                </button>
            `;
        });

        suggestionsHtml += `
                </div>
            </div>
        `;

        suggestionsDiv.innerHTML = suggestionsHtml;
        messagesContainer.appendChild(suggestionsDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    useChatSuggestion(suggestion) {
        const chatInput = document.getElementById('aiChatInput');
        if (chatInput) {
            chatInput.value = suggestion;
            chatInput.focus();

            // Auto-send the suggestion
            this.sendAIChatMessage();
        }
    }

    // Enhanced send chat message to include article context
    async sendAIChatMessage() {
        const chatInput = document.getElementById('aiChatInput');
        const sendBtn = document.getElementById('aiChatSendBtn');
        const messagesContainer = document.getElementById('aiChatMessages');

        if (!chatInput || !messagesContainer || this.aiFeatures.isProcessing) return;

        const message = chatInput.value.trim();
        if (!message) return;

        // Disable input while processing
        this.aiFeatures.isProcessing = true;
        chatInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="spinner"></div>';

        try {
            // Add user message to chat (but not system context messages)
            if (!message.startsWith('📰 Article Context:')) {
                this.addChatMessage(message, 'user');
            }
            chatInput.value = '';

            // Prepare context including recent articles for better responses
            const recentArticles = this.allNewsData.slice(0, 5); // Include recent articles for context

            // Send to AI assistant
            const response = await fetch('/api/ai-features/ai-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: {
                        conversation_history: this.aiFeatures.chatHistory || [],
                        recent_articles: recentArticles,
                        chat_mode: 'article_discussion'
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success && data.response) {
                // Handle the structured response from AI assistant chat
                let responseText = '';
                let followUpSuggestions = [];

                if (typeof data.response === 'string') {
                    responseText = data.response;
                } else if (data.response && typeof data.response === 'object') {
                    // Extract main message text
                    if (data.response.message) {
                        responseText = data.response.message;
                    } else if (data.response.response) {
                        responseText = data.response.response;
                    } else if (data.response.content) {
                        responseText = data.response.content;
                    } else if (data.response.text) {
                        responseText = data.response.text;
                    } else {
                        // Fallback: try to extract meaningful content from object
                        responseText = JSON.stringify(data.response, null, 2);
                    }

                    // Extract follow-up suggestions if available
                    if (data.response.follow_up_suggestions && Array.isArray(data.response.follow_up_suggestions)) {
                        followUpSuggestions = data.response.follow_up_suggestions.slice(0, 3);
                    }
                } else {
                    responseText = 'No response available';
                }

                // Add AI response to chat
                this.addChatMessage(responseText, 'ai');

                // Add follow-up suggestions if available
                if (followUpSuggestions.length > 0) {
                    this.addFollowUpSuggestions(followUpSuggestions);
                }

                // Update chat history
                this.aiFeatures.chatHistory = this.aiFeatures.chatHistory || [];
                this.aiFeatures.chatHistory.push(
                    { role: 'user', content: message },
                    { role: 'assistant', content: responseText }
                );
            } else {
                const errorMsg = data.error || 'Unknown error occurred';
                this.addChatMessage(`Sorry, I encountered an error: ${errorMsg}`, 'ai', true);
            }

        } catch (error) {
            console.error('AI Chat error:', error);
            this.addChatMessage('Sorry, I\'m having trouble connecting right now. Please try again.', 'ai', true);
        } finally {
            // Re-enable input
            this.aiFeatures.isProcessing = false;
            chatInput.disabled = false;
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<span class="send-icon">📤</span>';
            chatInput.focus();
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM Content Loaded - Initializing NewsFeedApp');

    // Debug: Check for existing loading overlays
    const existingOverlays = document.querySelectorAll('.loading-overlay');
    console.log(`Found ${existingOverlays.length} existing loading overlays:`, existingOverlays);

    // Debug: Check page state
    console.log('Page state on load:', {
        readyState: document.readyState,
        body: document.body,
        loadingElements: document.querySelectorAll('.loading-overlay, .skeleton-loader, .loading-spinner').length
    });

    window.app = new NewsFeedApp();

    // Debug: Final state after app initialization
    setTimeout(() => {
        const finalOverlays = document.querySelectorAll('.loading-overlay');
        console.log(`After app init - ${finalOverlays.length} loading overlays:`, finalOverlays);
        finalOverlays.forEach((overlay, index) => {
            console.log(`Overlay ${index + 1}:`, {
                classes: overlay.className,
                display: overlay.style.display,
                visibility: overlay.style.visibility,
                hidden: overlay.classList.contains('hidden')
            });
        });

        // Automatic UI accessibility check
        if (window.app && typeof window.app.ensureUIAccessible === 'function') {
            console.log('🔓 Running automatic UI accessibility check');
            window.app.ensureUIAccessible();
        }
    }, 1000);
});

// Global emergency functions for browser console
window.emergencyUIReset = function() {
    console.log('🚨 Global Emergency UI Reset - Starting comprehensive cleanup');

    // Use the app's comprehensive UI management if available
    if (window.app && typeof window.app.ensureUIAccessible === 'function') {
        console.log('Using app.ensureUIAccessible()');
        window.app.ensureUIAccessible();
    } else {
        console.log('App not available, using manual cleanup');

        // Manual cleanup
        const allLoadingElements = document.querySelectorAll('.loading-overlay, .skeleton-loader, .loading-spinner');
        console.log(`Found ${allLoadingElements.length} loading elements to hide:`, allLoadingElements);

        allLoadingElements.forEach((element, index) => {
            console.log(`Hiding element ${index + 1}:`, element);
            element.classList.add('hidden');
            element.style.display = 'none';
            element.style.visibility = 'hidden';
            element.style.opacity = '0';
            element.style.zIndex = '-1';
        });

        // Force show main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.display = 'block';
            mainContent.style.visibility = 'visible';
            mainContent.style.opacity = '1';
            console.log('✅ Main content forced visible');
        } else {
            console.log('⚠️ Main content not found');
        }

        // Re-enable buttons
        const buttons = document.querySelectorAll('button:disabled');
        buttons.forEach(button => {
            button.disabled = false;
        });
    }

    // Check final state
    const stillVisible = document.querySelectorAll('.loading-overlay:not(.hidden)');
    console.log(`Still visible loading elements: ${stillVisible.length}`, stillVisible);

    console.log('✅ Global Emergency UI Reset Complete');
    return 'UI accessible now - try refreshing if needed';
};

window.forceResetProcessing = async function() {
    console.log('🔄 Force Reset Processing');
    try {
        const response = await fetch('/api/reset-processing', { method: 'POST' });
        const data = await response.json();
        console.log('Reset response:', data);

        // Also clear UI
        window.emergencyUIReset();

        return 'Processing reset complete';
    } catch (error) {
        console.error('Reset failed:', error);
        return 'Reset failed - try refreshing the page';
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NewsFeedApp;
}
