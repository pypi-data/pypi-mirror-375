from setuptools import setup, find_packages
import os 

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="alb-listener-rule",
    version="0.1.0",
    author="David Foley",
    description="Reusable CDK construct to add ALB listener rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
        install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
)