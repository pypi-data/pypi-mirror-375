from setuptools import setup, find_packages

setup(
    name="vlhmath",  # Package name on PyPI
    version="1.0.0",
    author="Aleksandar Ovcharov",
    author_email="",  # you said "without"
    description="Useful math library",
    long_description="Useful math library for equations and trigonometry.",
    long_description_content_type="text/markdown",
    url="",  # Optional, can be GitHub repo later
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "sympy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
