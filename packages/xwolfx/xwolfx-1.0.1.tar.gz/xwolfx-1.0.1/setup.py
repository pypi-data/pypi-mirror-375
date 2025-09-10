from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xwolfx",
    version="1.0.1", 
    author="Python Port of wolf.js",
    author_email="", 
    description="An unofficial Python API for WOLF (AKA Palringo)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xwolfx-python/xwolfx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websocket-client>=1.0.0",
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
        "python-socketio>=5.0.0",
        "aiohttp>=3.7.0",
    ],
)