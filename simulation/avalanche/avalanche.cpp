#include <sstream>
#include <iostream>
#include <iomanip>
#include <signal.h>
#include <errno.h>

#include <TCanvas.h>
#include <TApplication.h>
#include <TFile.h>
#include <TTree.h>
#include <TRandom3.h>
#include <TVector3.h>
#include <TMath.h>
/* [[[cog
from MMconfig import *
if conf.getboolean('amplification', 'store_time_per_event', fallback=False):
   cog.outl('#include<chrono>')
]]]*/
//[[[end]]]

#include "MediumMagboltz.hh"
#include "ComponentVoxel.hh"
#include "SensorCOMSOL.hh"
#include "ViewField.hh"
#include "ViewCell.hh"
#include "Plotting.hh"
#include "ViewFEMesh.hh"
#include "ViewSignal.hh"
#include "FundamentalConstants.hh"
#include "GarfieldConstants.hh"
#include "AvalancheMicroscopicCOMSOL.hh"

using namespace std;
using namespace Garfield;
TFile* outputFile;

void exitSignalHandler(int _ignored) {
   cout << "Simulation aborted because of timeout (" << _ignored << ")." << endl;
   outputFile->Write();
   outputFile->Close();
   exit(1);
}

int main(int argc, char * argv[]) {
   if (signal((int)SIGUSR2, exitSignalHandler) == SIG_ERR) {
      std::cout << "Error setting up signal." << std::endl;
   }
 
   /* [[[cog
   from MMconfig import *
   cog.outl(
      """
      const int maxAvalancheSize = {}; // constrains the maximum avalanche size, 0 means no limit
      double areaXmin = {}, areaXmax = -areaXmin;
      double areaYmin = {}, areaYmax = -areaYmin;
      double areaZmin = {}, areaZmax = {} + {}; // begin and end of the drift region, 100µm above the mesh where the field gets inhomogeneous (value from: http://iopscience.iop.org/article/10.1088/1748-0221/6/06/P06011/pdf)
      """.format(
         conf["amplification"]["max_avalanche_size"],
         -float(conf["detector"]["size_x"]) / 2.,
         -float(conf["detector"]["size_y"]) / 2.,
         conf["amplification"]["z_min"], conf["amplification"]["z_max"], conf["amplification"]["z_max_safety"]
      )
   )
   ]]] */
   // [[[end]]]

   TString inputfileName, outputfileName, meshFile;
   // use file from conf
   /*[[[cog
   from MMconfig import *
   cog.outl("inputfileName = \"{}\";".format(conf["amplification"]["in_filename"]))
   cog.outl("outputfileName = \"{}\";".format(conf["amplification"]["out_filename"]))
   cog.outl("meshFile = \"{}\";".format(conf["amplification"]["mesh_file"]))
   ]]]*/
   //[[[end]]]

   if (argc == 3) {
      inputfileName = argv[1];
      outputfileName = argv[2];
   } else if (argc == 2) {
      cerr << "Only input or output file specified, give both!" << endl;
   }

   if (!inputfileName || !outputfileName) {
      cerr << "No input/output file specified or given!" << endl;
      return 1;
   }
   if (!meshFile) {
      cerr << "No mesh file specified or given!" << endl;
      return 1;
   }

   TFile* inputFile = TFile::Open(inputfileName);
   if (!inputFile->IsOpen()) {
      cout << "Error opening file: " << argv[1] << endl;
      return 1;
   }
   TTree* inputTree = (TTree*)inputFile->Get("driftTree");
   Int_t numberOfEvents = inputTree->GetEntriesFast();

   Int_t inEventID;
   Int_t inNele;
   vector<Double_t> *inPosX = 0, *inPosY = 0, *inPosZ = 0, *inEkin = 0, *inT = 0;
   inputTree->SetBranchAddress("eventID", &inEventID);
   inputTree->SetBranchAddress("x1", &inPosX); inputTree->SetBranchAddress("y1", &inPosY);   inputTree->SetBranchAddress("z1", &inPosZ);
   inputTree->SetBranchAddress("e1", &inEkin);
   inputTree->SetBranchAddress("t1", &inT);
   inputTree->SetBranchAddress("nele", &inNele);
   cout << "Reading " << numberOfEvents << " events from " << inputFile->GetPath() << endl;

   Int_t eventID;
   Int_t nele_drift; // number of electrons from drift
   Int_t nele_gain;
   Int_t nele;  // number of electrons in avalanche
   Int_t nelep; // number of electron end points
   Double_t gain; // gain per electron
   vector<Int_t> status;
   vector<Double_t> x0, y0, z0, e0, t0;
   vector<Double_t> x1, y1, z1, e1, t1;
   Double_t x1_mean, y1_mean;
   Double_t x1_std, y1_std;
   vector<Double_t> signal_t;
   vector<Double_t> signal_amplitude;

   outputFile = new TFile(outputfileName, "RECREATE");
   outputFile->cd();
   TTree* outputTree = new TTree("avalancheTree", "Avalanches");
   outputTree->Branch("eventID", &eventID);
   outputTree->Branch("nele_drift", &nele_drift, "nele_drift/I");
   outputTree->Branch("nele_gain", &nele_gain, "nele_gain/I");
   outputTree->Branch("nele", &nele, "nele/I");
   outputTree->Branch("nelep", &nelep, "nelep/I");
   outputTree->Branch("gain", &gain, "gain/D");
   outputTree->Branch("status", &status);
   outputTree->Branch("x0", &x0); outputTree->Branch("y0", &y0); outputTree->Branch("z0", &z0); outputTree->Branch("e0", &e0); outputTree->Branch("t0", &t0);
   outputTree->Branch("x1", &x1); outputTree->Branch("y1", &y1); outputTree->Branch("z1", &z1); outputTree->Branch("e1", &e1); outputTree->Branch("t1", &t1);
   outputTree->Branch("x1_mean", &x1_mean, "x1_mean/D"); outputTree->Branch("y1_mean", &y1_mean, "y1_mean/D");
   outputTree->Branch("x1_std", &x1_std, "x1_std/D"); outputTree->Branch("y1_std", &y1_std, "y1_std/D");
   outputTree->Branch("signal_t", &signal_t);
   outputTree->Branch("signal_amplitude", &signal_amplitude);
   /*[[[cog
   from MMconfig import *
   if conf.getboolean('amplification', 'store_time_per_event', fallback=False):
      cog.outl('Double_t time_per_event;')
      cog.outl('outputTree->Branch("time_per_event", &time_per_event);')
   ]]]*/
   //[[[end]]]

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
      fm->PrintRegions();
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
   gas->EnableDrift();                    // Allow for drifting in this medium
   gas->SetMaxElectronEnergy(200.);
   gas->Initialise(true);

   fm->SetMedium(0, gas);
   fm->PrintRegions();

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

   SensorCOMSOL* sensor = new SensorCOMSOL();
   sensor->AddComponent(fm);
   sensor->SetArea(areaXmin, areaYmin, areaZmin, areaXmax, areaYmax, areaZmax);

   /*
    * Create the avalanche calculation and enable signal calculations if activated in the config.
    */
   AvalancheMicroscopicCOMSOL* avalanchemicroscopic = new AvalancheMicroscopicCOMSOL();
   avalanchemicroscopic->SetSensor(sensor);
   avalanchemicroscopic->SetCollisionSteps(1);
   if (maxAvalancheSize > 0) {
      avalanchemicroscopic->EnableAvalancheSizeLimit(maxAvalancheSize);
   }
   /*[[[cog
   from MMconfig import *
   if conf['amplification'].getboolean('signal_calculation_enable'):
      cog.outl(
         '''
   Double_t signal_t_min = {};
   Double_t signal_t_stepsize = {};
   Double_t signal_t_steps = {};
   sensor->SetTimeWindow(signal_t_min, signal_t_stepsize, signal_t_steps);
         '''.format(
               conf['amplification']['signal_calculation_t_min'],
               conf['amplification']['signal_calculation_t_stepsize'],
               conf['amplification']['signal_calculation_t_steps']
      ))
      cog.outl('avalanchemicroscopic->EnableSignalCalculation();')
   ]]]*/
   //[[[end]]]

   /* [[[cog
   from MMconfig import *
   if conf['amplification'].getboolean('save_drift_lines'):
      cog.outl('SaveDrift* savedrift = new SaveDrift("{}");'.format(conf['amplification']['drift_lines_path']))
      cog.outl('avalanchemicroscopic->EnableSaving(savedrift);')
      cog.outl('avalanchemicroscopic->SetSkippingFactor({});'.format(conf['amplification']['drift_lines_skipping_factor']))
      cog.outl('avalanchemicroscopic->SetSavingAutoEndEvent(false);')
   ]]]*/
   ///[[[end]]]

   /* [[[cog
   from MMconfig import *
   if conf['amplification'].getboolean('save_electric_field'):
      cog.outl('''TCanvas *c1 = new TCanvas();
   ViewField *viewfield = new ViewField();
   viewfield->SetCanvas(c1);
   viewfield->SetPlane(0., -1., 0., 0., 0., 0.);
   viewfield->SetComponent(fm);
   viewfield->SetArea({x_min}, {z_min}, {x_max}, {z_max});
   viewfield->SetNumberOfContours(255);
   viewfield->SetNumberOfSamples2d({bins_x}, {bins_y});
   viewfield->PlotContour();
   c1->SaveAs("{filename}");
   delete viewfield;
   delete c1;'''.format(bins_x=conf['amplification']['electric_field_xbins'],
         bins_y=conf['amplification']['electric_field_ybins'],
         x_min=conf['amplification']['electric_field_xmin'],
         x_max=conf['amplification']['electric_field_xmax'],
         z_min=conf['amplification']['electric_field_zmin'],
         z_max=conf['amplification']['electric_field_zmax'],
         filename=conf['amplification']['electric_field_path']))
      if conf['amplification'].getboolean('plot_only'):
         cog.outl('exit(0);')
   ]]]*/
   ///[[[end]]]

   // actual simulation
   for (int i = 0; i < numberOfEvents; i++) {

      /*[[[cog
      from MMconfig import *
      if conf.getboolean('amplification', 'store_time_per_event', fallback=False):
         cog.outl('auto begin = std::chrono::high_resolution_clock::now();')
      ]]]*/
      //[[[end]]]
      int numberOfElectrons;

      inputTree->GetEvent(i, 0); // 0 get only active branches, 1 get all branches
      eventID = inEventID;
      //inputTree->Show(i);
      numberOfElectrons = inNele;
      nele_drift = numberOfElectrons;
      nele = 0;
      nele_gain = 0;
      nelep = 0;
      x1_mean = 0;
      y1_mean = 0;
      x1_std = 0;
      y1_std = 0;

      for (int e = 0; e < numberOfElectrons; e++) {
         // Set the initial position [cm], direction, starting time [ns] and initial energy [eV]
         /*[[[cog
         from MMconfig import *
         if not conf.getboolean('amplification', 'study_transparency', fallback=False):
            cog.outl("TVector3 initialPosition = TVector3(inPosX->at(e), inPosY->at(e), {});".format(conf["amplification"]["z_max"]))
         else:
            cog.outl("TVector3 initialPosition = TVector3(inPosX->at(e), inPosY->at(e), inPosZ->at(e));")
         ]]]*/
         //[[[end]]]
         TVector3 initialDirection = TVector3(0., 0., -1.); // 0,0,0 for random initial direction
         Double_t initialTime = inT->at(e);
         Double_t initialEnergy = inEkin->at(e); // override default energy

         //cout << "Initial Time  : " << initialTime << " ns" << endl;
         //cout << "Initial Energy  : " << initialEnergy << " eV" << endl;
         //cout << "Initial position: " << initialPosition.x() << ", " << initialPosition.y()  << ", " << initialPosition.z() << " cm" << endl;

         /*[[[cog
         from MMconfig import *
         if conf.getboolean('amplification', 'study_transparency', fallback=False):
            method = 'DriftElectron'
         else:
            method = 'AvalancheElectron'
         cog.outl(
         '''avalanchemicroscopic->{}(initialPosition.x(), initialPosition.y(), initialPosition.z(), 
         initialTime, initialEnergy, initialDirection.x(), initialDirection.y(), 
         initialDirection.z());'''.format(method))
         ]]]*/
         //[[[end]]]

         Int_t ne, ni;
         avalanchemicroscopic->GetAvalancheSize(ne, ni);
         nele += ne;

         // local variables to be pushed into vectors
         Double_t xi, yi, zi, ti, ei;
         Double_t xf, yf, zf, tf, ef;
         Int_t stat;

         // number of electron endpoints - 1 is the number of hits on the readout for an event passing the mesh
         int np = avalanchemicroscopic->GetNumberOfElectronEndpoints();
         nelep += np;
         cout << "Number of electron endpoints: " << np << endl;

         for (int j = 0; j < np; j++) {
            avalanchemicroscopic->GetElectronEndpoint(j, xi, yi, zi, ti, ei, xf, yf, zf, tf, ef, stat);

            if (zf <= -25e-4) {
               nele_gain++;
               x1_mean += xf;
               y1_mean += yf;
            }

            x0.push_back(xi); y0.push_back(yi); z0.push_back(zi);
            x1.push_back(xf); y1.push_back(yf); z1.push_back(zf);
            e0.push_back(ei);
            e1.push_back(ef);

            /*[[[cog
            from MMconfig import *
            if conf['amplification'].getboolean('use_local_time'):
               cog.outl('t0.push_back(ti - initialTime); t1.push_back(tf - initialTime);')
            else:
               cog.outl('t0.push_back(ti); t1.push_back(tf);')
            ]]]*/
            //[[[end]]]
            status.push_back(stat);
         }

         cout << setw(5) << i/(double)numberOfEvents*100. << "% of all events done." << endl;
         cout << setw(4) << e/(double)numberOfElectrons*100. << "% of this event done." << endl;
      }

      /*[[[cog
      from MMconfig import *
      if conf['amplification'].getboolean('signal_calculation_enable'):
         cog.outl(
         '''for (int bin = 0; bin < signal_t_steps; bin++) {
         signal_t.push_back(signal_t_min + bin * signal_t_stepsize);
         signal_amplitude.push_back(sensor->GetSignal("readout", bin) / ElementaryCharge);
      }''')
      ]]]*/
      //[[[end]]]

      /*[[[cog
      from MMconfig import *
      if conf.getboolean('amplification', 'store_time_per_event', fallback=False):
         cog.outl('auto end = std::chrono::high_resolution_clock::now();')
         cog.outl('time_per_event = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count();')
      ]]]*/
      //[[[end]]]

      /* [[[cog
      from MMconfig import *
      if conf['amplification'].getboolean('save_drift_lines'):
         cog.outl('avalanchemicroscopic->SavingEndEvent();')
      ]]]*/
      //[[[end]]]

      gain = (double)nele_gain / (double)nele_drift;
      x1_mean /= (double)nele_gain;
      y1_mean /= (double)nele_gain;
      for (unsigned int i = 0; i < x1.size(); i++) {
         if (z1.at(i) <= 25e-4) {
            x1_std += (x1.at(i) - x1_mean) * (x1.at(i) - x1_mean);
            y1_std += (y1.at(i) - y1_mean) * (y1.at(i) - y1_mean);
         }
      }
      x1_std /= (double)nele_gain;
      y1_std /= (double)nele_gain;
      /*[[[cog
      from MMconfig import *
      if not conf['amplification'].getboolean('save_electron_coordinates'):
         cog.outl('x0.clear(); y0.clear(); z0.clear();')
         cog.outl('x1.clear(); y1.clear(); z1.clear();')
         cog.outl('e0.clear(); t0.clear();')
         cog.outl('e1.clear(); t1.clear();')
         cog.outl('status.clear();')
      ]]]*/
      //[[[end]]]
      outputTree->Fill();
      x0.clear(); y0.clear(); z0.clear(); e0.clear(); t0.clear();
      x1.clear(); y1.clear(); z1.clear(); e1.clear(); t1.clear();
      status.clear();
      /*[[[cog
      from MMconfig import *
      if conf['amplification'].getboolean('signal_calculation_enable'):
         cog.outl(
         '''signal_t.clear();
         signal_amplitude.clear()''')
      ]]]*/
      //[[[end]]]
   }

   outputFile->cd();

   /*[[[cog
   from MMconfig import *
   if False and conf.getboolean('amplification', 'save_hists', fallback=False):
      for var_name, num_bins in eval(conf.get('amplification', 'save_variables', fallback='{}')).items():
         cog.outl('''
         outputTree->Draw("{name}>>htemp({num_bins})");
         TH1F *{name}_hist = (TH1F*)gPad->GetPrimitive("htemp");
         {name}_hist->SetName("{name}");
         {name}_hist->Write();
         delete {name}_hist;
         '''.format(name=var_name, num_bins=num_bins))
   if False and not conf.getboolean('amplification', 'save_tree', fallback=True):
      cog.outl('delete outputTree;')
   ]]]*/
   //[[[end]]]

   outputFile->Write();
   outputFile->Close();
   inputFile->Close();
   /* [[[cog
   from MMconfig import *
   if conf['amplification'].getboolean('save_drift_lines'):
      cog.outl('delete savedrift;')
   ]]]*/
   ///[[[end]]]

   cout << "Done." << endl;
   return 0;
}
