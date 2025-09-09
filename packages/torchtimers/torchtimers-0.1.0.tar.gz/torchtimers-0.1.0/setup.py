from setuptools import setup, find_packages

setup(
    name="torchtimers",
    version="0.1.0",
    description="Lightweight timing utilities for PyTorch training and inference (CPU & GPU).",
    author="Naga Adithya Kaushik (GenAIDevTOProd)",
    author_email="adithyakaushikch@gmail.com",
    url="https://huggingface.co/GenAIDevTOProd",
    packages=find_packages(),
    install_requires=["torch>=1.10"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
