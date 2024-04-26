import numpy as np
import pandas as pd


def LoadData(DaqFile, MotorFile):
    daqf = pd.ExcelFile(DaqFile)
    sheets = daqf.sheet_names
    dfDAQ = pd.read_excel(DaqFile,
                          names=['Current', 'Time'],
                          sheet_name=sheets[1])

    dfMOT = pd.read_csv(MotorFile,
                        names=['Time', 'Voltage', 'Force', 'Current', 'Position'],
                        header=0,
                        index_col=False,
                        delimiter=',',
                        decimal='.')

    # Create interpolated data
    for col in ('Position', 'Force'):
        dfDAQ[col] = np.interp(dfDAQ.Time, dfMOT.Time, dfMOT[col])

    return dfDAQ

def GenerateCyclesList(df, ExtractInds=(-100, 400), Theshold=4e-6,
                       Column='Current'):

    dt = df.Time[df[Column] < Theshold].diff()
    CycleInds = dt[dt > 5e-4].index
    CycleInds = CycleInds.insert(0, dt.index[1])
    CyclesList = []
    for ind in CycleInds[:-1]:
        dfCycle = df[ind + ExtractInds[0]:ind + ExtractInds[1]]
        tinit = dfCycle.Time.iloc[0]
        dfCycle.Time = dfCycle.Time - tinit
        CyclesList.append(dfCycle)

        # ax.axvline(x=df.Time[ind], color='y')
        # axp.axvline(x=df.Time[ind], color='y')
        # ax.axvline(x=df.Time[ind+ExtractInds[0]], color='r')
        # axp.axvline(x=df.Time[ind+ExtractInds[0]], color='r')
        # ax.axvline(x=df.Time[ind+ExtractInds[1]], color='r')
        # axp.axvline(x=df.Time[ind+ExtractInds[1]], color='r')

    return CyclesList


