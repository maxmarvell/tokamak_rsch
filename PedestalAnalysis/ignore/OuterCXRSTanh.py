import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from scipy.optimize import curve_fit

def main():

    LHData = pd.read_excel('LHdata.xlsx',index_col='Shot Number')

    for shot in LHData.index:
        f,ax = plt.subplots(2,1,sharex=True)
        f.subplots_adjust(hspace=0)

        vTorrPed, = ax[0].plot([],[],'o--',lw=1)
        #vTorrTanh, = ax[0].plot([],[],lw=1)
        TiPed, = ax[1].plot([],[],'o--',lw=1)
        #TiTanh, = ax[1].plot([],[],lw=1)

        ax[0].set(title=f'Pedestal evolution for shot {shot}',xlim=(1.1,1.5),ylim=(0,1))
        ax[1].set(ylim=(0,1.5))
        time_text = ax[1].text(0.5, 0.8, '', transform=ax[1].transAxes,fontweight='bold')

        ax[0].annotate('Toroidal velocity x $10^{-5}$ [m$s^{-1}$]',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        ax[1].annotate('Ion temperature [keV]',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        def init():
            vTorrPed.set_data([],[])
            #vTorrTanh.set_data([],[])
            TiPed.set_data([],[])
            #TiTanh.set_data([],[])

            return vTorrPed,TiPed#,vTorrTanh,TiTanh

        def animate(j):

            times = pd.read_csv(f'radialData/{shot}/CXRSTime.csv')
            t = times.iat[j,0]
            LHtime = LHData.at[shot,'L-H time']

            data = pd.read_csv(f'radialData/{shot}/CXRS-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)
            data = data.loc[data['R'] > 1.1]

            R = data['R'].values
            vTorr = data['vTorr'].values*10**(-5)
            vTorrErr = data['vTorrErr'].values*10**(-5)
            Ti = data['Ti'].values*10**(-3)
            TiErr = data['TiErr'].values*10**(-3)

            time_text.set_text(f'Transition time - t : {round(t-LHtime,4)*10**3}ms')

            vTorrPed.set_data(R,vTorr)
            TiPed.set_data(R,Ti)

            #r = np.linspace(min(R),max(R),1000)
            #
            #try:
            #    vTorrOpt, vTorrCov = curve_fit(mtanh,R,vTorr,sigma=vTorrErr,absolute_sigma=True)
            #    y1 = mtanh(r,*vTorrOpt)
            #except:
            #    y1 = np.zeros(len(r))
            #    y1[:] = np.nan

            #try:
            #    TiOpt, TiCov = curve_fit(mtanh,R,Ti,sigma=TiErr,absolute_sigma=True)
            #    y2 = mtanh(r,*TiOpt)
            #except:
            #    y2 = np.empty(len(r))
            #    y2[:] = np.nan

            #vTorrTanh.set_data([r],[y1])
            #TiTanh.set_data([r],[y2])

            return vTorrPed,TiPed#,vTorrTanh,TiTanh

        times = pd.read_csv(f'radialData/{shot}/CXRSTime.csv')
        anim = FuncAnimation(f,animate,init_func=init,frames=len(times['t [s]'].values),interval=150,blit=False)
        try:
            anim.save(f'PedFinal/CXRS/Outboard/PedEv{shot}.gif')
        except:
            print(f'check {shot}')

def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

if __name__ == '__main__':
    main()