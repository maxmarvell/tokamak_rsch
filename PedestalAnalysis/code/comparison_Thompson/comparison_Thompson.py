import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():

    # obtaining transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # initializing the subplots
    f1,axes1 = plt.subplots(3,2,sharex=True,sharey='row',figsize=(7,7),)
    f2,axes2 = plt.subplots(3,2,sharex=True,sharey='row',figsize=(7,7),)
    f1.subplots_adjust(hspace=0)
    f2.subplots_adjust(hspace=0)

    # setting the plot aesthetics
    for axes in [axes1,axes2]:
        axes[1][0].set(ylim=(-0.04,0.4))
        axes[2][0].set(ylim=(0,1.5))
        axes[0][0].set(xlim=(1.25,1.5),ylim=(-0.3,3))
        axes[0][0].annotate('$n_{e}$ [$10^{19}$m$^{-3}$]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
        axes[1][0].annotate('$T_{e}$ [keV]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
        axes[2][0].annotate('$p_{e}$ [$kNm^{-2}$]', xy=(0.02,0.02),xycoords='axes fraction',fontsize=9)
        axes[2][0].annotate('Major Radius [m]', xy=(0.78,-0.22),xycoords='axes fraction',fontsize=11)
        axes[0][0].annotate(f'L mode: $LH_t$-10ms', xy=(0.5,0.90),xycoords='axes fraction',fontsize=9)
        axes[0][1].annotate(f'H mode: $LH_t$+10ms', xy=(0.5,0.90),xycoords='axes fraction',fontsize=9)

    axes1[0][0].annotate('Conventional pedestal',xy=(0.72,1.04),xycoords='axes fraction',fontsize=11,fontweight='bold')
    axes1[0][0].annotate('$I_{p}=600kA$', xy=(0.02,1.04),xycoords='axes fraction',fontsize=9, color='tab:red')
    axes1[0][0].annotate('$I_{p}=700kA-Set:1$', xy=(0.02,1.14),xycoords='axes fraction',fontsize=9, color='tab:blue')
    axes1[0][0].annotate('$I_{p}=700kA-Set:2$', xy=(0.02,1.24),xycoords='axes fraction',fontsize=9, color='tab:purple')
    axes2[0][0].annotate('SUPER-X pedestal',xy=(0.82,1.04),xycoords='axes fraction',fontsize=11,fontweight='bold')

    # looping over every shot in the transition data
    for shot in transition_data.index:

        # obtaining the primary shot characteristics
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']

        # selecting one axes for each type of divertor
        if transition_data.at[shot,'Divertor']=='Conventional':
            axes = axes1
            axes1[0][1].annotate(f'$B_t$= {abs(Bt)}T', xy=(0.86,1.04),xycoords='axes fraction',fontsize=9)
        else:
            axes = axes2
            axes2[0][1].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T', xy=(0.82,1.04),xycoords='axes fraction',fontsize=9)

        # obtaining the thompson times
        Thomtimes = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')
        LHtime = transition_data.at[shot,'LH']

        # for comparison taking 10ms before and after the transition
        times = [LHtime-0.01,LHtime+0.01]

        # changing the marker color based on current and set
        if current == 600:
            c = 'tab:red'
        elif set == 2:
            c = 'tab:purple'
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
    f1.savefig(f'./figures/convCompare.png')
    f2.savefig(f'./figures/supXCompare.png')

if __name__ == '__main__':
    main()       