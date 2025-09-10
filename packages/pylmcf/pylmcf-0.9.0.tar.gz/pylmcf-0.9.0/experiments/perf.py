import pyopenms as oms
import pandas as pd
import numpy as np
from sliced_transport_plan import *
from parse_data import *
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

featurexml_path_or09 = r"data/100901O2c1_MT-AU-0044-2010-08-23_008.featureXML"  # path to 100901O2c1_MT-AU-0044-2010-08-23_008.featureXML
featurexml_path_pd01 = r"data/100920O2c1_MT-AU-0044-2010-08-64_035.featureXML"  # path to 100920O2c1_MT-AU-0044-2010-08-64_035.featureXML

df_featurexml_or09 = load_featurexml(featurexml_path_or09)
df_featurexml_pd01 = load_featurexml(featurexml_path_pd01)

df_featurexml_or09.rename(
    columns={"MZ": "mz", "RT": "rt", "Intensity": "intensity"}, inplace=True
)
df_featurexml_pd01.rename(
    columns={"MZ": "mz", "RT": "rt", "Intensity": "intensity"}, inplace=True
)

df_featurexml_or09["id"] = df_featurexml_or09.index
df_featurexml_pd01["id"] = df_featurexml_pd01.index

"""
consensus, full_tp = sliced_masserstein(df_featurexml_or09[(df_featurexml_or09.mz>1000)&(df_featurexml_or09.mz<1200)&(df_featurexml_or09.rt>6000)&(df_featurexml_or09.rt<8000)],
                                 df_featurexml_pd01[(df_featurexml_pd01.mz>1000)&(df_featurexml_pd01.mz<1200)&(df_featurexml_pd01.rt>6000)&(df_featurexml_pd01.rt<8000)],
                                 scale_mz=100, MTD=30)
"""

S1 = df_featurexml_or09
S2 = df_featurexml_pd01

from pylmcf import wasserstein

result = wasserstein(
    S1.mz.values,
    S1.rt.values,
    S1.intensity.values,
    S2.mz.values,
    S2.rt.values,
    S2.intensity.values,
    1000,
)
from pprint import pprint

pprint(result)
