/**
 * UI Helpers - Common patterns for consistent UX across all pages
 * Provides utilities for forms, AJAX, confirmations, and loading states
 */

/**
 * Form Handler - Automatic button disabling, loading states, and feedback
 * Usage:
 *   FormHandler.setup(formElement, {
 *       confirmMessage: 'Are you sure?',  // optional confirmation
 *       onSuccess: (data) => { ... },      // success callback
 *       onError: (error) => { ... }        // error callback
 *   });
 */
const FormHandler = {
    setup(form, options = {}) {
        if (!form) return;

        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show confirmation if needed
            if (options.confirmMessage) {
                return Confirm.show({
                    message: options.confirmMessage,
                    confirmText: 'Confirm',
                    cancelText: 'Cancel',
                    type: 'warning',
                    onConfirm: () => this._submit(form, submitBtn, options)
                });
            }

            await this._submit(form, submitBtn, options);
        });
    },

    async _submit(form, submitBtn, options) {
        // Disable button and show loading state
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="inline-flex items-center gap-2"><svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" style="opacity:0.25"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>' + (options.loadingText || 'Processing...') + '</span>';

        try {
            const formData = new FormData(form);
            const url = form.action || window.location.href;
            const method = form.method.toUpperCase() || 'POST';

            const response = await fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const result = await response.json();

            if (result.success) {
                Toast.success(result.message || 'Operation successful');
                if (options.onSuccess) {
                    options.onSuccess(result);
                } else if (result.redirect_url) {
                    setTimeout(() => window.location.href = result.redirect_url, 500);
                }
            } else {
                Toast.error(result.message || 'Operation failed');
                if (options.onError) options.onError(result);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            Toast.error('An error occurred. Please try again.');
            if (options.onError) options.onError(error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
};

/**
 * Button Action - Handle AJAX button clicks with confirmation and feedback
 * Usage:
 *   ButtonAction.setup(buttonElement, {
 *       url: '/api/endpoint/',
 *       method: 'POST',
 *       data: { key: 'value' },
 *       confirm: true,
 *       confirmMessage: 'Are you sure?',
 *       successMessage: 'Success!',
 *       redirectUrl: '/orders/'
 *   });
 */
const ButtonAction = {
    setup(button, options = {}) {
        if (!button) return;

        button.addEventListener('click', async (e) => {
            e.preventDefault();

            if (options.confirm) {
                Confirm.show({
                    message: options.confirmMessage || 'Are you sure?',
                    confirmText: 'Confirm',
                    cancelText: 'Cancel',
                    type: options.confirmType || 'warning',
                    onConfirm: () => this._execute(button, options)
                });
            } else {
                await this._execute(button, options);
            }
        });
    },

    async _execute(button, options) {
        const originalText = button.innerHTML;
        const originalDisabled = button.disabled;

        // Show loading state
        button.disabled = true;
        button.innerHTML = '<span class="inline-flex items-center gap-2"><svg class="animate-spin h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" style="opacity:0.25"></circle><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>' + (options.loadingText || 'Processing...') + '</span>';

        try {
            const url = options.url || button.dataset.url;
            const method = (options.method || button.dataset.method || 'POST').toUpperCase();
            const data = options.data || {};

            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            let response;
            if (method === 'GET') {
                response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
            } else {
                const formData = new FormData();
                Object.keys(data).forEach(key => {
                    formData.append(key, data[key]);
                });

                response = await fetch(url, {
                    method: method,
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
            }

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const result = await response.json();

            if (result.success) {
                Toast.success(options.successMessage || result.message || 'Operation successful');
                if (options.onSuccess) {
                    options.onSuccess(result);
                } else if (options.redirectUrl) {
                    setTimeout(() => window.location.href = options.redirectUrl, 500);
                } else if (options.reload) {
                    setTimeout(() => location.reload(), 500);
                }
            } else {
                Toast.error(options.errorMessage || result.message || 'Operation failed');
                if (options.onError) options.onError(result);
            }
        } catch (error) {
            console.error('Button action error:', error);
            Toast.error('An error occurred. Please try again.');
            if (options.onError) options.onError(error);
        } finally {
            button.disabled = originalDisabled;
            button.innerHTML = originalText;
        }
    }
};

/**
 * Table Row Action - Handle actions on table rows with confirmation
 * Usage:
 *   TableRowAction.setup(tableSelector, {
 *       actionSelector: '[data-action]',
 *       actions: {
 *           'delete': { url: '/api/delete/', confirm: true },
 *           'approve': { url: '/api/approve/', confirm: false }
 *       }
 *   });
 */
const TableRowAction = {
    setup(tableSelector, options = {}) {
        const table = document.querySelector(tableSelector);
        if (!table) return;

        table.addEventListener('click', (e) => {
            const actionBtn = e.target.closest('[data-action]');
            if (!actionBtn) return;

            const action = actionBtn.dataset.action;
            const actionConfig = options.actions?.[action];
            if (!actionConfig) return;

            const row = actionBtn.closest('tr');
            const itemId = row?.dataset.id || actionBtn.dataset.id;
            if (!itemId) {
                Toast.error('Item ID not found');
                return;
            }

            ButtonAction.setup(actionBtn, {
                url: actionConfig.url.replace(':id', itemId),
                confirm: actionConfig.confirm,
                confirmMessage: actionConfig.confirmMessage,
                confirmType: actionConfig.confirmType || 'warning',
                ...actionConfig
            });

            // Trigger the click
            actionBtn.click();
        });
    }
};

/**
 * Search Handler - Debounced search with loading state
 * Usage:
 *   SearchHandler.setup('#search-input', {
 *       url: '/api/search/',
 *       resultSelector: '#results',
 *       delay: 500,
 *       minChars: 2
 *   });
 */
const SearchHandler = {
    setup(inputSelector, options = {}) {
        const input = document.querySelector(inputSelector);
        if (!input) return;

        let timeout;
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);

            const query = e.target.value.trim();
            const minChars = options.minChars || 2;

            if (query.length < minChars) {
                const resultEl = document.querySelector(options.resultSelector);
                if (resultEl) resultEl.innerHTML = '';
                return;
            }

            timeout = setTimeout(() => this._search(query, options), options.delay || 500);
        });
    },

    async _search(query, options) {
        try {
            const url = new URL(options.url, window.location.origin);
            url.searchParams.append('q', query);

            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const results = await response.json();
            const resultEl = document.querySelector(options.resultSelector);

            if (options.renderResults) {
                resultEl.innerHTML = options.renderResults(results);
            }

            if (options.onResults) {
                options.onResults(results);
            }
        } catch (error) {
            console.error('Search error:', error);
            Toast.error('Search failed. Please try again.');
        }
    }
};

/**
 * Modal Handler - Consistent modal behavior
 * Usage:
 *   ModalHandler.open(modalSelector);
 *   ModalHandler.close(modalSelector);
 */
const ModalHandler = {
    open(selector) {
        const modal = document.querySelector(selector);
        if (!modal) return;

        modal.classList.remove('hidden');
        modal.querySelector('input, button, select, textarea')?.focus();
    },

    close(selector) {
        const modal = document.querySelector(selector);
        if (!modal) return;

        modal.classList.add('hidden');
        const form = modal.querySelector('form');
        if (form) form.reset();
    },

    setup(triggerSelector, modalSelector) {
        const trigger = document.querySelector(triggerSelector);
        if (!trigger) return;

        trigger.addEventListener('click', () => this.open(modalSelector));

        const modal = document.querySelector(modalSelector);
        if (!modal) return;

        // Close on Escape
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.close(modalSelector);
        });

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.close(modalSelector);
        });

        // Close on cancel button
        const cancelBtn = modal.querySelector('[data-modal-close], .modal-close');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.close(modalSelector));
        }
    }
};

