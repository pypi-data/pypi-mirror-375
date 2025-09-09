# 👻 Haunted - 靈異軟體解決方案

**你的程式庫剛被超自然開發力量附身了。**

用自主 AI 靈體轉變你的開發流程，這個靈體會思考、編碼，並在你專注於更大藍圖時自動交付功能。Haunted 不只是輔助工具 - 它會附身於你的儲存庫，處理從規劃到部署的完整開發週期。

**🌙 無需 API 降靈儀式** - 無縫連接你的 Claude Code 驗證，輕鬆進行靈異整合。

[English README](README.md) | [繁體中文](#)

## 🔮 超自然功能

- **👻 靈體驗證**：無需 API 金鑰 - 直接引導你的 Claude Code 力量
- **🎭 自主附身**：AI 從概念到部署完全掌控功能開發
- **🌙 並行靈異現象**：同時在你的程式庫中開發多個 issues
- **🕯️ 自我驅魔**：當 bug 出現時，靈體會自動除錯並修復
- **🦇 Git 顯靈**：以幽靈般的精確度自動建立分支、測試和合併
- **👺 Issue 驅動降靈**：所有開發都從清晰的 issue 描述和優先級開始
- **🎃 靈體工作流**：完整開發生命週期 - 規劃 → 編碼 → 測試 → 除錯 → 發佈

## 🕯️ 召喚需求

- **Python 3.10+** - 靈體力量的容器
- **Node.js 18+** - Claude Code 通靈必需
- **Claude Code CLI** - 你通往超自然領域的門戶：

```bash
# 安裝 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 與靈體領域認證（這會開啟傳送門！）
claude login
```

## 🎭 附身儀式

```bash
# 即時靈體附身（推薦）
uvx haunted

# 或使用 pipx 全域召喚
pipx install haunted

# 用於開發附身
git clone <repository-url>
cd haunted
uv sync
```

**🌙 附身完成！** 無需 API 金鑰 - Haunted 會自動引導你的 Claude Code 驗證。

### 🔮 確認靈異現象

```bash
# 測試靈體連接
uvx haunted --help

# pipx 安裝的話
haunted --help
```

## 🌙 召喚你的靈體開發者

### 1. 開始附身

```bash
# 邀請靈體進入你的專案
uvx haunted init

# 或如果已用 pipx 全域安裝
haunted init
```

這個靈體儀式將會：
- 顯現 `.haunted/` 聖域與資料庫及配置
- 驗證你的 Git 儲存庫已準備好被附身
- 建立超自然配置

### 2. 低語你的願望

```bash
# 向靈體傳達你的高優先級願望
uvx haunted issue create "實現用戶認證" --priority high --description "添加登入/登出功能與 JWT 令牌"

# 將超自然工作組織成階段
uvx haunted phase create "第一階段 - 核心功能" --description "MVP 的基本功能"

# 將額外請求引導到特定階段
uvx haunted issue create "添加密碼重設" --phase <phase-id> --priority medium
```

### 3. 釋放自主靈體

```bash
# 釋放你的靈體開發者
uvx haunted start
```

你的幽靈助手將會：
- 按超自然優先級掃描開放的 Issues
- 為每個靈體任務顯現 Git 分支
- 通過完整開發週期附身你的程式庫
- 自動合併完成的靈異現象

### 4. 監控進度

```bash
# 檢查整體狀態
uvx haunted status

# 列出所有 issues
uvx haunted issue list

# 查看特定 issue 詳情
uvx haunted issue show <issue-id>

# 按狀態查看 issues
uvx haunted issue list --status in_progress
```

## 🎪 靈異工作流程

Haunted 實現了來自 `docs/DEVELOPMENT_WORKFLOW.md` 的開發工作流程：

1. **規劃**：AI 分析需求並創建實施策略
2. **實現**：AI 按照計劃編寫代碼
3. **單元測試**：AI 創建並運行單元測試
4. **修復問題**：AI 修復任何測試失敗
5. **整合測試**：AI 運行整合測試
6. **診斷**：如果整合測試失敗，AI 診斷並重新規劃
7. **完成**：Issue 完成並合併

## 🦇 核心咒語

### 基本命令

- `uvx haunted init` - 在當前專案中初始化 Haunted
- `uvx haunted start` - 啟動 AI 守護程序
- `uvx haunted stop` - 停止守護程序
- `uvx haunted status` - 顯示當前狀態

### Issue 管理

- `uvx haunted issue create <標題>` - 創建新 issue
- `uvx haunted issue list` - 列出所有 issues
- `uvx haunted issue show <id>` - 顯示 issue 詳情
- `uvx haunted issue comment <id> <訊息>` - 為 issue 添加評論

### 階段管理

- `uvx haunted phase create <名稱>` - 創建新階段
- `uvx haunted phase list` - 列出所有階段

## ⚙️ 靈異配置

配置存儲在 `.haunted/config.yaml`：

```yaml
api:
  # 無需 API 金鑰！使用 Claude Code 驗證
  model: claude-3-5-sonnet-20241022  # Claude Code 模型
  max_concurrent_issues: 3
  rate_limit_retry: true

daemon:
  scan_interval: 30  # 秒
  max_iterations: 3  # 每個 issue 的最大工作流週期

git:
  auto_merge: true
  auto_commit: true

database:
  url: sqlite:///.haunted/haunted.db
```

## 🏗️ 靈異架構

```
haunted/
├── cli/           # 命令行介面
├── core/          # 核心業務邏輯
│   ├── claude_wrapper.py # Claude Code SDK 整合
│   ├── workflow.py       # 工作流引擎
│   ├── database.py       # 資料庫管理
│   └── git_manager.py    # Git 操作
├── models/        # SQLModel 資料模型
├── daemon/        # 後台服務
├── mcp/           # Claude 的 MCP 工具
└── utils/         # 工具和配置
```

## 🎭 開發工作流程整合

Haunted 設計與你現有的開發工作流程配合：

1. **創建 Issues** 用於功能、錯誤或任務
2. **讓 AI 工作** - Haunted 自主處理 Issues
3. **審查結果** - 在 Git 分支中檢查 AI 的工作
4. **提供反饋** - 為被阻塞的 Issues 添加評論
5. **合併與部署** - 完成的 Issues 會自動合併

## 🌿 Git 分支策略

- **main**：生產分支
- **phase/<名稱>**：組織工作的階段分支
- **issue/<id>**：個別 Issue 分支
- 自動合併：Issues → Phases → Main（準備就緒時）

## 🛠️ MCP 工具

Claude 可使用綜合工具：
- 檔案操作（讀取、寫入、列表）
- 命令執行
- Git 操作
- Issue 管理
- 代碼搜尋和分析

## 🔧 故障排除

### 常見問題

1. **Claude Code 未驗證**：先運行 `claude login`
2. **Claude Code 未安裝**：用 `npm install -g @anthropic-ai/claude-code` 安裝
3. **Python 版本 < 3.10**：升級到 Python 3.10 或更高版本
4. **非 Git 儲存庫**：先運行 `git init`
5. **資料庫錯誤**：刪除 `.haunted/haunted.db` 並重新初始化

### 日誌

啟用詳細日誌：
```bash
uvx haunted --verbose start
```

或指定日誌檔案：
```bash
uvx haunted --log-file haunted.log start
```

## 🎃 使用範例

### 基本工作流程

```bash
# 初始化專案
uvx haunted init

# 創建 issues
uvx haunted issue create "添加用戶模型" --priority high
uvx haunted issue create "實現 API 端點" --priority high
uvx haunted issue create "添加輸入驗證" --priority medium

# 開始 AI 處理
uvx haunted start

# 監控進度
watch uvx haunted status
```

### Issue 管理

```bash
# 查看 issue 詳情
uvx haunted issue show abc123

# 添加澄清評論
uvx haunted issue comment abc123 "請使用 bcrypt 進行密碼雜湊"

# 檢查所有開放的 issues
uvx haunted issue list --status open
```

## 🤝 參與貢獻

1. Fork 儲存庫
2. 創建功能分支：`git checkout -b feature/name`
3. 進行更改並測試
4. 提交拉取請求

## 📜 授權

MIT 授權 - 詳見 LICENSE 檔案。

---

**👻 你的程式庫永遠不會再一樣了。擁抱這個靈異現象。**