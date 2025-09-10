# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="database-smartools",  # 包的名字（PyPI 上必须唯一，重名会传不上去）
    version="0.0.3",  # 版本号（格式：主版本.次版本.修订号，比如 0.0.1）
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
        "altgraph==0.17.4",
        "annotated-types==0.7.0",
        "backports.tarfile==1.2.0",
        "certifi==2025.8.3",
        "cffi==2.0.0",
        "charset-normalizer==3.4.3",
        "cryptography==45.0.7",
        "DBUtils==3.1.2",
        "dmPython==2.5.22",
        "docutils==0.22",
        "greenlet==3.2.4",
        "id==1.5.0",
        "idna==3.10",
        "importlib_metadata==8.7.0",
        "jaraco.classes==3.4.0",
        "jaraco.context==6.0.1",
        "jaraco.functools==4.3.0",
        "JayDeBeApi==1.2.3",
        "jpype1==1.5.2",
        "keyring==25.6.0",
        "markdown-it-py==4.0.0",
        "mdurl==0.1.2",
        "more-itertools==10.8.0",
        "mysql-connector-python==9.4.0",
        "nh3==0.3.0",
        "numpy==2.3.3",
        "oracledb==3.3.0",
        "packaging==25.0",
        "pandas==2.3.2",
        "pefile==2023.2.7",
        "psycopg2-binary==2.9.10",
        "pycparser==2.23",
        "pydantic==2.11.7",
        "pydantic_core==2.33.2",
        "Pygments==2.19.2",
        "pyinstaller==6.15.0",
        "pyinstaller-hooks-contrib==2025.8",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "pywin32-ctypes==0.2.3",
        "readme_renderer==44.0",
        "requests==2.32.5",
        "requests-toolbelt==1.0.0",
        "rfc3986==2.0.0",
        "rich==14.1.0",
        "six==1.17.0",
        "SQLAlchemy==2.0.43",
        "twine==6.2.0",
        "typing-inspection==0.4.1",
        "typing_extensions==4.15.0",
        "tzdata==2025.2",
        "urllib3==2.5.0",
        "zipp==3.23.0"
    ]
)

