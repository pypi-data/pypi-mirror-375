from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='abstract_security',
    version='0.64',
    author='putkoff',
    author_email="partners@abstractendeavors.com",
    description='The `abstract_security` module is a Python utility that provides functionality for managing environment variables and securely loading sensitive information from `.env` files. It is designed to simplify the process of accessing and managing environment variables within your Python applications.',

    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/AbstractEndeavors/abstract_security',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "abstract_solcatcher": ["database_calls/*.json"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
    ],
    install_requires=[
        "abstract_utilities",
        "python-dotenv",
    ],
    extras_require={
        "dev": ["pytest", "flake8", "mypy"],
    },
    python_requires=">=3.6",
    license="MIT",
    license_files=("LICENSE",),
    setup_requires=["wheel"],
)
