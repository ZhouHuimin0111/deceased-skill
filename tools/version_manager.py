#!/usr/bin/env python3
"""数字记忆档案版本存档与回滚管理器

Usage:
    python3 version_manager.py --action <backup|rollback|list> --slug <slug> --base-dir <path> [--version <v>]
"""

import argparse
import os
import sys
import shutil
import json
from datetime import datetime


def backup(base_dir: str, slug: str):
    """备份当前档案版本"""
    skill_dir = os.path.join(base_dir, slug)
    versions_dir = os.path.join(skill_dir, 'versions')
    meta_path = os.path.join(skill_dir, 'meta.json')
    
    if not os.path.exists(meta_path):
        print(f"系统错误：meta.json 配置文件不存在", file=sys.stderr)
        sys.exit(1)
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    current_version = meta.get('version', 'v0')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{current_version}_{timestamp}"
    backup_dir = os.path.join(versions_dir, backup_name)
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # 备份核心档案文件
    for fname in ['memory.md', 'persona.md', 'SKILL.md', 'meta.json']:
        src = os.path.join(skill_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_dir, fname))
    
    print(f"已成功备份记忆版本 {backup_name} 到 {backup_dir}")
    return backup_name


def rollback(base_dir: str, slug: str, version: str):
    """回滚到指定的历史记忆版本"""
    skill_dir = os.path.join(base_dir, slug)
    versions_dir = os.path.join(skill_dir, 'versions')
    
    # 查找匹配的版本
    target_dir = None
    if os.path.exists(versions_dir):
        for vname in os.listdir(versions_dir):
            if vname.startswith(version) or vname == version:
                target_dir = os.path.join(versions_dir, vname)
                break
    
    if not target_dir or not os.path.isdir(target_dir):
        print(f"错误：在本地找不到记忆版本 {version}", file=sys.stderr)
        list_versions(base_dir, slug)
        sys.exit(1)
    
    # 先备份当前版本，以防万一
    backup(base_dir, slug)
    
    # 恢复核心档案文件
    for fname in ['memory.md', 'persona.md', 'SKILL.md', 'meta.json']:
        src = os.path.join(target_dir, fname)
        dst = os.path.join(skill_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    
    print(f"档案已安全回滚到记忆版本 {version}")


def list_versions(base_dir: str, slug: str):
    """列出当前档案的所有历史版本"""
    versions_dir = os.path.join(base_dir, slug, 'versions')
    
    if not os.path.isdir(versions_dir):
        print("当前档案没有历史记忆版本。")
        return
    
    versions = sorted(os.listdir(versions_dir), reverse=True)
    if not versions:
        print("当前档案没有历史记忆版本。")
        return
    
    print(f"历史记忆版本（共 {len(versions)} 个）：\n")
    for v in versions:
        print(f"  {v}")


def main():
    parser = argparse.ArgumentParser(description='版本存档与回滚管理器')
    parser.add_argument('--action', required=True, choices=['backup', 'rollback', 'list'])
    parser.add_argument('--slug', required=True, help='数字档案专属代号 (ID)')
    # 修复了硬编码的默认路径
    parser.add_argument('--base-dir', default='./archives', help='档案本地存储基础目录')
    parser.add_argument('--version', help='回滚目标记忆版本号')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup(args.base_dir, args.slug)
    elif args.action == 'rollback':
        if not args.version:
            print("参数错误：执行 rollback 回滚指令需要提供 --version 目标版本号", file=sys.stderr)
            sys.exit(1)
        rollback(args.base_dir, args.slug, args.version)
    elif args.action == 'list':
        list_versions(args.base_dir, args.slug)


if __name__ == '__main__':
    main()