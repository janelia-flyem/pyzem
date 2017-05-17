init:
	pip install -r requirements.txt

test:
	py.test tests

install:
	pip install --editable .

.PHONY: init test
