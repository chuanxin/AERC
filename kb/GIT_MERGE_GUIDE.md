# Git 本地与远程分支合并操作指南

## 概述
本指南用于处理本地有未提交修改，同时远程分支有新更新的情况下，如何安全地合并代码。

## 场景描述
- **本地状态**: 有未提交的修改（工作目录或暂存区有变更）
- **远程状态**: 远程分支有新的提交需要合并
- **目标**: 保留本地修改的同时合并远程更新

## 标准操作流程

### 1. 检查当前状态
```powershell
# 查看本地修改状态
git status

# 查看本地未推送的提交（如果有）
git log --oneline origin/[branch-name]..HEAD

# 获取远程更新信息
git fetch origin

# 查看远程未合并的提交
git log --oneline HEAD..origin/[branch-name]
```

### 2. 暂存本地修改
```powershell
# 暂存所有本地修改（包括工作目录和暂存区）
git stash push -m "Local changes before merge - [描述性信息]"

# 验证工作目录干净
git status
```

### 3. 合并远程更新
```powershell
# 合并远程分支（通常是快进合并）
git merge origin/[branch-name]

# 如果需要，也可以使用 rebase（保持线性历史）
# git rebase origin/[branch-name]
```

### 4. 恢复本地修改
```powershell
# 恢复之前暂存的修改
git stash pop

# 如果有冲突，解决冲突后继续
```

### 5. 处理可能的冲突
如果 `git stash pop` 出现冲突：
```powershell
# 查看冲突文件
git status

# 手动解决冲突后
git add [解决冲突的文件]

# 清理stash记录
git stash drop
```

### 6. 提交合并后的修改
```powershell
# 查看当前修改
git diff

# 添加修改到暂存区
git add .

# 提交修改
git commit -m "feat: [描述本地修改内容]"

# 推送到远程
git push origin [branch-name]
```

## 实际案例记录

### 案例：2025-08-18 windows-deployment 分支合并

#### 初始状态
- **分支**: windows-deployment
- **本地修改**: 
  - `Init_AERC_Deployment.ps1` (增强部署脚本)
  - `dry-farm/package.json` (版本号修改)
- **远程新提交**: `5a25f8a` (feat: cross-platform compatibility fixes and dev tools)

#### 执行步骤
```powershell
# 1. 检查状态
git status
git fetch origin
git log --oneline HEAD..origin/windows-deployment

# 2. 暂存本地修改
git stash push -m "Local changes before merge"

# 3. 合并远程更新
git merge origin/windows-deployment
# 结果：Fast-forward merge 成功

# 4. 恢复本地修改
git stash pop
# 结果：成功恢复，无冲突

# 5. 验证状态
git status
```

#### 合并结果
- ✅ 远程更新成功合并
- ✅ 本地修改完整保留
- ✅ 无冲突产生
- ✅ 历史记录清晰

## 替代方案

### 方案一：使用 Rebase（保持线性历史）
```powershell
git stash push -m "Local changes before rebase"
git rebase origin/[branch-name]
git stash pop
```

### 方案二：创建备份分支（安全第一）
```powershell
# 创建备份分支
git checkout -b backup-before-merge-$(date +%Y%m%d)
git checkout [original-branch]

# 然后执行标准合并流程
```

### 方案三：使用 GUI 工具
- **VS Code**: 使用源代码管理面板
- **Git GUI**: `git gui`
- **TortoiseGit**: Windows 图形界面工具

## 常见问题与解决方案

### Q1: git stash pop 时出现冲突怎么办？
```powershell
# 查看冲突
git status
git diff

# 解决冲突后
git add [冲突文件]
git stash drop  # 清理stash记录
```

### Q2: 忘记暂存直接合并导致冲突？
```powershell
# 取消合并
git merge --abort

# 暂存修改后重新合并
git stash push -m "Forgot to stash before merge"
git merge origin/[branch-name]
git stash pop
```

### Q3: 想要撤销合并操作？
```powershell
# 查看合并前的提交
git reflog

# 重置到合并前状态
git reset --hard [合并前的commit-hash]

# 如果已经推送了，需要强制推送（危险操作）
# git push --force-with-lease origin [branch-name]
```

### Q4: 如何查看合并后的变更？
```powershell
# 查看最近的合并提交
git show --stat

# 查看详细差异
git log --oneline -10
git diff HEAD~[n]  # n为要比较的提交数
```

## 最佳实践

### 1. 合并前的准备
- ✅ 确保本地修改已测试
- ✅ 备份重要修改
- ✅ 了解远程更新内容
- ✅ 选择合适的时间进行合并

### 2. 合并过程中
- ✅ 逐步执行，验证每一步
- ✅ 遇到问题及时停止
- ✅ 仔细解决冲突
- ✅ 测试合并后的代码

### 3. 合并后的验证
- ✅ 运行项目确保正常工作
- ✅ 检查所有修改是否保留
- ✅ 提交有意义的commit消息
- ✅ 及时推送到远程

## 工具推荐

### 命令行工具
```powershell
# 美化Git日志显示
git log --oneline --graph --decorate --all

# 交互式暂存
git add -i

# 查看分支关系
git log --graph --pretty=format:'%h -%d %s (%cr) <%an>' --abbrev-commit
```

### VS Code 扩展
- **GitLens**: 增强Git功能
- **Git Graph**: 可视化分支图
- **Git History**: 文件历史查看

## 紧急情况处理

### 如果合并过程中系统崩溃
```powershell
# 检查Git状态
git status

# 如果在合并过程中
git merge --abort

# 恢复工作目录
git reset --hard HEAD
git stash pop  # 如果stash还在
```

### 数据恢复
```powershell
# 查看所有操作历史
git reflog

# 恢复到特定状态
git reset --hard [commit-hash]

# 查看丢失的stash
git stash list
git show stash@{0}
```

---

## 版本信息
- **创建日期**: 2025-08-18
- **适用项目**: AERC
- **Git版本**: 2.x+
- **测试环境**: Windows PowerShell

## 更新记录
- 2025-08-18: 初始版本，基于 windows-deployment 分支合并经验创建

---

*这份指南基于实际操作经验编写，建议在重要合并前先在测试分支上练习。*
