import masserstein
from masserstein import Spectrum
from masserstein import estimate_proportions
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import random
from time import time
from pulp.apis import LpSolverDefault
import tqdm
from IPython.display import clear_output


def transport_plan(
    sp1: Spectrum,
    sp2: Spectrum,
    what_to_compare="area",
    MTD=0.01,
    verbose=False,
    solver=LpSolverDefault,
):
    """
    Calculate the transport plan between two spectra.

    Parameters
    ----------
    sp1 : Spectrum
        First spectrum.
    sp2 : Spectrum
        Second spectrum.
    what_to_compare : str, optional
        What to compare. The default is 'area'.
    MTD : float, optional
        Maximum transport distance. The default is 0.01.
    verbose : bool, optional
        Print the progress. The default is False.
    solver : LpSolverDefault, optional
        Solver for the linear program. The default is LpSolverDefault.

    Returns
    -------
    transport_plan : list
        List of tuples (conf1, conf2, amount) where conf1 is a configuration in sp1, conf2 is a configuration in sp2, and amount is the amount of conf1 to be moved to conf2.
    """
    if max([el[0] for el in sp1.confs]) + MTD < min([el[0] for el in sp2.confs]) or max(
        [el[0] for el in sp2.confs]
    ) + MTD < min([el[0] for el in sp1.confs]):
        return []
    sp1.normalize()
    sp2.normalize()
    estimation = estimate_proportions(
        sp1,
        [sp2],
        what_to_compare=what_to_compare,
        MTD=MTD,
        MTD_th=MTD,
        verbose=verbose,
        solver=solver,
    )
    common_horizontal_axis = estimation["common_horizontal_axis"]
    updated = []
    if len(sp1.confs) != len(estimation["common_horizontal_axis"]) and len(
        sp2.confs
    ) != len(estimation["common_horizontal_axis"]):
        for sp in [sp1, sp2]:
            missing = set(estimation["common_horizontal_axis"]).difference(
                [el[0] for el in sp.confs]
            )
            new_confs = sp.confs + [(missing_point, 0.0) for missing_point in missing]
            updated.append(Spectrum(confs=new_confs))
        sp1, sp2 = updated
    noise_in_sp1 = estimation["noise"]
    noise_in_sp2 = estimation["noise_in_components"]
    p0 = 1 - sum(estimation["proportions"])
    p0_prime = estimation["proportion_of_noise_in_components"]
    sp1.normalize(target_value=1 - p0_prime)
    sp2.normalize(target_value=1 - p0)
    if len(sp1.confs) != len(noise_in_sp1) or len(sp2.confs) != len(noise_in_sp2):
        return []
    intensities = list(np.array([el[1] for el in sp1.confs]) - np.array(noise_in_sp1))
    sp1 = Spectrum(confs=list(zip(common_horizontal_axis, intensities)))
    intensities = list(np.array([el[1] for el in sp2.confs]) - np.array(noise_in_sp2))
    sp2 = Spectrum(confs=list(zip(common_horizontal_axis, intensities)))
    transport_plan = [
        (el[1], el[0], el[2]) for el in list(sp1.WSDistanceMoves(sp2)) if el[2] > 0
    ]
    return transport_plan


def project(spectrum: pd.DataFrame, theta: float, scale_mz: float = 1):
    """
    Project spectrum onto a line with angle theta.

    Parameters
    ----------
    spectrum : pd.DataFrame
        Data Frame with columns 'id', 'mz', 'rt', 'intensity'.
    theta : float
        Angle of projection.
    scale_mz : float, optional
        Scale of mz axis. The default is 1.

    Returns
    -------
    projection : pd.DataFrame
        Data Frame with columns 'id', 'value', 'intensity'.
    """
    projection = pd.DataFrame(columns=["id", "value", "intensity"])
    projection["id"] = spectrum["id"]
    projection["value"] = scale_mz * spectrum["mz"] * np.cos(theta) + spectrum[
        "rt"
    ] * np.sin(theta)
    projection["intensity"] = spectrum["intensity"]
    return projection


