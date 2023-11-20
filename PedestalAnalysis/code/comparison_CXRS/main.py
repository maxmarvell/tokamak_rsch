import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():

    print('WARNING UNFINISHED - UNABLE TO CALCULATE Er!')

    # obtaining transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')
    
    # initializing the subplots
    f1,axes1 = plt.subplots(2,2,sharex=True,sharey='col',figsize=(7,7),)
    f2,axes2 = plt.subplots(2,2,sharex=True,sharey='col',figsize=(7,7),)
    f1.subplots_adjust(hspace=0)
    f2.subplots_adjust(hspace=0)

    # setting the plot aesthetics
    for ax in [axes1,axes2]:
        ax[0][0].set(xlim=(1.2,1.5),ylim=(-0.5,1.3))
        ax[0][0].annotate('$V_{Torr}$ [$10^{5}$m$^{-3}$]', xy=(0.02,0.92),xycoords='axes fraction',fontsize=9)
        ax[0][1].annotate('$E_{R}$ []', xy=(0.02,0.92),xycoords='axes fraction',fontsize=9)
        ax[1][0].annotate('Major Radius [m]', xy=(0.78,-0.22),xycoords='axes fraction',fontsize=11)
        ax[0][0].annotate('$I_{p}=600kA$', xy=(0.02,1.04),xycoords='axes fraction',fontsize=9, color='tab:red')
        ax[0][0].annotate('$I_{p}=700kA-Set:1$', xy=(0.02,1.14),xycoords='axes fraction',fontsize=9, color='tab:blue')
        ax[0][0].annotate('$I_{p}=700kA-Set:2$', xy=(0.02,1.24),xycoords='axes fraction',fontsize=9, color='tab:purple')

    axes1[0][0].annotate('Conventional pedestal',xy=(0.72,1.04),xycoords='axes fraction',fontsize=11,fontweight='bold')
    axes2[0][0].annotate('SUPER-X pedestal',xy=(0.72,1.04),xycoords='axes fraction',fontsize=11,fontweight='bold')

    # looping over every shot in the transition data
    for shot in transition_data.index:

        # selecting one axes for each type of divertor
        if transition_data.at[shot,'Divertor']=='Conventional':
            ax = axes1
        else:
            ax = axes2

        # obtaining the primary shot characteristics
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']

        # changing the marker color based on current and set
        if current == 600:
            c = 'tab:red'
        elif set == 2:
            c = 'tab:purple'
        else:
            c = 'tab:blue'

        # annotating the toroidal magnetic field
        ax[0][1].annotate(f'$B_t$= {abs(Bt)}T', xy=(0.86,1.04),xycoords='axes fraction',fontsize=9)

        # obtaining the charge exchange times
        CXtimes = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRSTime.csv')
        LHtime = transition_data.at[shot,'LH']

        # for comparison taking 10ms before and after the transition
        times = [LHtime-0.01,LHtime+0.01]

        for i,t in enumerate(times):

            # finding the closest time to before and after the transition
            CXt = CXtimes.at[(CXtimes['t']-(t)).abs().argsort()[0],'t']

            # try except statement to avois errors from missing data
            try:
                # obtain corresponding charge exchange radial profile
                data = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{CXt}s.csv')
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # only looking to outboard pedestal
                data = data.loc[data['R'] > 1.2]

                # plotting the errorbar for torroidal velocity
                ax[i][0].errorbar(data['R'],data['vTorr']*1e-5,fmt='^',yerr=data['vTorrErr']*1e-5,ms=3,color=c,alpha=0.8)

            # print error message warning of missing data
            except:
                print(f'No charge exchange for {int(shot)}!')
                break
    
    # saving the figures
    f1.savefig(f'./figures/convCompare.png')
    f2.savefig(f'./figures/supXCompare.png')

if __name__ == '__main__':
    main()       