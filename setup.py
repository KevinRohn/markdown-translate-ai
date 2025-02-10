from setuptools import setup, find_packages

setup(
    name="markdown-translate-ai",
    version="0.1.0",
    description="Python package to translate markdown files with multiple AI service providers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="KevinRohn",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "openai",
        "httpx",
        "marko",
        "httpx[http2]",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "markdown-translate-ai=markdown_translate_ai.translator:main",
        ],
    },
)