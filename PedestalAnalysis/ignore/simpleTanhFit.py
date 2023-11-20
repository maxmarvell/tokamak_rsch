import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import os

def main():

    LHdata = pd.read_excel('LHdata.xlsx',index_col='Shot Number')
    cwd = os.getcwd()

    for shot in LHdata.index[2:4]:

        divertor = LHdata.at[shot,'Divertor']

        times = pd.read_csv(f'radialData/{shot}/ThompsonTime.csv')
        f,ax = plt.subplots()
        df = pd.DataFrame(index=times['t [s]'])

        for t in times['t [s]'].values[::7]:

            data = pd.read_csv(f'radialData/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)
            data = data.loc[data['R'] > 1.25]
            R = data['R'].values
            
            ne = data['ne'].values*10**(-19)
            neErr = data['neErr'].values*10**(-19)
            Te = data['Te'].values
            TeErr = data['TeErr'].values
            pe = data['pe']*10**(-3)
            peErr = data['peErr']*10**(-3)

            bounds = ([0,0,min(R),0,-np.inf,0,min(R)],[(max(pe)-min(pe)),np.inf,max(R),max(R),np.inf,np.inf,max(R)])

            try:
                popt, pcov = curve_fit(than,R,pe,bounds=bounds,sigma=peErr,absolute_sigma=True)
                r = np.linspace(min(R),max(R),1000)
                ax.errorbar(R,pe,yerr=peErr,LineStyle='--')
                ax.plot(r, than(r,*popt),label=f'time - {t}s')
                ax.set_title(f'#{int(shot)} {divertor}',fontweight='bold')
                ax.set_ylabel('Pressure [$kNm^{-2}$]')
                ax.set_xlabel('Major Radius [m]')
                ax.set_xlim(1.25,1.45)
                df.at[t,'a'] = popt[0]
                df.at[t,'b'] = popt[1]
                df.at[t,'xSym'] = popt[2]
                df.at[t,'width'] = popt[3]
                df.at[t,'m'] = popt[4]
                df.at[t,'c'] = popt[5]
                df.at[t,'d'] = popt[6]
            except:
                print('bounds not sufficent')

        plt.savefig(cwd+f'/old/plots/beginnerTanh{shot}.png')

def than(x,a,b,xSym,width,m,c,d):
    return (a*np.tanh(2*(xSym-x)/width)+b)*(x>=d) + (m*x+c)*(x<d)

def function_converter(x_list, x_value):
    for i in range(len(x_list)):
        if x_list[i] >= x_value:
            return i
    return -1

if  __name__ == '__main__':
    main()