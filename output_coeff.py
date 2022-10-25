import numpy as np
from numpy import polyfit, poly1d
import os
import pandas as pd
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit
import time


def main():
    data_path = '../Assets/Resources/CSVOutput/'
    file_name = 'test_lumin_HMD.csv'
    data_file = data_path + 'Lumin/' + file_name
    print()
    while True:
        if (os.path.isfile(data_file)):
            time.sleep(1)
            t=pd.read_csv(data_file,index_col=0)
            process_data(data_path, data_file)
            break

def process_data(data_path, data_file):
    ## formal inpout data
    data_collection = ['LeftPupilD','RightPupilD','Lumin']
    data=[]
    blink_rate = 0

    t=pd.read_csv(data_file,index_col=0)
    for i in range(1,len(t[["LeftPupilD"]][100:-100])):
        if (t[["LeftPupilD"]].values[i] < 0 and t[["LeftPupilD"]].values[i-1] >0):
            blink_rate = blink_rate + 1
    t = interpolate_pupil(t[data_collection])
    t.index = range(len(t))
    t.rename(columns={'Unnamed: 0': 'Time'}, inplace=True)
    data.append(t[data_collection]) 

    # for test, choose which file
    data_index = 0
    # start frame
    start = 100
    # end frame
    end = len(data[data_index][['Lumin']].values)-100
    # lumin times adjustion
    multi_lumin = 1

    # equation matching
    x_lumin = data[data_index][['Lumin']][start:end].values.ravel()*multi_lumin
    x_lumin[x_lumin == 0] = 0.00001
    left_original_pupil = data[data_index][['LeftPupilD']][start:end].values.ravel()
    right_original_pupil = data[data_index][['RightPupilD']][start:end].values.ravel()
    coeff_left = curve_fit(func_curve, x_lumin, left_original_pupil)
    coeff_right = curve_fit(func_curve, x_lumin, right_original_pupil)
    ## coeff_left[0][0] * np.exp(coeff_left[0][1] *x) + coeff_left[0][2]
    output_csv = pd.DataFrame({
        'coeff_left': coeff_left[0].ravel(),
        'coeff_right': coeff_right[0].ravel(),
        'blink_rate': blink_rate
    })
    output_csv.to_csv(data_path + "python_data/" + "output.csv")


def interpolate_pupil(data, shi=20):
    data['LeftPupilD'][data['LeftPupilD']<0] = np.nan
    data['RightPupilD'][data['RightPupilD']<0] = np.nan
    data = data.interpolate(method='linear',axis=0,limit_direction ='both')
    data.dropna(axis=0)
    data_s = SG_fil(data,shi+1,2)
    return data_s

def SG_fil(data,shi,order=2):
    df = data.copy()
    column_name = df.columns.tolist()
    df_new = pd.DataFrame(columns=column_name)
    for n in column_name:
        df_new[n] = savgol_filter(df.loc[:,n],shi,order)
    return df_new  

def func_curve(x, a, b, c):
    return a * np.exp(b * x) + c

if __name__ == "__main__":
    main()