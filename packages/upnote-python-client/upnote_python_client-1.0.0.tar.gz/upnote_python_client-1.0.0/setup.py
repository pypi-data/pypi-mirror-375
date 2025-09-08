"""
UpNote Python 클라이언트 설치 스크립트
"""

from setuptools import setup, find_packages
import os

# 현재 디렉토리 경로
here = os.path.abspath(os.path.dirname(__file__))

# README.md 읽기
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

# requirements.txt 읽기 (없으면 빈 리스트)
requirements = []
requirements_path = os.path.join(here, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="upnote-python-client",
    version="1.0.0",
    author="UpNote Python Client Team",
    author_email="upnote.python.client@gmail.com",
    description="A Python client for UpNote using URL schemes to create and manage notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upnote-python/upnote-python-client",
    project_urls={
        "Bug Reports": "https://github.com/upnote-python/upnote-python-client/issues",
        "Source": "https://github.com/upnote-python/upnote-python-client",
        "Documentation": "https://github.com/upnote-python/upnote-python-client/blob/main/docs/API_REFERENCE.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="upnote, notes, markdown, productivity, url-scheme, x-callback-url",
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "twine>=3.0",
            "wheel>=0.36",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    package_data={
        "upnote_python_client": ["*.md"],
    },
)