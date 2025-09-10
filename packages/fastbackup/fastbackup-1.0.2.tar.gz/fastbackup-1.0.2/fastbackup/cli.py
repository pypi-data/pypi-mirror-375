#!/usr/bin/env python3
"""命令行接口"""

import argparse
import os
from .core import FastBackup


def main():
    parser = argparse.ArgumentParser(description='FastBackup - 快速实验备份工具')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有备份')
    parser.add_argument('--restore', '-r', help='恢复指定备份')
    parser.add_argument('--project', '-p', help='项目路径（默认当前目录）')
    parser.add_argument('--version', '-v', action='store_true', help='显示版本信息')
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"FastBackup {__version__}")
        return
    
    if args.list:
        FastBackup.list_backups(args.project or os.getcwd())
    elif args.restore:
        FastBackup.restore_backup(args.restore, args.project or os.getcwd())
    else:
        print("FastBackup - 一行导入式实验备份工具")
        print("使用方法:")
        print("  在你的Python脚本开头添加: import fastbackup")
        print("  命令行查看备份: fastbackup --list")
        print("  恢复备份: fastbackup --restore backup_20240101_120000")


if __name__ == "__main__":
    main()