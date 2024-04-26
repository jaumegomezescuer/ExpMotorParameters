from nptdms import TdmsFile


tdms_file = TdmsFile.read("./Data/0403DAQ/0703DAQ01.tdms")
df = tdms_file.as_dataframe(time_index=True,
                            scaled_data=False)
df.reset_index(inplace=True)
df = df.set_axis(['Time', 'Voltage'], axis=1)

