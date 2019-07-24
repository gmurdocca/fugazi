SRC_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
.SILENT:

help:
	echo "  env		create/activate a development environment using virtualenv"
	echo "  deps	update any dependencies if their version was changed"
	echo "  clean	clean this repo of superfluous files"

env:
	which virtualenv >/dev/null || (echo "Please install virtualenv (`pip install virtualenv`)" && exit 1)

	# create the virtualenv if it doesn't already exist
	test -d .env || virtualenv -p python3 .env >&2
	. .env/bin/activate >&2 && \
	pip install -r requirements.txt >&2
	test ! -t 1 || (echo 'To activate the virtualenv, please source the output of this command. Eg: . $$(make env)' && exit 1)
	echo .env/bin/activate

deps:
	. .env/bin/activate && \
	pip install -r requirements.txt --upgrade

clean:
	find . \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} \;

