import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent


def get_long_description():
    with open(HERE / "README.md", encoding="utf-8") as f:
        return f.read()


setup(
    name="cprdspy",
    version="0.1.1",  # 版本号递增
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
    ],
    python_requires=">=3.8",
    author="lbylzk8",
    author_email="3962465714@qq.com",
    description="Circle Point Round Dot Surface Python Package",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/lbylzk8/cprdspy",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0"],
        "test": ["pytest-cov>=3.0"],
    },
)
