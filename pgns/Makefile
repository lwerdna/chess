# get list of .cards files
CARDS = $(wildcard *.cards)
$(info cards list:)
$(info $(CARDS))

# get list of .pgn by swapping ".cards" with ".pgn" in CARDS list
PGNS = $(CARDS:.cards=.pgn)
$(info pgns list:)
$(info $(PGNS))

.PHONY: all

# make PGN files
all: $(PGNS)

# pattern rule tells make how to build pgns
%.pgn : %.cards
	./cards2pgn.py $< $@

