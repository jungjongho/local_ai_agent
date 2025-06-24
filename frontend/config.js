// Configuration for the frontend application
const CONFIG = {
    // API Base URL - 개발환경에 맞게 수정하세요
    API_BASE_URL: 'http://localhost:8025',
    
    // API Endpoints
    ENDPOINTS: {
        CHAT_COMPLETION: '/api/chat/completion',
        CHAT_STREAM: '/api/chat/stream',
        CHAT_CONVERSATION: '/api/chat/conversation',
        CHAT_VALIDATE: '/api/chat/validate',
        CHAT_STATISTICS: '/api/chat/statistics',
        CHAT_HEALTH: '/api/chat/health',
        SYSTEM_HEALTH: '/api/system/health',
        SYSTEM_STATUS: '/api/system/status',
        SYSTEM_CONFIG: '/api/system/config',
        CACHE_CLEAR: '/api/system/cache/clear',
        CACHE_STATS: '/api/system/cache/stats'
    },
    
    // Default Settings
    DEFAULT_SETTINGS: {
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        maxTokens: 1000,
        useCache: true,
        streamMode: false,
        contextLength: 10,
        systemPrompt: ''
    },
    
    // UI Settings
    UI: {
        maxChatMessages: 100,
        autoRefreshInterval: 30000, // 30 seconds
        typingIndicatorDelay: 500,
        toastDuration: 3000,
        maxMessageLength: 4000
    },
    
    // Feature Flags
    FEATURES: {
        streamingChat: true,
        conversationMode: true,
        cacheControl: true,
        systemPrompts: true,
        tokenCounting: true,
        exportChat: false, // Future feature
        voiceInput: false, // Future feature
        fileUpload: false  // Future feature
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