def collect_single_vote(
    theta: float,
    sp1: pd.DataFrame,
    sp2: pd.DataFrame,
    scale_mz: float = 1,
    MTD: float = 1,
):
    """
    Collect a single vote for a given projection.

    Parameters
    ----------
    theta : float
        Angle of projection.
    sp1 : pd.DataFrame
        Data Frame with columns 'id', 'mz', 'rt', 'intensity'.
    sp2 : pd.DataFrame
        Data Frame with columns 'id', 'mz', 'rt', 'intensity'.
    scale_mz : float, optional
        Scale of mz axis. The default is 1.
    MTD : float, optional
        Maximum transport distance. The default is 1.

    Returns
    -------
    vote : pd.DataFrame
        Data Frame with columns 'feature1', 'feature2', 'transported_intensity'.
    """
    # project spectra
    projection1 = project(sp1, theta, scale_mz)
    projection2 = project(sp2, theta, scale_mz)
    # shift spectra so there are no negative values
    min_value = min(projection1["value"].min(), projection2["value"].min())
    projection1.value = projection1.value - min_value + 1
    projection2.value = projection2.value - min_value + 1
    # compute transport plan
    sp1_proj = Spectrum(confs=list(zip(projection1["value"], projection1["intensity"])))
    sp2_proj = Spectrum(confs=list(zip(projection2["value"], projection2["intensity"])))
    tp = transport_plan(sp1_proj, sp2_proj, MTD=MTD)
    tp = pd.DataFrame(tp, columns=["value1", "value2", "transported_intensity"])
    vote = tp.merge(projection1, left_on="value1", right_on="value", how="inner")
    vote = vote.merge(projection2, left_on="value2", right_on="value", how="inner")
    vote = vote[["id_x", "id_y", "transported_intensity"]]
    vote.columns = ["feature1", "feature2", "transported_intensity"]
    vote.groupby(["feature1", "feature2"]).sum().reset_index()
    return vote


