"""
FastBackup - 一行导入式实验备份工具

只需要在你的Python脚本开头添加:
    import fastbackup

就能自动为你的项目创建备份，再也不用担心忘记实验参数了！

功能特点:
- 🚀 一行导入自动备份
- 📁 智能检测项目根目录  
- 💾 只在文件变化时备份
- 🔍 完整的备份历史管理
- 🎯 零配置开箱即用
"""

from .core import FastBackup, backup, list_backups, restore

__version__ = "1.0.1"
__author__ = "chenziwen"
__email__ = "1304005976@qq.com"

# 导出主要功能
__all__ = ['FastBackup', 'backup', 'list_backups', 'restore']

# 当模块被导入时自动执行备份
try:
    backup()
except Exception as e:
    print(f"FastBackup初始化失败: {e}")