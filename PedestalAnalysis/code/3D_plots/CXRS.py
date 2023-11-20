import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

def main():

    # load the transition data
    transitionData = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # loop over every shot to plot
    for shot in transitionData.index:

        # initilize 3D subpolts
        f, ax = plt.subplots(1,2,subplot_kw={'projection': '3d'},figsize=(12,9))

        # read the CXRS time data into main
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRSTime.csv')

        # extract key shot parameters
        divertor = transitionData.at[shot,'Divertor']
        set = transitionData.at[shot,'SET']

        # loop over every time
        for t in times['t'].values:

            # try except in case of missing data
            try:
                # read the correspondong CXRS radial data into main
                data = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{t}s.csv')
                data['t'] = np.ones(len(data['R']))*t
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # plot the radial profile in a 3D plot
                ax[0].plot3D(data['R'].values,data['t'].values,data['Ti'].values*1e-3)
                ax[1].plot3D(data['R'].values,data['t'].values,data['vTorr'].values*1e-5)

            # report missing data
            except:
                print(f'No CXRS data for {int(shot)}')
                break

        # setting plot aesthetics
        for a in ax:
            a.set_xlabel('Major Radius [m]')
            a.set_ylabel('Time [s]')
        
        ax[0].set_title(f'#{int(shot)} Set-{set}',fontweight='bold')
        ax[1].set_title(f'{divertor} config',fontweight='bold')
        ax[0].set_zlim(0,2.5)
        ax[0].set_zlabel('Ion temperature $[keV]$')
        ax[1].set_zlim(0,2)
        ax[1].set_zlabel('Toroidal velocity $[10^{5}ms^{-1}]$')

        # saving the figure
        f.savefig(f'./figures/CXRS-{shot}.png')

if __name__ == '__main__':
    main()