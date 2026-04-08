# Git 常用命令速查

---

## 初始化与配置

| 命令 | 说明 |
|------|------|
| `git init` | 初始化本地仓库 |
| `git config` | 配置用户信息 |
| `git clone <url>` | 克隆远程仓库 |

```bash
# 初始化仓库
git init

# 配置用户名和邮箱（全局）
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 克隆仓库
git clone https://github.com/user/repo.git

# 克隆并指定本地目录名
git clone https://github.com/user/repo.git my-project
```

---

## 查看状态与日志

| 命令 | 说明 |
|------|------|
| `git status` | 查看工作区状态 |
| `git log` | 查看提交历史 |
| `git diff` | 查看文件差异 |

```bash
# 查看当前状态
git status

# 查看简洁状态
git status -s

# 查看提交历史（详细）
git log

# 单行显示历史
git log --oneline

# 图形化显示分支历史
git log --oneline --graph --all

# 查看未暂存的修改
git diff

# 查看已暂存的修改
git diff --staged
```

---

## 暂存与提交

| 命令 | 说明 |
|------|------|
| `git add` | 将文件加入暂存区 |
| `git commit` | 提交暂存区内容 |
| `git rm` | 删除文件并暂存 |

```bash
# 暂存指定文件
git add index.html

# 暂存所有修改
git add .

# 提交并写入提交信息
git commit -m "feat: add login page"

# 暂存并提交（跳过 git add，仅对已跟踪文件有效）
git commit -am "fix: correct typo"

# 修改最近一次提交信息（未推送时使用）
git commit --amend -m "fix: correct commit message"

# 删除文件并将删除操作加入暂存
git rm old-file.txt
```

---

## 分支操作

| 命令 | 说明 |
|------|------|
| `git branch` | 查看 / 创建分支 |
| `git checkout` | 切换分支或文件 |
| `git switch` | 切换分支（推荐） |
| `git merge` | 合并分支 |
| `git rebase` | 变基 |

```bash
# 查看所有本地分支
git branch

# 查看所有分支（含远程）
git branch -a

# 创建新分支
git branch feature/login

# 切换分支
git switch feature/login
# 或（旧语法）
git checkout feature/login

# 创建并切换到新分支
git switch -c feature/signup

# 合并分支到当前分支
git merge feature/login

# 删除已合并的分支
git branch -d feature/login

# 强制删除分支
git branch -D feature/login

# 变基（将当前分支的提交接到目标分支末端）
git rebase main
```

---

## 远程操作

| 命令 | 说明 |
|------|------|
| `git remote` | 管理远程仓库 |
| `git fetch` | 拉取远程更新（不合并） |
| `git pull` | 拉取并合并 |
| `git push` | 推送到远程 |

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 拉取远程更新（不自动合并）
git fetch origin

# 拉取并合并（fetch + merge）
git pull origin main

# 推送到远程
git push origin main

# 首次推送并关联上游分支
git push -u origin feature/login

# 强制推送（谨慎使用）
git push --force-with-lease origin feature/login

# 删除远程分支
git push origin --delete feature/login
```

---

## 撤销与回退

| 命令 | 说明 |
|------|------|
| `git restore` | 撤销工作区修改 |
| `git reset` | 回退提交或取消暂存 |
| `git revert` | 创建反向提交（安全回退） |

```bash
# 撤销工作区文件的修改（恢复到上次提交状态）
git restore index.html

# 取消暂存（保留工作区修改）
git restore --staged index.html

# 回退到上一个提交（保留修改在工作区）
git reset HEAD~1

# 回退到指定提交并保留修改（soft）
git reset --soft <commit-hash>

# 回退并丢弃所有修改（危险）
git reset --hard <commit-hash>

# 安全回退：创建一个反向提交（适合已推送的提交）
git revert <commit-hash>
```

---

## 暂存工作现场（Stash）

| 命令 | 说明 |
|------|------|
| `git stash` | 临时保存未提交的修改 |
| `git stash pop` | 恢复并删除最近的 stash |
| `git stash list` | 查看所有 stash |

```bash
# 保存当前工作现场
git stash

# 保存时附加描述
git stash push -m "WIP: login form"

# 查看所有 stash
git stash list

# 恢复最近的 stash 并删除
git stash pop

# 恢复指定 stash（不删除）
git stash apply stash@{1}

# 删除指定 stash
git stash drop stash@{0}

# 清空所有 stash
git stash clear
```

---

## 标签

| 命令 | 说明 |
|------|------|
| `git tag` | 查看 / 创建标签 |
| `git push --tags` | 推送标签到远程 |

```bash
# 查看所有标签
git tag

# 创建轻量标签
git tag v1.0.0

# 创建附注标签（推荐）
git tag -a v1.0.0 -m "Release version 1.0.0"

# 给指定提交打标签
git tag -a v0.9.0 <commit-hash>

# 推送单个标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin --delete v1.0.0
```

---

## 实用技巧

```bash
# 查看某个文件的修改历史
git log --follow -p src/index.js

# 查找引入 bug 的提交（二分查找）
git bisect start
git bisect bad          # 当前版本有问题
git bisect good v1.0.0  # 该版本正常
# Git 会自动切换到中间提交，测试后继续标记 good/bad

# 挑选某个提交应用到当前分支
git cherry-pick <commit-hash>

# 查看命令历史（找回误删的提交）
git reflog

# 统计代码贡献
git shortlog -sn
```

---

## 提交信息规范（Conventional Commits）

```
<type>: <subject>

type 常用值：
  feat     新功能
  fix      修复 bug
  docs     文档变更
  style    代码格式（不影响逻辑）
  refactor 重构
  test     测试相关
  chore    构建/工具配置
```

**示例：**
```
feat: add user authentication
fix: resolve null pointer in login handler
docs: update API usage in README
```
