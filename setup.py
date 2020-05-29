from setuptools import setup, find_packages
import sys

# pip3 install -e .
# or
# [sudo] python3.8 setup.py develop
found_packages = find_packages(exclude=["tests?", "*.tests*", "*.tests*.*", "tests*.*", ])
ok = input(f'found_packages:\n{repr(found_packages)}\ncontinue? y/n ').lower() == 'y'
if not ok:
    sys.exit()
setup(name='IGit',
      version='1.0.3',
      description='Like IPython, for Git',
      author='Gilad Barnea',
      author_email='giladbrn@gmail.com',

      packages=found_packages,
      install_requires=['requests', 'click', 'fuzzysearch', 'prompt_toolkit'],
      tests_require=['pytest', 'hypothesis', 'birdseye', 'ipdb', 'IPython']
      )
