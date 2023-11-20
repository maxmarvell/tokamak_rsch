import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # looping over every shot in the transition data
    for shot in transition_data.index:

        # initialising subfigure layout
        f = plt.figure(figsize=(7, 9))
        subf = f.subfigures(2,1,height_ratios=[3,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(2,2,sharex='col',sharey='row')
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.2)

        # obtain the import shot features plasma curret etc
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']
        Pth = transition_data.at[shot,'Pth_LH']

        # initilize the raw torroidal velocity data plot
        vTorrPedInner, = axes1[0][0].plot([],[],lw=1)
        vTorrPedOuter, = axes1[0][1].plot([],[],lw=1)

        # initilize the raw ion temperature data plot
        TiPedInner, = axes1[1][0].plot([],[],lw=1)
        TiPedOuter, = axes1[1][1].plot([],[],lw=1)

        # label the plot with shot number and divertor configuration
        axes1[0][0].annotate(f'#{int(shot)}-{set}\n{divertor} configuration', xy=(1.12,1.04),xycoords='axes fraction',fontsize=13,fontweight='bold',ha='center')

        # set limits for the plot
        axes1[0][0].set(xlim=(0.7,.85),ylim=((-0.5,1.3)))
        axes1[0][1].set(xlim=(1.3,1.45))
        axes1[1][0].set(ylim=(-0.5,1.9))

        # annotate with shot features and pedestal parameter
        axes1[0][1].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=10)
        axes1[0][0].annotate('$V_{Torr}$ [$10^{5}ms^{-1}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[1][0].annotate('$T_{i}$ [keV]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        # initilizing a time bar for the second subfigure
        timeBar = axes2.axvline(c='tab:red',linestyle='--')

        # loading the dalpha trace for the desired shot
        dAlpha = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['DalphaSP','DalphaSPTime'],index_col='DalphaSPTime')

        # plotting the second subfigure with dalpha time trace
        axes2.plot(dAlpha)
        axes2.set_xlim(transition_data.at[shot,'start'],
        transition_data.at[shot,'end'])

        # initializing a reference time in the top right hand corner
        time_text = axes1[0][0].text(-0.15, 1.2, '', transform=axes1[0][0].transAxes,fontweight='bold')

        # splining the plot to show inboard and outboard pedestals
        spliner(axes1[0])
        spliner(axes1[1])

        # initialzing all the animated lines to feed into animate
        def init():
            vTorrPedOuter.set_data([],[])
            vTorrPedInner.set_data([],[])
            TiPedOuter.set_data([],[])
            TiPedInner.set_data([],[])
            timeBar.set_xdata(0)
            return vTorrPedOuter,vTorrPedInner,TiPedOuter,TiPedInner,timeBar

        # animator function
        def animate(t):

            # load the transition time
            LHtime = transition_data.at[shot,'LH']

            # load the corresponding CXRS radial date
            data = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)

            # set the time text to t
            time_text.set_text(f'Transition time - t : {round(t-LHtime,3)*1e+3}ms')

            # filter for outer pedestal data
            dataOuter = data.loc[data['R'] > 1.1]
            OuterR = dataOuter['R'].values
            vTorrOuter = dataOuter['vTorr'].values*1e-5
            TiOuter = dataOuter['Ti'].values*1e-3

            # filter for inner pedestal data
            dataInner = data.loc[data['R'] < 1.05]
            InnerR = dataInner['R'].values
            vTorrInner = dataInner['vTorr'].values*1e-5
            TiInner = dataInner['Ti'].values*1e-3

            # set the raw inner and outer pedestal line values
            vTorrPedOuter.set_data(OuterR,vTorrOuter)
            vTorrPedInner.set_data(InnerR,vTorrInner)
            TiPedOuter.set_data(OuterR,TiOuter)
            TiPedInner.set_data(InnerR,TiInner)

            # set the time bar data to t
            timeBar.set_xdata(t)

            # return the lines
            return vTorrPedOuter,vTorrPedInner,TiPedOuter,TiPedInner,

        # load the corresponding thompson time data
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRSTime.csv')

        # call the animate function
        anim = FuncAnimation(f,animate,init_func=init,frames=times.t.values,interval=130,blit=False)
        
        # try saveing the function - error when no charge exchange data for shot
        try:
            anim.save(f'./figures/profile_{shot}.gif')
        except:
            print(f'No charge exchange data {shot}!')

# self defined spliner function to spline each row of the subplot array
def spliner(axes):

    axes[0].spines['right'].set_visible(False)
    axes[1].spines['left'].set_visible(False)
    axes[0].yaxis.tick_left()
    axes[1].yaxis.tick_right()

    d = .015

    kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False)
    axes[0].plot((1-d,1+d), (-d,+d), **kwargs)
    axes[0].plot((1-d,1+d),(1-d,1+d), **kwargs)

    kwargs.update(transform=axes[1].transAxes)
    axes[1].plot((-d,+d), (1-d,1+d), **kwargs)
    axes[1].plot((-d,+d), (-d,+d), **kwargs)

if __name__ == '__main__':
    main()