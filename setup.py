import os
import sys
from setuptools import setup, find_packages
from les.__version__ import __version__

long_description = """
"""

install_requires = ["click", "z3-solver"]

setup(name="les",
      version=__version__,
      description="Leaving Earth Solver",
      long_description=long_description,
      classifiers=[],
      keywords="",
      author="Benjamin Trigona-Harany",
      author_email="",
      url="",
      license="",
      packages=find_packages(exclude=["tests"]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          "console_scripts" : "les=les.scripts.cli:cli"
      }
)
