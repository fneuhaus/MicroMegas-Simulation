INCDIR = $(GARFIELD_HOME)/Include
HEEDDIR = $(GARFIELD_HOME)/Heed
LIBDIR = $(GARFIELD_HOME)/lib
PYTHONPATH=..:$PYTHONPATH

# Compiler flags
CFLAGS = -Wall -Wextra -Wno-long-long \
	`root-config --cflags` \
	 -fno-common -c \
	-I$(INCDIR) -I$(HEEDDIR)

LDFLAGS = `root-config --glibs` -lGeom -lgfortran -lm \
	-L$(LIBDIR) -lGarfield

all: avalanche

gas_file: gas_file.cpp ../simulation.conf
	# cog.py -r gas_file.cpp
	$(CXX) $(CFLAGS) gas_file.cpp
	$(CXX) -o gas_file gas_file.o $(LDFLAGS)
	rm gas_file.o

plot_field: plot_field.cpp ../simulation.conf
	cog.py -r plot_field.cpp
	$(CXX) $(CFLAGS) plot_field.cpp
	$(CXX) -o plot_field plot_field.o $(LDFLAGS)
	rm plot_field.o

avalanche: avalanche.cpp ../simulation.conf
	cog.py -r avalanche.cpp
	$(CXX) $(CFLAGS) avalanche.cpp
	$(CXX) -o avalanche avalanche.o $(LDFLAGS)
	rm avalanche.o

avalanche-no-cog: avalanche.cpp
	$(CXX) $(CFLAGS) avalanche.cpp
	$(CXX) -o avalanche avalanche.o $(LDFLAGS)
	rm avalanche.o

clean-cog:
	cog.py -x -r gas_file.cpp
	cog.py -x -r plot_field.cpp
	cog.py -x -r avalanche.cpp

clean:
	make clean-cog
	rm gas_file
	rm plot_field
	rm avalanche
	
