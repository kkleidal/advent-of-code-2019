PRODUCTS := shuffler.x shuffler2.x

CFLAGS := -Wall --std=c99
CXXFLAGS := -Wall --std=c++11
ifdef DEBUG
	CFLAGS += -O0 -g
	CXXFLAGS += -O0 -g
else
	CFLAGS += -O3 -march=native -mtune=native
	CXXFLAGS += -O3 -march=native -mtune=native
endif

ifndef NSHORTCUT
	CXXFLAGS += -DSHORTCUT
endif

.PHONY: all

all: $(PRODUCTS)

%.x: %.c
	gcc $(CFLAGS) -o $@ $<

%.x: %.cpp
	g++ $(CXXFLAGS) -o $@ $<

clean:
	$(RM) -f $(PRODUCTS)
