---
title: "Skill Documentation Structure"
description: "Split skill docs into SKILL.md (workflow) + references/ (technical details)"
tags: skills/agent-centric
---

## Context

agent-centric skill 的文档最初是单个 SKILL.md 文件（223 行）。需要决定是否拆分以及如何组织。

## Decision

拆分为：

```
skills/agent-centric/
├── SKILL.md           # 核心工作流 (~100 行)
└── references/
    ├── agd.md         # AGD 字段、语义
    ├── config.md      # config.json 配置
    └── index.md       # 索引文件格式
```

### 拆分原则

- **SKILL.md**: When to Use, Setup, 基本用法
- **references/**: 技术细节、完整字段表、配置选项

## Consequences

**Benefits:**
- Progressive Disclosure：Claude 首次加载只需 SKILL.md
- 按需加载技术细节，节省 context
- 每个 reference 文件职责单一

**Trade-offs:**
- 文件数量增加
- 需要维护多个文件的一致性
