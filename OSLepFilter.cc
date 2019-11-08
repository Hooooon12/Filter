// -*- C++ -*-
//
// Package:    FourLepFilter
// Class:      FourLepFilter
//
/**\class FourLepFilter FourLepFilter.cc psi2s1s/FourLepFilter/src/FourLepFilter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  bian jianguo
//         Created:  Tue Nov 22 20:39:54 CST 2011
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"

#include <iostream>

//
// class declaration
//

class SSLepFilter : public edm::EDFilter {
public:
  explicit SSLepFilter(const edm::ParameterSet&);
  ~SSLepFilter() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  bool filter(edm::Event&, const edm::EventSetup&) override;

  // ----------member data ---------------------------

  edm::EDGetToken token_;
  double minPt;
  double maxEta;
  double maxPt;
  double minEta;
  int particleID;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
SSLepFilter::SSLepFilter(const edm::ParameterSet& iConfig)
    : token_(consumes<edm::HepMCProduct>(
          edm::InputTag(iConfig.getUntrackedParameter("moduleLabel", std::string("generator")), "unsmeared"))),
      minPt(iConfig.getUntrackedParameter("MinPt", 0.)),
      maxEta(iConfig.getUntrackedParameter("MaxEta", 10.)),
      maxPt(iConfig.getUntrackedParameter("MaxPt", 1000.)),
      minEta(iConfig.getUntrackedParameter("MinEta", 0.)),
      particleID(iConfig.getUntrackedParameter("ParticleID", 0)) {}

SSLepFilter::~SSLepFilter() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
}

//
// member functions
//

// ------------ method called on each new Event  ------------
bool SSLepFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;

  int LepCharge = 1;

  Handle<HepMCProduct> evt;
  iEvent.getByToken(token_, evt);
  const HepMC::GenEvent* myGenEvent = evt->GetEvent();

  for (HepMC::GenEvent::particle_const_iterator p = myGenEvent->particles_begin(); p != myGenEvent->particles_end();
       ++p) {
    if ((*p)->status() != 1) continue;

    if ((*p)->pdg_id()==11||(*p)->pdg_id()==13) LepCharge *= -1;
    else if ((*p)->pdg_id()==-11||(*p)->pdg_id()==-13) LepCharge *= 1;
  }

  if (LepCharge < 0) return true;
  else return false;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void SSLepFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(SSLepFilter);
