import pandas as pd
import numpy as np
import pyopenms


def load_mzml(file_path):
    """
    Load an mzML file and return a DataFrame with m/z, RT, and intensity values.

    Parameters
    ----------
    file_path : str
        Path to the mzML file.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with columns 'MZ', 'RT', and 'Intensity'.
    """
    # Load mzML file using OpenMS
    exp = pyopenms.MSExperiment()
    mzml_file = pyopenms.MzMLFile()
    mzml_file.load(file_path, exp)

    # Extract m/z, RT, and intensity values from MS1 spectra
    mz_list = []
    rt_list = []
    intensity_list = []

    for spectrum in exp:
        if spectrum.getMSLevel() == 1:  # Only process MS1 (full-scan) spectra
            rt = spectrum.getRT()  # Retention time
            for peak in spectrum:
                mz, intensity = peak.getMZ(), peak.getIntensity()
                mz_list.append(mz)
                rt_list.append(rt)
                intensity_list.append(intensity)

    # Convert lists to NumPy arrays and create a DataFrame
    mz_array = np.array(mz_list)
    rt_array = np.array(rt_list)
    intensity_array = np.array(intensity_list)

    df = pd.DataFrame({"MZ": mz_array, "RT": rt_array, "Intensity": intensity_array})

    return df


def load_featurexml(file_path):
    """
    Load a featureXML file and return a DataFrame with m/z, RT, and intensity values.

    Parameters
    ----------
    file_path : str
        Path to the featureXML file.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with columns 'MZ', 'RT', and 'Intensity'.
    """
    # Load featureXML file using OpenMS
    exp = pyopenms.FeatureMap()
    featurexml_file = pyopenms.FeatureXMLFile()
    featurexml_file.load(file_path, exp)

    # Extract m/z, RT, and intensity values from features
    mz_list = []
    rt_list = []
    intensity_list = []

    for feature in exp:
        rt = feature.getRT()  # Retention time
        mz = feature.getMZ()  # m/z
        intensity = feature.getIntensity()  # Intensity

        mz_list.append(mz)
        rt_list.append(rt)
        intensity_list.append(intensity)

    # Convert lists to NumPy arrays and create a DataFrame
    mz_array = np.array(mz_list)
    rt_array = np.array(rt_list)
    intensity_array = np.array(intensity_list)

    df = pd.DataFrame({"MZ": mz_array, "RT": rt_array, "Intensity": intensity_array})

    return df
