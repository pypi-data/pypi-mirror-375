from setuptools import setup, find_packages

setup(
    name="torchregularize",
    version="0.1.0",
    description="Advanced regularization layers for PyTorch (DropBlock, Stochastic Depth, ShakeDrop).",
    author="Adie Kaushik",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/torchregularize",
    packages=find_packages(),
    install_requires=["torch>=1.10"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
