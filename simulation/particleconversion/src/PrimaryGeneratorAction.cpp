#include "PrimaryGeneratorAction.hpp"
#include "OutputManager.hpp"

#include "G4LogicalVolumeStore.hh"
#include "G4LogicalVolume.hh"
#include "G4Box.hh"
#include "G4RunManager.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"
#include "TRandom3.h"
#include "Randomize.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction(OutputManager *outputManager)
   : G4VUserPrimaryGeneratorAction(), fParticleGun(0), fOutputManager(outputManager), fRandom(0) {
   G4int n_particle = 1;
   fParticleGun = new G4ParticleGun(n_particle);
   fRandom = new TRandom3();

   // default particle kinematic
   G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
   /*[[[cog
   from MMconfig import *
   cog.outl('G4ParticleDefinition* particle = particleTable->FindParticle("{}");'.format(conf['general']['particle_type']))
   ]]]*/
   //[[[end]]]
   fParticleGun->SetParticleDefinition(particle);

}

PrimaryGeneratorAction::~PrimaryGeneratorAction() {
   delete fParticleGun;
}

double PrimaryGeneratorAction::GetIronSpectrumEnergy() {
   double rand = fRandom->Uniform(100);
   if (rand <= 68.76) {
      return 5.19 * keV;
   }
   if (rand <= 87.33) {
      return 5.89875 * keV;
   }
   if (rand <= 96.72) {
      return 5.88765 * keV;
   }
   return 6.49045 * keV;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent) {
   double particleEnergy = 0;
   /*[[[cog
   from MMconfig import *
   if conf['general']['particle_energy'] == 'fe55':
      cog.outl('particleEnergy = GetIronSpectrumEnergy();')
   else:
      cog.outl('particleEnergy = {} * keV;'.format(conf['general']['particle_energy']))
   ]]]*/
   //[[[end]]]

   G4double x0 = 0, y0 = 0;
   /*[[[cog
   from MMconfig import *
   cog.outl("G4double z0 = {} * cm + {} * cm + 1 * mm;".format(
      conf["particleconversion"]["z_cathode"],
      conf["detector"]["cathode_thickness"]
   ))
   ]]]*/
   //[[[end]]]

   fParticleGun->SetParticlePosition(G4ThreeVector(x0, y0, z0));
   fParticleGun->SetParticleEnergy(particleEnergy);
   G4ThreeVector momentum_direction = fParticleGun->GetParticleMomentumDirection();

   fOutputManager->SetPrimaryParticleProperties(momentum_direction.x(),
         momentum_direction.y(), momentum_direction.z(),
         particleEnergy / eV);

   /*
   G4double angle = G4UniformRand() * pi;
   fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0, 0, 1).rotateX(angle));
   */

   fParticleGun->GeneratePrimaryVertex(anEvent);
}
