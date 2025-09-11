# -*- coding: utf-8 -*-

import setuptools

from lesscode import version

# 读取版本信息（如果项目中有版本定义文件）

install_requires = []
with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

# with open("/Users/chao.yy/PycharmProjects/lesscode-fastapi/requirements.txt", "r") as requirements:
with open("requirements.txt", "r") as requirements:
    for line in requirements:
        # 去除首尾空白
        line = line.strip()
        # 跳过空行和注释行
        if line and not line.startswith("#"):
            # 移除行内注释部分
            line = line.split("#", 1)[0].strip()
            if line:
                install_requires.append(line)
setuptools.setup(
    name="lesscode-fastapi",
    version=version,  # 根据实际版本号调整
    author="Chao.yy",
    author_email="yuyc@shangqi.com.cn",
    description="lesscode-fastapi 是基于FastAPI的web开发脚手架项目，该项目初衷为简化开发过程，让研发人员更加关注业务。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lesscode-fastapi",  # 根据实际情况调整
    packages=setuptools.find_packages(exclude=["tests*", "docs"]),
    classifiers=[
        # "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        # "Framework :: FastAPI",
        # "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires='>=3.9',
    platforms='any',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            # 如果有命令行工具，可以在这里定义
            'lesscode=lesscode.server:main',
        ],
    },
)
