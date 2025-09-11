from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="banana-nft-sdk",
    version="2.0.0",
    author="BananaNFT Team",
    author_email="hello@banana-nft.ai",
    description="🍌 Revolutionary AI-powered NFT SDK with nano-banana multimodal intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/banana-nft/sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pillow>=8.0.0",
        "pydantic>=1.8.0",
        "tqdm>=4.60.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "banana-nft=banana_nft.cli:main",
        ],
    },
    keywords="nft, ai, art, blockchain, collection, generator, banana, nano-banana, multimodal",
    project_urls={
        "Bug Reports": "https://github.com/banana-nft/sdk/issues",
        "Source": "https://github.com/banana-nft/sdk",
        "Documentation": "https://banana-nft.ai/docs",
    },
)