# -*- coding: utf-8 -*-
"""
@项目名称 : yhfin-data-agent
@文件名称 : setup.py
@创建人   : zhongbinjie
@创建时间 : 2025/9/9 16:30
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""
from setuptools import setup, find_packages

setup(
    name="database-smartools",  # 包的名字（PyPI 上必须唯一，重名会传不上去）
    version="0.0.1",  # 版本号（格式：主版本.次版本.修订号，比如 0.0.1）
    author="joelz",
    author_email="zhongbj_26210@163.com",
    description="数据库操作工具包",
    long_description=open("README.md", encoding="utf-8").read(),  # 从 README 读取详细描述
    long_description_content_type="text/markdown",  # 说明 README 是 Markdown 格式
    url="",
    packages=find_packages(),  # 自动找到所有包
    classifiers=[  # 分类标签（帮助别人在 PyPI 上搜到你的包）
    ],
    python_requires=">=3.11",  # 支持的 Python 版本
    install_requires=[  # 你的包依赖的其他包（比如需要 requests 就写进去）
        "altgraph == 0.17.4",
        "annotated-types == 0.7.0",
        "anyio == 4.9.0",
        "click == 8.1.8",
        "colorama == 0.4.6",
        "oracledb == 3.0.0",
        "DBUtils == 3.0.0",
        "dmPython == 2.5.8",
        "fastapi == 0.115.12",
        "greenlet == 3.2.1",
        "h11 == 0.16.0",
        "idna == 3.10",
        "mysql-connector-python == 8.4.0",
        "numpy == 2.0.0",
        "packaging == 25.0",
        "pandas == 2.2.3",
        "pefile == 2023.2.7",
        "psycopg2-binary == 2.9.8",
        "pydantic == 2.11.3",
        "pydantic_core == 2.33.1",
        "pyinstaller == 6.14.0",
        "pyinstaller-hooks-contrib == 2025.4",
        "python-dateutil == 2.9.0.post0",
        "pytz == 2025.2",
        "pywin32-ctypes == 0.2.3",
        "six== 1.17.0",
        "sniffio == 1.3.1",
        "SQLAlchemy == 2.0.40",
        "starlette == 0.46.2",
        "typing-inspection == 0.4.0",
        "typing_extensions == 4.13.2",
        "tzdata == 2025.2",
        "uvicorn == 0.34.2",
        "JayDeBeApi == 1.2.3",
        "jpype1 >= 1.5.2"
    ]
)