/**
 * Pagination Handler - AJAX pagination
 * Usage:
 *   PaginationHandler.setup({
 *       containerSelector: '#orders-container',
 *       pageParam: 'page',
 *       url: '/orders/',
 *       onLoad: (data) => { ... }
 *   });
 */
const PaginationHandler = {
    setup(options = {}) {
        const container = document.querySelector(options.containerSelector);
        if (!container) return;

        container.addEventListener('click', (e) => {
            const pageBtn = e.target.closest('[data-page]');
            if (!pageBtn || pageBtn.disabled) return;

            e.preventDefault();
            const page = pageBtn.dataset.page;
            this._loadPage(page, options);
        });
    },

    async _loadPage(page, options) {
        try {
            const url = new URL(options.url || window.location.href);
            url.searchParams.set(options.pageParam || 'page', page);

            Loading.show();

            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            if (options.onLoad) {
                options.onLoad(data);
            }

            if (options.containerSelector) {
                const container = document.querySelector(options.containerSelector);
                if (container && data.html) {
                    container.innerHTML = data.html;
                }
            }
        } catch (error) {
            console.error('Pagination error:', error);
            Toast.error('Failed to load page');
        } finally {
            Loading.hide();
        }
    }
};

/**
 * Inline Edit Handler - Edit content in place
 * Usage:
 *   InlineEditHandler.setup('[data-edit]', {
 *       url: '/api/update/',
 *       method: 'PATCH'
 *   });
 */
