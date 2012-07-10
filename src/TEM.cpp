/**
 *  TEM.cpp
 *  main program for running DVM-DOS-TEM
 *  
 *  It runs at 3 run-mods:
 *      (1) site-specific
 *      (2) regional - time series
 * 		(3) regional - spatially (not yet available)
 * 
 * Authors: Shuhua Yi - the original codes
 * 		    Fengming Yuan - re-designing and re-coding for (1) easily code managing;
 *                                        (2) java interface developing for calibration;
 *                                        (3) stand-alone application of TEM (java-c++)
 *                                        (4) inputs/outputs using netcdf format, have to be modified
 *                                        to fix memory-leaks
 *                                        (5) fix the snow/soil thermal/hydraulic algorithms
 *                                        (6) DVM coupled
 *
 * Affilation: Spatial Ecology Lab, University of Alaska Fairbanks 
 *
 * started: 11/01/2010
 * last modified: 06/25/2012
*/

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <ctime>
#include <cstdlib>
#include <exception>
using namespace std;

#include "assembler/Runner.h"

// defines the mode of run: Single-site or Multiple-site (regional)
#define SITERUN
//#define REGNRUN

int main(int argc, char* argv[]){

	setvbuf(stdout, NULL, _IONBF, 0); // no buffering
	setvbuf(stderr, NULL, _IONBF, 0); // no buffering

	#ifdef SITERUN 
		time_t stime;
		time_t etime;
		stime=time(0);
		cout<<"run TEM stand-alone - start @"<<ctime(&stime)<<"\n";

		string controlfile="";
		string chtid = "1";    /* default chtid 1 for siter-runmode  */
		if(argc == 1){   //if there is no control file specified
			controlfile ="config/controlfile_site.txt";
		} else if(argc == 2) { // if only control file specified
			controlfile = argv[1];
		} else if(argc == 3) { // both control file and chtid specified in the order
			controlfile = argv[1];
			chtid = argv[2];
		}

		Runner siter;

		siter.chtid = atoi(chtid.c_str());

		siter.initInput(controlfile, "siter");

		siter.initOutput();

 		siter.setupData();

 		siter.setupIDs();

 		siter.runmode1();
 
 		etime=time(0);
		cout <<"run TEM stand-alone - done @"<<ctime(&etime)<<"\n";
		cout <<"total seconds: "<<difftime(etime, stime)<<"\n";
	#endif

	#ifdef REGNRUN
		time_t stime;
		time_t etime;
		stime=time(0);
		cout <<"run TEM regionally - start @"<<ctime(&stime)<<"\n";

		string controlfile="";
		string runmode = "regner2";
		if(argc == 1){ //if there is no control file specified
			controlfile ="config/controlfile_regn.txt";
		} else if(argc == 2) {
			controlfile = argv[1];
		} else if (argc == 3) {   // both control file and runmode specified in order
			controlfile = argv[1];
			runmode     = argv[2];
		}

		Runner regner;

		regner.initInput(controlfile, runmode);

		regner.initOutput();

		regner.setupData();

		regner.setupIDs();

 		if (runmode.compare("regner1")==0) {
 			regner.runmode2();
 		} else if (runmode.compare("regner2")==0){
 			regner.runmode3();
		} else {
			cout <<"run-mode for TEM regional run must be: \n";
			cout <<" EITHER 'regner1' OR 'regner2' \n";
			exit(-1);
		}

		etime=time(0);
		cout <<"run TEM regionally - done @"<<ctime(&etime)<<"\n";
		cout <<"total seconds: "<<difftime(etime, stime)<<"\n";

	#endif

	return 0;

};
