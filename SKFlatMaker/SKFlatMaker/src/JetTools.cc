#include "SKFlatMaker/SKFlatMaker/interface/JetTools.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/Math/interface/deltaPhi.h"
#include "fastjet/GhostedAreaSpec.hh"
#include "fastjet/ClusterSequenceArea.hh"
#include <TLorentzVector.h>
#include <TMath.h>
#include <TMatrixDSym.h>
#include <TMatrixDSymEigen.h>
#include <vector>

void JetTools::calcQGLVars(const reco::PFJet &jet, float &out_axis2, float &out_ptD, int &out_mult)
{
  // based on: RecoJets/JetProducers/plugins/QGTagger.cc
  float sum_weight = 0., sum_deta = 0., sum_dphi = 0., sum_deta2 = 0., sum_dphi2 = 0., sum_detadphi = 0., sum_pt = 0.;
  int mult = 0;

  const unsigned int nPFCands = jet.nConstituents ();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    float deta,dphi,partPt,charge=0;
    if(packCand != 0) { 
      charge = packCand->charge();
      deta   = packCand->eta() - jet.eta();
      dphi   = reco::deltaPhi(packCand->phi(), jet.phi());
      partPt = packCand->pt();
    } else { 
      const reco::PFCandidatePtr pfcand = jet.getPFConstituents().at(ipf);
      const reco::TrackRef       track  = pfcand->trackRef();
      // multiplicity = all charged particles + neutrals above 1 GeV
      if(track.isNull()) charge = 0;
      deta   = pfcand->eta() - jet.eta();
      dphi   = reco::deltaPhi(pfcand->phi(), jet.phi());
      partPt = pfcand->pt();
    }
    if((charge == 0 && partPt > 1) || charge != 0) mult++;
    float weight = partPt*partPt;
    sum_weight   += weight;
    sum_pt       += partPt;
    sum_deta     += deta*weight;
    sum_dphi     += dphi*weight;
    sum_deta2    += deta*deta*weight;
    sum_detadphi += deta*dphi*weight;
    sum_dphi2    += dphi*dphi*weight;
  }

  //Calculate axis2 and ptD
  float a = 0., b = 0., c = 0.;
  float ave_deta = 0., ave_dphi = 0., ave_deta2 = 0., ave_dphi2 = 0.;
  if(sum_weight > 0){
    ave_deta  = sum_deta/sum_weight;
    ave_dphi  = sum_dphi/sum_weight;
    ave_deta2 = sum_deta2/sum_weight;
    ave_dphi2 = sum_dphi2/sum_weight;
    a         = ave_deta2 - ave_deta*ave_deta;  			
    b         = ave_dphi2 - ave_dphi*ave_dphi;  			
    c         = -(sum_detadphi/sum_weight - ave_deta*ave_dphi); 	       
  }
  float delta = sqrt(fabs((a-b)*(a-b)+4*c*c));
  float axis2 = (a+b-delta > 0 ?  sqrt(0.5*(a+b-delta)) : 0);
  float ptD   = (sum_weight > 0 ? sqrt(sum_weight)/sum_pt : 0);

  out_axis2 = axis2;
  out_ptD   = ptD;
  out_mult  = mult;
}

