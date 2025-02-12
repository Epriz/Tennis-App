import numpy as np
import pandas as pd

'''This script was run only once and was used used to calibrate 
   the sensors and calculate the offset between the sensors that. 
   were placed on the hand and the sensor. This was a manifacturer
   issue which appeared to be constant, therefore it was decided
   to apply those offsets to every calibration, without the needing
   of recalibrating the sensors every time.'''

def import_data(data_x, data_y, data_z):
    """Import data from filepath and return a pandas dataframe."""
    dataframe_x = pd.read_csv(data_x, skiprows=4, header=0, sep=';', usecols=[0,1], names=['Time', 'Angle'])
    dataframe_y = pd.read_csv(data_y, skiprows=4, header=0, sep=';', usecols=[0,1], names=['Time', 'Angle'])
    dataframe_z = pd.read_csv(data_z, skiprows=4, header=0, sep=';', usecols=[0,1], names=['Time', 'Angle'])
    #convert dataframe values (time and angle) to numeric values
    dataframe_x['Time'] = pd.to_numeric(dataframe_x['Time'].str.replace(',','.'))
    dataframe_x['Angle'] = pd.to_numeric(dataframe_x['Angle'].str.replace(',','.'))
    dataframe_y['Time'] = pd.to_numeric(dataframe_y['Time'].str.replace(',','.'))
    dataframe_y['Angle'] = pd.to_numeric(dataframe_y['Angle'].str.replace(',','.'))
    dataframe_z['Time'] = pd.to_numeric(dataframe_z['Time'].str.replace(',','.'))
    dataframe_z['Angle'] = pd.to_numeric(dataframe_z['Angle'].str.replace(',','.'))

    
    return dataframe_x, dataframe_y, dataframe_z


def sensor_to_sensor_calibration(sens_sens_x, sens_sens_y, sens_sens_z):
    """Zero the offset of the sensor-to-sensor data and return the calibrated signal."""
    sens_sens_x_cal = dataframe_x['Angle'] - np.mean(dataframe_x['Angle'])
    sens_sens_y_cal = dataframe_y['Angle'] - np.mean(dataframe_y['Angle'])
    sens_sens_z_cal = dataframe_z['Angle'] - np.mean(dataframe_z['Angle'])
    #create a new dataframe with the calibrated data and the time
    dataframe_x_new = pd.DataFrame({'Time': dataframe_x['Time'], 'Angle': sens_sens_x_cal})
    dataframe_y_new = pd.DataFrame({'Time': dataframe_y['Time'], 'Angle': sens_sens_y_cal})
    dataframe_z_new = pd.DataFrame({'Time': dataframe_z['Time'], 'Angle': sens_sens_z_cal})

    return dataframe_x_new, dataframe_y_new, dataframe_z_new


#call the functions
data_x = r"/Users/tommaso/Università /MCI Bachelor MGST/Kurse/5. Semester/Project/TENNIS APP 2/CODE_AND_DATA/calibration_data/Test_Tennis_sensor_error/Noraxon_MyoMotion-Segments-Object_1-RT_Angle1_x.csv"
data_y = r"/Users/tommaso/Università /MCI Bachelor MGST/Kurse/5. Semester/Project/TENNIS APP 2/CODE_AND_DATA/calibration_data/Test_Tennis_sensor_error/Noraxon_MyoMotion-Segments-Object_1-RT_Angle1_y.csv"
data_z = r"/Users/tommaso/Università /MCI Bachelor MGST/Kurse/5. Semester/Project/TENNIS APP 2/CODE_AND_DATA/calibration_data/Test_Tennis_sensor_error/Noraxon_MyoMotion-Segments-Object_1-RT_Angle1_z.csv"

dataframe_x, dataframe_y, dataframe_z = import_data(data_x, data_y, data_z)

#sens_sens_x_filt, sens_sens_y_filt, sens_sens_z_filt = filter_data(dataframe_x['Angle'], dataframe_y['Angle'], dataframe_z['Angle'])

dataframe_x_new, dataframe_y_new, dataframe_z_new = sensor_to_sensor_calibration(dataframe_x, dataframe_y, dataframe_z)

mean_x = np.mean(dataframe_x['Angle'])
mean_y = np.mean(dataframe_y['Angle'])
mean_z = np.mean(dataframe_z['Angle'])

#round the result to 2 decimal places
global Offset_x, Offset_y, Offset_z

Offset_x = round(mean_x, 2)
Offset_y = round(mean_y, 2)
Offset_z = round(mean_z, 2)

print("The mean error in the angle between the sensors is: ", "X: ",Offset_x, "Y: ", Offset_y, "Z: ", Offset_z)