from setuptools import setup, find_packages

setup(
    name="java-coder",  # 包名称
    version="0.0.5",  # 版本号
    author="chonmb",  # 作者
    author_email="weichonmb@foxmail.com",  # 作者邮箱
    description="A java class file operate tools",  # 简要描述
    packages=find_packages(),  # 自动查找包含 __init__.py 的包
    install_requires=open("requirements.txt", encoding='utf-8').read().strip('\n').split('\n'),  # 指定依赖包,
    python_requires=">=3.6",  # 指定支持的 Python 版本
    long_description=open("README.MD", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chonmb/javacoder",
    license="MIT",
    include_package_data=True
)
