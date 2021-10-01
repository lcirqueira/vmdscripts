"""
Script to setup a new system using CHARMM 36
and reducing number of water molecules.
"""
import numpy as np
import os
from random import sample
from pyvmd import *
from pylbtc.misc import evalbash, rmfile


CONCENTRATION = 50 #mM concentration
CONV_FACTOR = 1660 * 1000 #conversion factor to molecules / A^3 to mmol/L

PROT_PATH = "/home/lcirqueira/Simulations/ionchannel/kv1/kv1.12/jhosoume/namd"
PROT_IN = "kv1.12"
PROT_NUM = 13

LIG_PDB = "/home/lcirqueira/Simulations/repository/namd/charmm/pdb-drugs/propofol.pdb"
LIG_TOP = "/home/lcirqueira/Simulations/repository/charmm/other/anesthetics.top"

LIG_SEGNAME = "PPFL"
LIG_RESNAME = LIG_SEGNAME
LIG_UNIQUE_SEL = "C1"

OUT_NAME = "kv1.12.pfl.0"


evaltcl("""
package require psfgen
topology /home/lcirqueira/Simulations/namd/charmm/toppar_c36/top_all36_prot.rtf
topology /home/lcirqueira/Simulations/namd/charmm/toppar_c36/top_all36_lipid.rtf
topology /home/lcirqueira/Simulations/namd/charmm/toppar_c36/toppar_water_ions.str
topology {}
pdbalias residue HIS HSD
pdbalias atom ILE CD1 CD
pdbalias atom HOH O OH2
pdbalias residue HOH TIP3
       """.format(LIG_TOP))


dcdsys = System()
dcdsys.load("{}/{}.0.psf".format(PROT_PATH, PROT_IN))
dcdsys.load("{}/{}.{}.dcd".format(PROT_PATH, PROT_IN, PROT_NUM))
dcdsys.wrap("protein")
for frame in dcdsys.trajectory:
    dcdsys.all.moveby(-dcdsys.selectAtoms("resname POPC").center)

dcdsys.all.write("psf" , "nolig.psf")
dcdsys.all.write("pdb" , "nolig.pdb")

evaltcl("""
    readpsf nolig.psf
    coordpdb nolig.pdb
""")

nolig = System()
nolig.load("nolig.psf")
nolig.load("nolig.pdb")

mmax = nolig.selectAtoms("water").minmax()
volume = np.prod(mmax[1] - mmax[0])

lignum = int(volume * CONCENTRATION / CONV_FACTOR )

print("""ligand number to {}mM concentration:
{} ligands""".format(CONCENTRATION, lignum))

for i in range(lignum):
    evaltcl("""
        segment L{0} {{
            pdb {1}
        }}
        coordpdb {1} L{0}
    """.format(i, LIG_PDB))

evaltcl("""
guesscoord
writepsf wlig.psf
writepdb wlig.pdb
""")

allsys = System()
allsys.load("wlig.psf")
allsys.load("wlig.pdb")
ligsel = allsys.selectAtoms("resname {}".format(LIG_RESNAME))
lipsel = allsys.selectAtoms("resname POPC")

allsys.all.moveby(-lipsel.center)
ligsel["segname"] = LIG_SEGNAME

farwat = allsys.selectAtoms("name OH2 and not same residue as (water and (within 5 of (resname POPC or resname {} or protein)))".format(LIG_RESNAME))
wat_list = farwat["residue"]

unsel = allsys.selectAtoms("name {} and resname {}".format(LIG_UNIQUE_SEL , LIG_RESNAME))
res_list = unsel["residue"]

lignum = len(unsel)

resid = 1
for i in range(lignum):
    farwat = allsys.selectAtoms("name OH2 and not same residue as ((water and (within 10 of (resname POPC or protein))) and not (within 4 of resname {}))".format(LIG_RESNAME))
    wat_res = sample(farwat["residue"], 1)[0]
    watsel = allsys.selectAtoms("water and residue {}".format(wat_res))
    ligsel = allsys.selectAtoms("resname {} and residue {}".format(LIG_RESNAME, res_list[i]))
    ligsel.moveby(-ligsel.center + watsel.center)
    xangle , yangle, zangle = sample(range(0, 360) , 3)
    ligsel.rotate(xangle, yangle , zangle)
    ligsel["resid"] = resid
    resid += 1

savesel = allsys.selectAtoms("all and not (same residue as (water and name OH2 and within 2 of segname {}))".format(LIG_SEGNAME))

savesel.write("psf" , "{}.0.psf".format(OUT_NAME))
savesel.write("pdb" , "{}.0.pdb".format(OUT_NAME))

sysminmax = allsys.selectAtoms("water").minmax()[1] - allsys.selectAtoms("water").minmax()[0]
syscenter = allsys.all.center
sysdens = CONV_FACTOR * lignum / np.prod(sysminmax)
print("""minmax {}
center {}
density {}mM""".format(sysminmax, syscenter, sysdens))

os.remove("nolig.pdb")
os.remove("nolig.psf")
os.remove("wlig.pdb")
os.remove("wlig.psf")

quit()
