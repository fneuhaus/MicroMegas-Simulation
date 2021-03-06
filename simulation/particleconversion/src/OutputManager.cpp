#include "OutputManager.hpp"

#include "G4Track.hh"
#include "G4ThreeVector.hh"
#include "G4PhysicalConstants.hh"
#include "G4SystemOfUnits.hh"

#include <TFile.h>
#include <TTree.h>
#include <TString.h>

OutputManager::OutputManager(TString outputfileName)
   : fRootFile(0), fEventID(0), fPrimaryEnergy(0), fPrimaryPx(0),
   fPrimaryPy(0), fPrimaryPz(0), fPhiVertex(0), fPhi(0), fThetaVertex(0),
   fTheta(0), fT(0), fEkinVertex(0), fEkin(0), fEloss(0), fZVertex(0),
   fTrackLength(0), fPx(0), fPy(0), fPz(0), fPosX(0), fPosY(0), fPosZ(0),
   fOutputfileName(outputfileName) {
}

OutputManager::~OutputManager() {
   if (fRootFile) {
      delete fRootFile;
   }
}

void OutputManager::Initialize() {
   fRootFile = new TFile(fOutputfileName, "RECREATE");

   if (!fRootFile) {
      G4cout << "OutputManager::Initialize: Problem creating the ROOT TFile" << G4endl;
      return;
   }

   fDetectorTree = new TTree("detectorTree", "Conversion");
   fDetectorTree->Branch("eventID", &fEventID, "eventID/i"); // event id
   fDetectorTree->Branch("primaryEnergy", &fPrimaryEnergy, "primaryEnergy/D"); // primary energy
   fDetectorTree->Branch("primaryPx", &fPrimaryPx, "primaryPx/D"); // primary px
   fDetectorTree->Branch("primaryPy", &fPrimaryPy, "primaryPy/D"); // primary py
   fDetectorTree->Branch("primaryPz", &fPrimaryPz, "primaryPz/D"); // primary pz
   fDetectorTree->Branch("phi", &fPhi, "phi/D"); // phi angle
   fDetectorTree->Branch("theta", &fTheta, "theta/D"); // theta angle to z axis
   fDetectorTree->Branch("EkinVertex", &fEkinVertex, "EkinVertex/D");
   fDetectorTree->Branch("Ekin", &fEkin, "Ekin/D"); // kinetic energy
   fDetectorTree->Branch("Eloss", &fEloss, "Eloss/D"); // kinetic energy
   fDetectorTree->Branch("ZVertex", &fZVertex, "ZVertex/D"); // z value of the vertex position (track creation point)
   fDetectorTree->Branch("TrackLength", &fTrackLength, "TrackLengh/D");
   fDetectorTree->Branch("PosX", &fPosX, "PosX/D"); // x position
   fDetectorTree->Branch("PosY", &fPosY, "PosY/D"); // y position
   fDetectorTree->Branch("PosZ", &fPosZ, "PosZ/D"); // z position
   fDetectorTree->Branch("Px", &fPx, "Px/D"); // x momentum
   fDetectorTree->Branch("Py", &fPy, "Py/D"); // y momentum
   fDetectorTree->Branch("Pz", &fPz, "Pz/D"); // z momentum
   fDetectorTree->Branch("t", &fT, "t/D"); // time

   G4cout << "\n----> Output file is: " << fOutputfileName << G4endl;
}

void OutputManager::Save() {
   if (fRootFile) {
      fRootFile->Write();
      fRootFile->Close();
      G4cout << "\n----> Output Tree is saved \n" << G4endl;
   }
}

void OutputManager::SetPrimaryParticleProperties(G4double px, G4double py, G4double pz,
            G4double energy) {
   fPrimaryEnergy = energy;
   fPrimaryPx = px;
   fPrimaryPy = py;
   fPrimaryPz = pz;
}

void OutputManager::FillEvent(TTree* tree, G4Track* track) {
   G4ThreeVector pos = track->GetPosition();
   G4ThreeVector dirVertex = track->GetVertexMomentumDirection();
   G4ThreeVector dir = track->GetMomentumDirection();
   fEventID += 1;
   fPhiVertex = dirVertex.getPhi();
   fPhi = dir.getPhi();
   fThetaVertex = dirVertex.getTheta();
   fTheta = dir.getTheta();
   fPx = dir.x();
   fPy = dir.y();
   fPz = dir.z();

   // using garfield++ units here (cm, ns, eV)
   fPosX = pos.x() / cm;
   fPosY = pos.y() / cm;
   fPosZ = pos.z() / cm;
   fT = track->GetLocalTime() / ns;
   fEkinVertex = track->GetVertexKineticEnergy() / eV;
   fEkin = track->GetKineticEnergy() / eV;
   fEloss = track->GetVertexKineticEnergy() / eV - track->GetKineticEnergy() / eV;

   fZVertex = track->GetVertexPosition().z() / cm;
   fTrackLength = track->GetTrackLength() / cm;
   if (tree) {
      tree->Fill();
   }
}

void OutputManager::PrintStatistic() {
   G4cout << "--- Tree Stats" << G4endl;
   if (fDetectorTree) {
      G4cout << " N_detector = " << fDetectorTree->GetEntries() << G4endl;
   }
   G4cout << "---" << G4endl;
}