def sliced_masserstein(
    sp1: pd.DataFrame,
    sp2: pd.DataFrame,
    n_slices: int = 50,
    strap_width: float = 15,
    overlap: float = 5,
    scale_mz: float = 1,
    MTD: float = 1,
    find_consensus_features: bool = True,
):
    """
    Approvimated transport plan between two spectra using sliced Wasserstein distance
    calculated between spectra divided into overlaping straps.

    Parameters
    ----------
    sp1 : pd.DataFrame
        Data Frame with columns 'id', 'mz', 'rt', 'intensity'.
    sp2 : pd.DataFrame
        Data Frame with columns 'id', 'mz', 'rt', 'intensity'.
    n_slices : int, optional
        Number of slices. The default is 20.
    strap_width : float, optional
        Width of a strap. The default is 50.
    overlap : float, optional
        Overlap between straps. The default is 10.
    scale_mz : float, optional
        Scale of mz axis. The default is 1.
    MTD : float, optional
        Maximum transport distance. The default is 1.
    find_consensus_features : bool, optional
        If True, the program returns pairs of consensus features. If False, the function returns full transport plan.
        The default is True.

    Returns
    -------
    votes : pd.DataFrame
        Data Frame with columns 'feature1', 'feature2', 'transported_intensity'.
    """
    # votes = pd.DataFrame(columns=['feature1', 'feature2', 'transported_intensity'])
    # # calculate strap positions
    # min_mz = min(sp1['mz'].min(), sp2['mz'].min())
    # max_mz = max(sp1['mz'].max(), sp2['mz'].max())
    # straps = [(i, i+strap_width) for i in np.arange(min_mz, max_mz, strap_width-overlap)]
    # # sliced  wasserstein on straps
    # for strap in tqdm.tqdm(straps, desc='Strap loop'):
    #     votes_strap = pd.DataFrame(columns=['feature1', 'feature2', 'transported_intensity'])
    #     # select features in the strap
    #     sp1_strap = sp1[(sp1['mz'] >= strap[0]) & (sp1['mz'] <= strap[1])]
    #     sp2_strap = sp2[(sp2['mz'] >= strap[0]) & (sp2['mz'] <= strap[1])]
    #     # vote on the spectrum strap projected on the m/z axis
    #     if len(sp1_strap) > 0 and len(sp2_strap) > 0:
    #         votes_strap = collect_single_vote(0, sp1_strap, sp2_strap, scale_mz=scale_mz, MTD=MTD)
    #         # vote on projections
    #         for _ in tqdm.tqdm(range(n_slices), desc='Projection loop',  leave=False):
    #             # sample theta
    #             theta = np.random.rand()*np.pi
    #             # vote
    #             vote = collect_single_vote(theta, sp1_strap, sp2_strap, scale_mz=scale_mz, MTD=MTD)
    #             votes_strap = pd.concat([votes_strap, vote])
    #             votes_strap = votes_strap.groupby(['feature1', 'feature2']).sum().reset_index()
    #         votes = pd.concat([votes, votes_strap])
    #         # if some features were in two straps, take the sum of transported intensities
    #         votes = votes.groupby(['feature1', 'feature2']).sum().reset_index()
    # full_transport_plan = votes.copy()
    # # find consensus features
    # if find_consensus_features:
    #     # votes = votes.loc[votes.groupby(['feature1'])['transported_intensity'].idxmax()].reset_index(drop=True)
    #     # votes = votes.loc[votes.groupby('feature2')['transported_intensity'].idxmax().reset_index(drop=True)]
    #     votes.sort_values('transported_intensity', ascending=False, inplace=True)
    #     consensus1  =set()
    #     consensus2 = set()
    #     for i, row in votes.iterrows():
    #         if row['feature1'] not in consensus1 and row['feature2'] not in consensus2:
    #             consensus1.add(row['feature1'])
    #             consensus2.add(row['feature2'])
    #         else:
    #             votes.drop(i, inplace=True)
    # # find centroids  of consensus features
    # transport_plan = votes.merge(sp1, left_on='feature1', right_on='id', how='inner')
    # transport_plan = transport_plan.merge(sp2, left_on='feature2', right_on='id', how='inner')
    # transport_plan = transport_plan[['mz_x', 'rt_x', 'mz_y', 'rt_y', 'transported_intensity']].drop_duplicates()
    # transport_plan = transport_plan.astype({'mz_x': 'float64', 'rt_x': 'float64', 'mz_y': 'float64', 'rt_y': 'float64', 'transported_intensity': 'float64'})
    # return transport_plan, full_transport_plan
    votes_list = []
    min_mz = min(sp1["mz"].min(), sp2["mz"].min())
    max_mz = max(sp1["mz"].max(), sp2["mz"].max())
    straps = [
        (i, i + strap_width) for i in np.arange(min_mz, max_mz, strap_width - overlap)
    ]
    theta_sample = np.linspace(0, 2 * np.pi, n_slices)
    theta_sample = np.concatenate([[np.pi / 2], theta_sample])
    for strap in tqdm.tqdm(straps, desc="Strap loop"):
        votes_strap_list = []
        sp1_strap = sp1[(sp1["mz"] >= strap[0]) & (sp1["mz"] <= strap[1])]
        sp2_strap = sp2[(sp2["mz"] >= strap[0]) & (sp2["mz"] <= strap[1])]
        if len(sp1_strap) > 0 and len(sp2_strap) > 0:
            # votes_strap = collect_single_vote(0, sp1_strap, sp2_strap, scale_mz=scale_mz, MTD=MTD)
            # votes_strap = votes_strap[votes_strap['transported_intensity'] > 0]
            # sp1_strap = sp1_strap[sp1_strap['id'].isin(votes_strap['feature1'])]
            # sp2_strap = sp2_strap[sp2_strap['id'].isin(votes_strap['feature2'])]
            # votes_strap_list.append(votes_strap)
            votes_strap_list = []
            for i in tqdm.tqdm(range(n_slices), desc="Projection loop", leave=False):
                if len(sp1_strap) == 0 or len(sp2_strap) == 0:
                    break
                theta = theta_sample[i]
                vote = collect_single_vote(
                    theta, sp1_strap, sp2_strap, scale_mz=scale_mz, MTD=MTD
                )
                vote = vote[vote["transported_intensity"] > 0]
                sp1_strap = sp1_strap[sp1_strap["id"].isin(vote["feature1"])]
                sp2_strap = sp2_strap[sp2_strap["id"].isin(vote["feature2"])]
                votes_strap_list.append(vote)
            votes_strap_df = pd.concat(votes_strap_list)
            votes_strap_df = (
                votes_strap_df.groupby(["feature1", "feature2"]).sum().reset_index()
            )
            votes_list.append(votes_strap_df)
    votes = pd.concat(votes_list)
    votes = votes.groupby(["feature1", "feature2"]).sum().reset_index()
    full_transport_plan = votes.copy()
    if find_consensus_features:
        votes.sort_values("transported_intensity", ascending=False, inplace=True)
        consensus1 = set()
        consensus2 = set()
        for i, row in votes.iterrows():
            if row["feature1"] not in consensus1 and row["feature2"] not in consensus2:
                consensus1.add(row["feature1"])
                consensus2.add(row["feature2"])
            else:
                votes.drop(i, inplace=True)
    transport_plan = votes.merge(sp1, left_on="feature1", right_on="id", how="inner")
    transport_plan = transport_plan.merge(
        sp2, left_on="feature2", right_on="id", how="inner"
    )
    transport_plan = transport_plan[
        ["mz_x", "rt_x", "mz_y", "rt_y", "transported_intensity"]
    ].drop_duplicates()
    transport_plan = transport_plan.astype(
        {
            "mz_x": "float64",
            "rt_x": "float64",
            "mz_y": "float64",
            "rt_y": "float64",
            "transported_intensity": "float64",
        }
    )
    return transport_plan, full_transport_plan
