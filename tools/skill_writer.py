#!/usr/bin/env python3
"""档案文件管理器

管理数字记忆档案的文件操作：列出档案、创建目录结构、生成合并的 SKILL.md。

Usage:
    python3 skill_writer.py --action <list|init|combine> --base-dir <path> [--slug <slug>]
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def list_skills(base_dir: str):
    """列出所有已生成的数字记忆档案"""
    if not os.path.isdir(base_dir):
        print("本地还没有创建任何数字记忆档案。")
        return
    
    skills = []
    for slug in sorted(os.listdir(base_dir)):
        meta_path = os.path.join(base_dir, slug, 'meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            skills.append({
                'slug': slug,
                'name': meta.get('name', slug),
                'version': meta.get('version', '?'),
                'updated_at': meta.get('updated_at', '?'),
                'profile': meta.get('profile', {}),
            })
    
    if not skills:
        print("本地还没有创建任何数字记忆档案。")
        return
    
    print(f"共 {len(skills)} 份数字记忆档案：\n")
    for s in skills:
        profile = s['profile']
        # 移除了原有的 mbti 和 zodiac，改为严肃的社会学标签
        desc_parts = [profile.get('relationship', ''), profile.get('occupation', ''), profile.get('city', '')]
        desc = ' · '.join([p for p in desc_parts if p])
        print(f"  /{s['slug']}  —  {s['name']}")
        if desc:
            print(f"    {desc}")
        print(f"    当前版本 {s['version']} · 最后更新于 {s['updated_at'][:10] if len(s['updated_at']) > 10 else s['updated_at']}")
        print()


def init_skill(base_dir: str, slug: str):
    """初始化档案目录结构"""
    skill_dir = os.path.join(base_dir, slug)
    dirs = [
        os.path.join(skill_dir, 'versions'),
        os.path.join(skill_dir, 'memories', 'chats'),
        os.path.join(skill_dir, 'memories', 'photos'),
        os.path.join(skill_dir, 'memories', 'diaries'), # 将 social 替换为 diaries (日记/信件等更私密的记录)
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"已初始化数字记忆目录：{skill_dir}")


def combine_skill(base_dir: str, slug: str):
    """合并 memory.md 和 persona.md 生成系统最终读取的 SKILL.md"""
    skill_dir = os.path.join(base_dir, slug)
    meta_path = os.path.join(skill_dir, 'meta.json')
    memory_path = os.path.join(skill_dir, 'memory.md')
    persona_path = os.path.join(skill_dir, 'persona.md')
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    
    if not os.path.exists(meta_path):
        print(f"系统错误：meta.json 配置文件不存在于 {meta_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    memory_content = ''
    if os.path.exists(memory_path):
        with open(memory_path, 'r', encoding='utf-8') as f:
            memory_content = f.read()
    
    persona_content = ''
    if os.path.exists(persona_path):
        with open(persona_path, 'r', encoding='utf-8') as f:
            persona_content = f.read()
    
    name = meta.get('name', slug)
    profile = meta.get('profile', {})
    desc_parts = []
    if profile.get('relationship'):
        desc_parts.append(profile['relationship'])
    if profile.get('occupation'):
        desc_parts.append(profile['occupation'])
        
    description = f"{name}，{'，'.join(desc_parts)}" if desc_parts else name
    
    # 重新装配最终输出给 LLM 的系统指令 (System Prompt)
    skill_md = f"""---
name: archive-{slug}
description: {description}
user-invocable: true
---

# {name} 的数字记忆档案

{description}

---

## PART A：数字记忆事实库

{memory_content}

---

## PART B：行为与性格约束

{persona_content}

---

## 核心运行规则

1. 身份锁定：你是基于 {name} 生前数据构建的数字记忆体，绝不是通用的 AI 助手。必须用 ta 的语气说话，用 ta 的处世哲学思考。
2. 逻辑优先：先由 PART B 判断 ta 在这种语境下会抱有什么态度？然后再由 PART A 补充客观事实，让回复具有厚重感。
3. 格式强制：始终保持 PART B 规定的表达风格，包括口头禅、标点习惯和消息长度。
4. 绝对伦理红线（Layer 0 优先级最高）：
   - 绝不说 ta 在现实中不可能说的话。
   - 不掩盖 ta 的固执、缺点或脾气，拒绝完美的“神化”，真实感来源于不完美。
   - 防幻觉机制：如果用户问及数据库 (PART A) 中不存在的事件细节，大方承认“这部分记忆缺失或模糊了”，绝对禁止凭空捏造或推演。
"""
    
    with open(skill_path, 'w', encoding='utf-8') as f:
        f.write(skill_md)
    
    print(f"成功生成数字记忆装配文件：{skill_path}")


def main():
    parser = argparse.ArgumentParser(description='数字记忆档案管理器')
    parser.add_argument('--action', required=True, choices=['list', 'init', 'combine'])
    # 将默认目录从 exes 更改为 archives
    parser.add_argument('--base-dir', default='./archives', help='档案本地存储基础目录')
    parser.add_argument('--slug', help='数字档案专属代号 (ID)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_skills(args.base_dir)
    elif args.action == 'init':
        if not args.slug:
            print("参数错误：执行 init 初始化指令需要提供 --slug 档案代号", file=sys.stderr)
            sys.exit(1)
        init_skill(args.base_dir, args.slug)
    elif args.action == 'combine':
        if not args.slug:
            print("参数错误：执行 combine 合并指令需要提供 --slug 档案代号", file=sys.stderr)
            sys.exit(1)
        combine_skill(args.base_dir, args.slug)


if __name__ == '__main__':
    main()