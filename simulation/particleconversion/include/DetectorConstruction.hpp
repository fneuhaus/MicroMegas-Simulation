#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;
class G4Material;

/**
 * @brief Detector construction class to define materials and geometry of the detector.
 */
class DetectorConstruction : public G4VUserDetectorConstruction {
	public:
		virtual G4VPhysicalVolume* Construct();

		G4VPhysicalVolume* GetDetectorVolume() { return fPhysDetector; }

		void SetPairEnergy(G4double val);

	private:
		G4Material			 *fDetectorMaterial;
		G4VPhysicalVolume* fPhysWorld;
		G4VPhysicalVolume* fPhysCathode;
		G4VPhysicalVolume* fPhysDetector;
		G4LogicalVolume*   fLogicWorld;
		G4LogicalVolume*   fLogicCathode;
		G4LogicalVolume*   fLogicDetector;
};

#endif

