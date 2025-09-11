from setuptools import setup, find_packages

setup(
    name="datapress-client",
    version="2.0.0",
    description="Deprecated package. Use 'datapress' instead.",
    long_description="This package has been deprecated. Please use 'datapress' directly. This package is now just a compatibility wrapper that re-exports everything from 'datapress'.",
    long_description_content_type="text/plain",
    packages=find_packages(),
    install_requires=[
        "datapress",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)