import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def main():

    LHData = pd.read_excel('LHdata.xlsx',index_col='Shot Number')

    for shot in LHData.index:

        times = pd.read_csv(f'radialData/{shot}/ThompsonTime.csv')
        f,ax = plt.subplots()
        cols = ['position','width','height','core_slope','offset']
        peDf = neDf = TeDf = pd.DataFrame(columns=cols)

        for t in times['t [s]'].values:

            data = pd.read_csv(f'radialData/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)
            data = data.loc[data['R'] > 1.25]
            R = data['R'].values
            
            ne = data['ne'].values*10**(-19)
            neErr = data['neErr'].values*10**(-19)
            Te = data['Te'].values
            TeErr = data['TeErr'].values
            pe = data['pe']
            peErr = data['peErr']

            nePopt = optimize(R,ne,neErr)
            TePopt = optimize(R,Te,TeErr)
            pePopt = optimize(R,pe,peErr)

            neDf = neDf.append(
                pd.Series(nePopt,index=cols),ignore_index=True
            )

            TeDf = TeDf.append(
                pd.Series(TePopt,index=cols),ignore_index=True
            )

            peDf = peDf.append(
                pd.Series(pePopt,index=cols),ignore_index=True
            )

        neDf.loc[:,'time'] = times['t [s]'].values
        TeDf.loc[:,'time'] = times['t [s]'].values
        peDf.loc[:,'time'] = times['t [s]'].values

        neDf.to_csv(f'pedDataNew/neData/ped{shot}.csv',index=False)
        TeDf.to_csv(f'pedDataNew/TeData/ped{shot}.csv',index=False)
        peDf.to_csv(f'pedDataNew/peData/ped{shot}.csv',index=False)

def optimize(R,param,error):
    r = np.linspace(min(R),max(R),1000)
    try:
        popt, pcov = curve_fit(mtanh,R,param,sigma=error,absolute_sigma=True)
        y1 = mtanh(r,*popt)
    except:
        y1 = np.zeros(len(r))
        y1[:] = np.nan
    return popt

def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

def function_converter(x_list, x_value):
    for i in range(len(x_list)):
        if x_list[i] >= x_value:
            return i
    return -1

if  __name__ == '__main__':
    main()