"""
Script to generate multiple configuration files for MD simulations.
"""

NAME = "kv1.12.pfl.0"
BEG, END = 1,2
DCDFREQ = 10000
STEPS = 500000
MINIMIZE_TERM = True
TCL_FORCES = False
CONSTRAINTS = False

template = """

# Structures
coordinates {2}.0.pdb
structure {2}.0.psf


# Restart files (Only for restart!!)
{0}bincoordinates {2}.{3}r.coor
{0}extendedsystem {2}.{3}r.xsc
{10}{0}binvelocities {2}.{3}r.vel


# Initial parameters
set temp 300
{1}temperature $temp			;# Only for initial
seed 12345


# Periodic Boundary Conditions
{1}cellBasisVector1	131.38899994	0.0 		0.0
{1}cellBasisVector2	0.0		138.55599976   	0.0
{1}cellBasisVector3	0.0		0.0		104.54100037
{1}cellOrigin	    	-0.21037145  0.32099348  4.74670172

# Harmonic constraints
constraints {12}
consexp 2
consref {2}.{4}.hrm
conskfile {2}.{4}.hrm
conskcol B
constraintScaling 1.0


# Output params
binaryoutput no
outputname {2}.{4}
outputenergies 10000
outputtiming 10000
outputpressure 10000
binaryrestart yes
dcdfile {2}.{4}.dcd
dcdfreq {6}
XSTFreq {7}
restartname {2}.{4}r
restartfreq {6}


# PME parameters
PME on
PMETolerance 10e-6
PMEInterpOrder 4
PMEGridSpacing 1.2


# Temperature control and equilibration
langevin on
langevintemp $temp
langevindamping 0.1
{1}reassignfreq 100			;# Only for initial
{1}reassigntemp 273			;# Only for initial
{1}reassignincr 0.06775		;# Only for initial
{1}reassignhold $temp			;# Only for initial


# Pressure control
usegrouppressure yes
useflexiblecell yes
langevinpiston on
langevinpistontarget 1
langevinpistonperiod 200
langevinpistondecay 100
langevinpistontemp $temp
surfacetensiontarget 0.0
strainrate 0. 0. 0.


# External eletric field
efieldon no
efield 0.0 0.0 0.058  #500mV


# brnch_root_list_opt
splitpatch hydrogen
hgroupcutoff 2.8


# Integrator params
timestep 2.0
fullElectFrequency 2
nonbondedfreq 1

# COLVARS SECTION
#colvars                 off
#colvarsConfig           colvar.conf


# Force field params
paratypecharmm on
parameters /home/lcirqueira/Simulations/namd/charmm/toppar_c36/par_all36_prot.prm
parameters /home/lcirqueira/Simulations/namd/charmm/toppar_c36/toppar_water_ions.str
parameters /home/lcirqueira/Simulations/namd/charmm/toppar_c36/par_all36_lipid.prm
parameters /home/lcirqueira/Simulations/repository/charmm/other/ppfl-all-iter1.par
exclude scaled1-4
1-4scaling 1.0
rigidbonds all
rigidtolerance 0.00001
rigiditerations 400
cutoff 11.0
pairlistdist 13.0
stepspercycle 16
switching on
switchdist 8.0

#script
tclforces {11}
set waterCheckFreq              100
set lipidCheckFreq              100
set allatompdb                  {2}.0.pdb
tclForcesScript                 keep_water_out.tcl

# Run
{9}minimize 800			;# Only for initial

{8}run {5}
"""

for i in range(BEG, END+1):
	with open("{}.{}.conf".format(NAME, i), "w") as fd:
		vel = ""
		if MINIMIZE_TERM:
			run = ""
			restart = "#" if i == 1 else ""
			initial = "" if i == 1 else "#"
			dcdfreq = 1000 if i == 1 else DCDFREQ
			steps = 40000 if i == 1 else STEPS
		else:
			if i == 1:
				run = "#"
				restart = "#"
				initial = ""
				dcdfreq = 100
				steps = 0
			else:
				run = ""
				restart = ""
				initial = "" if i == 2 else "#"
				vel = "#" if i == 2 else ""
				dcdfreq = 1000 if i == 2 else DCDFREQ
				steps = 40000 if i == 2 else STEPS
		minimize = "" if i == 1 else "#"
		steps = 40000 if i == 1 else STEPS
		xstfreq = 1000 if i <= 2 else DCDFREQ
		tclforces = "on" if TCL_FORCES else "off"
		constraints = "on" if CONSTRAINTS else "off"
		fd.write(template.format(restart, initial, NAME, i-1, i, steps, dcdfreq, xstfreq, run, minimize, vel, tclforces,constraints))
#resolver problema de ident : copiar linha anterior e substituir conteudo
