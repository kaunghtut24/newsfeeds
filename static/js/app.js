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
            </article>
        `;
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

            if (data.success) {
                this.displayLLMProviders(data);
                this.updateCostTracking(data.budget);
                this.populateProviderSelectors(data.available_providers, data.available_models);
            } else {
                this.showToast('Error loading LLM providers', 'error');
            }
        } catch (error) {
            console.error('Error loading LLM providers:', error);
            this.showToast('Error loading LLM providers', 'error');
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

        if (dailyCost) dailyCost.textContent = `$${budget.current_daily.toFixed(2)}`;
        if (monthlyCost) monthlyCost.textContent = `$${budget.current_monthly.toFixed(2)}`;
        if (dailyLimit) dailyLimit.textContent = `$${budget.daily_limit.toFixed(2)}`;
        if (monthlyLimit) monthlyLimit.textContent = `$${budget.monthly_limit.toFixed(2)}`;

        if (budgetProgress) {
            const dailyPercent = (budget.current_daily / budget.daily_limit) * 100;
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
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                const results = data.health_results;
                const healthyCount = Object.values(results).filter(Boolean).length;
                const totalCount = Object.keys(results).length;

                this.showToast(
                    `Health check complete: ${healthyCount}/${totalCount} providers healthy`,
                    healthyCount === totalCount ? 'success' : 'warning'
                );

                this.loadLLMProviders(); // Refresh the display
            } else {
                this.showToast(`Health check failed: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Health check error: ${error.message}`, 'error');
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
        const article = result.article;
        const score = (result.relevance_score * 100).toFixed(0);
        const timeAgo = this.getTimeAgo(article.timestamp);

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
                    ${result.highlighted_text.summary || result.highlighted_text.title || article.summary || 'No summary available'}
                </div>

                ${result.matched_fields.length > 0 ? `
                    <div class="search-result-matched-fields">
                        <strong>Matched in:</strong>
                        ${result.matched_fields.map(field =>
                            `<span class="matched-field-tag">${field}</span>`
                        ).join('')}
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
        if (!ollamaModelSelect) return;

        ollamaModelSelect.innerHTML = '<option value="">Loading models...</option>';

        try {
            const response = await fetch('/api/ollama-status');
            const data = await response.json();

            ollamaModelSelect.innerHTML = '';

            if (data.available && data.models && data.models.length > 0) {
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

                ollamaModelSelect.disabled = false;
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Ollama not available';
                ollamaModelSelect.appendChild(option);
                ollamaModelSelect.disabled = true;
            }
        } catch (error) {
            console.error('Error fetching Ollama models:', error);
            ollamaModelSelect.innerHTML = '<option value="">Error loading models</option>';
            ollamaModelSelect.disabled = true;
        }
    }

    async saveOllamaModel() {
        const selectedModel = document.getElementById('ollamaModelSelect')?.value;
        if (!selectedModel) {
            this.showToast('Please select an Ollama model', 'warning');
            return;
        }

        try {
            this.currentConfig.ollama_model = selectedModel;
            await this.saveConfig();
            this.showToast(`Model updated to: ${selectedModel}`, 'success');
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
