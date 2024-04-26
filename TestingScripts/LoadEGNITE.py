from nptdms import TdmsFile
from matplotlib import pyplot as plt
from scipy.signal import butter, sosfiltfilt, welch

tdms_file = TdmsFile.read("../Data/Egnite/1203DAQ06.tdms")
df = tdms_file.as_dataframe(time_index=True,
    scaled_data=False)

df.reset_index(inplace=True)
dfDAQ = df.set_axis(['Time', 'Voltage1', 'Voltage2'], axis=1)
DaqFs = 1 / dfDAQ.Time.diff().mean()
print(f'Found DAQ sampling rate: {DaqFs}')

## 50 Hz notch filter
sosfilt = butter(5, (950, 1050), 'bandstop', fs=DaqFs, output='sos')
sosfilt2 = butter(5, (1950, 2050), 'bandstop', fs=DaqFs, output='sos')


dfDAQ['Voltage1f'] = sosfiltfilt(sosfilt, dfDAQ.Voltage1, axis=0)
dfDAQ['Voltage1f'] = sosfiltfilt(sosfilt2, dfDAQ.Voltage1f, axis=0)
dfDAQ['Voltage2f'] = sosfiltfilt(sosfilt, dfDAQ.Voltage2, axis=0)




# calculate plot Power spectral density
f, psd = welch(dfDAQ.Voltage1, DaqFs, nperseg=1024)
f, psd2 = welch(dfDAQ.Voltage1f, DaqFs, nperseg=1024)

plt.figure()
plt.semilogy(f, psd)
plt.semilogy(f, psd2)
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()

dfDAQ['ElectV'] = dfDAQ.Voltage1f - dfDAQ.Voltage2f


fig, ax = plt.subplots()
ax.plot(dfDAQ.Time, dfDAQ.Voltage1, label='Voltage1', alpha=0.5)
ax.plot(dfDAQ.Time, dfDAQ.Voltage2, label='Voltage2', alpha=0.5)
ax.plot(dfDAQ.Time, dfDAQ.Voltage1f, label='Voltage1f')
ax.plot(dfDAQ.Time, dfDAQ.Voltage2f, label='Voltage2f')
axe = plt.twinx(ax)
axe.plot(dfDAQ.Time, dfDAQ.ElectV, label='V1-V2', color='k', alpha=0.5)


ax.set_xlabel('Time [s]')
ax.set_ylabel('Voltage [V]')
axe.set_ylabel('Current [A]')
ax.set_title('EGNITE 1203 50Hz notch filter')

ax.legend()
axe.legend()
plt.show()