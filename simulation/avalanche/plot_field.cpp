#include <sstream>
#include <iostream>
#include <iomanip>

#include <TCanvas.h>
#include <TApplication.h>
#include <TFile.h>
#include <TTree.h>
#include <TRandom3.h>
#include <TVector3.h>
#include <TMath.h>

#include "MediumMagboltz.hh"
#include "ComponentVoxel.hh"
#include "Sensor.hh"
#include "ViewField.hh"
#include "Plotting.hh"
#include "ViewFEMesh.hh"
#include "ViewSignal.hh"
#include "FundamentalConstants.hh"
#include "GarfieldConstants.hh"

using namespace std;
using namespace Garfield;

int main(int argc, char * argv[]) {
   /* [[[cog
   from MMconfig import *
   cog.outl(
      """
      double areaXmin = {}, areaXmax = -areaXmin;
      double areaYmin = {}, areaYmax = -areaYmin;
      double areaZmin = {}, areaZmax = {} + {}; // begin and end of the drift region, 100µm above the mesh where the field gets inhomogeneous (value from: http://iopscience.iop.org/article/10.1088/1748-0221/6/06/P06011/pdf)
      """.format(
         -float(conf["detector"]["size_x"]) / 2.,
         -float(conf["detector"]["size_y"]) / 2.,
         conf["amplification"]["z_min"], conf["amplification"]["z_max"], conf["amplification"]["z_max_safety"]
      )
   )
   ]]] */
   // [[[end]]]

   TString outputfileName, meshFile;
   // use file from conf
   /*[[[cog
   from MMconfig import *
   cog.outl("outputfileName = \"{}\";".format(conf["amplification"]["electric_field_path"]))
   cog.outl("meshFile = \"{}\";".format(conf["amplification"]["mesh_file"]))
   ]]]*/
   //[[[end]]]

   if (argc == 2) {
      outputfileName = argv[1];
   }
   if (!outputfileName) {
      cerr << "No output file specified or given!" << endl;
      return 1;
   }
   if (!meshFile) {
      cerr << "No mesh file specified or given!" << endl;
      return 1;
   }

   // Import a COMSOL generated field map
   /* [[[cog
   from MMconfig import *
   from MMutils import determine_mesh_cells
   mesh_file = conf['amplification']['mesh_file']
   mesh_definition = determine_mesh_cells(mesh_file)
   if not mesh_definition:
      mesh_definition = 'fm->SetMesh(65, 65, 227, -64e-4, 64e-4, -64e-4, 64e-4, -152.1e-4, 300.1e-4);'

   cog.outl(
      """
      ComponentVoxel *fm = new ComponentVoxel();
      {}
      if (!(fm->LoadData("{}", "XYZ", true, true, 1e-4, 1., 1.))) {{
         return 1;
      }}
      fm->EnableMirrorPeriodicityX();
      fm->EnableMirrorPeriodicityY();
      """.format(mesh_definition, mesh_file)
   )
   ]]] */
   //[[[end]]]

   // Define the medium
   MediumMagboltz* gas = new MediumMagboltz();
   /*[[[cog
   from MMconfig import *
   gas_composition = eval(conf["detector"]["gas_composition"])
   cog.outl("gas->SetComposition({});".format(', '.join(['\"{}\",{}'.format(comp, fract) for comp, fract in gas_composition.items()])))
   cog.outl("gas->SetTemperature({}+273.15);".format(conf["detector"]["temperature"]))
   cog.outl("gas->SetPressure({} * 7.50062);".format(conf["detector"]["pressure"]))
   ]]]*/
   //[[[end]]]
   gas->Initialise(true);

   fm->SetMedium(0, gas);
   fm->PrintRegions();

   Sensor* sensor = new Sensor();
   sensor->AddComponent(fm);
   sensor->SetArea(areaXmin, areaYmin, areaZmin, areaXmax, areaYmax, areaZmax);

   int steps = 50;
   double stepsize = 62.5e-4 / steps;
   TFile *outputFile = new TFile(outputfileName, "RECREATE");
   outputFile->mkdir("X");
   outputFile->cd("X");
   for (int i = 0; i < steps; i++) {
      std::stringstream ss;
      ss << "Field_x_" << i * stepsize * 1e4 << "um";
      ViewField *viewfield = new ViewField();
      viewfield->SetPlane(0., -1., 0., 0, stepsize * i, 0.);
      viewfield->SetComponent(fm);
      /*[[[cog
      from MMconfig import *
      cog.outl('viewfield->SetNumberOfSamples2d(400, 250);'.format(
       bins_x=conf['amplification']['electric_field_xbins'],
       bins_y=conf['amplification']['electric_field_ybins']))
      cog.outl('viewfield->SetArea({x_min}, {z_min}, {x_max}, {z_max});'.format(
         x_min=conf['amplification']['electric_field_xmin'],
         x_max=conf['amplification']['electric_field_xmax'],
         z_min=conf['amplification']['electric_field_zmin'],
         z_max=conf['amplification']['electric_field_zmax']))
      ]]]*/
      //[[[end]]]
      TH2F *hist = viewfield->PlotHist(ss.str());
      hist->Write();
      delete hist;
   }
   outputFile->cd("..");
   outputFile->mkdir("Y");
   outputFile->cd("Y");
   for (int i = 0; i < steps; i++) {
      std::stringstream ss;
      ss << "Field_y_" << i * stepsize * 1e4 << "um";
      ViewField *viewfield = new ViewField();
      viewfield->SetPlane(-1., 0., 0., stepsize * i, 0, 0.);
      viewfield->Rotate(1.5707963267948966);
      viewfield->SetComponent(fm);
      /*[[[cog
      from MMconfig import *
      cog.outl('viewfield->SetNumberOfSamples2d(400, 250);'.format(
       bins_x=conf['amplification']['electric_field_xbins'],
       bins_y=conf['amplification']['electric_field_ybins']))
      cog.outl('viewfield->SetArea({x_min}, {z_min}, {x_max}, {z_max});'.format(
         x_min=conf['amplification']['electric_field_xmin'],
         x_max=conf['amplification']['electric_field_xmax'],
         z_min=conf['amplification']['electric_field_zmin'],
         z_max=conf['amplification']['electric_field_zmax']))
      ]]]*/
      //[[[end]]]
      TH2F *hist = viewfield->PlotHist(ss.str());
      hist->Write();
      delete hist;
   }
   outputFile->Write();
   outputFile->Close();
   cout << "Done plotting." << endl;
   delete outputFile;

   cout << "Done." << endl;
   return 0;
}
