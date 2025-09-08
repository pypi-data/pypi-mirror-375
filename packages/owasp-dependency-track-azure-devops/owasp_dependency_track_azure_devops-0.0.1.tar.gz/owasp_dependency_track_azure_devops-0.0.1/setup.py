from pathlib import Path

from setuptools import setup, find_packages
import os

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = os.environ.get("PACKAGE_VERSION", "0.0.1")

def read_requirements(filename):
    with open(filename) as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]


setup(
    name="owasp-dependency-track-azure-devops",
    description="OWASP Dependency Track to Azure DevOps sync",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://github.com/mreiche/owasp-dependency-track-azure-devops",
    author="Mike Reiche",
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'owasp-dtrack-azure-devops = owasp_dt_sync.cli:run',
        ],
    },
)
