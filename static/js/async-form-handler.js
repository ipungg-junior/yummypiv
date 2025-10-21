/**
 * AsyncFormHandler - A reusable JavaScript class for handling asynchronous form submissions
 * using fetch API with JSON responses, CSRF protection, and error handling.
 *
 * Features:
 * - Prevents default form submission
 * - Collects form data automatically
 * - Handles CSRF tokens
 * - Supports success/failure callbacks
 * - Displays validation errors
 * - Configurable options
 */
class AsyncFormHandler {
    /**
     * Constructor for AsyncFormHandler
     * @param {Object} options - Configuration options
     * @param {string|HTMLElement} options.form - Form element or selector
     * @param {string} options.endpoint - API endpoint URL
     * @param {string} [options.method='POST'] - HTTP method
     * @param {Function} [options.onSuccess] - Success callback
     * @param {Function} [options.onError] - Error callback
     * @param {string} [options.submitButton] - Submit button selector
     * @param {string} [options.loadingClass='loading'] - CSS class for loading state
     * @param {boolean} [options.useFormData=true] - Whether to use FormData or JSON
     */
    constructor(options) {
        this.form = typeof options.form === 'string' ? document.querySelector(options.form) : options.form;
        this.endpoint = options.endpoint;
        this.method = options.method || 'POST';
        this.onSuccess = options.onSuccess || this.defaultSuccessHandler;
        this.onError = options.onError || this.defaultErrorHandler;
        this.submitButton = options.submitButton ? this.form.querySelector(options.submitButton) : this.form.querySelector('button[type="submit"]');
        this.loadingClass = options.loadingClass || 'loading';
        this.useFormData = options.useFormData !== false;

        if (!this.form) {
            throw new Error('Form element not found');
        }

        this.csrfToken = this.getCsrfToken();
        this.init();
    }

    /**
     * Initialize event listeners
     */
    init() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submit();
        });
    }

    /**
     * Get CSRF token from meta tag or form input
     * @returns {string|null} CSRF token
     */
    getCsrfToken() {
        // Try to get from meta tag first
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        // Try to get from form input
        const csrfInput = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }

        return null;
    }

    /**
     * Collect form data
     * @returns {FormData|Object} Form data
     */
    collectFormData() {
        if (this.useFormData) {
            return new FormData(this.form);
        } else {
            const data = {};
            const inputs = this.form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.name && !input.disabled) {
                    if (input.type === 'checkbox') {
                        data[input.name] = input.checked;
                    } else if (input.type === 'file') {
                        // Skip file inputs for JSON, handle separately if needed
                        return;
                    } else {
                        data[input.name] = input.value;
                    }
                }
            });
            return data;
        }
    }

    /**
     * Set loading state
     * @param {boolean} loading - Whether to show loading state
     */
    setLoading(loading) {
        if (this.submitButton) {
            if (loading) {
                this.submitButton.disabled = true;
                this.submitButton.classList.add(this.loadingClass);
                this.submitButton.dataset.originalText = this.submitButton.textContent;
                this.submitButton.textContent = 'Loading...';
            } else {
                this.submitButton.disabled = false;
                this.submitButton.classList.remove(this.loadingClass);
                if (this.submitButton.dataset.originalText) {
                    this.submitButton.textContent = this.submitButton.dataset.originalText;
                }
            }
        }
    }

    /**
     * Submit the form asynchronously
     */
    async submit() {
        this.clearErrors();
        this.setLoading(true);

        try {
            const formData = this.collectFormData();
            const headers = {};

            if (this.csrfToken) {
                headers['X-CSRFToken'] = this.csrfToken;
            }

            let body;
            if (this.useFormData) {
                body = formData;
            } else {
                headers['Content-Type'] = 'application/json';
                body = JSON.stringify(formData);
            }

            const response = await fetch(this.endpoint, {
                method: this.method,
                headers: headers,
                body: body
            });

            const result = await response.json();

            if (response.ok && result.success !== false) {
                this.onSuccess(result, response);
            } else {
                this.onError(result, response);
            }

        } catch (error) {
            console.error('Form submission error:', error);
            this.onError({
                success: false,
                message: 'Network error occurred. Please try again.',
                errors: {}
            });
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Clear previous error messages
     */
    clearErrors() {
        // Clear field-specific errors
        const errorElements = this.form.querySelectorAll('.field-error');
        errorElements.forEach(el => el.remove());

        // Clear general error messages
        const generalErrors = this.form.querySelectorAll('.general-error');
        generalErrors.forEach(el => el.remove());
    }

    /**
     * Display field-specific errors
     * @param {Object} errors - Error object with field names as keys
     */
    displayFieldErrors(errors) {
        Object.keys(errors).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error text-danger';
                errorDiv.textContent = Array.isArray(errors[fieldName])
                    ? errors[fieldName].join(', ')
                    : errors[fieldName];

                field.parentNode.insertBefore(errorDiv, field.nextSibling);
                field.classList.add('is-invalid');
            }
        });
    }

    /**
     * Default success handler
     * @param {Object} result - Response data
     * @param {Response} response - Fetch response
     */
    defaultSuccessHandler(result, response) {
        // Show success message
        if (result.message) {
            this.showMessage(result.message, 'success');
        }

        // Reset form if configured
        if (this.form.dataset.resetOnSuccess !== 'false') {
            this.form.reset();
        }

        // Redirect if specified
        if (result.redirect) {
            window.location.href = result.redirect;
        }
    }

    /**
     * Default error handler
     * @param {Object} result - Response data
     * @param {Response} response - Fetch response
     */
    defaultErrorHandler(result, response) {
        // Display field errors
        if (result.errors) {
            this.displayFieldErrors(result.errors);
        }

        // Show general error message
        const message = result.message || 'An error occurred. Please try again.';
        this.showMessage(message, 'error');
    }

    /**
     * Show message to user
     * @param {string} message - Message text
     * @param {string} type - Message type (success/error)
     */
    showMessage(message, type) {
        // Try to find existing message container
        let messageContainer = this.form.querySelector('.message-container');

        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'message-container';
            this.form.insertBefore(messageContainer, this.form.firstChild);
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        messageDiv.textContent = message;

        messageContainer.appendChild(messageDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    /**
     * Static method to initialize multiple forms
     * @param {Array} configs - Array of configuration objects
     */
    static initMultiple(configs) {
        return configs.map(config => new AsyncFormHandler(config));
    }
}

// Export for module usage (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AsyncFormHandler;
}