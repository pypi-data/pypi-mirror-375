from setuptools import setup, find_packages

setup(
    name="DDS_All",
    version="0.1.1",
    packages=find_packages(),
    package_data={
        "my_package": ["*.pyd"],  # 包含 pyd 文件
    },
    description="Your package description",
    author="JackyJia",
    install_requires=[],  # 依赖项（可选）
)