from setuptools import setup, find_packages

setup(
    name="pyupstool",  # đổi tên gói
    version="1.0.0",
    description="Python update & PyPI upload tool for Termux",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Trọng Phúc",
    author_email="phuctrongytb16@gmail.com",
    url="https://github.com/phuctrong1tuv/pyupstool",
    packages=find_packages(include=["pyupstool", "pyupstool.*"]),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "twine",
        "setuptools",
        "wheel"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "pyup=pyupstool.cli:main",  # đổi lệnh CLI
        ],
    },
    keywords="termux update python package pypi aistv",
)