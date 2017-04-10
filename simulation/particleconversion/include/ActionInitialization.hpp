#ifndef ActionInitialization_h
#define ActionInitialization_h 1

#include "G4VUserActionInitialization.hh"

#include "DetectorConstruction.hpp"
#include <TString.h>

/**
 * @brief This class is responsible for creating the action.
 */
class ActionInitialization : public G4VUserActionInitialization {
	public:
		ActionInitialization(DetectorConstruction*, TString);
		virtual ~ActionInitialization();

		virtual void BuildForMaster() const;
		virtual void Build() const;

	private:
		DetectorConstruction* fDetector;
      TString fOutputfileName;
};

#endif

		
