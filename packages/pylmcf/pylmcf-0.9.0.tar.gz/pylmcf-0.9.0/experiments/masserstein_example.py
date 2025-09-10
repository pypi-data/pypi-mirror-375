#!/usr/bin/env python


from copy import deepcopy
import scipy as sp
import numpy as np
from matplotlib import pyplot as plt


myoglobin = """GLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASE
DLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKH
PGDFGADAQGAMNKALELFRKDMASNYKELGFQG"""
haemoglobinB = """VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPK
VKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFG
KEFTPPVQAAYQKVVAGVANALAHKYH"""
haemoglobinA = """VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG
KKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTP
AVHASLDKFLASVSTVLTSKYR"""


from masserstein import peptides

haemoglobinA_formula = peptides.get_protein_formula(haemoglobinA)
haemoglobinB_formula = peptides.get_protein_formula(haemoglobinB)
myoglobin_formula = peptides.get_protein_formula(myoglobin)


from masserstein import Spectrum

hA19 = Spectrum(haemoglobinA_formula, charge=19, adduct="H", label="hA 19+")
hA20 = Spectrum(haemoglobinA_formula, charge=20, adduct="H", label="hA 20+")
hA21 = Spectrum(haemoglobinA_formula, charge=21, adduct="H", label="hA 21+")
hB20 = Spectrum(haemoglobinB_formula, charge=20, adduct="H", label="hB 20+")
hB21 = Spectrum(haemoglobinB_formula, charge=21, adduct="H", label="hB 21+")
hB22 = Spectrum(haemoglobinB_formula, charge=22, adduct="H", label="hB 22+")
m21 = Spectrum(myoglobin_formula, charge=21, adduct="H", label="myo 21+")
m22 = Spectrum(myoglobin_formula, charge=22, adduct="H", label="myo 22+")
m23 = Spectrum(myoglobin_formula, charge=23, adduct="H", label="myo 23+")
m24 = Spectrum(myoglobin_formula, charge=24, adduct="H", label="myo 24+")
spectra = [hA19, hA20, hA21, hB20, hB21, hB22, m21, m22, m23, m24]


spectra.sort(key=lambda x: x.confs[0][0])
k = len(spectra)


for s in spectra:
    s.normalize()


proportions = [1, 2, 1.2, 0.5, 0.9, 0.6, 0.2, 0.3, 0.4, 0.0]
proportions = [p / sum(proportions) for p in proportions]


convolved = Spectrum(label="Convolved")
for s, p in zip(spectra, proportions):
    convolved += s * p


convolved.add_chemical_noise(100, 0.1)


len(convolved.confs)

convolved.gaussian_smoothing(0.01, 0.001)


convolved.add_gaussian_noise(0.01)


peaks = sp.signal.argrelmax(np.array([i for m, i in convolved.confs]), order=21)[0]
peaks = [convolved.confs[i] for i in peaks]


from masserstein import estimate_proportions


convolved.normalize()

masserstein_convolved = deepcopy(convolved)
masserstein_spectra = [deepcopy(s) for s in spectra]

res = estimate_proportions(convolved, spectra, MTD=0.05)
print("Masserstein result:", np.array(res["proportions"]))

import pylmcf
from tqdm import tqdm

convolved = pylmcf.Spectrum.FromMasserstein(convolved)
spectra = [pylmcf.Spectrum.FromMasserstein(s) for s in spectra]

from pylmcf.solver import Solver


solver = Solver(
    convolved, spectra, lambda x, y: 100 * np.linalg.norm(x - y, axis=0), 5, 10, 100.0
)

solver.set_point([1] * len(spectra))
solver.print_diagnostics()
solution = solver.solve(debug_prints=True)
# DG = DecompositableFlowGraph(convolved, spectra, lambda x, y: 100*np.linalg.norm(x - y, axis=0), 5)
# DG.add_empirical_spectrum(convolved)
# for s in tqdm(spectra):
#    DG.add_theoretical_spectrum(s, lambda x, y: np.linalg.norm(x - y, axis=0), 0.05)
# DG.build([pylmcf.TrashFactorySimple(1000000)])
# print(DG.set_point([1]*len(spectra)))
