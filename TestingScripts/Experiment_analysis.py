import math

import pandas as pd
from matplotlib import pyplot as plt
from Tools import LoadData, GenerateCyclesList
from glob import glob
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import math

plt.close('all')

MotorFileFilter = './Data/MOTOR/*.csv'
MotorFiles = glob(MotorFileFilter)

MeasuresDict = {}
for MotorFile in MotorFiles:
    MeasName = MotorFile.split('/')[-1].split('.')[0]
    DaqFile = MotorFile.replace('Motor', 'DAQ')
    DaqFile = DaqFile.replace('.csv', '.xlsx')
    DaqFile = DaqFile.replace('MOTOR', 'DAQ')
    df = LoadData(MotorFile=MotorFile,
                  DaqFile=DaqFile)
    Resistance = 100e3
    df['Power'] = df.Current ** 2 / Resistance
    MeasuresDict[MeasName] = df

PlotCols = {
            'Current': 'b',
            'Position': 'k',
            'Force': 'g',
            'Power': 'purple'}

PDF = PdfPages('Cycles.pdf')

pdSeries = []
for MeasName, df in MeasuresDict.items():
    CyclesList = GenerateCyclesList(df,
                                    ExtractInds=(0, 400),
                                    Theshold=-67,
                                    Column='Position')

    # calc values
    for ic, cy in enumerate(CyclesList):
        Imax = cy.Current.max()
        Imin = cy.Current.min()
        iImax = cy.Current.idxmax()
        iImin = cy.Current.idxmin()
        PosMax = cy.loc[iImax].Position
        PosMin = cy.loc[iImin].Position
        Vals = {'Experiment': MeasName,
                'Resistance': int(MeasName[-1]),
                'Imax': Imax,
                'Imin': Imin,
                'PosMax': PosMax,
                'PosMin': PosMin,
                'Cycle': ic,
                }
        pdSeries.append(pd.Series(Vals))

    # plot cycles time
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    axp = None
    fig.suptitle(MeasName)
    for ic, (col, color) in enumerate(PlotCols.items()):
        if axp is None:
            axp = ax
        else:
            axp = plt.twinx(ax)
        if ic > 1:
            axp.spines.right.set_position(("axes", 1+(0.2*(ic-1))))

        axp.set_ylabel(col)
        axp.set_xlabel('Time (s)')
        axp.yaxis.label.set_color(color)
        axp.tick_params(axis='y', colors=color)
        for cy in CyclesList:
            axp.plot(cy.Time, cy[col], color, alpha=0.5)

    fig.tight_layout()
    PDF.savefig(fig)

    # plot cycles position
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    axp = None
    fig.suptitle(MeasName)
    for ic, (col, color) in enumerate(PlotCols.items()):
        if col == 'Position':
            continue

        if axp is None:
            axp = ax
        else:
            axp = plt.twinx(ax)
        if ic > 1:
            axp.spines.right.set_position(("axes", 1+(0.2*(ic-1))))

        axp.set_ylabel(col)
        axp.set_xlabel('Position (mm)')
        axp.set_xlim(-70, -68)
        axp.yaxis.label.set_color(color)
        axp.tick_params(axis='y', colors=color)
        for cy in CyclesList:
            axp.plot(cy.Position, cy[col], color, alpha=0.5)

    fig.tight_layout()
    PDF.savefig(fig)
    plt.close('all')


PDF.close()



#%% Analysis of full experiment

dfAll = pd.concat(pdSeries, axis=1).transpose()

PlotPars = ('Imax', 'Imin', 'PosMax', 'PosMin',)

nRows = 2
nCols = math.ceil(len(PlotPars)/nRows)
fig, ax = plt.subplots(nRows, nCols, figsize=(10, 8))
axs = ax.flatten()

for ic, par in enumerate(PlotPars):
    ax = axs[ic]
    sns.stripplot(data=dfAll,
                x='Resistance',
                y=par,
                hue='Cycle',
                ax=ax
                )

fig.tight_layout()
