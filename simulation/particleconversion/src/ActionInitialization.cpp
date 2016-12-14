#include "ActionInitialization.hpp"
#include "DetectorConstruction.hpp"
#include "OutputManager.hpp"
#include "PrimaryGeneratorAction.hpp"
#include "RunAction.hpp"
#include "EventAction.hpp"
#include "SteppingAction.hpp"

ActionInitialization::ActionInitialization(DetectorConstruction* detector) : G4VUserActionInitialization(), fDetector(detector) {
}

ActionInitialization::~ActionInitialization() {}

/**
 * @brief Build action for master (if multithreaded)
 */
void ActionInitialization::BuildForMaster() const {
	OutputManager* outManager = new OutputManager();

	SetUserAction(new RunAction(outManager));
}

/**
 * @brief Build action for worker threads.
 * @details For the worker threads (normal thread if multitasking is disabled).
 */
void ActionInitialization::Build() const {
	OutputManager* outManager = new OutputManager();

	SetUserAction(new PrimaryGeneratorAction());
	SetUserAction(new RunAction(outManager));
	
	EventAction* eventAction = new EventAction;
	SetUserAction(eventAction);
	
	SetUserAction(new SteppingAction(eventAction, fDetector, outManager));
}  
