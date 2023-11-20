import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

def main():

    # load the transition data
    transitionData = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # loop over every shot to plot
    for shot in transitionData.index:

        # initilize 3D subpolts
        f, ax = plt.subplots(1,3,subplot_kw={'projection': '3d'},figsize=(12,9))

        # read the thompson time data into main
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')

        # extract key shot parameters
        divertor = transitionData.at[shot,'Divertor']
        set = transitionData.at[shot,'SET']

        # loop over every time
        for t in times['t'].values:

            # try except in case of missing data
            try:
                # read the correspondong thompson radial data into main
                data = pd.read_csv(f'../../data/radial_data_LH/{shot}/Thompson-{t}s.csv')
                data['t'] = np.ones(len(data['R']))*t
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # plot the radial profile in a 3D plot
                ax[0].plot3D(data['R'].values,data['t'].values,data['ne'].values*10**(-19))
                ax[1].plot3D(data['R'].values,data['t'].values,data['Te'].values*10**(-3))
                ax[2].plot3D(data['R'].values,data['t'].values,data['pe'].values*10**(-3))

            # report missing data
            except:
                print(f'No Thompson data for {int(shot)}')
                break

        # setting plot aesthetics
        for a in ax:
            a.set_xlabel('Major Radius [m]')
            a.set_ylabel('Time [s]')
        
        ax[0].set_title(f'#{int(shot)}',fontweight='bold')
        ax[1].set_title(f'Set-{set}',fontweight='bold')
        ax[2].set_title(f'{divertor} config',fontweight='bold')
        ax[0].set_zlim(0,7.5)
        ax[0].set_zlabel('Electron density $[10^{19}m^{-3}]$')
        ax[1].set_zlabel('Electron Temperature $[keV]$')
        ax[2].set_zlabel('Electron pressure $[kNm^{-2}]$')

        # saving the figure
        f.savefig(f'./figures/thompson-{shot}.png')

if __name__ == '__main__':
    main()