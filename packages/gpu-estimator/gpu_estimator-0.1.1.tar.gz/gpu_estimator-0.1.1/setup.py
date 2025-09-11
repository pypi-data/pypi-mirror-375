from setuptools import setup, find_packages

setup(
    name="gpu-estimator",
    version="0.1.1",
    author="Hemanth HM",
    author_email="hemanth.hm@gmail.com",
    description="A Python package for estimating GPU requirements for ML training",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "click>=8.0.0",
        "transformers>=4.30.0",
        "huggingface_hub>=0.16.0",
        "torch>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gpu-estimate=gpu_estimator.cli:cli",
        ],
    },
)