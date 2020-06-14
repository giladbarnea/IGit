from setuptools import setup, find_packages
import sys
from pathlib import Path
import os

# pip3 install -e .
# or
# [sudo] python3.8 setup.py develop
print('\n', os.getcwd(), '\n', sys.argv, '\n')
should_prompt = True
for arg in sys.argv:
    # when installing from any other dir, first arg isn't 'setup.py' but a longer (absolute) path
    if 'pip' in arg or ('setup.py' in arg and len(Path(arg).parts) > 1):
        should_prompt = False
        break
print(f'should_prompt: {should_prompt}')
found_packages = find_packages(exclude=["tests?", "*.tests*", "*.tests*.*", "tests*.*", ])
if should_prompt:
    ok = input(f'found_packages:\n{repr(found_packages)}\ncontinue? y/n ').lower() == 'y'
    if not ok:
        sys.exit()

# protocol      domain              repo                    extra
# ---------
# https         github.com          more_termcolor         /tarball/master
# git+https     git@github.com      more_termcolor.git     /archive/1.0.0.tar.gz
# git+ssh                                                   @tag


# /tarball/master
# ---------------
# https         github.com          more_termcolor      fail
# git+https     github.com          more_termcolor      fail
# git+ssh       github.com          more_termcolor      fail
# https         github.com          more_termcolor.git  fail
# git+ssh       github.com          more_termcolor.git  fail
# git+https     github.com          more_termcolor.git  fail
# https         git@github.com      more_termcolor.git  fail
# git+ssh       git@github.com      more_termcolor.git  fail
# git+https     git@github.com      more_termcolor.git  fail
# https         git@github.com      more_termcolor
# git+ssh       git@github.com      more_termcolor
# git+https     git@github.com      more_termcolor

# /archive/1.0.0.tar.gz
# ---------------------
# https         github.com          more_termcolor      fail
# git+https     github.com          more_termcolor      fail
# git+ssh       github.com          more_termcolor      fail
# https         github.com          more_termcolor.git  fail
# git+ssh       github.com          more_termcolor.git  fail
# git+https     github.com          more_termcolor.git  fail
# https         git@github.com      more_termcolor.git
# git+ssh       git@github.com      more_termcolor.git
# git+https     git@github.com      more_termcolor.git
# https         git@github.com      more_termcolor
# git+ssh       git@github.com      more_termcolor
# git+https     git@github.com      more_termcolor


# dependency_links = ["git+https://github.com/giladbarnea/more_termcolor.git#egg=more_termcolor-1.0.0"]
# dependency_links = ["git+https://git@github.com/giladbarnea/more_termcolor.git#egg=more_termcolor-1.0.0"]
# dependency_links = ["git+https://github.com/giladbarnea/more_termcolor.git@ae4929ce8153759ca12f22ce35c6ac1a8e4f3a24#egg=more_termcolor-1.0.0"]
# dependency_links = ["git+https://github.com/giladbarnea/more_termcolor/archive/1.0.0.tar.gz#egg=more_termcolor-1.0.0"]

# tarball:
# dependency_links = ['https://git@github.com/giladbarnea/more_termcolor.git/archive/1.0.0.tar.gz#egg=more_termcolor-1.0.0']
# print(f'dependency_links: ', '\n', "\n\t".join(dependency_links))
setup(name='IGit',
      version='1.0.3',
      description='Like IPython, for Git',
      author='Gilad Barnea',
      author_email='giladbrn@gmail.com',

      # dependency_links=dependency_links,
      packages=found_packages,
      install_requires=[
          # 'more_termcolor @ https://github.com/giladbarnea/more_termcolor/archive/master.zip#egg=more_termcolor-1.0.0',
          'more_termcolor',
          'requests',
          'click',
          'fuzzysearch',
          'prompt_toolkit',
          'traitlets',
          'igit_debug'],
      tests_require=['pytest', 'hypothesis', 'birdseye', 'ipdb', 'IPython', 'logbook'],
      classifiers=[
          # https://pypi.org/classifiers/
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          "License :: OSI Approved :: MIT License",
          'Operating System :: OS Independent',
          "Programming Language :: Python :: 3 :: Only",
          'Topic :: Software Development :: Version Control :: Git',
          ]
      )
