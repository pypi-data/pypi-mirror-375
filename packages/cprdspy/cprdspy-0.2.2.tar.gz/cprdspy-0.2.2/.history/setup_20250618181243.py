from setuptools import setup, find_packages

setup(
    name="cprdspy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib", "plotly", "dash"],
    author="lbylzk8",
    author_email="3962465714@qq.com",
    description="A short description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/your_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
