import os
import sys

from setuptools import find_packages, setup

__version__ = "2025.1.2"

# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

# 'setup.py test' shortcut.
# !pip install --index-url https://test.pypi.org/simple/ mplabml -U
if sys.argv[-1] == "test":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
    sys.exit()

setup(
    name="mplabml",
    description="MPLABML Python SDK",
    version=__version__,
    author="Microchip",
    author_email="nicholas.copeland@microchip.com",
    license="Proprietary",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*test*", "*widgets*"]),
    package_data={
        "mplabml.datasets": ["*.csv"],
        "mplabml.widgets": ["*.pem"],
        "mplabml.image": ["*.png"],
    },
    include_package_data=True,
    long_description=open("README.md").read(),
    install_requires=[
        "cookiejar==0.0.2",
        "requests>=2.14.2",
        "requests-oauthlib>=0.7.0",
        "appdirs",
        "semantic_version>=2.6.0",
        "numpy",
        "pandas",
        "matplotlib",
        "prompt-toolkit",
        "seaborn",
        "wurlitzer",
        "tabulate",
        "scipy",
    ],
)
