from setuptools import setup, find_packages

setup(
    name="langchain-moxe",
    version="0.1.2",
    author="Fourlabs UN2",
    author_email="fourlabs-un2@foursys.com.br",
    description="Integração da Moxe com LangChain para chat models, LLMs e embeddings.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="langchain moxe ai nlp chat llm embeddings",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "langchain-core>=0.2.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black",
            "flake8",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
