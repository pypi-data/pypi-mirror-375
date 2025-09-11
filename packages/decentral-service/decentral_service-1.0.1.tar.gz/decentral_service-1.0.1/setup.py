"""
Setup script for DecentralService
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dependencies are now defined in pyproject.toml
requirements = [
    "flask>=3.1.2",
    "flask-cors>=6.0.1", 
    "psutil>=7.0.0",
    "requests>=2.31.0",
]

setup(
    name="decentral-service",
    version="1.0.0",
    author="DecentralService Team",
    author_email="team@decentralservice.com",
    description="A Redis-like edge microservice for multi-threaded task processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/decentral-service",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "decentral-service=decentral_service.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
