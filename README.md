Wiggle
======

An image editor.

Quick Start
-----------

```sh
git clone https://github.com/tnterdan/wiggle.git
cd wiggle

# Set up your virtualenv if you wish
#
#   pyenv install 3.6.1
#   pyenv virtualenv 3.6.1 wiggle
#   pyenv local wiggle
#   echo '.python-version' >> .git/info/exclude

# Or otherwise, make sure you're using a recent version of Python

pip install -r requirements.txt

python .
```

Contributing
------------

Before contributing a change, please run the following checks:

```sh
# The first time, install the flake8 git commit hook. Only needs to be done
# once.
flake8 --install-hook=git

# The above will automatically run the linter whenever you commit, but it's a
# good habit to just run it across the whole project occasionally.
flake8

# There are no automated tests yet. Once they are set up, instructions will be
# added on how to run them.
```
