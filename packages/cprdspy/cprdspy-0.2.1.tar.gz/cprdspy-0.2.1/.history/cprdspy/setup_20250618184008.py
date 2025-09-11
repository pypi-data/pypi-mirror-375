from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cprdspy",
    version="0.1.0",
    author="CPR Team",
    author_email="3962465714@qq.com",  # 请替换为实际的邮箱
    description="A Python library for creating and visualizing CPR (Circle Point Round) patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cprdspy",  # 请替换为实际的仓库URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "matplotlib>=3.3.0",
        "ipywidgets>=7.0.0",
        "notebook>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.9",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    include_package_data=True,
    package_data={
        "cprdspy": [
            "CPR_js/*.html",
            "CPR_js/*.js",
            "CPR_js/*/*.js",
            "CPR_matplotlib/image/*",
        ],
    },
)
