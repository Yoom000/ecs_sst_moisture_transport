
contact: aym0466@hanyang.ac.kr

# East China Sea SST Variability and Moisture Flux into the Korean Peninsula

This project investigates the relationship between East China Sea (ECS) summer sea surface temperature (SST) variability and low-level moisture transport into the Korean Peninsula using ERA5 reanalysis data.

The workflow reproduces the methodology of the study, including SST event definition, moisture flux calculation, t-test, and composite analysis


##Project Structure
├── main.py
├── requirements.txt
├── module/
│ ├── sst_event_definition/
│ ├── moisture_flux/
│ └── t_test/
├── composites/
├── plot/
└── data/

- module/ contains the core calculation (eg. SST climatology, moisture_flux, t-test) 
- composites/ contains codes for composite analysis .
- plot/ contains codes used to generate figures.


##Objective
The code package consists of five main steps:

    1. Compute JJA SST climatology 
    2. Compute JJA ECS SST anomaly
    3. Define high/low SST years (HSST / LSST) using ±1 standard deviation
    4. Perform two-sample t-test to evaluate statistical significance
    5. Composite analysis (IWV, LHF, SLP, wind fields) 


##Workflow
Step 1 — Main analysis

Run python main.py 

	This performs:

	- SST climatology & anomaly calculation

	- HSST / LSST classification

	- Moisture flux integration (Qw, Qs)

	- Q flux t-test 

	Results are saved to: (data/interim/) and (data/final)


# (Plotting codes in Step 2 and 3 use resulting data file from step1, so make sure you run main.py first)


Step 2 - Plotting figures(optional)

	After running main.py, figures can be plotted by scripts in: 

        plot/plotting_code/

	- The plotted figure will be saved in plot/ as .png
        

Step 3 - Composite analysis

	Composite analysis of climate variables can be run from:

	composites/
	
	-The plotted figure will be saved in plot/ as .png

##Data

ERA5 climate data are used in this study. 
Download available at: https://cds.climate.copernicus.eu/datasets

The following ERA5 raw data files (.nc) must exist in data/raw:

	1. Monthly averaged data on single levels
		1.1 Sea surface temperature 
		1.2 Latent heat flux 
		1.3 Sea level pressure 
	2. Monthly averaged data on pressure levels (In this study every pressure level between 1000hPa to 850 hPa are used)
		2.1 u/v wind component
		2.2 Specific humidity
	
##Environment

Developed and tested in Python 3.11.

Required packages:

numpy
pandas
xarray
scipy
matplotlib
netCDF4
cartopy

Install using:

pip install -r requirements.txt


For stable installation of cartopy, installation via conda is recommended:

conda install -c conda-forge numpy pandas xarray scipy matplotlib netcdf4 cartopy



