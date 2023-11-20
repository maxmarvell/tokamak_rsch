import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

def main():

    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')
    
    f1,axes1 = plt.subplots(2,1,sharex=True)
    f2,axes2 = plt.subplots(2,1,sharex=True)

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

                ax[1].plot(ne,Ti(t),'^',color=c)

            except:

                print(f'NO CC {shot}')


    f1.savefig('./figures/Lmode_compare.png')
    f2.savefig('./figures/Hmode_compare.png')


if __name__ == '__main__':
    main()


#
#
#            thompsonData = pd.read_csv(f'../../data/pedestal_interpolation_Thompson/ped{shot}.csv',index_col='t')
#
#            try:
#                CXData = pd.read_csv(f'../../data/pedestal_interpolation_CXRS/ped{shot}.csv',index_col='t')
#            except:
#                print(f'No charge exchange {shot}!')
#                continue
#
#            thomTime = pd.read_csv(f'../../data/radial_data/{shot}/ThompsonTime.csv')
#
#            LHtime = transition_data.at[shot,'LH']
#
#            times = thomTime.loc[(thomTime['t [s]']-(LHtime)).abs().argsort()[2:4]]
#            times.sort_values('t [s]',inplace=True)

        

