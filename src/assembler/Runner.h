/*  Runner.h
 *
 *  Runner is a general class used to:
 *
 *  1) Initialize all the necessary classes
 *  2) get I/O
 *  3) run one or more cohort(s)
 *
 */

#ifndef RUNNER_H_
#define RUNNER_H_
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <deque>

#ifdef WITHMPI
#include <mpi.h>
#endif

#include "../data/RegionData.h"
#include "RunGrid.h"
#include "RunCohort.h"

#include "../runmodule/ModelData.h"
#include "../ArgHandler.h"

using namespace std;

class Runner {
public:
  Runner();
  ~Runner();

  int chtid;    /* currently-running 'cohort' id */
  int error;    /* error index */

  void initialize_regional_data(std::string filename);

  /* general initialization */
  void initInput(const string &controlfile, const string &runmode);
  void initOutput();
  void setupData();
  void setupIDs();

  /* three settings for running TEM */
  void single_site();  /* one site run-mode, used for stand-alone TEM
                         for any purpose */
  void regional_space_major();  /* multi-site (regional) with cohorts (spatial steps) as outer loop */
  void regional_time_major(int processors, int rank);  /* multi-site (regional) run-mode, time steps as outer loop(s) */
  int runSpatially(const int icalyr, const int im, const int jj);

  vector<int> runchtlist;  //a vector listing all cohort id
  vector<float> runchtlats;  //a vector of latitudes for all cohorts in
                             //  order of 'runchtlist'
  vector<float> runchtlons;  //a vector of longitudes for all cohorts in
                             //  order of 'runchtlist'

  /* all data record no. lists FOR all cohorts in 'runchtlist',
   *   IN EXACTLY SAME ORDER, for all !
   * the 'record' no. (starting from 0) is the order in the netcdf files
   * for all 'chort (cell)' in the 'runchtlist',
   * so, the length of all these lists are same as that of 'runchtlist'
   * will save time to search those real data ids if do the ordering in
   *   the first place
   * */

  /* from grided-data (geo-referenced only, or grid-level)*/
  vector<int> reclistgrid;
  vector<int> reclistdrain;
  vector<int> reclistsoil;
  vector<int> reclistgfire;

  /* from grided-/non-grided and time-series data (cohort-level)*/
  vector<int> reclistinit;
  vector<int> reclistclm;
  vector<int> reclistveg;
  vector<int> reclistfire;
  void set_calibrationMode(bool new_setting);
  bool get_calibrationMode();
  void modeldata_module_settings_from_args(const ArgHandler &args);

private:
  bool calibrationMode;

  std::string runmode;
  std::string loop_order;

  // Regional Data (applies to entire grid, but can be timeseries?)
  RegionData regionaldata;

  //TEM domains (hiarchy)
  RunGrid rungrd;
  RunCohort runcht;

  //data classes
  ModelData md;     /* model controls, options, switches and so on */

  EnvData  grded;   // grid-aggregated 'ed' (not yet done)
  BgcData  grdbd;   // grid-aggregared 'bd' (not yet done)

  EnvData  chted;   // withing-grid cohort-level aggregated 'ed'
                    //   (i.e. 'edall in 'cht')
  BgcData  chtbd;
  FirData  chtfd;

  deque<RestartData> mlyres;

  //util
  Timer timer;

  void createCohortList4Run();
  void createOutvarList(string & txtfile);

};
#endif /*RUNNER_H_*/
