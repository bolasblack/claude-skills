# Skill 开发与导入指南

本文档总结了导入或创建 Claude Code Skill 的完整流程。

## 目录结构

```
claude-skills/
├── .claude/
│   └── agents/           # 项目级 subagent（可选）
├── CLAUDE.md             # 项目说明
├── CONTRIBUTING.md       # 本指南
└── <skill-name>/         # 每个 skill 一个目录
    ├── SKILL.md          # Skill 文档和使用说明（必须）
    └── ...               # 其他必要文件
```

---

## 一、从其他地方导入 Skill

### 1. 安全检查（重要！）

导入前必须检查源文件是否包含：
- 不可见字符（零宽字符等）
- Prompt injection 风险
- 恶意代码

### 2. 筛选必要文件

只保留 skill 运行必需的文件，删除：
- Plugin 元信息目录（如 `.claude-plugin/`）
- LICENSE、README.md、CONTRIBUTING.md 等
- 测试文件、CI 配置等

**通常需要保留：**
- `SKILL.md` - Skill 文档（必须）
- 核心代码文件
- `package.json`（如果有依赖）

### 3. 根据需求修改

常见修改：
- 包管理器偏好（npm/bun/pnpm）
- 依赖安装策略（自动/手动）
- 默认配置调整

---

## 二、代码审查

### 使用 Subagent 审查

```
让 @agent-code-reviewer , @agent-security-auditor , @agent-prompt-injection-auditor 来 review 一下 @<skill-dir>/ 里的代码
```

### 区分问题优先级

| 类型 | 处理方式 |
|------|---------|
| 真正的 bug | 必须修复 |
| 设计决策 | 评估后决定是否接受 |
| 过度设计建议 | 通常忽略 |

**常见"过度设计"：**
- 完整的 package.json 元信息（skill 不是 npm 包）
- TypeScript 重写
- 完整测试套件
- 复杂的日志系统
- 沙箱环境

---

## 三、修复问题

---

## 四、测试 Skill

### 1. 基本功能测试

直接运行 skill 的核心功能，确保：
- 依赖能正确安装
- 主要功能正常工作
- 错误处理正确

### 2. 模拟实际使用

假装你是用户，给 Claude 一个任务，让它使用这个 skill：

```
帮我测试一下 example.com 在手机和桌面端的显示效果
```

观察：
- Claude 是否理解 SKILL.md 的用法
- 执行流程是否正确
- 输出是否符合预期

