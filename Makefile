init:
	pip install -r requirements.txt

test:
	py.test tests

install:
	python setup.py install

.PHONY: init test
