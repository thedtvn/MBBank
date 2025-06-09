import re
from setuptools import setup

with open("requirements.txt", "r") as f:
    req = f.read().splitlines()

with open("README.MD", "r") as f:
    ldr = f.read()

with open('mbbank/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name='mbbank-lib',
    version=version,
    license="MIT",
    description='A unofficially light weight Python Api for the "Military Commercial Joint Stock Bank" personal accounts',
    long_description=ldr,
    long_description_content_type="text/markdown",
    url='https://github.com/thedtvn/MBBank',
    author='The DT',
    packages=["mbbank", "mbbank.wasm_helper"],
    install_requires=req,
    include_package_data=True
)
