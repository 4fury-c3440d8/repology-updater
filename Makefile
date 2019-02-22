FLAKE8?=	flake8
MYPY?=		mypy

STATICDIR=	repologyapp/static

all: gzip-static

gzip-static:
	gzip -9 -f -k -v ${STATICDIR}/*.css ${STATICDIR}/*.js ${STATICDIR}/*.ico ${STATICDIR}/*.svg

clean:
	rm -f ${STATICDIR}/*.gz

lint:: test flake8 mypy

test::
	python3 -m unittest discover

profile-dump::
	python3 -m cProfile -o _profile ./repology-dump.py --stream >/dev/null 2>&1
	python3 -c 'import pstats; stats = pstats.Stats("_profile"); stats.sort_stats("time"); stats.print_stats()' | less

profile-reparse::
	python3 -m cProfile -o _profile ./repology-update.py -P >/dev/null 2>&1
	python3 -c 'import pstats; stats = pstats.Stats("_profile"); stats.sort_stats("time"); stats.print_stats()' | less

flake8:
	# D10  - Missing docstrings
	# E265 - Block comment should start with '# '
	# E501 - Line too long
	# E722 - Do not use bare except
	# N802 - Bad function name
	#
	# New in flake8 3.6.0, fix and reenable
	# W504 - Line break after binary operator
	# W605 - Invalid escape sequence
	${FLAKE8} --ignore=D10,E265,E501,E722,N802,W504,W605 --count --application-import-names=repology *.py repology repologyapp test

flake8-all:
	${FLAKE8} --application-import-names=repology *.py repology repologyapp test

mypy:
	${MYPY} --ignore-missing-imports repology

check:
	python3 repology-schemacheck.py -s repos $$(find repos.d -name "*.yaml")
