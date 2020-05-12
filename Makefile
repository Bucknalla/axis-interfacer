.PHONY: all docs

all:

install:
	pip install -r requirements.txt

docs:
	mkdocs build

serve: docs
	mkdocs serve

github: docs
	mkdocs gh-deploy