const InlineEditHandler = {
    setup(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.tagName === 'INPUT') return; // Already editing

                const field = el.dataset.field;
                const value = el.textContent.trim();
                const id = el.dataset.id || el.closest('[data-id]')?.dataset.id;

                this._makeEditable(el, { field, value, id, ...options });
            });
        });
    },

    _makeEditable(element, options) {
        const input = document.createElement('input');
        input.type = 'text';
        input.value = options.value;
        input.className = 'w-full px-2 py-1 border border-fjc-blue-500 rounded';

        const originalHTML = element.innerHTML;

        element.innerHTML = '';
        element.appendChild(input);
        input.focus();
        input.select();

        const save = async () => {
            const newValue = input.value.trim();
            if (newValue === options.value) {
                element.innerHTML = originalHTML;
                return;
            }

            try {
                const formData = new FormData();
                formData.append(options.field, newValue);
                formData.append('id', options.id);

                const response = await fetch(options.url, {
                    method: options.method || 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const result = await response.json();

                if (result.success) {
                    element.textContent = newValue;
                    Toast.success('Updated successfully');
                    if (options.onSuccess) options.onSuccess(result);
                } else {
                    element.innerHTML = originalHTML;
                    Toast.error(result.message || 'Update failed');
                }
            } catch (error) {
                element.innerHTML = originalHTML;
                Toast.error('Error updating value');
            }
        };

        const cancel = () => {
            element.innerHTML = originalHTML;
        };

        input.addEventListener('blur', save);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') save();
            if (e.key === 'Escape') cancel();
        });
    }
};

// Auto-initialize common elements on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find and setup forms with [data-async] attribute
    document.querySelectorAll('form[data-async]').forEach(form => {
        FormHandler.setup(form, {
            confirmMessage: form.dataset.confirmMessage
        });
    });

    // Find and setup buttons with [data-action-url] attribute
    document.querySelectorAll('button[data-action-url]').forEach(btn => {
        ButtonAction.setup(btn, {
            url: btn.dataset.actionUrl,
            method: btn.dataset.actionMethod,
            confirm: btn.dataset.confirm === 'true',
            confirmMessage: btn.dataset.confirmMessage,
            successMessage: btn.dataset.successMessage,
            redirectUrl: btn.dataset.redirectUrl
        });
    });

    // Find and setup modals
    document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
        const modalSelector = trigger.dataset.modalTrigger;
        ModalHandler.setup(`[data-modal-trigger="${modalSelector}"]`, modalSelector);
    });
});

/**
 * URL Helper - Utilities for URL parameter management
 * Usage:
 *   UrlHelper.getFiltersFromUrl()
 *   UrlHelper.updateUrl(params)
 *   UrlHelper.restoreFilters(filterConfig)
 */
const UrlHelper = {
    // Get current filter state from URL as object
    getFiltersFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return Object.fromEntries(params.entries());
    },

    // Update URL without page reload
    updateUrl(params) {
        const searchParams = params instanceof URLSearchParams ? params : new URLSearchParams(params);
        // Remove empty params
        for (const [key, value] of [...searchParams.entries()]) {
            if (!value) searchParams.delete(key);
        }
        const newUrl = searchParams.toString()
            ? `${window.location.pathname}?${searchParams.toString()}`
            : window.location.pathname;
        history.pushState({ filters: searchParams.toString() }, '', newUrl);
    },

    // Restore filter inputs from URL state
    restoreFilters(filterConfig) {
        const params = this.getFiltersFromUrl();
        filterConfig.forEach(config => {
            const element = document.querySelector(config.selector);
            if (element && params[config.param] !== undefined) {
                if (element.type === 'checkbox') {
                    element.checked = params[config.param] === 'true';
                } else {
                    element.value = params[config.param];
                }
            }
        });
    },

    // Build URLSearchParams from filter config
    buildParams(filterConfig) {
        const params = new URLSearchParams();
        filterConfig.forEach(config => {
            const element = document.querySelector(config.selector);
            if (element) {
                const value = element.type === 'checkbox' ? element.checked : element.value;
                if (value) {
                    params.set(config.param, value);
                }
            }
        });
        return params;
    }
};

