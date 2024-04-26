import os

import numpy as np
import pandas as pd
from nptdms import TdmsFile

MotColumnRenames = {
    'Time(s)': 'Time',
    'MC SW Overview - Actual Position(mm)': 'Position',
    'MC SW Force Control - Measured Force(N)': 'Force',
}

DQAColumnRenames = {
    'Input 0': 'Voltage',
    'Unnamed: 1': 'Time',
}


def LoadMotorFile(MotorFile):
    """
    LoadMotorFile reads a CSV file and processes it to remove non-defined columns and rename columns.
    It takes a single parameter MotorFile, which is the path to the CSV file.
    It returns a pandas DataFrame dfMOT.
    """
    dfMOT = pd.read_csv(MotorFile,
                        header=0,
                        index_col=False,
                        delimiter=',',
                        decimal='.')
    # drop Non-defined columns
    dropcols = []
    for col in dfMOT.columns:
        if col not in MotColumnRenames.keys():
            dropcols.append(col)
    dfMOT = dfMOT.drop(columns=dropcols)
    # rename columns
    dfMOT = dfMOT.rename(columns=MotColumnRenames)
    return dfMOT


def LoadDAQFile(DaqFile):
    """
    A function to load a DAQ file and return a DataFrame based on the file type.
    Parameters:
    - DaqFile: the file path of the DAQ file to be loaded
    Return:
    - dfDAQ: a DataFrame containing the DAQ data
    - None if the file type is not recognized
    """
    if DaqFile.endswith('.tdms'):
        tdms_file = TdmsFile.read(DaqFile)
        dfDAQ = tdms_file.as_dataframe(time_index=True,
                                       scaled_data=False)
        dfDAQ.reset_index(inplace=True)
        dfDAQ = dfDAQ.set_axis(['Time', 'Voltage'], axis=1)
        return dfDAQ
    elif DaqFile.endswith('.xlsx'):
        daqf = pd.ExcelFile(DaqFile)
        sheets = daqf.sheet_names
        dfDAQ = pd.read_excel(DaqFile,
                              sheet_name=sheets[1])
        # rename columns
        dfDAQ = dfDAQ.rename(columns=DQAColumnRenames)
        return dfDAQ
    else:
        print(f'File {DaqFile} not recognized')
        return None


def Loadfiles(ExpDef):
    """
    Loads data files, calculates sampling rates, interpolates data, and calculates voltage, current, and power.

    Parameters:
    - ExpDef: Experiment definition containing file paths, gain, and resistance values.

    Returns:
    - dfData: DataFrame containing loaded and processed data.
    """
    r = ExpDef

    if not os.path.isfile(r.DaqFile):
        print(f'File {r.DaqFile} not found')
        return None
    if not os.path.isfile(r.MotorFile):
        print(f'File {r.MotorFile} not found')
        return None

    # Load DAQ file
    dfDAQ = LoadDAQFile(r.DaqFile)

    # Load Motor file
    dfMOT = LoadMotorFile(r.MotorFile)

    # Motor sampling Rate
    MotFs = 1 / dfMOT.Time.diff().mean()
    print(f'Motor sampling rate: {MotFs}')

    # DAQ sampling rate
    if 'Time' in dfDAQ.columns:
        DaqFs = 1 / dfDAQ.Time.diff().mean()
        print(f'Found DAQ sampling rate: {DaqFs}')
    else:
        nSamps = dfDAQ.Voltage.size
        DaqFs = nSamps / (1 / MotFs * dfMOT.Time.size)
        print(f'Calculated DAQ sampling rate: {DaqFs}')
        dfDAQ['Time'] = np.arange(0, nSamps) / DaqFs

    # Create interpolated data
    dfData = dfDAQ
    for col in dfMOT.columns:
        if col == 'Time':
            continue
        dfData[col] = np.interp(dfData.Time, dfMOT.Time, dfMOT[col])

    #FILTRO SEÑAL
    window_size = 9  # Tamaño de la ventana del filtro
    #  dfData['SmoothVoltages'] = dfData['Voltage'].rolling(window=window_size).median()
    dfData['SmoothVoltage'] = dfData['Voltage'].rolling(window=window_size).mean()

# Calculate Voltage, Current and Power
    dfData['VoltageAcq'] = dfData.Voltage
    dfData['Voltage'] = dfData['SmoothVoltage'] / r.Gain
    dfData['Current'] = dfData.Voltage / r.Req
    dfData['Power'] = dfData.Current * dfData.Voltage

    return dfData
