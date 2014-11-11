/*
 * This class is used to run a cohort: from input to output
 *
 */

#ifndef RUNGRID_H_
#define RUNGRID_H_

#include <iostream>
#include <vector>
using namespace std;

#include "../runmodule/Grid.h"
#include "../runmodule/ModelData.h"
class RunGrid {
public:
  RunGrid();
  ~RunGrid();

  void setup_gridids_from_files(int recno);

  /* all grid data id lists
   * ids are labeling the datasets, which exist in .nc files
   * and, the order (index) in these lists are actually record no.
   * in the .nc files
   */
  vector<int> grdids;      // 'grid.nc'
  vector<int> grddrgids;
  vector<int> grdsoilids;
  vector<int> grdfireids;

  vector<int> drainids;    // 'drainage.nc'
  vector<int> soilids;     // 'soiltexture.nc'
  vector<int> gfireids;    // 'firestatistics.nc'

  /* The following is for ONE grid only (the grid for current cohort)
   *
   */
  int gridrecno;
  int drainrecno;
  int soilrecno;
  int gfirerecno;

  //
  Grid grid;

  void setModelData(ModelData * mdp);

  int allgridids();
  int readData();


private:
  ModelData *md;

};
#endif /*RUNGRID_H_*/
