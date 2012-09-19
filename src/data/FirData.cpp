#include "FirData.h"

FirData::FirData(){
	ysf=0;
	fire_a2soi.orgn=0;
	useseverity =false;
};

FirData::~FirData(){
	
};

void FirData::clear(){
    ysf         = 0;
    useseverity = false;

	fire_soid = soidiag_fir();

	fire_v2a  = veg2atm_fir();
	fire_v2soi= veg2soi_fir();

	fire_soi2a= soi2atm_fir();
	fire_a2soi= atm2soi_fir();

};

void FirData::init(){
	ysf =0;
};

void FirData::beginOfYear(){
	fire_soid.burnthick =0.;

	fire_v2a.orgc =0.;
	fire_v2a.orgn =0.;

	fire_v2soi.abvc =0.;
	fire_v2soi.blwc =0.;
	fire_v2soi.abvn =0.;
	fire_v2soi.blwn =0.;

	fire_soi2a.orgc =0.;
	fire_soi2a.orgn =0.;
	
};

void FirData::endOfYear(){
	ysf++;
};

void FirData::burn(){
	ysf=0;
}
