import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
from scipy.optimize import curve_fit
from scipy import interpolate

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # looping over every shot in the transition data
    for shot in transition_data.index:

        # obtianing the thompson time resolution data
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')

        # obtaining the corresponding LCFS data 
        time_trace_data = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['LCFS','LCFSTime'],index_col='LCFSTime')
        time_trace_data.dropna(inplace=True)

        # calling important shot features from data set
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']
        Pth = transition_data.at[shot,'Pth_LH']

        # initialising subfigure layout
        f = plt.figure(figsize=(5, 9))
        subf = f.subfigures(2,1,height_ratios=[3,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(3,1,sharex='col',sharey='row')
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.2)

        # initialising the pedestal curves and curve fits
        nePed, = axes1[0].plot([],[],'x',lw=1)
        neTanh, = axes1[0].plot([],[],lw=1)
        TePed, = axes1[1].plot([],[],'x',lw=1)
        TeTanh, = axes1[1].plot([],[],lw=1)
        pePed, = axes1[2].plot([],[],'x',lw=1)
        peTanh, = axes1[2].plot([],[],lw=1)

        # initialising the LCFS bar for each subplot
        LCFS1 = axes1[0].axvline(c='k',linestyle='--')
        LCFS2 = axes1[1].axvline(c='k',linestyle='--')
        LCFS3 = axes1[2].axvline(c='k',linestyle='--')

        # setting the aesthetics of subfigure 1
        axes1[0].set(xlim=(1.3,1.5),ylim=(-0.5,5))
        axes1[1].set(ylim=(-0.1,1.1))
        axes1[2].set(ylim=(0,4.4),xlabel='Major Radius')

        # adding a time text to represent count down to transition
        timeText = axes1[0].text(-0.15, 1.3, '', transform=axes1[0].transAxes,fontweight='bold')

        # annotating the subfigures
        axes1[0].set_title(f'{int(shot)}-{set}\n{divertor} configuration',fontweight='bold')
        axes1[0].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=10)
        axes1[0].annotate('$n_{e}$ [$10^{19}$m$^{-3}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[1].annotate('$T_{e}$ [keV]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[2].annotate('$p_{e}$ [$kNm^{-2}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        # adding moving time bar to dalpha trace
        timeBar = axes2.axvline(c='tab:red',linestyle='--')

        # loading the dalpha trace for the desired shot
        dAlpha = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['DalphaSP','DalphaSPTime'],index_col='DalphaSPTime')

        # plotting the second subfigure with dalpha time trace
        axes2.plot(dAlpha)
        axes2.set_xlim(transition_data.at[shot,'start'],
        transition_data.at[shot,'end'])

        # annotating the second subfigure
        axes2.annotate(r'$D_{\alpha} [V]$',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        # setting empty data for all curves
        def init():

            nePed.set_data([],[])
            neTanh.set_data([],[])
            TePed.set_data([],[])
            TeTanh.set_data([],[])
            pePed.set_data([],[])
            peTanh.set_data([],[])
            LCFS1.set_xdata(0)
            LCFS2.set_xdata(0)
            LCFS3.set_xdata(0)
            timeBar.set_xdata(0)

            return nePed,TePed,pePed,neTanh,TeTanh,peTanh,LCFS1,LCFS2,LCFS3,timeBar

        # animating the plot
        def animate(t):

            # loading the time and transition time for animated plot
            LHtime = transition_data.at[shot,'LH']

            # change color of fit based on L mode or H mode
            if LHtime < t:
                neTanh.set(color='red')
                TeTanh.set(color='red')
                peTanh.set(color='red')
            else:
                neTanh.set(color='green')
                TeTanh.set(color='green')
                peTanh.set(color='green')

            # linear interpolating to find LCFS from EFIT
            LCFS = interpolate.interp1d(time_trace_data.index,time_trace_data.LCFS.values)

            # setting the LCFS to the subplots
            LCFS1.set_xdata(LCFS(t))
            LCFS2.set_xdata(LCFS(t))
            LCFS3.set_xdata(LCFS(t))

            # obtaing the corresponding thompson radial data
            data = pd.read_csv(f'../../data/radial_data_LH/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)

            # filtering to outboard region
            data = data.loc[data['R'] > 1.2]

            # loading the results into list formats
            R = data.R.values
            ne = data['ne'].values*1e-19
            neErr = data.neErr.values*1e-19
            Te = data.Te.values*1e-3
            TeErr = data.TeErr.values*1e-3
            pe = data.pe.values*1e-3
            peErr = data.peErr.values*1e-3

            # setting the time text display
            timeText.set_text(f'Transition time - t : {round(t-LHtime,3)*1e+3}ms')

            # setting the raw pedestal data
            nePed.set_data(R,ne)
            TePed.set_data(R,Te)
            pePed.set_data(R,pe)

            # populating major radial co-ordinates with more values
            r = np.linspace(min(R),max(R),1000)
            
            # using self defined optimise function
            y1 = optimize(R,ne,neErr)
            y2 = optimize(R,Te,TeErr)
            y3 = optimize(R,pe,peErr)

            # setting the data to be animated
            neTanh.set_data([r],[y1])
            TeTanh.set_data([r],[y2])
            peTanh.set_data([r],[y3])

            # setting the time bar on the dalpha trace
            timeBar.set_xdata(t)

            return nePed,TePed,pePed,neTanh,TeTanh,peTanh,LCFS1,LCFS2,LCFS3

        # animating the plot
        anim = animation.FuncAnimation(f,animate,init_func=init,frames=times.t.values,interval=150,blit=False)

        # attempt to save
        try:
            anim.save(f'./figures/outboard_{shot}.gif')
        except:
            print(f'Check {shot}')

# utilizing  curve fit module to attempt to fit the pedestal : returns curve fit
def optimize(R,param,error):
    r = np.linspace(min(R),max(R),1000)
    try:
        popt,pcov = curve_fit(mtanh,R,param,sigma=error,absolute_sigma=True)
        y = mtanh(r,*popt)
    except:
        y = np.zeros(len(r))
        y[:] = np.nan
    return y

# using well documented mtanh function to approximate pedestal
# Arends, E. (2003) Density gradients in spherical tokamak plasmas. Technische Universiteit Eindhoven.
def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

if __name__ == '__main__':
    main()