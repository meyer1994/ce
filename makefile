
compile:
	python main.py -f example.ce | tail -n +4 | tee out.txt
	llc out.txt -filetype=obj
	gcc -o t out.txt.o

test: clean
	python main.py -f example.ce

clean:
	rm -vf ce/parser.out ce/parsetab.py
	rm -vf out.txt* t

lint: clean
	python -m flake8 ce

debug:
	python -m pdb main.py -f example.ce
