import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages

from TryPy.Calculations import ExtractCycles
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure

import seaborn as sns

mpl.use("QtAgg")
plt.close('all')
plt.ion()

DataDir = './Data/'
ExpDef = './Data/Experiments.ods'
LoadsDef = './Data/LoadsDescription.ods'

FindCyclesBy = 'Position'

# %% Load Experiment Info
dfExps = pd.read_excel(ExpDef)
dfLoads = pd.read_excel(LoadsDef)
dfLoads.Req = dfLoads.Req * 1000

# %% Add Loads Fields
LoadsFields = ('Req', 'Gain')
for lf in LoadsFields:
    dfExps.insert(1, lf, None)

for index, r in dfExps.iterrows():
    if r.RloadId in dfLoads.RloadId.values:
        for lf in LoadsFields:
            dfExps.loc[index, lf] = dfLoads.loc[dfLoads.RloadId == r.RloadId, lf].values

# %% load data files

# create abs path
for index, r in dfExps.iterrows():
    dfExps.loc[index, 'DaqFile'] = os.path.join(DataDir, r.DaqFile)
    dfExps.loc[index, 'MotorFile'] = os.path.join(DataDir, r.MotorFile)

# Select experiments
dfExps.query("ExpId == '0703-RL003'", inplace=True)

dfCycles = pd.DataFrame()
for index, r in dfExps.iterrows():

    print(f'Processing: {r.ExpId}')

    dfData = Loadfiles(r)
    # Reference position and force
    dfData.Position = dfData.Position - dfData.Position.min()
    dfData.Force = -dfData.Force

    # Calculate Contact Position
    if FindCyclesBy == 'Position':
        CyclesList = ExtractCycles(dfData,
                                   ContactPosition=r.ContactPosition,
                                   Latency=r.Latency,
                                   CurrentTh=r.CurrentTh,
                                   )
    else:
        CyclesList = ExtractCycles(dfData,
                                   ContactPosition=None,
                                   ContactForce=r.ContactForce,
                                   Latency=r.Latency,
                                   CurrentTh=r.CurrentTh,
                                   )

    # stack cycles
    for cy in CyclesList:
        cy.update(r.to_dict())
    dfCycle = pd.DataFrame(CyclesList)
    dfCycles = pd.concat([dfCycles, dfCycle])

    # Generate Debug Figures
    XVar = 'Time'
    AxsDict, PlotCols = GenFigure(dfData, xVar=XVar, axisFactor=0.1, figsize=(12, 5))
    for col, ax in AxsDict.items():
        ax.set_xlabel(XVar)
        ax.plot(dfData[XVar], dfData[col], PlotCols[col])

    for cy in CyclesList:
        ax.axvline(x=cy['tStart'], color='y', linewidth=2)
        ax.axvline(x=cy['tEnd'], color='y', linestyle='-.', linewidth=2)
        ax.axvline(x=cy['tStart'] + cy['tTransition'], color='y', linestyle='--', linewidth=1)
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)


    XVar = 'Position'
    AxsDict, PlotCols = GenFigure(dfData, xVar=XVar, figsize=(10, 5))
    for col, ax in AxsDict.items():
        ax.set_xlabel(XVar)
        ax.plot(dfData[XVar], dfData[col], PlotCols[col])
    ax.set_xlim(0, np.mean([cy['PosStart'] for cy in CyclesList]))
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.tight_layout()