/**
 * AsyncFilterHandler - Reusable async filtering with URL sync, debounce, and loading states
 * Usage:
 *   const filter = new AsyncFilterHandler({
 *       url: '/api/items/',
 *       filterInputs: [
 *           { selector: '#search-input', param: 'search', debounce: true },
 *           { selector: '#status-filter', param: 'status' },
 *           { selector: '#category-filter', param: 'category' }
 *       ],
 *       buttonFilters: [
 *           { selector: '.time-filter-btn', param: 'days', activeClass: 'bg-blue-600 text-white' }
 *       ],
 *       resultsContainer: '#results-container',
 *       loadingContainer: '#loading-indicator',
 *       renderResults: (data) => { return html; },
 *       onSuccess: (data) => { },
 *       updateUrl: true,
 *       debounceDelay: 500
 *   });
 *   filter.init();
 */
class AsyncFilterHandler {
    constructor(options) {
        this.options = {
            url: window.location.pathname,
            filterInputs: [],
            buttonFilters: [],
            resultsContainer: null,
            loadingContainer: null,
            summaryContainers: {},
            paginationContainer: null,
            renderResults: null,
            renderPagination: null,
            onSuccess: null,
            onError: null,
            updateUrl: true,
            debounceDelay: 500,
            minSearchLength: 0,
            ...options
        };

        this.debounceTimers = {};
        this.currentPage = 1;
        this.isLoading = false;
    }

    init() {
        this._setupInputFilters();
        this._setupButtonFilters();
        this._setupPagination();
        this._setupPopState();
        this._restoreFromUrl();
    }

    _setupInputFilters() {
        this.options.filterInputs.forEach(config => {
            const element = document.querySelector(config.selector);
            if (!element) return;

            const eventType = element.tagName === 'SELECT' ? 'change' : 'input';
            const shouldDebounce = config.debounce !== false && element.tagName !== 'SELECT';

            element.addEventListener(eventType, (e) => {
                if (shouldDebounce) {
                    this._debounce(config.selector, () => this._triggerFilter(), this.options.debounceDelay);
                } else {
                    this._triggerFilter();
                }
            });
        });
    }

