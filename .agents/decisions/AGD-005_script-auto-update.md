---
title: "Script Auto-Update Mechanism"
description: "Skill scripts can auto-update project scripts with opt-out config"
tags: skills/agent-centric
---

## Context

agent-centric skill 会在项目中创建 `.agents/scripts/` 目录存放脚本。当 skill 更新时，需要决定如何同步项目中的脚本。

## Decision

### 默认自动更新

脚本执行时检查 skill 目录的脚本版本，如果不同则自动更新项目中的脚本。

### Opt-out 配置

在 `.agents/config.json` 中配置禁用：

```json
{
  "disableAutoUpdateScripts": ["validate-agds.py"]
}
```

或禁用全部：

```json
{
  "disableAutoUpdateScripts": true
}
```

### 脚本顶部提示

每个脚本顶部包含注释：
```
DO NOT MODIFY THIS FILE - it will be automatically updated from the skill directory.
To disable auto-update, add this filename to disableAutoUpdateScripts in config.json.
```

## Consequences

**Benefits:**
- Skill 更新后项目自动获得最新脚本
- 用户可按需禁用特定脚本的更新
- 允许用户自定义脚本（禁用更新后）

**Trade-offs:**
- 用户可能不知道脚本被更新了
- 自定义修改会被覆盖（除非禁用）
