import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
from scipy.optimize import curve_fit
import os

def main():

    LHData = pd.read_excel('../LHdata.xlsx',index_col='Shot Number')
    cwd = os.getcwd()

    for shot in LHData.index:

        set = LHData.at[shot,'SET']
        current = LHData.at[shot,'LoopCurrent']
        Bt = LHData.at[shot,'BT']
        divertor = LHData.at[shot,'Divertor']

        f,ax = plt.subplots(3,1,sharex=True)
        f.subplots_adjust(hspace=0)

        nePed, = ax[0].plot([],[],'x',lw=1)
        neTanh, = ax[0].plot([],[],lw=1)
        TePed, = ax[1].plot([],[],'x',lw=1)
        TeTanh, = ax[1].plot([],[],lw=1)
        pePed, = ax[2].plot([],[],'x',lw=1)
        peTanh, = ax[2].plot([],[],lw=1)

        ax[0].set(title=f'{divertor} pedestal #{int(shot)}-{set}',xlim=(0.3,0.8),ylim=(0,5))
        ax[1].set(ylim=(0,1))
        ax[2].set(ylim=(0,4),xlabel='Major Radius')
        time_text = ax[1].text(0.5, 0.8, '', transform=ax[1].transAxes,fontweight='bold')

        ax[0].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T', xy=(0.86,1.04),xycoords='axes fraction',fontsize=10)
        ax[0].annotate('$n_{e}$ [$10^{-19}$m$^{-3}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        ax[1].annotate('$T_{e}$ [keV]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        ax[2].annotate('$p_{e}$ [$10^{-3}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        def init():
            nePed.set_data([],[])
            neTanh.set_data([],[])
            TePed.set_data([],[])
            TeTanh.set_data([],[])
            pePed.set_data([],[])
            peTanh.set_data([],[])
            return nePed,TePed,pePed,neTanh,TeTanh,peTanh

        def animate(j):

            times = pd.read_csv(f'../radialData/{shot}/ThompsonTime.csv')
            t = times.iat[j,0]
            LHtime = LHData.at[shot,'L-H time']

            if LHtime < t:
                neTanh.set(color='red')
                TeTanh.set(color='red')
                peTanh.set(color='red')
            else:
                neTanh.set(color='green')
                TeTanh.set(color='green')
                peTanh.set(color='green')

            data = pd.read_csv(f'../radialData/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)
            data = data.loc[data['R'] < 0.8]

            R = data['R'].values
            ne = data['ne'].values*10**(-19)
            neErr = data['neErr'].values*10**(-19)
            Te = data['Te'].values*10**(-3)
            TeErr = data['TeErr'].values*10**(-3)
            pe = data['pe'].values*10**(-3)
            peErr = data['peErr'].values*10**(-3)

            time_text.set_text(f'Transition time - t : {round(t-LHtime,3)*10**3}ms')

            nePed.set_data(R,ne)
            TePed.set_data(R,Te)
            pePed.set_data(R,pe)

            r = np.linspace(min(R),max(R),1000)
            
            y1 = optimize(R,ne,neErr)
            y2 = optimize(R,Te,TeErr)
            y3 = optimize(R,pe,peErr)

            neTanh.set_data([r],[y1])
            TeTanh.set_data([r],[y2])
            peTanh.set_data([r],[y3])

            return nePed,TePed,pePed,neTanh,TeTanh,peTanh

        times = pd.read_csv(f'../radialData/{shot}/ThompsonTime.csv')
        anim = animation.FuncAnimation(f,animate,init_func=init,frames=len(times['t [s]'].values),interval=130,blit=False)
        anim.save(cwd+f'/Inboard/PedEv{shot}.gif')

def optimize(R,param,error):
    r = np.linspace(min(R),max(R),1000)
    try:
        neOpt, neCov = curve_fit(mtanh,R,param,sigma=error,absolute_sigma=True)
        y1 = mtanh(r,*neOpt)
    except:
        y1 = np.zeros(len(r))
        y1[:] = np.nan
    return y1

def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

if __name__ == '__main__':
    main()