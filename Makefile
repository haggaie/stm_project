TARBALL=../stm_project.tar.bz2
EXCLUDE=$(addprefix --exclude=, .git)
DIRS=cache-conf man no-cache-conf httpd-2.2.x httpd-2.2.x.no-transactions test
FILES=README man2html/ siege-2.67.tar.gz apr-1.3.3.tar.bz2 apr-util-1.3.4.tar.bz2 \
	$(PAPER)

PAPER=doc/paper.pdf

TAR=tar

all: $(TARBALL)

DIR=$(shell basename `pwd`)

$(TARBALL): $(DIRS) $(FILES)
	cd ..; $(TAR) cjvf $(notdir $@) $(addprefix $(DIR)/,$^) $(EXCLUDE)

$(PAPER): doc/SYSTOR09/eran.pdf
	cp $^ $@
