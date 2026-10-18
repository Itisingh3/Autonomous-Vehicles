CXX ?= g++
OQS_ROOT ?= /usr/local
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
all: crypto_benchmark
crypto_benchmark: crypto_benchmark.cpp
	$(CXX) $(CXXFLAGS) -I$(OQS_ROOT)/include $< -L$(OQS_ROOT)/lib -Wl,-rpath,$(OQS_ROOT)/lib -loqs -o $@
clean:
	rm -f crypto_benchmark
