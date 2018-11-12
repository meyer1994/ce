
compile:
	python -m compileall ce tests

clean:
	rm -vf ce/parser.out ce/parsetab.py
