/**
 * Script Management JavaScript Module
 * Provides functionality for fetching script lists and executing scripts via API
 */

class ScriptManager {
    constructor() {
        this.apiBase = '/api';
        this.scripts = [];
        this.currentScript = null;
        this.init();
    }

    /**
     * Initialize the script manager
     */
    init() {
        this.bindEvents();
        this.loadScripts();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Refresh scripts button
        const refreshBtn = document.getElementById('refresh-scripts');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadScripts());
        }

        // Clear results button
        const clearBtn = document.getElementById('clear-results');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearResults());
        }
    }

    /**
     * Fetch and display available scripts
     */
    async loadScripts() {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/scripts`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.scripts = data.scripts || [];
            this.displayScripts();
            this.showNotification(`Loaded ${this.scripts.length} scripts`, 'success');
            
        } catch (error) {
            console.error('Failed to load scripts:', error);
            this.showNotification(`Failed to load scripts: ${error.message}`, 'error');
            this.displayError('Failed to load scripts. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Display scripts in the UI
     */
    displayScripts() {
        const container = document.getElementById('scripts-container');
        if (!container) return;

        if (this.scripts.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <div class="text-gray-500 text-lg mb-2">No scripts available</div>
                    <div class="text-gray-400">Scripts will be loaded automatically</div>
                </div>
            `;
            return;
        }

        const scriptsHtml = this.scripts.map(script => this.createScriptCard(script)).join('');
        container.innerHTML = scriptsHtml;
    }

    /**
     * Create HTML for a script card
     */
    createScriptCard(script) {
        const gradientClass = this.getGradientClass(script.name);
        const description = script.description || 'No description available';
        const modifiedDate = new Date(script.modified_at).toLocaleDateString();
        const fileSize = this.formatFileSize(script.file_size);

        return `
            <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                <div class="h-32 ${gradientClass} flex items-center justify-center">
                    <div class="text-white text-center">
                        <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                        </svg>
                        <h3 class="text-lg font-semibold">${this.escapeHtml(script.name)}</h3>
                    </div>
                </div>
                <div class="p-6">
                    <h4 class="text-xl font-bold text-gray-800 mb-3">${this.escapeHtml(script.name)}</h4>
                    <p class="text-gray-600 mb-4">${this.escapeHtml(description)}</p>
                    
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">Python</span>
                        <span class="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">${fileSize}</span>
                        <span class="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full" title="Modified: ${script.modified_at}">${modifiedDate}</span>
                    </div>
                    
                    <div class="flex gap-3">
                        <button 
                            onclick="scriptManager.runScript('${script.name}')" 
                            class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            data-script="${script.name}"
                        >
                            Run Script
                        </button>
                        <button 
                            onclick="scriptManager.viewScript('${script.name}')" 
                            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                        >
                            View Code
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Execute a script via API
     */
    async runScript(scriptName) {
        if (!scriptName) {
            this.showNotification('No script selected', 'error');
            return;
        }

        const button = document.querySelector(`[data-script="${scriptName}"]`);
        const originalText = button ? button.textContent : 'Run Script';
        
        try {
            this.setButtonState(scriptName, 'running', 'Running...');
            this.showNotification(`Running script: ${scriptName}`, 'info');

            const response = await fetch(`${this.apiBase}/scripts/${scriptName}/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}`);
            }

            this.displayResults(result, scriptName);
            this.showNotification(`Script completed: ${scriptName}`, 'success');

        } catch (error) {
            console.error(`Failed to run script ${scriptName}:`, error);
            this.showNotification(`Script failed: ${error.message}`, 'error');
            this.displayError(`Failed to run ${scriptName}: ${error.message}`);
        } finally {
            this.setButtonState(scriptName, 'idle', originalText);
        }
    }

    /**
     * View script source code
     */
    async viewScript(scriptName) {
        if (!scriptName) {
            this.showNotification('No script selected', 'error');
            return;
        }

        try {
            this.showLoading(true);
            const response = await fetch(`/view/${scriptName}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const code = await response.text();
            this.displayResults({ stdout: code, script_name: scriptName }, scriptName, true);
            this.showNotification(`Loaded script: ${scriptName}`, 'success');
            
        } catch (error) {
            console.error(`Failed to load script ${scriptName}:`, error);
            this.showNotification(`Failed to load script: ${error.message}`, 'error');
            this.displayError(`Failed to load ${scriptName}: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Display script execution results
     */
    displayResults(result, scriptName, isCode = false) {
        const resultsDiv = document.getElementById('results');
        const outputContent = document.getElementById('output-content');
        
        if (!resultsDiv || !outputContent) return;

        resultsDiv.classList.remove('hidden');

        let content = '';
        let title = `Script Output: ${scriptName}`;

        if (isCode) {
            content = `<pre class="whitespace-pre-wrap overflow-x-auto">${this.escapeHtml(result.stdout || '')}</pre>`;
        } else {
            // Display execution results
            let output = '';
            
            if (result.status === 'success') {
                output += `<div class="text-green-400 mb-2">✓ Script completed successfully (exit code: ${result.return_code})</div>`;
            } else {
                output += `<div class="text-red-400 mb-2">✗ Script failed (exit code: ${result.return_code})</div>`;
            }

            if (result.stdout) {
                output += `<div class="mb-2"><strong>Output:</strong></div><pre class="whitespace-pre-wrap">${this.escapeHtml(result.stdout)}</pre>`;
            }

            if (result.stderr) {
                output += `<div class="mb-2 mt-4"><strong>Errors:</strong></div><pre class="text-red-400 whitespace-pre-wrap">${this.escapeHtml(result.stderr)}</pre>`;
            }

            if (result.error_message) {
                output += `<div class="mb-2 mt-4"><strong>Error Message:</strong></div><div class="text-red-400">${this.escapeHtml(result.error_message)}</div>`;
            }

            content = output || '<div class="text-gray-400">No output generated</div>';
        }

        // Update the results section
        const resultsHeader = resultsDiv.querySelector('h3');
        if (resultsHeader) {
            resultsHeader.textContent = title;
        }

        outputContent.innerHTML = content;

        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Display error message
     */
    displayError(message) {
        const resultsDiv = document.getElementById('results');
        const outputContent = document.getElementById('output-content');
        
        if (!resultsDiv || !outputContent) return;

        resultsDiv.classList.remove('hidden');
        
        const resultsHeader = resultsDiv.querySelector('h3');
        if (resultsHeader) {
            resultsHeader.textContent = 'Error';
        }

        outputContent.innerHTML = `<div class="text-red-400">${this.escapeHtml(message)}</div>`;
    }

    /**
     * Clear results display
     */
    clearResults() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.classList.add('hidden');
        }
        
        const outputContent = document.getElementById('output-content');
        if (outputContent) {
            outputContent.innerHTML = '';
        }
    }

    /**
     * Set button state during script execution
     */
    setButtonState(scriptName, state, text) {
        const button = document.querySelector(`[data-script="${scriptName}"]`);
        if (button) {
            button.textContent = text;
            button.disabled = state === 'running';
            
            if (state === 'running') {
                button.classList.add('opacity-75', 'cursor-not-allowed');
            } else {
                button.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        }
    }

    /**
     * Show/hide loading state
     */
    showLoading(show) {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            if (show) {
                loadingDiv.classList.remove('hidden');
            } else {
                loadingDiv.classList.add('hidden');
            }
        }
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.className = 'fixed top-4 right-4 z-50 transition-all duration-300';
            document.body.appendChild(notification);
        }

        const colors = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500'
        };

        notification.innerHTML = `
            <div class="${colors[type] || colors.info} text-white px-6 py-3 rounded-lg shadow-lg">
                <div class="flex items-center">
                    <span>${this.escapeHtml(message)}</span>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                        ×
                    </button>
                </div>
            </div>
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Get gradient class based on script name
     */
    getGradientClass(scriptName) {
        const gradients = [
            'bg-gradient-to-br from-blue-500 to-purple-600',
            'bg-gradient-to-br from-green-500 to-teal-600',
            'bg-gradient-to-br from-orange-500 to-red-600',
            'bg-gradient-to-br from-purple-500 to-pink-600',
            'bg-gradient-to-br from-indigo-500 to-blue-600',
            'bg-gradient-to-br from-yellow-500 to-orange-600'
        ];

        // Use script name to deterministically pick a gradient
        const index = scriptName.split('').reduce((a, b) => a + b.charCodeAt(0), 0) % gradients.length;
        return gradients[index];
    }

    /**
     * Format file size in human readable format
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the script manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.scriptManager = new ScriptManager();
});

// Legacy function support for existing HTML
function runScript(scriptName) {
    if (window.scriptManager) {
        window.scriptManager.runScript(scriptName);
    } else {
        console.error('ScriptManager not initialized');
    }
}

function viewScript(scriptName) {
    if (window.scriptManager) {
        window.scriptManager.viewScript(scriptName);
    } else {
        console.error('ScriptManager not initialized');
    }
}