from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastbackup",
    version="1.0.1",
    author="chenziwen",
    author_email="1304005976@qq.com",
    description="一行导入式Python项目实验备份工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chenziwenhaoshuai/fastbackup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Backup",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "fastbackup=fastbackup.cli:main",
        ],
    },
    keywords="backup experiment version-control development",
    project_urls={
        "Bug Reports": "https://github.com/chenziwenhaoshuai/fastbackup/issues",
        "Source": "https://github.com/chenziwenhaoshuai/fastbackup/",
    },
)