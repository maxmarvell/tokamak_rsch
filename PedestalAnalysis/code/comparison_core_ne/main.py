import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def main():

    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')
    
    f1,axes1 = plt.subplots(3,1,sharex=True)
    f2,axes2 = plt.subplots(3,1,sharex=True)

    axes1[0].annotate('$P_{th}$ [$MW$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes1[1].annotate('$T_{e}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes1[2].annotate('$T_{i}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

    axes2[0].annotate('$P_{th}$ [$MW$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes2[1].annotate('$T_{e}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes2[2].annotate('$T_{i}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

    axes1[0].annotate('SUPER-X', xy=(0.02,1.04),xycoords='axes fraction',fontsize=9, color='tab:red')
    axes1[0].annotate('Conventional:$I_p=750kA$', xy=(0.02,1.14),xycoords='axes fraction',fontsize=9, color='tab:blue')
    axes1[0].annotate('Conventional:$I_p=750kA$', xy=(0.02,1.24),xycoords='axes fraction',fontsize=9, color='tab:purple')

    axes2[0].annotate('SUPER-X', xy=(0.02,1.04),xycoords='axes fraction',fontsize=9, color='tab:red')
    axes2[0].annotate('Conventional:$I_p=750kA$', xy=(0.02,1.14),xycoords='axes fraction',fontsize=9, color='tab:blue')
    axes2[0].annotate('Conventional:$I_p=600kA$', xy=(0.02,1.24),xycoords='axes fraction',fontsize=9, color='tab:purple')

    for shot in transition_data.index:

        # obtain transition features
        LH = transition_data.at[shot,'LH']
        Pth = transition_data.at[shot,'Pth_LH']
        ne = transition_data.at[shot, 'ne_LH']

        # obtain shot features
        divertor = transition_data.at[shot, 'Divertor']
        Ip = transition_data.at[shot, 'Ip']

        # stratifying colors based on divertor and plasma current
        if divertor == 'SUPER-X':
            c = 'tab:red'
        elif Ip == 600:
            c = 'tab:purple'
        else:
            c = 'tab:blue'

        # loading the time resolution data for thompson scattering and CXRS
        ThomTimes = pd.read_csv(f'../../data/radial_data/{shot}/ThompsonTime.csv')

        # selecting the times to plot
        times = ThomTimes.loc[(ThomTimes['t [s]']-(LH)).abs().argsort()[0:2]]
        times.sort_index(inplace=True)
        times = times['t [s]'].values

        # looping over Lmode and Hmode
        for t,ax in zip(times,[axes1,axes2]):

            ax[0].plot(ne,Pth,'x',color=c)

            try:

                TeDf = pd.read_excel(f'../../data/pedestal_fit/outboard_{shot}.xlsx',sheet_name='Te',usecols=['height','time'],
                index_col='time')

                Te = interpolate.interp1d(TeDf.index,TeDf.height.values)

                if np.isnan(Te(t)):
                    raise Exception('pedestal was not fitted well before transition')

                ax[1].plot(ne,Te(t),'x',color=c)
        
            except:

                print('Pedestal fit for electron temperature not good enough')

                TeDf = pd.read_excel(f'../../data/interpolations/thompson/outboard_{shot}.xlsx',usecols=['t','Te'],
                index_col='t')

                Te = interpolate.interp1d(TeDf.index,TeDf.Te.values,fill_value='extrapolate')

                ax[1].plot(ne,Te(t),'x',color=c)
        
            try:

                TiDf = pd.read_excel(f'../../data/interpolations/CXRS/outboard_{shot}.xlsx',usecols=['t','Ti'],
                index_col='t')

                TiDf = TiDf.loc[(TiDf['Ti']>0) & (TiDf['Ti']<400)]

                Ti = interpolate.interp1d(TiDf.index,TiDf.Ti.values)

                ax[2].plot(ne,Ti(t),'^',color=c)

            except:

                print(f'NO CC {shot}')


    f1.savefig('./figures/Lmode_stratified.png')
    f2.savefig('./figures/Hmode_stratified.png')


if __name__ == '__main__':
    main()