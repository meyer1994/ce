
compile:
	python -m compileall ce tests

test: clean
	python main.py -f tests/test.txt

clean:
	rm -vf ce/parser.out ce/parsetab.py

lint: clean
	python -m flake8 ce
