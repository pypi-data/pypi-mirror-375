"""
Setup script para el paquete lambda_manager.
"""

from setuptools import setup, find_packages
import os

# Leer el README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Lambda Manager - Herramienta para administrar AWS Lambda y EventBridge"

# Leer requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['boto3>=1.26.0', 'botocore>=1.29.0']

setup(
    name="aws-lambda-manager",
    version="1.0.0",
    author="Edwin Caicedo Venté",
    author_email="ecaicedo@rapicredit.com",
    description="Herramienta simple y directa para administrar AWS Lambda y EventBridge desde Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/lambda-manager/",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Testing",
        "Environment :: Console",
        "Natural Language :: Spanish",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="aws lambda eventbridge boto3 automation serverless cloud management",
    project_urls={
        "Homepage": "https://pypi.org/project/lambda-manager/",
        "Documentation": "https://pypi.org/project/lambda-manager/",
    },
    include_package_data=True,
    zip_safe=False,
)
