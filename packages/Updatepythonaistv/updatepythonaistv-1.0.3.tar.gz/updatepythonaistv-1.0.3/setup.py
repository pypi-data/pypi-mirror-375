from setuptools import setup, find_packages
setup(
    name="Updatepythonaistv",
    version="1.0.3",
    description="Library auto update & upload Python packages on Termux",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Trọng Phúc",
    author_email="phuctrongytb16@gmail.com",
    url="https://github.com/phuctrong1tuv/Updatepythonaistv",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "twine",
        "setuptools",
        "wheel",
        "build",
        "rust"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "updateaistv=Updatepythonaistv.cli:main",
        ],
    },
    keywords="termux update python package pypi aistv",
)