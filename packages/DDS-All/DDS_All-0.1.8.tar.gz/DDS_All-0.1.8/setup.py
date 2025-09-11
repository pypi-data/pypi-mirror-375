from setuptools import setup, find_packages

setup(
    name="DDS_All",  # 保持与包目录名一致
    version="0.1.8",  # 更新版本号
    packages=find_packages(),
    package_data={
        "DDS_All": ["*.pyd", "*.dll", "*.lib"],  # 关键修正：包名改为 DDS_All
    },
    include_package_data=True,  # 确保包含非Python文件
    python_requires=">=3.9, <3.13",
    description="为解决不同版本Python的兼容性问题，提供多版本的预编译二进制文件。",
    author="JackyJia",
)
