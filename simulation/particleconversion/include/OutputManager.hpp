#ifndef OutputManager_h
#define OutputManager_h 1

#include "G4Track.hh"
#include "G4ThreeVector.hh"
#include "globals.hh"

#include <TTree.h>
#include <TString.h>

class TFile;
class TTree;
class TH1D;

class OutputManager {
	public:
		OutputManager(TString outputfileName);
		~OutputManager();
	 
		void Initialize();
		void Save();
		void PrintStatistic();
      void SetPrimaryParticleProperties(G4double px, G4double py, G4double pz,
            G4double energy);
		TTree* GetDetectorTree() { return fDetectorTree; }

		void FillEvent(TTree*, G4Track*);

	private:
      TString  fOutputfileName;
		TFile*   fRootFile;

		TTree*   fDetectorTree;

		G4int		fEventID;
		G4double fPrimaryEnergy;
      G4double fPrimaryPx, fPrimaryPy, fPrimaryPz;
		G4double fPhiVertex, fPhi;
		G4double fThetaVertex, fTheta;
		G4double fT;
		G4double fEkinVertex, fEkin;
		G4double fEloss;
		G4double fZVertex;
		G4double fTrackLength;
		G4double fPx, fPy, fPz;
		G4double fPosX, fPosY, fPosZ;
};

#endif
