# Git to SVN 自动同步操作说明书

## 概述
`sync-git-to-svn.ps1` 脚本提供了从 Git 仓库到 SVN 仓库的自动化同步功能，支持安全的文件同步和远程提交操作。

## 脚本功能特性

### 🔄 **核心功能**
- **Git 仓库更新**：自动拉取远程 Git 更新
- **智能文件同步**：使用 Robocopy 镜像同步文件
- **SVN 自动提交**：自动处理新增、修改、删除文件并提交到 SVN 远程
- **排除文件支持**：根据配置文件排除不需要同步的文件

### 🛡️ **安全特性**
- **干运行模式**：预览操作不做实际更改
- **跳过提交选项**：只同步文件不提交到 SVN
- **详细日志记录**：完整的操作记录和错误追踪
- **前置条件检查**：确保环境配置正确

## 目录结构要求

```
svn-bridge/
├── scripts/
│   └── sync-git-to-svn.ps1          # 主脚本
├── config/
│   └── exclude-files.txt             # 排除文件配置
├── repos/
│   ├── git-mirror/                   # Git 镜像目录
│   └── svn-working/
│       └── trunk/                    # SVN 工作目录
└── logs/                             # 日志文件目录
    └── sync_YYYYMMDD_HHMMSS.log     # 自动生成的日志
```

## 命令参数说明

### 基本语法
```powershell
.\sync-git-to-svn.ps1 [参数]
```

### 参数选项

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `-DryRun` | 开关 | 预览模式，模拟运行不做实际更改 | 否 |
| `-SkipSvnCommit` | 开关 | 跳过 SVN 提交步骤 | 否 |

## 使用示例

### 1. 完整同步（推荐）
```powershell
# 完整的 Git 到 SVN 同步，包含远程提交
.\sync-git-to-svn.ps1
```

### 2. 预览模式
```powershell
# 查看将要执行的操作，不做实际更改
.\sync-git-to-svn.ps1 -DryRun
```

### 3. 只同步文件
```powershell
# 同步文件但不提交到 SVN 远程
.\sync-git-to-svn.ps1 -SkipSvnCommit
```

### 4. 组合使用
```powershell
# 预览只同步文件的操作
.\sync-git-to-svn.ps1 -DryRun -SkipSvnCommit
```

## 操作流程详解

### 阶段 1: 环境检查
```
✓ 检查 Git 命令是否可用
✓ 检查 SVN 命令是否可用  
✓ 验证 Git 镜像目录存在
✓ 验证 SVN 工作目录存在
```

### 阶段 2: Git 仓库更新
```
1. 获取当前分支名称
2. 执行 git fetch origin
3. 检查是否落后于远程分支
4. 处理未提交的更改（自动 stash）
5. 执行 git pull 更新代码
```

### 阶段 3: 文件同步
```
1. 读取排除文件配置
2. 使用 Robocopy 镜像同步
3. 应用文件和目录排除规则
4. 记录同步结果和统计信息
```

### 阶段 4: SVN 提交
```
1. 检查 SVN 工作目录状态
2. 自动添加新文件 (svn add)
3. 自动移除已删除文件 (svn remove)
4. 生成带时间戳的提交信息
5. 执行 svn commit 推送到远程
```

## 配置文件说明

### exclude-files.txt 格式
```text
# 注释行以 # 开头
# 文件排除模式
*.tmp
*.log
.DS_Store

# 目录排除模式（以 / 结尾）
node_modules/
.git/
.svn/
temp/

# 具体文件路径
config/local.conf
```

### 排除规则类型
- **文件模式**：`*.tmp`, `debug.log`
- **目录模式**：`node_modules/`, `.git/`
- **路径模式**：`config/local.conf`

## 日志系统

### 日志级别
| 级别 | 颜色 | 用途 |
|------|------|------|
| INFO | 白色 | 普通信息 |
| SUCCESS | 绿色 | 成功操作 |
| WARNING | 黄色 | 警告信息 |
| ERROR | 红色 | 错误信息 |

### 日志文件
- **位置**：`logs/sync_YYYYMMDD_HHMMSS.log`
- **编码**：UTF-8
- **内容**：完整的操作记录和错误详情

## 错误处理与故障排除

### 常见问题

#### 1. Git/SVN 命令不可用
```
错误：Git is not available or not in PATH
解决：确保 Git 和 SVN 已安装并添加到系统 PATH
```