void JetTools::calcQGLVars(const pat::Jet &jet, float &out_axis2, float &out_ptD, int &out_mult)
{
  std::vector<reco::Candidate const *> constituents;
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    reco::Candidate const *cand = jet.daughter(ida);
    if(cand->numberOfDaughters()==0) {  // AK8 jets in MINIAOD are SUBJETS
      constituents.emplace_back(cand);
    } else {
      for(unsigned int jda=0; jda<cand->numberOfDaughters(); jda++) {
        reco::Candidate const *cand2 = cand->daughter(jda);
        constituents.emplace_back(cand2);
      }
    }
  }
  std::sort(constituents.begin(), constituents.end(), [] (reco::Candidate const * ida, reco::Candidate const * jda) { return ida->pt() > jda->pt(); } );

  // based on: RecoJets/JetProducers/plugins/QGTagger.cc
  float sum_weight = 0., sum_deta = 0., sum_dphi = 0., sum_deta2 = 0., sum_dphi2 = 0., sum_detadphi = 0., sum_pt = 0.;
  int mult = 0;

  const unsigned int nPFCands = constituents.size();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const pat::PackedCandidate &pfcand = dynamic_cast<const pat::PackedCandidate &>(*constituents[ipf]);

    // multiplicity = all charged particles + neutrals above 1 GeV
    if(pfcand.charge()!=0) {
      if(pfcand.pt()>1) { mult++; }
    } else {
      mult++;
    }

    float deta   = pfcand.eta() - jet.eta();
    float dphi   = reco::deltaPhi(pfcand.phi(), jet.phi());
    float partPt = pfcand.pt();
    float weight = partPt*partPt;

    sum_weight   += weight;
    sum_pt       += partPt;
    sum_deta     += deta*weight;
    sum_dphi     += dphi*weight;
    sum_deta2    += deta*deta*weight;
    sum_detadphi += deta*dphi*weight;
    sum_dphi2    += dphi*dphi*weight;
  }

  //Calculate axis2 and ptD
  float a = 0., b = 0., c = 0.;
  float ave_deta = 0., ave_dphi = 0., ave_deta2 = 0., ave_dphi2 = 0.;
  if(sum_weight > 0){
    ave_deta  = sum_deta/sum_weight;
    ave_dphi  = sum_dphi/sum_weight;
    ave_deta2 = sum_deta2/sum_weight;
    ave_dphi2 = sum_dphi2/sum_weight;
    a         = ave_deta2 - ave_deta*ave_deta;
    b         = ave_dphi2 - ave_dphi*ave_dphi;
    c         = -(sum_detadphi/sum_weight - ave_deta*ave_dphi);
  }
  float delta = sqrt(fabs((a-b)*(a-b)+4*c*c));
  float axis2 = (a+b-delta > 0 ?  sqrt(0.5*(a+b-delta)) : 0);
  float ptD   = (sum_weight > 0 ? sqrt(sum_weight)/sum_pt : 0);

  out_axis2 = axis2;
  out_ptD   = ptD;
  out_mult  = mult;
}

double JetTools::angle_squared(const fastjet::PseudoJet& jet1, const fastjet::PseudoJet& jet2)  {
  return jet1.squared_distance(jet2);
}
double JetTools::e2_func(double beta, fastjet::contrib::EnergyCorrelator::Measure measurelist, fastjet::PseudoJet myjet ){
  fastjet::contrib::EnergyCorrelator ECF1(1,beta,measurelist);
  fastjet::contrib::EnergyCorrelator ECF2(2,beta,measurelist);
  double temp = ECF2(myjet)/(pow(ECF1(myjet),2));
  return temp;
}

