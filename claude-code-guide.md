# Claude Code 常用功能速查手册

---

## 键盘快捷键

### 核心操作

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Esc` `Esc` | **回退对话** | 撤销上一次操作，恢复代码/会话到指定检查点 |
| `Shift+Tab` | **切换权限模式** | 循环切换：default → acceptEdits → plan → auto |
| `Ctrl+C` | **取消操作** | 中断当前输入或正在生成的响应 |
| `Ctrl+D` | **退出** | 退出 Claude Code 会话 |
| `Ctrl+R` | **搜索历史** | 反向搜索命令历史记录 |
| `Ctrl+O` | **详细模式** | 切换显示完整工具调用记录 |
| `Ctrl+B` | **后台运行** | 将当前任务放到后台执行 |
| `Ctrl+T` | **任务列表** | 显示/隐藏任务进度列表 |

### 模型与模式

| 快捷键 | 功能 |
|--------|------|
| `Option+P` / `Alt+P` | 切换模型（不清空当前输入） |
| `Option+T` / `Alt+T` | 开关深度思考模式（Extended Thinking） |
| `Option+O` / `Alt+O` | 开关快速模式（Fast Mode） |

### 文本编辑

| 快捷键 | 功能 |
|--------|------|
| `Shift+Enter` | 输入换行（多行输入） |
| `\` + `Enter` | 输入换行（通用，所有终端） |
| `Ctrl+K` | 删除光标到行尾 |
| `Ctrl+U` | 删除光标到行首 |
| `Ctrl+Y` | 粘贴刚才删除的内容 |
| `Ctrl+G` / `Ctrl+X Ctrl+E` | 在外部编辑器中编辑当前输入 |

> **macOS 用户注意**：`Option` 键快捷键需在终端中将 Option 设为 Meta 键：
> - **iTerm2**：Settings → Profiles → Keys → Left Option Key → `Esc+`
> - **VS Code**：设置 `"terminal.integrated.macOptionIsMeta": true`

---

## 斜杠命令（Slash Commands）

输入 `/` 可查看所有可用命令，输入字母可过滤。

### 项目与会话

| 命令 | 功能 |
|------|------|
| `/init` | **自动生成配置** — 扫描项目并生成 `CLAUDE.md` 配置文件，快速初始化项目 |
| `/resume` | **恢复会话** — 按 ID/名称恢复历史会话，无参数则弹出选择器 |
| `/clear` | 清空当前对话历史，释放上下文空间 |
| `/rename [name]` | 重命名当前会话（无参数则自动生成） |
| `/branch [name]` | 从当前对话创建分支（会话分叉） |
| `/rewind` | 回退到上一个检查点（同 `Esc+Esc`） |
| `/export` | 将当前对话导出为纯文本文件 |

### 上下文管理

| 命令 | 功能 |
|------|------|
| `/compact [说明]` | **压缩上下文** — 将历史对话压缩摘要，节省 Token，可附加保留重点的说明 |
| `/context` | **查看上下文** — 以彩色网格可视化当前 Token 使用量，并给出优化建议 |
| `/cost` | 查看当前会话的 Token 消耗统计 |
| `/btw <问题>` | 快速提问，不计入主对话上下文（节省 Token） |

### 规划与执行

| 命令 | 功能 |
|------|------|
| `/plan [描述]` | **进入规划模式** — Claude 只探索不修改，生成变更方案后由你决定是否执行 |
| `/ultraplan <任务>` | 在浏览器中进行深度规划，完成后返回终端执行 |

### 代码与审查

| 命令 | 功能 |
|------|------|
| `/diff` | 打开交互式差异查看器（含 git diff 和本轮变更） |
| `/security-review` | 对当前分支未提交变更进行安全漏洞分析 |

### 配置与工具

| 命令 | 功能 |
|------|------|
| `/config` | 打开设置界面（主题、模型、输出风格等） |
| `/model [模型名]` | 切换 AI 模型 |
| `/memory` | 管理 `CLAUDE.md` 和自动记忆文件 |
| `/permissions` | 管理工具允许/拒绝规则 |
| `/doctor` | 诊断 Claude Code 安装和配置问题 |
| `/help` | 查看帮助信息 |

### 统计与状态

| 命令 | 功能 |
|------|------|
| `/status` | 查看版本、模型、账户、网络连接状态 |
| `/usage` | 查看计划用量和限速状态 |
| `/stats` | 可视化每日用量、会话历史、模型偏好 |

---

## @ 引用 — 精准指定上下文

在提问时输入 `@` 可触发自动补全，精准将文件内容注入上下文。

### 基本用法

```
# 引用单个文件
请分析 @src/main.py 的性能问题

# 同时引用多个文件
对比 @src/old.js 和 @src/new.js 的区别

