from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.1'
DESCRIPTION = 'Python lib for sending sensor data to Consentium IoT server.'
LONG_DESCRIPTION = (
    "A Python library that enables developers to send sensor data to the "
    "Consentium IoT server for monitoring and analysis."
)

# Setting up
setup(
    name="consentiumthings",
    version=VERSION,
    author="Consentium IoT",
    author_email="official@consentiumiot.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/ConsentiumIoT/consentiumthings-py",  # Add repo URL
    packages=find_packages(),
    install_requires=['requests'],  # Dependencies
    keywords=['Python', 'IoT', 'Internet of Things', 'Sensor Data', 'Consentium IoT'],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Update as needed
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Ensure Python version compatibility
)
