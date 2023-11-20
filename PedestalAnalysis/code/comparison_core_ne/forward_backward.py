import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')
    
    f,axes = plt.subplots(3,4,sharex=True,sharey='row',figsize=(9,6))
    f.subplots_adjust(hspace=0)

    axes[0][0].annotate('$P_{th}$ [$MW$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes[1][0].annotate('$T_{e}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
    axes[2][0].annotate('$T_{i}$ [$eV$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

    axes[0][0].annotate('SUPER-X:$I_p=600kA$', xy=(-0.7,1.08),xycoords='axes fraction',fontsize=9, color='tab:red')
    axes[0][0].annotate('Conventional:$I_p=750kA$', xy=(-0.7,1.20),xycoords='axes fraction',fontsize=9, color='tab:blue')
    axes[0][0].annotate('Conventional:$I_p=600kA$', xy=(-0.7,1.32),xycoords='axes fraction',fontsize=9, color='tab:purple')

    axes[0][0].set_title('Last L mode',fontstyle='italic')
    axes[0][1].set_title('First H mode',fontstyle='italic')
    axes[0][2].set_title('Last H mode',fontstyle='italic')
    axes[0][3].set_title('First L mode',fontstyle='italic')

    axes[2][1].annotate('Line averaged $n_{e}$ $[m^{-3}]$',xy=(0.65,-0.3),xycoords='axes fraction',fontsize=12)

    axes[0][0].set(ylim=(-0.3,3),xlim=(0,3.8))

    for transition,ax in zip(['LH','HL'],[axes.T[0:2],axes.T[2:4]]):

        for shot in transition_data.index:

            # obtain transition features
            LH = transition_data.at[shot,transition]
            Pth = transition_data.at[shot,'Pth_'+transition]
            ne = transition_data.at[shot, 'ne_'+transition]*1e-19

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

            # loading the time resolution data for thompson scattering
            try:
                ThomTimes = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/ThompsonTime.csv')
            except:
                print('No '+transition+f' transition for {shot}!')
                continue

            # selecting the times to plot
            times = ThomTimes.loc[(ThomTimes['t']-(LH)).abs().argsort()[2:4]]

            if transition == 'LH':
                times.sort_index(inplace=True)
            else:
                times.sort_index(inplace=True,ascending=False)

            times = times['t'].values

            # looping over Lmode and Hmode
            for i,t in enumerate(times):

                ax[i][0].plot(ne,Pth,'x',color=c)

                try:
                    TeDf = pd.read_excel(f'../../data/pedestal_fit/'+transition+f'/outboard_{shot}.xlsx',sheet_name='Te',usecols=['height','time'],index_col='time')
                    Te = interpolate.interp1d(TeDf.index,TeDf.height.values)
                    if np.isnan(Te(t)):
                        raise Exception('pedestal was not fitted well before transition')
                    ax[i][1].plot(ne,Te(t),'x',color=c)
            
                except:
                    TeDf = pd.read_excel(f'../../data/interpolations/'+transition+f'/thompson/outboard_{shot}.xlsx',usecols=['t','Te'],index_col='t')
                    Te = interpolate.interp1d(TeDf.index,TeDf.Te.values,fill_value='extrapolate')
                    ax[i][1].plot(ne,Te(t),'x',color=c)
            
                try:
                    TiDf = pd.read_excel(f'../../data/interpolations/'+transition+f'/CXRS/outboard_{shot}.xlsx',usecols=['t','Ti'],index_col='t')
                    TiDf = TiDf.loc[(TiDf['Ti']>0) & (TiDf['Ti']<400)]
                    Ti = interpolate.interp1d(TiDf.index,TiDf.Ti.values)
                    ax[i][2].plot(ne,Ti(t),'x',color=c)

                except:
                    print(f'No charge exchange data {shot}!')

    f.savefig('./figures/stratified.png')


if __name__ == '__main__':
    main()