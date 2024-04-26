
#Importar librerias
import numpy as np #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt #importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages #importar libreria para hacer pdfs

#Arcgivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.Calculations import ExtractCycles
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure

# Analisis Estadistico con pandas. boxplots etc.
import seaborn as sns


mpl.use("QtAgg")#backend es la herramienta de visor de graficas
plt.close('all') #cerrar todas las graficas antes de empezar
plt.ion() #activar las graficas que se vean y que no se escondan

#definimos entradas y salidas
DataDir = './Data/'
ExpDef = './Data/Experiments.ods'
LoadsDef = './Data/LoadsDescription.ods'
PDF = PdfPages('./Reports/LoadReport.pdf')
OutFile = './DataSets/Cycles.pkl' #le dices que habra un archivo llmadao cycles

FindCyclesBy = 'Position' #le definimos en funcion de que va a ser el metodo de busqueda de ciclos.

# %% Load Experiments carga los excels
dfExp = pd.read_excel(ExpDef)
dfLoads = pd.read_excel(LoadsDef)
dfLoads.Req = dfLoads.Req * 1000 #pasamos a ohmios
#  Only loads the specified data name in quotes inside the excel labels.
# dfExps = dfExp.query("TribuId == 'SwTENG-Tt1t2' ")
#dfExps = dfExp.query("TribuId == 'SwTENG-St1t2' " )
#dfExps = dfExp.query("TribuId == 'SwTENG-SB3' ")
dfExps = dfExp.query("TribuId == 'SwTENG-1ST' ")
#dfExps = dfExp carga todo entero sin filtrar

# %% Add Loads Fields. Mezcla dos excels en uno con datos de lo dos escogidos
LoadsFields = ('Req', 'Gain')
for lf in LoadsFields:
    dfExps.insert(1, lf, None)

for index, r in dfExps.iterrows():
    if r.RloadId in dfLoads.RloadId.values:
        for lf in LoadsFields:
            dfExps.loc[index, lf] = dfLoads.loc[dfLoads.RloadId == r.RloadId, lf].values
    else:
        print(f'Warning Load {r.RloadId} not found !!!!')
        dfExps.drop(index, inplace=True)
        print("Deleted")


# %% load data files

# create abs path
for index, r in dfExps.iterrows():
    dfExps.loc[index, 'DaqFile'] = os.path.join(DataDir, r.DaqFile)
    dfExps.loc[index, 'MotorFile'] = os.path.join(DataDir, r.MotorFile)

plt.ioff()
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
                                   #CurrentTh=None,
                                   )
    else:
        CyclesList = ExtractCycles(dfData,
                                   ContactPosition=None,
                                   ContactForce=r.ContactForce,
                                   Latency=r.Latency,
                                   CurrentTh=r.CurrentTh,
                                   #CurrentTh=None,
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
    fig.tight_layout()
    PDF.savefig(fig)

    XVar = 'Position'
    AxsDict, PlotCols = GenFigure(dfData, xVar=XVar, figsize=(10, 5))
    for col, ax in AxsDict.items():
        ax.set_xlabel(XVar)
        ax.plot(dfData[XVar], dfData[col], PlotCols[col])
    ax.set_xlim(0, np.mean([cy['PosStart'] for cy in CyclesList]))
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.tight_layout()
    PDF.savefig(fig)
    plt.close('all')

plt.ion()
PDF.close()

dfCycles = dfCycles.astype({'Gain': float,
                            'Req': float,
                            })

dfCycles.to_pickle(OutFile)

