from setuptools import setup, find_packages

setup(
    name="DDS_All",
    version="0.1.2",
    packages=find_packages(),
    package_data={
        "my_package": ["*.pyd"],  # 包含 pyd 文件
    },
    description="新增__init__.py文件",
    author="JackyJia",
    install_requires=[],  # 依赖项（可选）
)