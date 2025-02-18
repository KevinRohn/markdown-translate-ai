from setuptools import setup, find_packages
from pathlib import Path

VERSION = "0.1.3"
NAME = "markdown-translate-ai"

INSTALL_REQUIRES = [
    "openai",
    "httpx",
    "marko",
    "httpx[http2]",
]

setup(
    name=NAME,
    version=VERSION,
    description="Python package to translate markdown files with multiple AI service providers.",
    url="https://github.com/KevinRohn/markdown-translate-ai",
    project_urls={
        "Source Code": "https://github.com/KevinRohn/markdown-translate-ai",
    },
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Kevin Rohn",
    author_email="kevin@rohn.tech",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "markdown-translate-ai=markdown_translate_ai.translator:main",
        ],
    },
)