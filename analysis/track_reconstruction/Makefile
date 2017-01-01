# Compiler flags
CFLAGS = -Wall -Wextra -Wno-long-long \
	`root-config --cflags` \
	-O3 -fno-common -c -std=c++11\
	-I$(INCDIR) -I$(HEEDDIR)

# Debug flags
CFLAGS += -g

LDFLAGS = `root-config --glibs` -lGeom -lgfortran -lm
LDFLAGS += -L$(LIBDIR)
LDFLAGS += -g

track_reco: track_reco.cpp
	$(CXX) $(CFLAGS) track_reco.cpp
	$(CXX) -o track_reco track_reco.o $(LDFLAGS)
	rm track_reco.o

clean:
	rm track_reco
