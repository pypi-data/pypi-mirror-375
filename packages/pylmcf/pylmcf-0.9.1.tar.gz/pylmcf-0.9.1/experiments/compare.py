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


import pylmcf

print(convolved)
print(spectra)
lconvolved = pylmcf.Spectrum.FromMasserstein(convolved)
lspectra = [pylmcf.Spectrum.FromMasserstein(s) for s in spectra]
solver = pylmcf.WassersteinSolver(
    lconvolved, lspectra, trash_cost=0.05, intensity_scaling=10000, costs_scaling=10000
)
# print(solver.estimate_proportions())
print(convolved)
print(spectra)


print("start")

res = estimate_proportions(convolved, spectra, MTD=0.05)


print("True:", "Estimate:", sep="\t")
for e, p in zip(res["proportions"], proportions):
    print(round(p, 3), round(e / sum(res["proportions"]), 3), sep="\t")

jnkjnjn

peaks, _ = convolved.centroid(peak_height_fraction=0.5, max_width=0.03)


# Show the first few detected peaks (typically corresponding to background noise):

# In[27]:


peaks[:5]


# Generate a new spectrum based on the computed peaks:

# In[28]:


centroided = Spectrum(confs=peaks)


# In[29]:


plt.figure()
plt.subplot(121)
plt.title("Profile mode")
convolved.plot(profile=True, show=False)
plt.subplot(122)
plt.title("Centroid mode")
centroided.plot(show=False)
plt.tight_layout()


# Regress the centroided spectrum against the theoretical spectra:

# In[30]:


centroided.normalize()


# In[31]:


res2 = estimate_proportions(centroided, spectra, MTD=0.05)


# In[32]:


print("True:", "Estimate:", sep="\t")
for e, p in zip(res2["proportions"], proportions):
    print(round(p, 3), round(e / sum(res2["proportions"]), 3), sep="\t")


# We get similar results for this spectrum in both profile and centroided modes.
