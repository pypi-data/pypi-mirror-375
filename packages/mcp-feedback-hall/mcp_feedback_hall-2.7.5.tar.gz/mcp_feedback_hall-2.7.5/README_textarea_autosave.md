# Textarea 自動暫存功能實作說明

## 📋 功能概述

為 mcp-feedback-hall 系統新增了 textarea 自動暫存功能，確保使用者在自動發送回饋功能執行時，能夠保存並還原輸入的內容。

## 🎯 主要特性

### ✅ 自動暫存時機
- **自動提交前**：在自動發送回饋功能執行前（每600秒或設定時間）自動保存 textarea 內容
- **定期備份**：每30秒自動保存一次（防抖處理）
- **內容變更時**：使用者輸入2秒後自動保存
- **失去焦點時**：當 textarea 失去焦點時保存

### 🔄 自動還原機制
- **頁面載入時**：檢查是否有暫存內容
- **智能提示**：如果 textarea 已有內容，會詢問使用者是否要還原暫存內容
- **內容預覽**：顯示暫存內容的前100字符供使用者確認
- **時間資訊**：顯示內容的暫存時間

### 🧹 自動清理
- **手動提交後**：成功提交回饋後自動清除暫存
- **內容清空時**：當使用者清空 textarea 時清除暫存
- **過期清理**：暫存內容7天後自動過期

## 🔧 技術實作

### 新增檔案
1. **`textarea-autosave.js`** - 核心自動保存模組
2. **`README_textarea_autosave.md`** - 功能說明文件

### 修改檔案
1. **`app.js`** - 整合自動保存管理器
2. **`feedback.html`** - 載入新的 JavaScript 模組

### 核心類別
```javascript
// 初始化自動保存管理器
this.textareaAutoSave = new window.MCPFeedback.TextareaAutoSave({
    textareaSelector: '#combinedFeedbackText',
    storageKey: 'mcp_feedback_textarea_autosave',
    autoSaveInterval: 30000, // 30秒
    enabled: true
});
```

## 📊 運作流程

### 保存流程
```
使用者輸入 → 防抖延遲 → 檢查內容變化 → localStorage 保存 → 觸發回調
```

### 還原流程
```
頁面載入 → 檢查暫存 → 驗證有效性 → 用戶確認 → 還原內容 → 清除暫存
```

### 自動提交流程
```
自動提交觸發 → 保存當前內容 → 執行自動提交 → 清除暫存
```

## ⚙️ 設定選項

### 初始化參數
- **textareaSelector**: 目標 textarea 選擇器 (預設: `#combinedFeedbackText`)
- **storageKey**: localStorage 儲存鍵值 (預設: `mcp_feedback_textarea_autosave`)
- **autoSaveInterval**: 自動保存間隔 (預設: 30000ms)
- **enabled**: 是否啟用功能 (預設: true)

### 回調函數
- **onSave**: 保存完成時觸發
- **onRestore**: 還原完成時觸發
- **onClear**: 清除暫存時觸發

## 🔒 資料安全

### 儲存格式
```json
{
    "content": "使用者輸入的內容",
    "timestamp": 1640995200000,
    "url": "當前頁面URL",
    "userAgent": "瀏覽器標識（限制100字符）"
}
```

### 安全機制
- **本地儲存**: 使用 localStorage，數據僅存在本地
- **過期清理**: 7天自動過期，避免佔用過多空間
- **格式驗證**: 載入時驗證數據格式有效性
- **錯誤處理**: 完整的異常處理機制

## 🔧 API 介面

### 主要方法
```javascript
// 初始化
textareaAutoSave.init()

// 手動保存
textareaAutoSave.saveContent()

// 手動還原
textareaAutoSave.restoreContent()

// 清除暫存
textareaAutoSave.clearSavedContent()

// 自動提交前保存
textareaAutoSave.saveBeforeSubmit()

// 手動提交後清除
textareaAutoSave.clearAfterSubmit()

// 獲取狀態
textareaAutoSave.getStatus()

// 啟用/停用
textareaAutoSave.setEnabled(enabled)

// 清理資源
textareaAutoSave.destroy()
```

## 🔍 除錯資訊

### 日誌輸出
系統會在 console 中輸出詳細的操作日誌：
- **💾 保存操作**: 顯示內容長度和時間戳
- **🔄 還原操作**: 顯示還原的內容資訊
- **🧹 清理操作**: 顯示清理狀態
- **⚠️ 錯誤處理**: 顯示錯誤訊息和原因

### 狀態檢查
```javascript
// 檢查當前狀態
const status = feedbackApp.textareaAutoSave.getStatus();
console.log('自動保存狀態:', status);
```

## 🧪 測試方式

### 基本功能測試
1. **輸入內容** → 等待2秒 → 檢查 console 是否有保存日誌
2. **刷新頁面** → 確認是否提示還原暫存內容
3. **手動提交** → 確認暫存內容被清除
4. **自動提交** → 確認在提交前保存內容

### 邊界條件測試
1. **空內容**: 清空 textarea → 確認暫存被清除
2. **過期內容**: 修改時間戳為7天前 → 確認不會還原
3. **損壞數據**: 手動修改 localStorage → 確認錯誤處理

## 🔗 整合點

### 與自動提交系統整合
```javascript
// 在 performAutoSubmit() 方法中
if (this.textareaAutoSave) {
    this.textareaAutoSave.saveBeforeSubmit();
}
```

### 與回饋處理系統整合
```javascript
// 在 handleFeedbackReceived() 方法中
if (this.textareaAutoSave) {
    this.textareaAutoSave.clearAfterSubmit();
}
```

## 📈 效能考量

### 優化措施
- **防抖處理**: 避免頻繁保存操作
- **內容比較**: 只在內容變化時保存
- **異步操作**: 不阻塞 UI 執行緒
- **錯誤隔離**: 保存失敗不影響主功能

### 資源佔用
- **記憶體**: 最小化物件儲存
- **儲存空間**: 自動清理過期數據
- **CPU**: 防抖和節流處理

## 🚀 未來擴展

### 可能的改進方向
1. **多 textarea 支援**: 支援多個輸入框的自動保存
2. **雲端同步**: 將暫存內容同步到伺服器
3. **版本歷史**: 保存多個版本的內容歷史
4. **智能提示**: 根據內容相似度提供更智能的還原建議

---

## 📧 支援

如有問題或建議，請參考：
- 系統日誌輸出
- 開發者工具 Console
- localStorage 儲存內容檢查

**實作完成時間**: 2025-09-10 06:53:02  
**功能狀態**: ✅ 已實作並測試
