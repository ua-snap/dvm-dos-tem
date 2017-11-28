#ifndef COHORT_H_
#define COHORT_H_

#include "Climate.h"

#include "../src/ecodomain/Ground.h"
#include "../src/ecodomain/Vegetation.h"

#include "../src/vegetation/Vegetation_Env.h"
#include "../src/vegetation/Vegetation_Bgc.h"

#include "../src/snowsoil/Snow_Env.h"
#include "../src/snowsoil/Soil_Env.h"
#include "../src/snowsoil/SoilParent_Env.h"
#include "../src/snowsoil/Soil_Bgc.h"

#include "WildFire.h"

#include "CohortData.h"

#include "EnvData.h"
#include "BgcData.h"
#include "FireData.h"

#include "RestartData.h"

#include "CohortLookup.h"

#include "../src/runmodule/Integrator.h"

// headers for run
#include "ModelData.h"

class Cohort {
public :
  Cohort();
  Cohort(int y, int x, ModelData* modeldatapointer);
  ~Cohort();
  
  int y;
  int x;

  float lon;
  float lat;

  // model running status
  int errorid;
  bool failed;    // when an exception is caught, set failed to be true

  /*
    Note: FRI is a member of CohortData because it is checked in
    Soil_Bgc::prepareintegration(...), and at that point there is no access to
    the members/fields of a Cohort...
  */

  // old? can I deprecate these??
  //double pfsize[NUM_FSIZE];
  //double pfseason[NUM_FSEASON];
  
  //inputs
  CohortLookup chtlu;

  // domain
  Vegetation veg;
  Ground ground;
  
  // new domain
  Climate climate;

  // processes
  Vegetation_Env vegenv[NUM_PFT];
  Snow_Env snowenv;
  Soil_Env soilenv;
  SoilParent_Env solprntenv;

  Vegetation_Bgc vegbgc[NUM_PFT];
  Soil_Bgc soilbgc;

  WildFire fire;

  // data
  EnvData ed[NUM_PFT];
  BgcData bd[NUM_PFT];
  EnvData * edall;
  BgcData * bdall;

  FirData year_fd[12]; //Monthly fire data, for all PFTs and soil
  FirData * fd;   //Fire data for an individual month 

  ModelData * md;

  CohortData cd;
  RestartData restartdata;
  

//  void NEW_load_climate_from_file(int y, int x);
//  void NEW_load_veg_class_from_file(int y, int x);
//  void NEW_load_fire_from_file(int y, int x);

  void initialize_internal_pointers();

  void setModelData(ModelData* md);
  void setProcessData(EnvData * alledp, BgcData * allbdp, FirData *fdp);

  void initialize_state_parameters();
  //void prepareAllDrivingData();
  //void prepareDayDrivingData(const int & yrcnt, const int &usedatmyr);
  void updateMonthly(const int & yrcnt, const int & currmind,
                     const int & dinmcurr, std::string stage);
  
  void set_state_from_restartdata();
  void set_restartdata_from_state();

  void load_proj_climate(const std::string&);//Provides data to Climate for loading proj data

private:

  Integrator vegintegrator[NUM_PFT];
  Integrator solintegrator;


  void updateMonthly_DIMveg(const int & currmind, const bool & dvmmodule);
  void updateMonthly_DIMgrd(const int & currmind, const bool & dslmodule);

  void updateMonthly_Env(const int & currmind, const int & dinmcurr);
  void updateMonthly_Bgc(const int & currmind);
  void updateMonthly_Dsb(const int & yrcnt, const int & currmind, std::string stage);

  // Fire is a type of disturbance
  void updateMonthly_Fir(const int & year, const int & midx, std::string stage);

  // update root distribution
  void getSoilFineRootFrac_Monthly();
  double assignSoilLayerRootFrac(const double & topz, const double & botz,
                                 const double csumrootfrac[MAX_ROT_LAY],
                                 const double dzrotlay[MAX_ROT_LAY]);

  //
  void assignAtmEd2pfts_daily();
  void assignGroundEd2pfts_daily();
  void getSoilTransfactor4all_daily();
  void getEd4allveg_daily();
  void getEd4land_daily();

  void assignSoilBd2pfts_monthly();
  void getBd4allveg_monthly();

};
#endif /*COHORT_H_*/