double JetTools::e3_func(double beta, fastjet::contrib::EnergyCorrelator::Measure measurelist, fastjet::PseudoJet myjet ){
  fastjet::contrib::EnergyCorrelator ECF1(1,beta,measurelist);
  fastjet::contrib::EnergyCorrelator ECF3(3,beta,measurelist);
  double temp =  ECF3(myjet)/(pow(ECF1(myjet),3));
  return temp;
}
double JetTools::e3_vn_func(unsigned int n, double beta,fastjet::contrib::EnergyCorrelator::Measure measurelist, fastjet::PseudoJet myjet ) {
  // n is the number of angles here used in the function, so 1 for 1e3, 2 for 2e3 and 3 for the usual e3.
  int N_total = 3;
  double temp = 0.0;
  double angle1, angle2, angle3;
  fastjet::contrib::EnergyCorrelator ECF1(1,beta,measurelist);
  double EJ = ECF1(myjet);
  std::vector<fastjet::PseudoJet> jet_consts = myjet.constituents();
  for (unsigned int i = 0; i< jet_consts.size(); i++){
    for (unsigned int j = i + 1; j < jet_consts.size(); j++){
      for (unsigned int k = j + 1; k < jet_consts.size(); k++) {
	angle1 = pow(angle_squared(jet_consts[i], jet_consts[j]), beta/2.);
	angle2 = pow(angle_squared(jet_consts[i], jet_consts[k]), beta/2.);
	angle3 = pow(angle_squared(jet_consts[j], jet_consts[k]), beta/2.);
	// Let's sort the angles first, then figure out what to multiply
	double angle_list[] = {angle1, angle2, angle3};
	std::vector<double> angle_vector (angle_list, angle_list+N_total);
	std::sort (angle_vector.begin(), angle_vector.begin()+N_total);
	double angle = 1.0;
	for (unsigned int l=0 ; l<n; l++){angle = angle*angle_vector[l];}
	temp += ( jet_consts[i].pt() / EJ) * ( jet_consts[j].pt() / EJ)*( jet_consts[k].pt() / EJ) * angle;
      }
    }
  }
  return temp;
}
bool JetTools::orderPseudoJet(fastjet::PseudoJet j1, fastjet::PseudoJet j2) {
  // to be used to order pseudojets in decreasing pT order
  return j1.perp2() > j2.perp2();
}
float JetTools::leadPt(const pat::Jet &jet) {
  double lPt = -1;
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    double pPt = jet.daughter(ida)->pt();
    if(pPt < lPt) continue;
    lPt = pPt;
  }
  float lFPt = lPt;
  return lFPt;
}
float JetTools::leadPt(const reco::PFJet &jet) { 
  double lPt = -1;

  const unsigned int nPFCands = jet.nConstituents ();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    if(packCand != 0) { 
      if(lPt < packCand->pt()) lPt = packCand->pt();
    } else { 
      const reco::PFCandidatePtr pfcand    = jet.getPFConstituents().at(ipf);
      if(lPt < pfcand->pt()) lPt = pfcand->pt();
    }
  }
  float lFPt = lPt;
  return lFPt;
}
float JetTools::leadTrkPt(const pat::Jet &jet) {
  double lPt = -1;
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    double pPt = jet.daughter(ida)->pt();
    int pQ = jet.daughter(ida)->charge();
    if(pQ != 0 || pPt < lPt) continue;
    lPt = pPt;
  }
  float lFPt = lPt;
  return lFPt;
}
float JetTools::leadTrkPt(const reco::PFJet &jet) { 
  double lPt = -1;

  const unsigned int nPFCands = jet.nConstituents ();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    if(packCand != 0) { 
      if(packCand->charge() != 0 || lPt < packCand->pt()) lPt = packCand->pt();
    } else { 
      const reco::PFCandidatePtr pfcand    = jet.getPFConstituents().at(ipf);
      if(pfcand->charge() != 0 || lPt < pfcand->pt()) lPt = pfcand->pt();
    }
  }
  float lFPt = lPt;
  return lFPt;
}
int JetTools::nDaughters(const pat::Jet &jet,float minPt) {
  int numDaughters = 0;
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    if (jet.daughter(ida)->pt()>minPt) numDaughters++;
  }
  return numDaughters;
}
int JetTools::nDaughters(const reco::PFJet &jet,float minPt) {
  int numDaughters = 0;
  const unsigned int nPFCands = jet.nConstituents();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    if(packCand != 0) {
      if(packCand->pt() > minPt) numDaughters++;
    } else {
      if(jet.getPFConstituents().at(ipf)->pt() > minPt) numDaughters++;
    }
  }
  return numDaughters;
}
void JetTools::energyRings(const pat::Jet &jet,std::vector<float> &chvec,std::vector<float> &emvec,std::vector<float> &nevec,std::vector<float> &muvec) {
  float cone_boundaries[] = { 0.05, 0.1, 0.2, 0.3, 0.4 }; // hardcoded boundaries: should be made configurable
  size_t ncone_boundaries = sizeof(cone_boundaries)/sizeof(float);
  std::vector<float> chEnergies(ncone_boundaries+1,0.);
  std::vector<float> emEnergies(ncone_boundaries+1,0.); 
  std::vector<float> neEnergies(ncone_boundaries+1,0.); 
  std::vector<float> muEnergies(ncone_boundaries+1,0.);
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    const reco::Candidate* pPart = jet.daughter(ida);
    float candDr = reco::deltaR(jet.eta(),jet.phi(),pPart->eta(),pPart->phi());
    int pdgid = abs(pPart->pdgId());
    size_t icone = std::lower_bound(&cone_boundaries[0],&cone_boundaries[ncone_boundaries],candDr) - &cone_boundaries[0];
    float candEnergy = pPart->energy();
    if( pdgid == 22 || pdgid == 11 ) {
       // std::cout << " fill EM" << std::endl;
       emEnergies[icone] += candEnergy;
    } else if ( pdgid == 13 ) { 
       // std::cout << " fill mu" << std::endl;
       muEnergies[icone] += candEnergy;
    } else if ( pPart->charge() != 0 ) {
       // std::cout << " fill ch" << std::endl;
      chEnergies[icone] += candEnergy;
    } else {
      // std::cout << " fill ne" << std::endl;
      neEnergies[icone] += candEnergy;
    }
  }
  chvec = chEnergies;
  emvec = emEnergies;
  nevec = neEnergies;
  muvec = muEnergies;
}
void JetTools::energyRings(const reco::PFJet &jet,std::vector<float> &chvec,std::vector<float> &emvec,std::vector<float> &nevec,std::vector<float> &muvec) {
  float cone_boundaries[] = { 0.05, 0.1, 0.2, 0.3, 0.4 }; // hardcoded boundaries: should be made configurable
  size_t ncone_boundaries = sizeof(cone_boundaries)/sizeof(float);
  std::vector<float> chEnergies(ncone_boundaries+1,0.);
  std::vector<float> emEnergies(ncone_boundaries+1,0.); 
  std::vector<float> neEnergies(ncone_boundaries+1,0.); 
  std::vector<float> muEnergies(ncone_boundaries+1,0.);
  const unsigned int nPFCands = jet.nConstituents ();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    float candDr = 0.;
    int pdgid = 0;
    float candEnergy = 0.;
    int candCharge = 0;
    if(packCand != 0) { 
      candDr = reco::deltaR(jet.eta(),jet.phi(),packCand->eta(),packCand->phi());
      pdgid = abs(packCand->pdgId());
      candEnergy = packCand->energy();
      candCharge = packCand->charge();      
    } else { 
      const reco::PFCandidatePtr pfcand    = jet.getPFConstituents().at(ipf);
      candDr = reco::deltaR(jet.eta(),jet.phi(),pfcand->eta(),pfcand->phi());
      pdgid = abs(pfcand->pdgId());
      candEnergy = pfcand->energy();
      candCharge = pfcand->charge();      
    }
    size_t icone = std::lower_bound(&cone_boundaries[0],&cone_boundaries[ncone_boundaries],candDr) - &cone_boundaries[0];
    if( pdgid == 22 || pdgid == 11 ) {
       // std::cout << " fill EM" << std::endl;
       emEnergies[icone] += candEnergy;
    } else if ( pdgid == 13 ) { 
       // std::cout << " fill mu" << std::endl;
       muEnergies[icone] += candEnergy;
    } else if ( candCharge != 0 ) {
       // std::cout << " fill ch" << std::endl;
      chEnergies[icone] += candEnergy;
    } else {
      // std::cout << " fill ne" << std::endl;
      neEnergies[icone] += candEnergy;
    }
  }
  chvec = chEnergies;
  emvec = emEnergies;
  nevec = neEnergies;
  muvec = muEnergies;
}
float JetTools::leptons(const reco::GenJet &jet,int iId) {
  TLorentzVector lVec; lVec.SetPtEtaPhiM(0.,0.,0.,0.);
  double lPt(-1), lEta(-1), lPhi(-1), lId(-1);
  double lPx(-1), lPy(-1), lPz(-1), lP(-1);
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    const reco::Candidate* pPart = jet.daughter(ida);
    if(fabs(pPart->pdgId()) != 11 && fabs(pPart->pdgId()) != 13) continue;
    if(pPart->pt() > lPt) { 
      lPt = pPart->pt(); 
      lEta = pPart->eta();
      lPhi = pPart->phi();
      lPx = pPart->px();
      lPy = pPart->py();
      lPz = pPart->pz();
      lP = pPart->p();
      lId = fabs(pPart->pdgId()); }
    TLorentzVector pVec; pVec.SetPtEtaPhiM(pPart->pt(),pPart->eta(),pPart->phi(),pPart->mass());
    lVec += pVec;
  }
  if(iId == 1) { 
    TVector3 lProj(jet.px(),jet.py(),jet.pz());
    return float(lVec.Perp(lProj));
  }
  if(iId == 2) {
    float pDPhi = fabs(jet.phi()-lVec.Phi());
    if(pDPhi > 2.*TMath::Pi()-pDPhi) pDPhi = 2.*TMath::Pi()-pDPhi;
    float pDEta = fabs(jet.eta()-lVec.Eta());
    return sqrt(pDPhi*pDPhi+pDEta*pDEta);
  }
  if(iId == 3) {
    float lLPt = lPt;
    return lLPt;
  }
  if(iId == 4) {
    float lLId = lId;
    return lLId;
  }
  if(iId == 5) {
    float lLEta = lEta;
    return lLEta;
  }
  if(iId == 6) {
    float lLPhi = lPhi;
    return lLPhi;
  }
  if(iId == 7){
    float lepjetdr = reco::deltaR(jet.eta(),jet.phi(),lEta,lPhi);
    return std::max(float(0.),lepjetdr);
  }
  if(iId == 8){
    float softLepPtRel = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / jet.p();
    softLepPtRel = sqrt( lP*lP - softLepPtRel*softLepPtRel );
    return std::max(float(0.),softLepPtRel);
  }
  if(iId == 9){
    float softLepPtRelInv = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / lP;
    softLepPtRelInv = sqrt( jet.p()*jet.p() - softLepPtRelInv*softLepPtRelInv );
    return std::max(float(0.),softLepPtRelInv);
  }
  float lFPt = lVec.Pt();
  return lFPt;
}
float JetTools::leptons(const pat::Jet &jet,int iId) {
  TLorentzVector lVec; lVec.SetPtEtaPhiM(0.,0.,0.,0.);
  double lPt(-1), lEta(-1), lPhi(-1), lId(-1);
  double lPx(-1), lPy(-1), lPz(-1), lP(-1);
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    const reco::Candidate* pPart = jet.daughter(ida);
    if(fabs(pPart->pdgId()) != 11 && fabs(pPart->pdgId()) != 13) continue;
    if(pPart->pt() > lPt) { 
      lPt = pPart->pt(); 
      lEta = pPart->eta();
      lPhi = pPart->phi();
      lPx = pPart->px();
      lPy = pPart->py();
      lPz = pPart->pz();
      lP = pPart->p();
      lId = fabs(pPart->pdgId()); }
    TLorentzVector pVec; pVec.SetPtEtaPhiM(pPart->pt(),pPart->eta(),pPart->phi(),pPart->mass());
    lVec += pVec;
  }
  if(iId == 1) { 
    TVector3 lProj(jet.px(),jet.py(),jet.pz());
    return float(lVec.Perp(lProj));
  }
  if(iId == 2) {
    float pDPhi = fabs(jet.phi()-lVec.Phi());
    if(pDPhi > 2.*TMath::Pi()-pDPhi) pDPhi = 2.*TMath::Pi()-pDPhi;
    float pDEta = fabs(jet.eta()-lVec.Eta());
    return sqrt(pDPhi*pDPhi+pDEta*pDEta);
  }
  if(iId == 3) {
    float lLPt = lPt;
    return lLPt;
  }
  if(iId == 4) {
    float lLId = lId;
    return lLId;
  }
  if(iId == 5) {
    float lLEta = lEta;
    return lLEta;
  }
  if(iId == 6) {
    float lLPhi = lPhi;
    return lLPhi;
  }
  if(iId == 7){
    float lepjetdr = reco::deltaR(jet.eta(),jet.phi(),lEta,lPhi);
    return std::max(float(0.),lepjetdr);
  }
  if(iId == 8){
    float softLepPtRel = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / jet.p();
    softLepPtRel = sqrt( lP*lP - softLepPtRel*softLepPtRel );
    return std::max(float(0.),softLepPtRel);
  }
  if(iId == 9){
    float softLepPtRelInv = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / lP;
    softLepPtRelInv = sqrt( jet.p()*jet.p() - softLepPtRelInv*softLepPtRelInv );
    return std::max(float(0.),softLepPtRelInv);
  }
  float lFPt = lVec.Pt();
  return lFPt;
}
float JetTools::leptons(const reco::PFJet &jet,int iId) {
  TLorentzVector lVec; lVec.SetPtEtaPhiM(0.,0.,0.,0.);
  double lPt(-1), lEta(-1), lPhi(-1), lId(-1);
  double lPx(-1), lPy(-1), lPz(-1), lP(-1);
  const unsigned int nPFCands = jet.nConstituents ();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    if(packCand != 0) { 
      if(fabs(packCand->pdgId()) != 11 && fabs(packCand->pdgId()) != 13) continue;
      if(packCand->pt() > lPt) { 
	lPt = packCand->pt(); 
	lEta = packCand->eta();
	lPhi = packCand->phi();
        lPx = packCand->px();
        lPy = packCand->py();
        lPz = packCand->pz();
        lP = packCand->p();
	lId = fabs(packCand->pdgId()); 
      }
      TLorentzVector pVec; pVec.SetPtEtaPhiM(packCand->pt(),packCand->eta(),packCand->phi(),packCand->mass());
      lVec += pVec;
    } else {
      const reco::PFCandidatePtr pfcand    = jet.getPFConstituents().at(ipf);
      if(fabs(pfcand->pdgId()) != 11 && fabs(pfcand->pdgId()) != 13) continue;
      if(pfcand->pt() > lPt) { 
	lPt = pfcand->pt();
	lEta = pfcand->eta();
        lPhi = pfcand->phi();
        lPx = pfcand->px();
        lPy = pfcand->py();
        lPz = pfcand->pz();
        lP = pfcand->p();
	lId = fabs(pfcand->pdgId()); 
      }
      TLorentzVector pVec; pVec.SetPtEtaPhiM(pfcand->pt(),pfcand->eta(),pfcand->phi(),pfcand->mass());
      lVec += pVec;
    }
  }
  if(iId == 1) { 
    TVector3 lProj(jet.px(),jet.py(),jet.pz());
    return float(lVec.Perp(lProj));
  }
  if(iId == 2) {
    float pDPhi = fabs(jet.phi()-lVec.Phi());
    if(pDPhi > 2.*TMath::Pi()-pDPhi) pDPhi = 2.*TMath::Pi()-pDPhi;
    float pDEta = fabs(jet.eta()-lVec.Eta());
    return sqrt(pDPhi*pDPhi+pDEta*pDEta);
  }
  if(iId == 3) {
    float lLPt = lPt;
    return lLPt;
  }
  if(iId == 4) {
    float lLId = lId;
    return lLId;
  }
  if(iId == 5) {
    float lLEta = lEta;
    return lLEta;
  }
  if(iId == 6) {
    float lLPhi = lPhi;
    return lLPhi;
  }
  if(iId == 7){
    float lepjetdr = reco::deltaR(jet.eta(),jet.phi(),lEta,lPhi);
    return std::max(float(0.),lepjetdr);
  }
  if(iId == 8){
    float softLepPtRel = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / jet.p();
    softLepPtRel = sqrt( lP*lP - softLepPtRel*softLepPtRel );
    return std::max(float(0.),softLepPtRel);
  }
  if(iId == 9){
    float softLepPtRelInv = ( jet.px()*lPx + jet.py()*lPy + jet.pz()*lPz ) / lP;
    softLepPtRelInv = sqrt( jet.p()*jet.p() - softLepPtRelInv*softLepPtRelInv );
    return std::max(float(0.),softLepPtRelInv);
  }
  float lFPt = lVec.Pt();
  return lFPt;  
}
float JetTools::ptD(const pat::Jet &jet) {
  float sumWeight=0;
  float sumPt=0;
  for(unsigned int ida=0; ida<jet.numberOfDaughters(); ida++) {
    float dpt = jet.daughter(ida)->pt();
    sumWeight+=(dpt*dpt);
    sumPt+=dpt;
  }
  return (sumWeight > 0 ? sqrt(sumWeight)/sumPt : 0.);
}
float JetTools::ptD(const reco::PFJet &jet) {
  float sumWeight=0;
  float sumPt=0;
  const unsigned int nPFCands = jet.nConstituents();
  for(unsigned int ipf=0; ipf<nPFCands; ipf++) {
    const reco::Candidate* cand = jet.getJetConstituentsQuick ()[ipf];
    const pat::PackedCandidate *packCand = dynamic_cast<const pat::PackedCandidate *>(cand);
    float dpt = 0;
    if(packCand != 0) {
      dpt = packCand->pt();
    } else {
      dpt = jet.getPFConstituents().at(ipf)->pt();
    }
    sumWeight+=(dpt*dpt);
    sumPt+=dpt;
  }
  return (sumWeight > 0 ? sqrt(sumWeight)/sumPt : 0.);
}
//JetTools::lsf(lClusterParticles, vSubC_3, lepCPt, lepCEta, lepCPhi, lepCId, 2.0, 3);
float JetTools::lsf(std::vector<fastjet::PseudoJet> iCParticles, std::vector<fastjet::PseudoJet> &ljets, 
		    float ilPt, float ilEta, float ilPhi, int ilId, double dr, int nsj, int iId) {
  float lsf(-100),lmd(-100);
  if(ilPt>0 && (ilId == 11 || ilId == 13)) {    
    TLorentzVector ilep; 
    if(ilId == 11) ilep.SetPtEtaPhiM(ilPt, ilEta, ilPhi, 0.000511);
    if(ilId == 13) ilep.SetPtEtaPhiM(ilPt, ilEta, ilPhi, 0.105658);
    fastjet::JetDefinition lCJet_def(fastjet::kt_algorithm, dr);
    fastjet::ClusterSequence lCClust_seq(iCParticles, lCJet_def);
    if (dr > 0.5) {
      ljets = sorted_by_pt(lCClust_seq.exclusive_jets_up_to(nsj));
    }
    else {
      ljets = sorted_by_pt(lCClust_seq.inclusive_jets());
    }
    int lId(-1);
    double dRmin = 999.;
    for (unsigned int i0=0; i0<ljets.size(); i0++) {
      double dR = reco::deltaR(ljets[i0].eta(), ljets[i0].phi(), ilep.Eta(), ilep.Phi());
      if ( dR < dRmin ) {
	dRmin = dR;
	lId = i0;
      }
    }
    if(lId != -1) {
      TLorentzVector pVec; pVec.SetPtEtaPhiM(ljets[lId].pt(), ljets[lId].eta(), ljets[lId].phi(), ljets[lId].m());
      lsf = ilep.Pt()/pVec.Pt();
      lmd = (ilep-pVec).M()/pVec.M();
    }
    if(iId == 1) {
      return lmd;
    }
  }
  return lsf;
}

