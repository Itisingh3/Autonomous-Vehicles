CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
OQS_ROOT ?= ../../.deps/oqs

all: pbft_reputation

pbft_reputation: pbft_reputation.cpp ../../crypto/PqcCrypto.cc
	$(CXX) $(CXXFLAGS) -I../../crypto -I$(OQS_ROOT)/include $^ -L$(OQS_ROOT)/lib -loqs -lcrypto -o $@

clean:
	rm -f pbft_reputation
