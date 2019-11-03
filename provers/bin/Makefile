.PHONY: all clean

all: prover9 vampire eprover

clean:
	rm isofilter prooftrans tptp_to_ladr ladr_to_tptp mace4 prover9 || true
	rm vampire || true
	rm eprover || true

prover9:
	mkdir tmp || true
	cd tmp && wget https://www.cs.unm.edu/~mccune/mace4/download/LADR-2009-11A.tar.gz
	cd tmp && tar -xzf LADR-2009-11A.tar.gz
	cd tmp/LADR-2009-11A/provers.src && sed -i.old 's/^\([ \t]*\$$(CC).*\) -lm \(.*\)$$/\1 \2 -lm/g' Makefile
	cd tmp/LADR-2009-11A && make all
	cp tmp/LADR-2009-11A/bin/isofilter .
	cp tmp/LADR-2009-11A/bin/interpformat .
	cp tmp/LADR-2009-11A/bin/prooftrans .
	cp tmp/LADR-2009-11A/bin/tptp_to_ladr .
	cp tmp/LADR-2009-11A/bin/ladr_to_tptp .
	cp tmp/LADR-2009-11A/bin/mace4 .
	cp tmp/LADR-2009-11A/bin/prover9 .
	rm -rf tmp

vampire:
	mkdir tmp || true
	cd tmp && git clone https://github.com/vprover/vampire.git || true
	cd tmp/vampire && make -j4 vampire_rel_static
	cp tmp/vampire/vampire_rel_static_master* vampire
	rm -rf tmp

eprover:
	mkdir tmp || true
	cd tmp && git clone https://github.com/eprover/eprover.git || true
	cd tmp/eprover && ./configure
	cd tmp/eprover && make -j4 rebuild
	cp tmp/eprover/PROVER/eprover .
	rm -rf tmp
