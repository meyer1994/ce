
compile:
	python -m compileall ce tests

test: clean
	python main.py -f example.ce

clean:
	rm -vf ce/parser.out ce/parsetab.py

lint: clean
	python -m flake8 ce

debug:
	python -m pdb main.py -f example.ce
