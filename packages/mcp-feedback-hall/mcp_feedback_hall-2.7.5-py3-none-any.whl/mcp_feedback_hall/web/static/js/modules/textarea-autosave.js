/**
 * MCP Feedback Enhanced - Textarea 自動保存模組
 * ===============================================
 * 
 * 提供 textarea 內容的自動保存和還原功能
 * 在自動提交執行前保存內容，頁面重新載入時還原
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    // 創建模組專用日誌器
    const logger = window.MCPFeedback.Logger ?
        new window.MCPFeedback.Logger({ moduleName: 'TextareaAutoSave' }) :
        console;

    /**
     * Textarea 自動保存管理器建構函數
     */
    function TextareaAutoSave(options) {
        options = options || {};
        
        // 設定
        this.textareaSelector = options.textareaSelector || '#combinedFeedbackText';
        this.storageKey = options.storageKey || 'mcp_feedback_textarea_autosave';
        this.autoSaveInterval = options.autoSaveInterval || 30000; // 30秒自動保存一次
        this.enabled = options.enabled !== false; // 預設啟用
        
        // 內部狀態
        this.textarea = null;
        this.autoSaveTimer = null;
        this.lastSavedContent = '';
        this.isRestoring = false;
        
        // 回調函數
        this.onSave = options.onSave || null;
        this.onRestore = options.onRestore || null;
        this.onClear = options.onClear || null;

        logger.info('Textarea 自動保存管理器初始化完成', {
            selector: this.textareaSelector,
            storageKey: this.storageKey,
            autoSaveInterval: this.autoSaveInterval
        });
    }

    /**
     * 初始化自動保存功能
     */
    TextareaAutoSave.prototype.init = function() {
        if (!this.enabled) {
            logger.info('Textarea 自動保存功能已停用');
            return;
        }

        // 尋找 textarea 元素
        this.textarea = document.querySelector(this.textareaSelector);
        if (!this.textarea) {
            logger.warn('找不到 textarea 元素：', this.textareaSelector);
            return;
        }

        // 初始化事件監聽器
        this.setupEventListeners();
        
        // 檢查並還原暫存內容
        this.restoreContent();
        
        // 啟動定期自動保存
        this.startAutoSave();

        logger.info('Textarea 自動保存功能初始化完成');
    };

    /**
     * 設置事件監聽器
     */
    TextareaAutoSave.prototype.setupEventListeners = function() {
        if (!this.textarea) return;

        const self = this;

        // 監聽內容變化
        this.textarea.addEventListener('input', function() {
            // 延遲保存，避免過於頻繁
            self.debouncedSave();
        });

        // 監聽失去焦點事件
        this.textarea.addEventListener('blur', function() {
            self.saveContent();
        });

        logger.debug('事件監聽器設置完成');
    };

    /**
     * 防抖保存函數
     */
    TextareaAutoSave.prototype.debouncedSave = (function() {
        let timeout;
        return function() {
            clearTimeout(timeout);
            const self = this;
            timeout = setTimeout(function() {
                self.saveContent();
            }, 2000); // 2秒後保存
        };
    })();

    /**
     * 保存 textarea 內容到 localStorage
     */
    TextareaAutoSave.prototype.saveContent = function() {
        if (!this.textarea || this.isRestoring) return;

        const content = this.textarea.value.trim();
        
        // 如果內容為空，清除暫存
        if (!content) {
            this.clearSavedContent();
            return;
        }

        // 如果內容沒有變化，跳過保存
        if (content === this.lastSavedContent) {
            return;
        }

        try {
            const saveData = {
                content: content,
                timestamp: Date.now(),
                url: window.location.href,
                userAgent: navigator.userAgent.substring(0, 100) // 限制長度
            };

            localStorage.setItem(this.storageKey, JSON.stringify(saveData));
            this.lastSavedContent = content;

            logger.debug('Textarea 內容已保存', {
                contentLength: content.length,
                timestamp: saveData.timestamp
            });

            // 觸發保存回調
            if (this.onSave) {
                this.onSave(content, saveData.timestamp);
            }

        } catch (error) {
            logger.error('保存 textarea 內容失敗：', error);
        }
    };

    /**
     * 從 localStorage 還原 textarea 內容
     */
    TextareaAutoSave.prototype.restoreContent = function() {
        if (!this.textarea) return;

        try {
            const savedData = localStorage.getItem(this.storageKey);
            if (!savedData) {
                logger.debug('沒有找到暫存的 textarea 內容');
                return;
            }

            const saveData = JSON.parse(savedData);
            
            // 檢查暫存數據的有效性
            if (!saveData.content || !saveData.timestamp) {
                logger.warn('暫存數據格式無效，清除暫存');
                this.clearSavedContent();
                return;
            }

            // 檢查暫存數據是否過期（7天）
            const maxAge = 7 * 24 * 60 * 60 * 1000; // 7天
            if (Date.now() - saveData.timestamp > maxAge) {
                logger.info('暫存數據已過期，清除暫存');
                this.clearSavedContent();
                return;
            }

            // 如果 textarea 已有內容，詢問用戶是否要還原
            const currentContent = this.textarea.value.trim();
            if (currentContent) {
                const confirmMessage = '檢測到有暫存的回饋內容，是否要還原？\n\n' +
                    '暫存內容預覽：\n' + 
                    saveData.content.substring(0, 100) + 
                    (saveData.content.length > 100 ? '...' : '') +
                    '\n\n暫存時間：' + new Date(saveData.timestamp).toLocaleString();
                
                if (!confirm(confirmMessage)) {
                    logger.info('用戶選擇不還原暫存內容');
                    return;
                }
            }

            // 還原內容
            this.isRestoring = true;
            this.textarea.value = saveData.content;
            this.lastSavedContent = saveData.content;
            this.isRestoring = false;

            // 觸發 input 事件以更新相關 UI（如字數統計等）
            const inputEvent = new Event('input', { bubbles: true });
            this.textarea.dispatchEvent(inputEvent);

            logger.info('Textarea 內容已還原', {
                contentLength: saveData.content.length,
                savedTime: new Date(saveData.timestamp).toLocaleString()
            });

            // 觸發還原回調
            if (this.onRestore) {
                this.onRestore(saveData.content, saveData.timestamp);
            }

            // 還原成功後清除暫存（避免重複還原）
            this.clearSavedContent();

        } catch (error) {
            logger.error('還原 textarea 內容失敗：', error);
            // 清除可能損壞的暫存數據
            this.clearSavedContent();
        }
    };

    /**
     * 清除保存的內容
     */
    TextareaAutoSave.prototype.clearSavedContent = function() {
        try {
            localStorage.removeItem(this.storageKey);
            this.lastSavedContent = '';
            
            logger.debug('已清除暫存的 textarea 內容');

            // 觸發清除回調
            if (this.onClear) {
                this.onClear();
            }

        } catch (error) {
            logger.error('清除暫存內容失敗：', error);
        }
    };

    /**
     * 手動觸發保存（在自動提交前調用）
     */
    TextareaAutoSave.prototype.saveBeforeSubmit = function() {
        logger.info('自動提交前保存 textarea 內容');
        this.saveContent();
    };

    /**
     * 手動提交成功後清除暫存
     */
    TextareaAutoSave.prototype.clearAfterSubmit = function() {
        logger.info('手動提交成功，清除暫存內容');
        this.clearSavedContent();
    };

    /**
     * 啟動定期自動保存
     */
    TextareaAutoSave.prototype.startAutoSave = function() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }

        const self = this;
        this.autoSaveTimer = setInterval(function() {
            self.saveContent();
        }, this.autoSaveInterval);

        logger.debug('定期自動保存已啟動，間隔：', this.autoSaveInterval + 'ms');
    };

    /**
     * 停止定期自動保存
     */
    TextareaAutoSave.prototype.stopAutoSave = function() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
            logger.debug('定期自動保存已停止');
        }
    };

    /**
     * 啟用/停用自動保存功能
     */
    TextareaAutoSave.prototype.setEnabled = function(enabled) {
        this.enabled = enabled;
        
        if (enabled) {
            this.init();
        } else {
            this.stopAutoSave();
            logger.info('Textarea 自動保存功能已停用');
        }
    };

    /**
     * 獲取當前暫存狀態
     */
    TextareaAutoSave.prototype.getStatus = function() {
        const savedData = localStorage.getItem(this.storageKey);
        
        return {
            enabled: this.enabled,
            hasSavedContent: !!savedData,
            savedData: savedData ? JSON.parse(savedData) : null,
            lastSavedContent: this.lastSavedContent
        };
    };

    /**
     * 清理資源
     */
    TextareaAutoSave.prototype.destroy = function() {
        this.stopAutoSave();
        
        // 移除事件監聽器
        if (this.textarea) {
            this.textarea.removeEventListener('input', this.debouncedSave);
            this.textarea.removeEventListener('blur', this.saveContent);
        }

        logger.info('Textarea 自動保存管理器已清理');
    };

    // 將 TextareaAutoSave 加入命名空間
    window.MCPFeedback.TextareaAutoSave = TextareaAutoSave;

    console.log('✅ TextareaAutoSave 模組載入完成');

})();