    _setupButtonFilters() {
        this.options.buttonFilters.forEach(config => {
            const buttons = document.querySelectorAll(config.selector);
            buttons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();

                    // Update active state
                    buttons.forEach(b => {
                        b.classList.remove(...(config.activeClass || 'bg-blue-600 text-white').split(' '));
                        b.classList.add(...(config.inactiveClass || 'bg-gray-100 text-gray-700').split(' '));
                    });
                    btn.classList.remove(...(config.inactiveClass || 'bg-gray-100 text-gray-700').split(' '));
                    btn.classList.add(...(config.activeClass || 'bg-blue-600 text-white').split(' '));

                    // Store the value
                    btn.dataset.selected = 'true';
                    this._triggerFilter();
                });
            });
        });
    }

    _setupPagination() {
        if (!this.options.paginationContainer) return;

        const container = document.querySelector(this.options.paginationContainer);
        if (!container) return;

        container.addEventListener('click', (e) => {
            const pageBtn = e.target.closest('[data-page]');
            if (!pageBtn || pageBtn.disabled) return;

            e.preventDefault();
            this.currentPage = parseInt(pageBtn.dataset.page);
            this._triggerFilter();
        });
    }

    _setupPopState() {
        window.addEventListener('popstate', (event) => {
            this._restoreFromUrl();
            this._triggerFilter(false); // Don't update URL on popstate
        });
    }

    _restoreFromUrl() {
        const params = new URLSearchParams(window.location.search);

        // Restore input filters
        this.options.filterInputs.forEach(config => {
            const element = document.querySelector(config.selector);
            if (element && params.has(config.param)) {
                element.value = params.get(config.param);
            }
        });

        // Restore button filters
        this.options.buttonFilters.forEach(config => {
            const buttons = document.querySelectorAll(config.selector);
            const value = params.get(config.param);

            buttons.forEach(btn => {
                const isActive = btn.dataset.value === value || (value === null && btn.dataset.default === 'true');
                btn.classList.remove(...(config.activeClass || 'bg-blue-600 text-white').split(' '));
                btn.classList.remove(...(config.inactiveClass || 'bg-gray-100 text-gray-700').split(' '));

                if (isActive) {
                    btn.classList.add(...(config.activeClass || 'bg-blue-600 text-white').split(' '));
                    btn.dataset.selected = 'true';
                } else {
                    btn.classList.add(...(config.inactiveClass || 'bg-gray-100 text-gray-700').split(' '));
                    delete btn.dataset.selected;
                }
            });
        });

        // Restore page
        this.currentPage = parseInt(params.get('page')) || 1;
    }

    _debounce(key, fn, delay) {
        clearTimeout(this.debounceTimers[key]);
        this.debounceTimers[key] = setTimeout(fn, delay);
    }

    _buildParams() {
        const params = new URLSearchParams();

        // Input filters
        this.options.filterInputs.forEach(config => {
            const element = document.querySelector(config.selector);
            if (element && element.value) {
                params.set(config.param, element.value);
            }
        });

        // Button filters
        this.options.buttonFilters.forEach(config => {
            const selectedBtn = document.querySelector(`${config.selector}[data-selected="true"]`);
            if (selectedBtn && selectedBtn.dataset.value) {
                params.set(config.param, selectedBtn.dataset.value);
            }
        });

        // Page
        if (this.currentPage > 1) {
            params.set('page', this.currentPage);
        }

        return params;
    }

    async _triggerFilter(updateUrl = true) {
        if (this.isLoading) return;

        const params = this._buildParams();

        // Update URL if enabled
        if (updateUrl && this.options.updateUrl) {
            UrlHelper.updateUrl(params);
        }

        await this._fetchResults(params);
    }

    async _fetchResults(params) {
        this.isLoading = true;
        this._showLoading();

        try {
            const url = new URL(this.options.url, window.location.origin);
            params.forEach((value, key) => url.searchParams.set(key, value));

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            if (data.success !== false) {
                this._renderResults(data);
                if (this.options.onSuccess) {
                    this.options.onSuccess(data);
                }
            } else {
                throw new Error(data.message || 'Filter failed');
            }
        } catch (error) {
            console.error('Filter error:', error);
            if (typeof Toast !== 'undefined') {
                Toast.error('Failed to load results. Please try again.');
            }
            if (this.options.onError) {
                this.options.onError(error);
            }
        } finally {
            this.isLoading = false;
            this._hideLoading();
        }
    }

    _showLoading() {
        if (this.options.loadingContainer) {
            const loader = document.querySelector(this.options.loadingContainer);
            if (loader) loader.classList.remove('hidden');
        }
        if (this.options.resultsContainer) {
            const container = document.querySelector(this.options.resultsContainer);
            if (container) container.classList.add('opacity-50', 'pointer-events-none');
        }
    }

    _hideLoading() {
        if (this.options.loadingContainer) {
            const loader = document.querySelector(this.options.loadingContainer);
            if (loader) loader.classList.add('hidden');
        }
        if (this.options.resultsContainer) {
            const container = document.querySelector(this.options.resultsContainer);
            if (container) container.classList.remove('opacity-50', 'pointer-events-none');
        }
    }

    _renderResults(data) {
        // Render main results
        if (this.options.resultsContainer && this.options.renderResults) {
            const container = document.querySelector(this.options.resultsContainer);
            if (container) {
                container.innerHTML = this.options.renderResults(data);
            }
        }

        // Render summary containers
        if (this.options.summaryContainers) {
            Object.entries(this.options.summaryContainers).forEach(([selector, render]) => {
                const container = document.querySelector(selector);
                if (container && typeof render === 'function') {
                    container.innerHTML = render(data);
                }
            });
        }

        // Render pagination
        if (this.options.paginationContainer && this.options.renderPagination) {
            const container = document.querySelector(this.options.paginationContainer);
            if (container) {
                container.innerHTML = this.options.renderPagination(data);
            }
        }
    }

    // Public method to trigger filter manually
    refresh() {
        this._triggerFilter();
    }

    // Public method to reset all filters
    reset() {
        this.options.filterInputs.forEach(config => {
            const element = document.querySelector(config.selector);
            if (element) element.value = '';
        });

        this.options.buttonFilters.forEach(config => {
            const buttons = document.querySelectorAll(config.selector);
            buttons.forEach(btn => {
                delete btn.dataset.selected;
                btn.classList.remove(...(config.activeClass || 'bg-blue-600 text-white').split(' '));
                btn.classList.add(...(config.inactiveClass || 'bg-gray-100 text-gray-700').split(' '));
            });
        });

        this.currentPage = 1;
        this._triggerFilter();
    }
}

/**
 * Export for use in templates
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        FormHandler,
        ButtonAction,
        TableRowAction,
        SearchHandler,
        ModalHandler,
        PaginationHandler,
        InlineEditHandler,
        UrlHelper,
        AsyncFilterHandler
    };
}
