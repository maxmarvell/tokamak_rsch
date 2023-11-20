import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    for shot in transition_data.index:

        # initialising subfigure layout
        f = plt.figure(figsize=(7, 9))
        subf = f.subfigures(2,1,height_ratios=[3,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(2,1,sharex='col')
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.2)

        # read the corresponding charge exchange time data
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRSTime.csv')

        # load the corresponding pedestal fit data
        ped = pd.read_excel(f'../../data/pedestal_fit/LH/outboard_{shot}.xlsx',sheet_name='ne',index_col='time')

        # insert a new row into the charge exchange time df
        for time in times.t.values:
            ped.loc[time] = [np.nan,np.nan,np.nan,np.nan,np.nan,]

        # sort the index and interpolate the values 
        ped.sort_index(inplace=True)
        ped.interpolate(inplace=True)

        # extract the key shot features
        divertor = transition_data.at[shot,'Divertor']
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        Pth = transition_data.at[shot,'Pth_LH']

        # initilize empty line for the raw torroidal velocitry and ion temperature profiles
        vTorrPed, = axes1[0].plot([],[],'o--',lw=1)
        TiPed, = axes1[1].plot([],[],'o--',lw=1)

        # initilize empty line to track the top of the pedestal
        pedVline0 =  axes1[0].axvline(c='red',lw=10,alpha=0.5)
        pedVline1 =  axes1[1].axvline(c='red',lw=10,alpha=0.5)

        # decorate plot with shot number and divertor configuration
        axes1[0].set_title(f'#{int(shot)}-{set}\n{divertor} configuration',fontweight='bold')

        # set the limits for the animated plot
        axes1[0].set(xlim=(1.1,1.5),ylim=(-0.5,1))
        axes1[1].set(ylim=(-0.5,1.7))

        # annotate jey parameters and pulse features
        axes1[0].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=10)
        axes1[0].annotate('Toroidal velocity [$10^{5}ms^{-1}$]',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[1].annotate('Ion temperature [keV]',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        # add a reference time tect
        time_text = axes1[0].text(-0.15, 1.2, '', transform=axes1[0].transAxes,fontweight='bold')

        # add a reference time bar to the second subfigure
        timeBar = axes2.axvline(c='tab:red',linestyle='--')

        # loading the dalpha trace for the desired shot
        dAlpha = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['DalphaSP','DalphaSPTime'],index_col='DalphaSPTime')

        # plotting the second subfigure with dalpha time trace
        axes2.plot(dAlpha)
        axes2.set_xlim(transition_data.at[shot,'start'],
        transition_data.at[shot,'end'])

        # label Dalpha trace 
        axes2.annotate(r'$D_{\alpha}[V]$',xy=(0.02,1.04),xycoords='axes fraction',fontsize=10)

        # initialize the lines with empty values and return them
        def init():
            vTorrPed.set_data([],[])
            TiPed.set_data([],[])
            pedVline0.set_xdata(0)
            pedVline1.set_xdata(0)
            timeBar.set_xdata(0)
            return vTorrPed,TiPed,pedVline0,pedVline1,timeBar

        # define the animate function
        def animate(t):

            # obtain shot transition time
            LHtime = transition_data.at[shot,'LH']

            # obtain radial data corresponding to time t
            data = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)

            # filter the data to only the outboard region
            data = data.loc[data['R'] > 1.1]

            # store radial data
            R = data['R'].values
            vTorr = data['vTorr'].values*1e-5
            Ti = data['Ti'].values*1e-3

            # set t in the time text window
            time_text.set_text(f'Transition time - t : {round(t-LHtime,4)*1e+3}ms')

            # set the lines for all raw pedestal data
            vTorrPed.set_data(R,vTorr)
            TiPed.set_data(R,Ti)

            # set the vertical line calculated from transport barrier and half pedestal width
            pedVline0.set_xdata(ped.loc[t,'position']-ped.loc[t,'width']/2)
            pedVline1.set_xdata(ped.loc[t,'position']-ped.loc[t,'width']/2)

            # set the time bar to t
            timeBar.set_xdata(t)

            # return the lines
            return vTorrPed,TiPed,pedVline0,pedVline1,timeBar

        # call animate function to try animate the plots
        anim = FuncAnimation(f,animate,init_func=init,frames=times.t.values,interval=150,blit=False)
        
        # try saveing the function - error when no charge exchange data for shot
        try:
            anim.save(f'./figures/ped_track_{shot}.gif')
        except:
            print(f'No charge exchange data {shot}!')

if __name__ == '__main__':
    main()