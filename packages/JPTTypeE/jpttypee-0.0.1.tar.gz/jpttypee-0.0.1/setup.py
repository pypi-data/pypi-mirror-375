from setuptools import setup, find_packages

setup(
    name="JPTTypeE",
    version="0.0.1",
    description="Python driver for JPT TypeE laser",
    author="cjdaic",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.5"
    ],
    entry_points={
        "console_scripts": [
            "jpt-typee-tester=JPTypeE.tester:main",
        ],
    },
    python_requires=">=3.7",
)