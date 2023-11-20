import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def main():

    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    f1,axes1 = plt.subplots(2,2,sharex=True,sharey=True)
    f2,axes2 = plt.subplots(2,2,sharex=True,sharey=True)

    f1.subplots_adjust(hspace=0)
    f2.subplots_adjust(hspace=0)

    for transition,ax1,ax2 in zip(['LH','HL'],axes1,axes2):

        for shot in transition_data.index:

            # obtain transition features
            LH = transition_data.at[shot,transition]

            # obtain shot features
            divertor = transition_data.at[shot, 'Divertor']
            Ip = transition_data.at[shot, 'Ip']

            try:
                # loading the time resolution data for thompson scattering and CXRS
                ThomTimes = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/ThompsonTime.csv')
            except:
                print('No '+transition+f' transition for {shot}!')
                continue

            # selecting the times to plot
            times = ThomTimes.loc[(ThomTimes['t']-(LH)).abs().argsort()[0:2]]
            times.sort_index(inplace=True)
            times = times['t'].values

            # stratifying colors based on divertor and plasma current
            if divertor == 'SUPER-X':
                c = 'tab:red'
            elif Ip == 600:
                c = 'tab:purple'
            else:
                c = 'tab:blue'

            for i,t in enumerate(times):
                
                # call method to find temperature, density and pressure pedestal height
                Te = find_ped_height(transition,shot,'Te',t,pow=1e-3)
                ne = find_ped_height(transition,shot,'ne',t,pow=1e-19)
                pe = find_ped_height(transition,shot,'pe',t,pow=1e-3)

                try:
                    TiDf = pd.read_excel('../../data/interpolations/'+transition+f'/CXRS/outboard_{shot}.xlsx',usecols=['t','Ti'],
                    index_col='t')
                    TiDf = TiDf.loc[(TiDf['Ti']>0) & (TiDf['Ti']<400)]
                    Ti = interpolate.interp1d(TiDf.index,TiDf.Ti.values*1e-3)
                except:
                    print(f'No charge exchange data {shot}!')
            
                try:
                    print(Te(t))
                    ax1[i].plot(ne(t),Te(t),'^',color=c)
                except:
                    print(f'Unable to plot Te pedestal {shot}!')

                try:
                    print(Te(t))
                    ax1[i].plot(ne(t),Ti(t),'^',color=c,markerfacecolor='none')
                except:
                    print(f'Unable to plot Ti pedestal {shot}!')

                try:
                    ax2[i].plot(ne(t),pe(t),'^',color=c)
                    ax1[i].annotate(f'{transition}',xy=(0.02,0.04),xycoords='axes fraction',fontsize=9)
                except:
                    print(f'Unable to plot pe pedestal {shot}!')

    for ax in [axes1,axes2]:
        ax[1][0].annotate('$n_{e-knee}$ $[10^{19}m^{-3}]$',xy=(0.85,-0.2),xycoords='axes fraction',fontsize=10,)
        ax[0][0].annotate('Last L mode point',xy=(0.02,0.92),xycoords='axes fraction',fontsize=9,fontweight='bold')
        ax[1][0].annotate('First H mode point',xy=(0.02,0.92),xycoords='axes fraction',fontsize=9,fontweight='bold')
        ax[0][1].annotate('Last H mode point',xy=(0.02,0.92),xycoords='axes fraction',fontsize=9,fontweight='bold')
        ax[1][1].annotate('First L mode point',xy=(0.02,0.92),xycoords='axes fraction',fontsize=9,fontweight='bold')
        ax[0][0].annotate('SUPER-X:$I_{p}=600kA$',xy=(0.02,1.04),xycoords='axes fraction',fontsize=9,color='tab:red',fontweight='bold')
        ax[0][0].annotate('Conventional:$I_{p}=750kA$',xy=(0.02,1.13),xycoords='axes fraction',fontsize=9,color='tab:blue',fontweight='bold')
        ax[0][0].annotate('Conventional:$I_{p}=600kA$',xy=(0.02,1.22),xycoords='axes fraction',fontsize=9,color='tab:purple',fontweight='bold')

    axes1[1][0].annotate('$T_{e-knee}$ / $T_{i-knee}$ [keV]',xy=(-0.23,0.5),xycoords='axes fraction',fontsize=10,rotation=90,ha='center')
    axes2[1][0].annotate('$p_{e-knee}$ $[kNm^{-3}]$',xy=(-0.23,0.7),xycoords='axes fraction',fontsize=10,rotation=90,ha='center')
    axes1[0][0].set_ylim(-0.04,0.45)

    f1.savefig('./figures/tempCorrelation.png')
    f2.savefig('./figures/pressureCorrelation.png')

def find_ped_height(transition,shot,sheetname,t,pow):

    try:
        df = pd.read_excel('../../data/pedestal_fit/'+transition+f'/outboard_{shot}.xlsx',sheet_name=sheetname,usecols=['height','time'],
        index_col='time')
        ped = interpolate.interp1d(df.index,df.height.values)
        if np.isnan(ped(t)):
            raise Exception('Pedestal was not fitted well around temporal location!')

    except:
        df = pd.read_excel('../../data/interpolations/'+transition+f'/thompson/outboard_{shot}.xlsx',usecols=['t',sheetname],
        index_col='t')
        ped = interpolate.interp1d(df.index,df.iloc[:,0].values*pow,fill_value='extrapolate')

    return ped

if __name__ == '__main__':
    main()