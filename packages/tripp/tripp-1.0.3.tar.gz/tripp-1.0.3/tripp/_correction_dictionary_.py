"""
    This file is part of the TrIPP software
    (https://github.com/fornililab/TrIPP).
    Copyright (c) Christos Matsingos, Ka Fu Man and Arianna Fornili.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

# Contains residue names recognised by MDAnalysis and
# associates them with residue names recognised by PROPKA
corrected_amino_acids = {
    "ARGN": "ARG",
    "ASN1": "ASN",
    "ASPH": "ASP",
    "ASPP": "ASP",
    "CALA": "ALA",
    "CARG": "ARG",
    "CASF": "ASP",
    "CASN": "ASN",
    "CASP": "ASP",
    "CCYS": "CYS",
    "CCYX": "CYS",
    "CGLN": "GLN",
    "CGLU": "GLU",
    "CGLY": "GLY",
    "CHID": "HIS",
    "CHIE": "HIS",
    "CHIP": "HIS",
    "CILE": "ILE",
    "CLEU": "LEU",
    "CLYS": "LYS",
    "CMET": "MET",
    "CPHE": "PHE",
    "CPRO": "PRO",
    "CSER": "SER",
    "CTHR": "THR",
    "CTRP": "TRP",
    "CTYR": "TYR",
    "CVAL": "VAL",
    "CYS1": "CYS",
    "CYS2": "CYS",
    "CYSH": "CYS",
    "GLUH": "GLU",
    "GLUP": "GLU",
    "HIS1": "HIS",
    "HIS2": "HIS",
    "HISA": "HIS",
    "HISB": "HIS",
    "HISD": "HIS",
    "HISE": "HIS",
    "HISH": "HIS",
    "LYSH": "LYS",
    "NALA": "ALA",
    "NARG": "ARG",
    "NASN": "ASN",
    "NASP": "ASP",
    "NCYS": "CYS",
    "NCYX": "CYS",
    "NGLN": "GLY",
    "NGLU": "GLU",
    "NGLY": "GLY",
    "NHID": "HIS",
    "NHIE": "HIS",
    "NHIP": "HIS",
    "NILE": "ILE",
    "NLEU": "LEU",
    "NLYS": "LYS",
    "NMET": "MET",
    "NPHE": "PHE",
    "NPRO": "PRO",
    "NSER": "SER",
    "NTHR": "THR",
    "NTRP": "TRP",
    "NTYR": "TYR",
    "NVAL": "VAL",
    "ASF": "ASP",
    "ASH": "ASP",
    "CYM": "CYS",
    "CYN": "CYS",
    "CYX": "CYS",
    "GLH": "GLU",
    "HID": "HIS",
    "HIE": "HIS",
    "HIP": "HIS",
    "HSD": "HIS",
    "HSE": "HIS",
    "HSP": "HIS",
}
# Dictionary for correcting C-terminal oxygen atoms to O and OXT
# for GROMOS, AMBER, and CHARMM force fields.
corrected_atom_names = {
    "O1": "O",  # COO- (GROMOS)
    "O2": "OXT",  # COO- (GROMOS)
    "OT": "OXT",  # COOH (GROMOS)
    "OC1": "O",  # COO- (AMBER)
    "OC2": "OXT",  # COO- (AMBER)
    "OT1": "O",  # COO- (CHARMM)
    "OT2": "OXT",  # COO- (CHARMM)
}
