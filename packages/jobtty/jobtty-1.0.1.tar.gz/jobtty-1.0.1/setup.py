from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jobtty",
    version="1.0.1",
    author="Croscom Software",
    author_email="konrad@croscomsoftware.com",
    description="🚀 Terminal Job Board - Find your next role from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/croscomsoftware/jobtty",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "requests>=2.28.0",
        "stripe>=5.0.0",
        "keyring>=23.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "qrcode[pil]>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jobtty=jobtty.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)