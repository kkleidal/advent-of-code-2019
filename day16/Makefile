CFLAGS := -Wall --std=c99
ifdef DEBUG
	CFLAGS += -O0 -g
else
	CFLAGS += -O3 -march=native -mtune=native
endif

.PHONY: all

all: part2.x

part2.x: part2.c
	gcc $(CFLAGS) -o $@ $<

clean:
	$(RM) -f part2.x
