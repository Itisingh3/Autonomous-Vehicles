# Run inside an OMNeT++ 6.0.1 opp_env session from simulation/omnetpp.
OMNETPP_ROOT ?= /home/opp_env/omnetpp-6.0.1
OQS_PREFIX ?= /usr/local
TARGET = cav_pqc_network
SOURCES = CAVApp.cc RSUApp.cc ../../crypto/src/PqcCrypto.cc CavMsg_m.cc

.PHONY: all run clean
all: CavMsg_m.cc Makefile.generated
	$(MAKE) -f Makefile.generated

CavMsg_m.cc CavMsg_m.h: CavMsg.msg
	$(OMNETPP_ROOT)/bin/opp_msgc CavMsg.msg

Makefile.generated: $(SOURCES) cav-pqc-network.ned
	$(OMNETPP_ROOT)/bin/opp_makemake -f --deep -o $(TARGET) -I../../crypto/include -I. -L$(OQS_PREFIX)/lib -loqs -lcrypto

run: all
	./$(TARGET) -u Cmdenv -f omnetpp.ini -c V2RHandshake

clean:
	rm -f CavMsg_m.cc CavMsg_m.h $(TARGET) Makefile.generated
