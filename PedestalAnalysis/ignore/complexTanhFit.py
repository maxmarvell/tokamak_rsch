import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def main():

    LHData = pd.read_excel('LHdata.xlsx',index_col='Shot Number')

    for shot in LHData.index:

        times = pd.read_csv(f'radialData/{shot}/ThompsonTime.csv')
        f,ax = plt.subplots()
        cols = ['ped','wid','off','pos','slo']
        peDf = pd.DataFrame(index=times['t [s]'],columns=cols)

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

            bounds = ([0,0,0,1.30,-np.inf],[max(pe)-min(pe),max(R),max(pe)-min(pe),1.45,np.inf])
            try:
                popt, pcov = curve_fit(than,R,pe,sigma=peErr,absolute_sigma=True)
                r = np.linspace(min(R),max(R),1000)
                ax.errorbar(R,pe,yerr=peErr)
                ax.plot(r, than(r,*popt),label=f'time - {t}s')
                ax.set_title(f'#{shot}',fontweight='bold')
                peDf = peDf.append(
                    pd.Series(popt,index=cols),ignore_index=True
                    )
            except:
                print('optimal parameters not obtained')

        peDf.to_csv(f'pedData/peData/ped{shot}.csv',index=False)
    plt.show()

def than(x,ped,wid,off,pos,slo):
    inside = (pos-x)/(2.*wid)
    mtanh = ((1.+slo*inside)*np.exp(inside)-np.exp(-inside))/(np.exp(inside)+np.exp(-inside))
    edge = (ped-off)/2.*(mtanh + 1.)+off
    return edge

def function_converter(x_list, x_value):
    for i in range(len(x_list)):
        if x_list[i] >= x_value:
            return i
    return -1

if  __name__ == '__main__':
    main()