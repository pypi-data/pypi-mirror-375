from setuptools import setup, find_packages

setup(
    name="DDS_All",  # 保持与包目录名一致
    version="0.1.3",  # 更新版本号
    packages=find_packages(),
    package_data={
        "DDS_All": ["*.pyd", "*.dll"],  # 关键修正：包名改为 DDS_All
    },
    include_package_data=True,  # 确保包含非Python文件
    description="修复.pyd文件打包问题",
    author="JackyJia",
)
