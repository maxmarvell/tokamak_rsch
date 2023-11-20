import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():

    # obtaining transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # initializing the subplots
    f,axes = plt.subplots(3,2,sharex='col',sharey='row',figsize=(7,7))
    f.subplots_adjust(hspace=0)

    # setting the plot aesthetics
    axes[1][0].set(ylim=(-0.1,1))
    axes[2][0].set(ylim=(0,4))
    axes[0][0].set(xlim=(1.25,1.5),ylim=(-0.5,5))
    axes[0][0].annotate('$n_{e}$ [$10^{19}$m$^{-3}$]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
    axes[1][0].annotate('$T_{e}$ [keV]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
    axes[2][0].annotate('$p_{e}$ [$kNm^{-2}$]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
    axes[0][0].annotate('Outer pedestal comparison',xy=(0.66,1.04),xycoords='axes fraction',fontsize=11,fontweight='bold')
    axes[2][0].annotate('Major Radius [m]', xy=(0.78,-0.22),xycoords='axes fraction',fontsize=11)
    axes[0][0].annotate(f'L mode: $LH_t$-10ms', xy=(0.5,0.90),xycoords='axes fraction',fontsize=9)
    axes[0][0].annotate(f'#45237 - Conventional', xy=(0.02,1.14),xycoords='axes fraction',fontsize=9,color='tab:blue')
    axes[0][0].annotate('#45154 - SUPER-X', xy=(0.02,1.04),xycoords='axes fraction',fontsize=9,color='tab:red')
    axes[0][1].annotate(f'H mode: $LH_t$+10ms', xy=(0.5,0.90),xycoords='axes fraction',fontsize=9)

    # looping over every shot in the transition data
    for shot in [45154.0,45237.0]:

        # obtaining the primary shot characteristics
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']

        axes[0][1].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T', xy=(0.82,1.04),xycoords='axes fraction',fontsize=9)

        # obtaining the thompson times
        Thomtimes = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')
        LHtime = transition_data.at[shot,'LH']

        # for comparison taking 10ms before and after the transition
        times = [LHtime-0.01,LHtime+0.01]

        # changing the marker color based on divertor
        if divertor == 'SUPER-X':
            c = 'tab:red'
        else:
            c = 'tab:blue'

        for i,t in enumerate(times):

            # finding the closest time to before and after the transition
            Thomt = Thomtimes.at[(Thomtimes['t']-(t)).abs().argsort()[0],'t']

            # try except statement to avois errors from missing data
            try:    
                # obtain corresponding thompson radial profile
                data = pd.read_csv(f'../../data/radial_data_LH/{shot}/Thompson-{Thomt}s.csv')
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # only looking to outboard pedestal
                data = data.loc[data['R'] > 1.2]

                # plotting the errorbar for ne, Te and pe
                axes[0][i].errorbar(data['R'],data['ne']*1e-19,fmt='^',yerr=data['neErr']*1e-19,ms=3,color=c,alpha=0.8)
                axes[1][i].errorbar(data['R'],data['Te']*1e-3,fmt='^',yerr=data['TeErr']*1e-3,ms=3,color=c,alpha=0.8)
                axes[2][i].errorbar(data['R'],data['pe']*1e-3,fmt='^',yerr=data['peErr']*1e-3,ms=3,color=c,alpha=0.8)

            # print error message warning of missing data
            except:
                print(f'No thompson for {int(shot)}!')
                break

    # saving the figures
    f.savefig(f'./figures/ConvSupXcompare.png')

if __name__ == '__main__':
    main()       