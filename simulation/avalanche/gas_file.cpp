#include <iostream>
#include "MediumMagboltz.hh"

using namespace Garfield;
using namespace std;

int main(int argc, char *argv[]) {
   if (argc != 2) {
      std::cout << "Usage: gas_file <output filename>" << std::endl;
      return 1;
   }

   MediumMagboltz* gas = new MediumMagboltz();
   /*[[[cog
   from MMconfig import *
   gas_composition = eval(conf["detector"]["gas_composition"])
   cog.outl("gas->SetComposition({});".format(', '.join(['\"{}\",{}'.format(comp, fract) for comp, fract in gas_composition.items()])))
   cog.outl("gas->SetTemperature({}+273.15);".format(conf["detector"]["temperature"]))
   cog.outl("gas->SetPressure({} * 7.50062);".format(conf["detector"]["pressure"]))
   ]]]*/
   //[[[end]]]
   // gas->SetFieldGrid(20000., 60000., 20, true, 0., 0., 1, 0., 0., 1);
   gas->EnableDebugging();
   gas->Initialise();  
   gas->DisableDebugging();

   // Penning transfer
   /*[[[cog
   from MMconfig import *
   if conf['detector'].getboolean('penning_transfer_enable'):
      penning_gases = eval(conf['detector']['penning_transfer_gas'])
      for gas, penning_r in penning_gases.items():
         cog.outl('gas->EnablePenningTransfer({}, 0., "{}");'.format(
            penning_r, gas))
   ]]]*/
   //[[[end]]]
   gas->GenerateGasTable(20, true);

   gas->WriteGasFile(argv[1]);
   return 0;
}
