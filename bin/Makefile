.PHONY: all clean

all: prover9

clean:
	rm prover9 mace4

prover9:
	mkdir tmp || true
	cd tmp && wget https://www.cs.unm.edu/~mccune/mace4/download/LADR-2009-11A.tar.gz
	cd tmp && tar -xzf LADR-2009-11A.tar.gz
	cd tmp/LADR-2009-11A/provers.src && sed -i.old 's/^\([ \t]*\$$(CC).*\) -lm \(.*\)$$/\1 \2 -lm/g' Makefile
	cd tmp/LADR-2009-11A && make all
	cp tmp/LADR-2009-11A/bin/mace4 .
	cp tmp/LADR-2009-11A/bin/prover9 .
	rm -rf tmp
