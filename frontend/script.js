// Main JavaScript file for the Local AI Agent frontend
class LocalAIAgent {
    constructor() {
        this.conversationId = null;
        this.isStreaming = false;
        this.currentSettings = { ...CONFIG.DEFAULT_SETTINGS };
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSettings();
        this.checkSystemHealth();
        this.startAutoRefresh();
        
        // Initialize UI
        this.updateUI();
        this.showToast('Local AI Agent 초기화 완료', 'success');
    }
    
    bindEvents() {
        // Chat form submission
        document.getElementById('chat-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSendMessage();
        });
        
        // Message input handling
        const messageInput = document.getElementById('message-input');
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        messageInput.addEventListener('input', () => {
            this.updateTokenCount();
        });
        
        // Settings controls
        document.getElementById('temperature-slider').addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.currentSettings.temperature = value;
            document.getElementById('temperature-value').textContent = value;
            this.saveSettings();
        });
        
        document.getElementById('max-tokens-input').addEventListener('change', (e) => {
            this.currentSettings.maxTokens = parseInt(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('model-select').addEventListener('change', (e) => {
            this.currentSettings.model = e.target.value;
            this.saveSettings();
        });
        
        document.getElementById('use-cache').addEventListener('change', (e) => {
            this.currentSettings.useCache = e.target.checked;
            this.saveSettings();
        });
        
        document.getElementById('stream-mode').addEventListener('change', (e) => {
            this.currentSettings.streamMode = e.target.checked;
            this.saveSettings();
        });
        
        document.getElementById('context-length').addEventListener('change', (e) => {
            this.currentSettings.contextLength = parseInt(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('system-prompt').addEventListener('change', (e) => {
            this.currentSettings.systemPrompt = e.target.value;
            this.saveSettings();
        });
        
        // Control buttons
        document.getElementById('clear-chat-btn').addEventListener('click', () => {
            this.clearChat();
        });
        
        document.getElementById('clear-cache-btn').addEventListener('click', () => {
            this.clearCache();
        });
        
        document.getElementById('refresh-stats-btn').addEventListener('click', () => {
            this.refreshStatistics();
        });
        
        document.getElementById('toggle-settings').addEventListener('click', () => {
            this.toggleSettings();
        });
    }
    
    async handleSendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Disable input while processing
        this.setUILoading(true);
        messageInput.value = '';
        
        // Add user message to chat
        this.addMessageToChat('user', message);
        
        try {
            if (this.currentSettings.streamMode) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendMessage(message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('메시지 전송 중 오류가 발생했습니다', 'error');
            this.addMessageToChat('assistant', '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.');
        } finally {
            this.setUILoading(false);
            this.updateTokenCount();
        }
    }
    
    async sendMessage(message) {
        const messages = this.buildMessagesArray(message);
        
        const requestBody = {
            messages: messages,
            model: this.currentSettings.model,
            temperature: this.currentSettings.temperature,
            max_tokens: this.currentSettings.maxTokens,
            use_cache: this.currentSettings.useCache,
            stream: false
        };
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT_COMPLETION}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.message || 'API 호출 실패');
        }
        
        const data = await response.json();
        const assistantMessage = data.choices[0]?.message?.content || '응답을 받지 못했습니다.';
        
        this.addMessageToChat('assistant', assistantMessage);
        
        // Update statistics
        if (data.usage) {
            this.updateUsageStats(data.usage);
        }
    }
    
    async sendStreamingMessage(message) {
        const messages = this.buildMessagesArray(message);
        
        const requestBody = {
            messages: messages,
            model: this.currentSettings.model,
            temperature: this.currentSettings.temperature,
            max_tokens: this.currentSettings.maxTokens,
            use_cache: false, // Streaming doesn't support cache
            stream: true
        };
        
        // Add typing indicator
        const typingId = this.addTypingIndicator();
        
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT_STREAM}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            this.removeTypingIndicator(typingId);
            const errorData = await response.json();
            throw new Error(errorData.detail?.message || 'Streaming API 호출 실패');
        }
        
        // Remove typing indicator and add message container
        this.removeTypingIndicator(typingId);
        const messageId = this.addMessageToChat('assistant', '');
        
        // Process streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedMessage = '';
        
        try {
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            break;
                        }
                        if (data.startsWith('ERROR:')) {
                            throw new Error(data.slice(7));
                        }
                        
                        accumulatedMessage += data;
                        this.updateMessageContent(messageId, accumulatedMessage);
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
    
    buildMessagesArray(currentMessage) {
        const messages = [];
        
        // Add system prompt if set
        if (this.currentSettings.systemPrompt) {
            messages.push({
                role: 'system',
                content: this.currentSettings.systemPrompt
            });
        }
        
        // Add recent conversation history
        const recentHistory = this.messageHistory.slice(-this.currentSettings.contextLength * 2);
        messages.push(...recentHistory);
        
        // Add current message
        messages.push({
            role: 'user',
            content: currentMessage
        });
        
        return messages;
    }
    
    addMessageToChat(role, content) {
        const chatMessages = document.getElementById('chat-messages');
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        messageElement.id = messageId;
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageElement.innerHTML = `
            <div class="message-content">${this.formatMessage(content)}</div>
            <div class="message-time">${timestamp}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        if (content) {
            this.messageHistory.push({ role, content });
            
            // Trim history if too long
            if (this.messageHistory.length > CONFIG.UI.maxChatMessages) {
                this.messageHistory = this.messageHistory.slice(-CONFIG.UI.maxChatMessages);
            }
        }
        
        return messageId;
    }
    
    updateMessageContent(messageId, content) {
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            const contentElement = messageElement.querySelector('.message-content');
            contentElement.innerHTML = this.formatMessage(content);
            
            // Scroll to bottom
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    formatMessage(content) {
        // Basic message formatting
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    addTypingIndicator() {
        const typingId = `typing-${Date.now()}`;
        const chatMessages = document.getElementById('chat-messages');
        
        const typingElement = document.createElement('div');
        typingElement.className = 'message assistant typing-indicator';
        typingElement.id = typingId;
        
        typingElement.innerHTML = `
            <div class="message-content">
                <span>AI가 입력 중입니다</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return typingId;
    }
    
    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    clearChat() {
        if (confirm('대화 내역을 모두 삭제하시겠습니까?')) {
            document.getElementById('chat-messages').innerHTML = `
                <div class="message assistant">
                    <div class="message-content">
                        안녕하세요! Local AI Agent입니다. 무엇을 도와드릴까요?
                    </div>
                    <div class="message-time">시스템</div>
                </div>
            `;
            this.messageHistory = [];
            this.conversationId = null;
            this.showToast('대화 내역이 초기화되었습니다', 'success');
        }
    }
    
    async clearCache() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CACHE_CLEAR}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showToast('캐시가 성공적으로 삭제되었습니다', 'success');
                this.refreshStatistics();
            } else {
                throw new Error('캐시 삭제 실패');
            }
        } catch (error) {
            console.error('Error clearing cache:', error);
            this.showToast('캐시 삭제 중 오류가 발생했습니다', 'error');
        }
    }
    
    async refreshStatistics() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHAT_STATISTICS}`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStatisticsDisplay(stats);
            }
        } catch (error) {
            console.error('Error refreshing statistics:', error);
        }
    }
    
    updateStatisticsDisplay(stats) {
        const chatStats = stats.chat_service || {};
        const apiStats = stats.api_stats?.api_usage || {};
        const cacheStats = stats.api_stats?.cache_stats || {};
        
        document.getElementById('total-requests').textContent = 
            chatStats.total_requests || apiStats.requests_count || '-';
        
        document.getElementById('total-tokens').textContent = 
            chatStats.total_tokens || apiStats.tokens_used || '-';
        
        const hitRate = cacheStats.hit_rate ? 
            `${(cacheStats.hit_rate * 100).toFixed(1)}%` : '-';
        document.getElementById('cache-hit-rate').textContent = hitRate;
        
        const avgTime = chatStats.average_response_time ? 
            `${chatStats.average_response_time.toFixed(2)}s` : '-';
        document.getElementById('avg-response-time').textContent = avgTime;
    }
    
    async checkSystemHealth() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.SYSTEM_HEALTH}`);
            const health = await response.json();
            
            this.updateSystemStatus(response.ok && health.status === 'healthy');
            
            if (response.ok) {
                console.log('System health check passed:', health);
            } else {
                console.warn('System health check failed:', health);
            }
        } catch (error) {
            console.error('Health check error:', error);
            this.updateSystemStatus(false);
        }
    }
    
    updateSystemStatus(isHealthy) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (isHealthy) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = '연결됨';
        } else {
            statusDot.className = 'status-dot error';
            statusText.textContent = '연결 오류';
        }
    }
    
    updateTokenCount() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value;
        
        // Simple token estimation (rough approximation)
        const tokenCount = Math.ceil(message.length / 4);
        document.getElementById('token-count').textContent = `토큰: ~${tokenCount}`;
    }
    
    setUILoading(loading) {
        const sendBtn = document.getElementById('send-btn');
        const sendText = document.getElementById('send-text');
        const loadingSpinner = document.getElementById('loading-spinner');
        const messageInput = document.getElementById('message-input');
        
        if (loading) {
            sendBtn.disabled = true;
            sendText.style.display = 'none';
            loadingSpinner.style.display = 'inline';
            messageInput.disabled = true;
        } else {
            sendBtn.disabled = false;
            sendText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
            messageInput.disabled = false;
            messageInput.focus();
        }
    }
    
    toggleSettings() {
        const settingsContent = document.getElementById('settings-content');
        const toggleBtn = document.getElementById('toggle-settings');
        
        if (settingsContent.style.display === 'none') {
            settingsContent.style.display = 'block';
            toggleBtn.textContent = '접기';
        } else {
            settingsContent.style.display = 'none';
            toggleBtn.textContent = '펼치기';
        }
    }
    
    saveSettings() {
        localStorage.setItem('localAIAgentSettings', JSON.stringify(this.currentSettings));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('localAIAgentSettings');
        if (saved) {
            this.currentSettings = { ...CONFIG.DEFAULT_SETTINGS, ...JSON.parse(saved) };
        }
        this.updateUI();
    }
    
    updateUI() {
        // Update form controls with current settings
        document.getElementById('model-select').value = this.currentSettings.model;
        document.getElementById('temperature-slider').value = this.currentSettings.temperature;
        document.getElementById('temperature-value').textContent = this.currentSettings.temperature;
        document.getElementById('max-tokens-input').value = this.currentSettings.maxTokens;
        document.getElementById('use-cache').checked = this.currentSettings.useCache;
        document.getElementById('stream-mode').checked = this.currentSettings.streamMode;
        document.getElementById('context-length').value = this.currentSettings.contextLength;
        document.getElementById('system-prompt').value = this.currentSettings.systemPrompt;
    }
    
    updateUsageStats(usage) {
        // Update usage statistics from API response
        // This could be expanded to track more detailed statistics
        console.log('Usage stats:', usage);
    }
    
    startAutoRefresh() {
        // Auto-refresh system statistics
        setInterval(() => {
            this.checkSystemHealth();
            this.refreshStatistics();
        }, CONFIG.UI.autoRefreshInterval);
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toastId = `toast-${Date.now()}`;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Auto-remove toast
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.remove();
            }
        }, CONFIG.UI.toastDuration);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.localAIAgent = new LocalAIAgent();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.localAIAgent) {
        window.localAIAgent.showToast('예상치 못한 오류가 발생했습니다', 'error');
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.localAIAgent) {
        window.localAIAgent.showToast('네트워크 오류가 발생했습니다', 'error');
    }
});
