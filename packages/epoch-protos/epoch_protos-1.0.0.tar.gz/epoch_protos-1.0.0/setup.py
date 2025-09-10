import os
from setuptools import setup, find_packages

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Protocol Buffer definitions for EpochFolio models"

setup(
    name="epoch-protos",
    version="1.0.0",
    description="Protocol Buffer definitions for EpochFolio models, generating C++, TypeScript, and Python code",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="EpochLab",
    author_email="dev@epochlab.ai",
    url="https://github.com/epochlab/epoch-protos",
    project_urls={
        "Bug Reports": "https://github.com/epochlab/epoch-protos/issues",
        "Source": "https://github.com/epochlab/epoch-protos",
        "Documentation": "https://github.com/epochlab/epoch-protos#readme",
    },
    packages=find_packages(),
    install_requires=[
        "protobuf>=3.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
        "pydantic": [
            "pydantic>=2.0.0",
            "typing-extensions>=4.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Code Generators",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "": ["*.proto", "*.py", "*.pyi"],
    },
    keywords="protobuf, protocol-buffers, epochfolio, financial, portfolio, analytics, grpc",
    zip_safe=False,
)
