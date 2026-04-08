# 回声.skill (Echo.skill) 安装指南

本项目作为 Claude Code 的本地 Meta-Skill 运行。

## 前置要求
1. 已安装 Node.js 18+ (Node.js 是一种 JavaScript 运行环境)
2. 已全局安装 `@anthropic-ai/claude-code`

## 安装步骤

在终端进入你希望存放数字记忆档案的任意本地项目目录，执行以下命令：

```bash
# 在 git 仓库根目录执行，将本项目克隆到本地技能库
mkdir -p .claude/skills
git clone https://github.com/ZhouHuimin0111/deceased-skill .claude/skills/deceased-skill
```

安装完成后，在终端启动 `claude` 命令，输入 `/create-archive` 即可开始构建你的第一份回声档案。