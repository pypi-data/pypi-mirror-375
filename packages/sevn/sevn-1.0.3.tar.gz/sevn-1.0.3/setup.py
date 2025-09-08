"""
Setup configuration for sevn - the secure environment variable manager.
"""

from setuptools import setup, find_packages

setup(
    name="sevn",
    version="1.0.3",
    description="A secure environment variable manager",
    author="Tim Hoerner",
    author_email="thoerner@gmail.com",
    url="https://github.com/thoerner/sevn",
    project_urls={
        "Bug Reports": "https://github.com/thoerner/sevn/issues",
        "Source": "https://github.com/thoerner/sevn",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "cryptography>=41.0.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sevn=sevn:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development",
    ],
    python_requires=">=3.9",
) 