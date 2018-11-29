compile:
	python main.py -f example.ce | tee out.ir
	llc out.ir -o out.o -filetype=obj
	gcc out.o

clean:
	rm -vf ce/parser.out ce/parsetab.py
	rm -vf out.txt* out.* a.out

lint: clean
	python -m flake8 ce

debug:
	python -m pdb main.py -f example.ce
