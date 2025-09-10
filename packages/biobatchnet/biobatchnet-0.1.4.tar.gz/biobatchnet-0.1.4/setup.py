from setuptools import setup, find_packages

setup(
    name="biobatchnet",
    version="0.1.1",
    author="Haochen Liu",
    author_email="haiping.liu.uom@gmail.com",
    description="Neural networks for batch effect correction in biological data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["BioBatchNet", "BioBatchNet.*"]),
    package_data={"BioBatchNet": ["config/**/*.yaml"]},
    include_package_data=True,
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.26.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.6.0",
        "scanpy>=1.10.0",
        "anndata>=0.10.0",
        "PyYAML>=6.0.0",
        "tqdm>=4.60.0",
        "wandb>=0.12.0",  # Added for trainer logging
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)