#### 2. 目录结构不正确
```
错误：Git mirror directory not found
解决：检查目录结构，确保 repos/git-mirror 存在
```

#### 3. SVN 提交失败
```
错误：SVN commit failed
解决：检查 SVN 认证信息和网络连接
```

#### 4. Git 更新冲突
```
警告：Uncommitted changes detected
解决：脚本会自动 stash 未提交更改
```

### 故障排除步骤

1. **检查日志文件**
   ```powershell
   Get-Content "logs\sync_*.log" | Select-Object -Last 50
   ```

2. **手动验证环境**
   ```powershell
   git --version
   svn --version
   Test-Path "repos\git-mirror"
   Test-Path "repos\svn-working\trunk"
   ```

3. **使用预览模式调试**
   ```powershell
   .\sync-git-to-svn.ps1 -DryRun
   ```

## 最佳实践

### 🔧 **操作建议**

1. **首次运行使用预览模式**
   ```powershell
   .\sync-git-to-svn.ps1 -DryRun
   ```

2. **定期备份 SVN 工作目录**
   ```powershell
   Copy-Item "repos\svn-working" "backup\svn-working-$(Get-Date -Format 'yyyyMMdd')" -Recurse
   ```

3. **监控日志文件大小**
   ```powershell
   Get-ChildItem "logs\*.log" | Where-Object Length -gt 10MB | Remove-Item
   ```

### 📅 **自动化建议**

#### 使用 Windows 任务计划程序
```powershell
# 创建每日自动同步任务
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\path\to\sync-git-to-svn.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
Register-ScheduledTask -TaskName "GitToSvnSync" -Action $Action -Trigger $Trigger
```

#### 批处理脚本包装
```batch
@echo off
cd /d "C:\path\to\svn-bridge\scripts"
powershell.exe -ExecutionPolicy Bypass -File "sync-git-to-svn.ps1"
pause
```

## 高级配置

### 自定义 Robocopy 参数
脚本中的 Robocopy 参数：
- `/MIR`：镜像目录（删除目标中不存在于源的文件）
- `/R:3`：重试 3 次
- `/W:10`：等待 10 秒后重试
- `/NP`：不显示进度百分比
- `/L`：列表模式（干运行时使用）

### SVN 提交信息自定义
默认格式：`"Automated sync from Git at yyyy-MM-dd HH:mm:ss"`

可在脚本第 217 行修改：
```powershell
$commitMessage = "Custom sync message at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
```

## 安全考虑

### 🛡️ **安全措施**

1. **认证信息管理**
   - 使用 SVN 存储认证避免重复输入
   - 考虑使用环境变量存储敏感信息

2. **权限控制**
   - 确保脚本执行账户有适当的文件系统权限
   - SVN 仓库访问权限配置

3. **备份策略**
   - 定期备份 Git 和 SVN 仓库
   - 保留重要的同步日志文件

## 版本信息

- **脚本版本**：2.0 Enhanced
- **兼容性**：PowerShell 5.0+
- **依赖**：Git 2.0+, SVN 1.8+
- **操作系统**：Windows 10/11, Windows Server 2016+

## 技术支持

### 📞 **联系信息**
- **创建日期**：2025-08-18
- **维护团队**：DevOps Team
- **更新记录**：详见 Git 提交历史

### 🔗 **相关文档**
- [Git 官方文档](https://git-scm.com/docs)
- [SVN 官方文档](https://svnbook.red-bean.com/)
- [Robocopy 参考文档](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)

---

## 快速参考卡片

```
常用命令：
├── 完整同步：.\sync-git-to-svn.ps1
├── 预览模式：.\sync-git-to-svn.ps1 -DryRun
├── 只同步：  .\sync-git-to-svn.ps1 -SkipSvnCommit
└── 查看日志：Get-Content logs\sync_*.log | Select-Object -Last 20

目录检查：
├── Git镜像：Test-Path repos\git-mirror
├── SVN工作：Test-Path repos\svn-working\trunk
├── 配置文件：Test-Path config\exclude-files.txt
└── 日志目录：Test-Path logs

状态检查：
├── Git状态：git status (在 git-mirror 目录)
├── SVN状态：svn status (在 svn-working\trunk 目录)
└── 工具版本：git --version; svn --version
```

---

*此说明书基于 sync-git-to-svn.ps1 v2.0 编写，建议定期更新以保持与脚本功能同步。*
