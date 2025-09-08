from setuptools import setup, find_packages

setup(
    name="itam_assistant",  # 包名称
    version="0.1.11",    # 版本号
    author="liujunmeiD",
    author_email="1105030421@qq.com",
    description="优化版本--技能分发的结果展示-新增时间控制 14s",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/liujunmeiD/itam_assistant",
    packages=find_packages(),  # 自动发现所有包
    install_requires=[         # 依赖项
        "requests>=2.25.1",
        "numpy>=1.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",   # Python版本要求
)