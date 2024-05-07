
from math import ceil
import numpy as np
import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from TryPy.PlotData import PlotScalarValues, GenFigure
import imageio.v2 as imageio  # Importar la versión 2 de imageio para evitar el aviso de deprecación

PDF = PdfPages('./Reports/DataSetsAnalysis.pdf')

# %% Load data

FileIn = './DataSets/Cycles.pkl'
dfData = pd.read_pickle(FileIn)
dfData = dfData.query("Cycle > 1")
#dfData = dfData.query("Cycle < 9")
# %% Plot experiments comparison

PlotPars = ('IMax',
            'VMax',
            'PosPMax',
            'PosEnergy',)

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='ExpId',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Tribu Comparison')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMax',
            'PosIMax',
            'VMax',
            'PosPMax',
            'PosEnergy')
fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='ExpId',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Positive peak Data')
fig.tight_layout()
PDF.savefig(fig)

PlotPars = ('IMin',
            'PosIMin',
            'VMin',
            'NegPMax',
            'NegEnergy')

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='ExpId',
                            hueVar='Cycle',
                            PltFunt=sns.scatterplot)
fig.suptitle('Negative peak Data')
fig.tight_layout()
PDF.savefig(fig)

# %% compare positive and negative peaks

"""dSel = dfData
fig, ax = plt.subplots()
sns.lineplot(data=dSel,
             x='ExpId',
             y='PosEnergy',
             ax=ax,
             label='PosEnergy')
sns.lineplot(data=dSel,
             x='ExpId',
             y='NegEnergy',
             ax=ax,
             label='NegEnergy')
sns.lineplot(data=dSel,
             x='ExpId',
             y='Energy',
             ax=ax,
             label='Energy')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Load Resistance (Ohm)')
ax.set_ylabel('Energy (J)')
ax.legend()
PDF.savefig(fig)"""



# Gráfica para Energia en función de T1 Y T2
# Obtener los nombres de los diferentes valores de ExpId
# Configurar el gráfico
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Contact Time Effect')
# Trazar los puntos para PosEnergy, NegEnergy y Energy en función de ExpId
sns.scatterplot(data=dfData, x='ExpId', y='PosEnergy', ax=ax, label='PosEnergy', color='blue')
sns.scatterplot(data=dfData, x='ExpId', y='NegEnergy', ax=ax, label='NegEnergy', color='red')
sns.scatterplot(data=dfData, x='ExpId', y='Energy', ax=ax, label='Energy', color='green')

ax.set_xlabel('ExpId')
ax.set_ylabel('Energy (J)')
ax.legend()

plt.xticks(rotation=45)  # Rotar las etiquetas del eje x para una mejor legibilidad
plt.tight_layout()
PDF.savefig(fig)



# Crear el directorio "images" si no existe
if not os.path.exists('images'):
    os.makedirs('images')
# %% Plot experiment time traces

VarColors = {
    'Voltage': 'r',
    'Current': 'b',
    'Position': 'k',
    'Force': 'g',
    'Power': 'purple'}
image_files = []


dSel = dfData
#dSel = dfData.query("TribuId == 'SwTENG-RF2' ")

for ex, dExp in dSel.groupby('ExpId'):
    fig, (axtime, axpos) = plt.subplots(2, 1, figsize=(11, 7))
    for gn, df in dExp.groupby('RloadId'):
        # plot time traces
        AxsDict, _ = GenFigure(dfData=df.loc[2, 'Data'],
                               xVar='Time',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axtime)
        for index, r in df.iterrows():
            Data = r.Data
            for col, ax in AxsDict.items():
                ax.plot(Data['Time'], Data[col], color=VarColors[col],
                        alpha=0.5)
                ax.axvline(x=r.tTransition, color='y')
                ax.set_xlabel('Time')

        # plot position traces
        AxsDict, _ = GenFigure(dfData=df.loc[2, 'Data'],
                               xVar='Position',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axpos)
        for index, r in df.iterrows():
            Data = r.Data
            for col, ax in AxsDict.items():
                ax.plot(Data['Position'], Data[col], color=VarColors[col],
                        alpha=0.5)
                ax.set_xlabel('Position')
                ax.set_xlim(0, 2)

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Rload: {r.RloadId}, Req: {r.Req}')
        fig.tight_layout()
        PDF.savefig(fig)
        plt.close(fig)
   # Guardar la figura como una imagen en la carpeta "images"
        image_file = f'./images/Experiment_{ex}_Rload_{gn}.png'
        fig.savefig(image_file)
        image_files.append(image_file)


# Crear animación con las imágenes
animation_file = 'animation.gif'
with imageio.get_writer(animation_file, mode='I', fps=1) as writer:
    for image_file in image_files:
        image = imageio.imread(image_file)
        writer.append_data(image)

print(f'Animation saved as {animation_file}')
PDF.close()