# 引用特定路径
查看 @config/database.yml 的配置是否有问题
```

### 在 CLAUDE.md 中导入文件

```markdown
# 项目说明
参考 @README.md 了解项目概述
遵循 @docs/coding-style.md 中的编码规范
依赖信息见 @package.json
```

> 路径相对于当前文件，支持最多 5 层递归导入。

---

## 规划模式 — 先规划后编码

避免 Claude 直接修改代码，先生成方案再决定是否执行。

### 进入方式

```bash
# 方式一：键盘循环切换
Shift+Tab  →  直到显示 plan 模式

# 方式二：命令
/plan 重构用户认证模块

# 方式三：启动时指定
claude --permission-mode plan
```

### 工作流程

```
1. Claude 读取文件、运行探索命令（不做任何修改）
      ↓
2. 生成详细变更方案供你审阅
      ↓
3. 你选择执行方式：
   ├─ 批准 → auto 模式（自动执行）
   ├─ 批准 → acceptEdits 模式（执行后逐个审阅）
   └─ 继续反馈 → 完善方案
```

### 适用场景
- 探索陌生代码库
- 大规模重构前评估影响
- 复杂架构决策

---

## 权限模式详解

`Shift+Tab` 循环切换，控制 Claude 执行操作前是否需要确认。

| 模式 | 无需确认的操作 | 适用场景 |
|------|--------------|----------|
| `default` | 仅读取文件 | 日常使用、敏感项目 |
| `acceptEdits` | 读取 + 文件编辑 | 迭代开发、边写边看 |
| `plan` | 仅读取（生成方案） | 评估变更影响 |
| `auto` | 几乎所有操作 | 长任务、减少打断 |
| `bypassPermissions` | 所有操作 | 仅限隔离容器/VM |

---

## 会话管理

### 命令行启动参数

```bash
# 继续上次会话
claude -c

# 按名称恢复会话
claude -r "my-feature-work"

# 交互式会话选择器
claude -r

# 启动时命名会话
claude -n "auth-refactor"

# 启动时指定模型
claude --model opus

# 启动时设置权限模式
claude --permission-mode plan
```

### 会话内操作

```bash
# 快速执行 shell 命令（! 前缀）
! git status
! npm test
! ls -la
```

---

## 模型切换

### 可用模型别名

| 别名 | 说明 |
|------|------|
| `opus` | 最强推理，适合复杂架构 |
| `sonnet` | 日常编码首选，速度与质量均衡 |
| `haiku` | 最快，适合简单任务 |
| `best` | 自动选择当前最强模型 |
| `sonnet[1m]` | Sonnet + 100 万 Token 超长上下文 |
| `opus[1m]` | Opus + 100 万 Token 超长上下文 |
| `opusplan` | Opus 规划 + Sonnet 执行（混合模式） |

```bash
# 切换模型
/model opus
/model sonnet[1m]

# 或按 Option+P 实时切换
```

---

## 记忆系统

Claude 可以跨会话记住项目约定，避免重复说明。

### CLAUDE.md 配置文件层级

| 文件位置 | 作用范围 |
|----------|----------|
| `./CLAUDE.md` | 当前项目（提交到 Git） |
| `./CLAUDE.local.md` | 当前项目（个人，不提交） |
| `~/.claude/CLAUDE.md` | 所有项目（全局） |

### 配置示例

```markdown
# 编码规范
- 使用 2 空格缩进
- 函数命名使用驼峰式
- 所有 API 接口需要错误处理

# 常用命令
- 运行测试：npm test
- 启动开发：npm run dev

# 注意事项
- 数据库迁移前必须备份
- 参考 @docs/api-spec.md 中的接口规范
```

### 管理记忆

```bash
# 查看和编辑记忆
/memory

# 让 Claude 记住某件事
"记住我们项目使用 PostgreSQL 15，不用 MySQL"
```

---

## 上下文优化技巧

```bash
# 1. 查看上下文使用量
/context

# 2. 手动压缩（保留关键信息）
/compact 保留数据库设计和 API 接口定义

# 3. 快速提问不占主上下文
/btw 这个函数的参数顺序是什么？

# 4. 清空重开
/clear
```

---

## 常用工作流速查

| 目标 | 操作 |
|------|------|
| 撤销误操作 | `Esc` `Esc` → 选择检查点 |
| 查看 Token 用量 | `/context` 或 `/cost` |
| 先规划再执行 | `Shift+Tab` 切到 plan 模式，或 `/plan` |
| 快速初始化项目 | `/init` |
| 节省 Token | `/compact` 压缩历史 |
| 自动接受编辑 | `Shift+Tab` 切到 acceptEdits 模式 |
| 取消当前操作 | `Ctrl+C` |
| 恢复历史会话 | `/resume` 或 `claude -r` |
| 引用文件上下文 | 输入 `@` 触发文件补全 |
| 切换模型 | `Option+P` 或 `/model opus` |
| 诊断安装问题 | `/doctor` |
| 退出 | `Ctrl+D` 或 `Ctrl+C` 两次 |
