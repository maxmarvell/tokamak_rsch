import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from scipy.optimize import curve_fit

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # looping over every shot in the transition data
    for shot in transition_data.index:

        # initialising subfigure layout
        f = plt.figure(figsize=(7, 9))
        subf = f.subfigures(2,1,height_ratios=[3,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(3,2,sharex='col',sharey='row')
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.2)

        # calling important shot features from data set
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']
        Pth = transition_data.at[shot,'Pth_LH']

        # initialising the ne curves and curve fits
        nePedInner, = axes1[0][0].plot([],[],'x',lw=1)
        neTanhInner, = axes1[0][0].plot([],[],lw=1)
        nePedOuter, = axes1[0][1].plot([],[],'x',lw=1)
        neTanhOuter, = axes1[0][1].plot([],[],lw=1)

        # initialising the Te curves and curve fits
        TePedInner, = axes1[1][0].plot([],[],'x',lw=1)
        TeTanhInner, = axes1[1][0].plot([],[],lw=1)
        TePedOuter, = axes1[1][1].plot([],[],'x',lw=1)
        TeTanhOuter, = axes1[1][1].plot([],[],lw=1)

        # initialising the pe curves and curve fits
        pePedInner, = axes1[2][0].plot([],[],'x',lw=1)
        peTanhInner, = axes1[2][0].plot([],[],lw=1)
        pePedOuter, = axes1[2][1].plot([],[],'x',lw=1)
        peTanhOuter, = axes1[2][1].plot([],[],lw=1)

        # setting the limits of subfigure 1
        axes1[0][0].set(xlim=(0.25,0.5),ylim=(0,5))
        axes1[0][1].set(xlim=(1.25,1.5))
        axes1[1][0].set(ylim=(0,0.75))
        axes1[2][0].set(ylim=(0,1.4))

        # annotating subfigure 1
        axes1[0][0].annotate(f'#{int(shot)}-{set}\n{divertor} configuration', xy=(1.12,1.04),xycoords='axes fraction',fontsize=13,fontweight='bold',ha='center')
        axes1[0][1].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=10)
        axes1[0][0].annotate('$n_{e}$ $[10^{19}m^{-3}]$', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[1][0].annotate('$T_{e}$ $[keV]$', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[2][0].annotate('$p_{e}$ $[kNm^{-3}]$', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        # adding a time text to represent count down to transition
        time_text = axes1[0][0].text(-0.15, 1.2, '', transform=axes1[0][0].transAxes,fontweight='bold')

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

        # splining the plot to show inboard and outboard pedestals
        spliner(axes1[0])
        spliner(axes1[1])
        spliner(axes1[2])

        # initialzing all the animated lines to feed into animate
        def init():
            nePedOuter.set_data([],[])
            neTanhOuter.set_data([],[])
            nePedInner.set_data([],[])
            neTanhInner.set_data([],[])
            TePedOuter.set_data([],[])
            TeTanhOuter.set_data([],[])
            TePedInner.set_data([],[])
            TeTanhInner.set_data([],[])
            pePedOuter.set_data([],[])
            peTanhOuter.set_data([],[])
            pePedInner.set_data([],[])
            peTanhInner.set_data([],[])
            timeBar.set_xdata(0)
            return nePedOuter,nePedInner,TePedOuter,TePedInner,pePedOuter,pePedInner,
        neTanhInner,TeTanhInner,peTanhInner,neTanhOuter,TeTanhOuter,peTanhOuter,timeBar

        # animating the plot
        def animate(t):

            # loading the time and transition time for animated plot
            LHtime = transition_data.at[shot,'LH']

            # change color of fit based on L mode or H mode
            if LHtime < t:
                neTanhOuter.set(color='red')
                TeTanhOuter.set(color='red')
                peTanhOuter.set(color='red')
                neTanhInner.set(color='red')
                TeTanhInner.set(color='red')
                peTanhInner.set(color='red')
            else:
                neTanhOuter.set(color='green')
                TeTanhOuter.set(color='green')
                peTanhOuter.set(color='green')
                neTanhInner.set(color='green')
                TeTanhInner.set(color='green')
                peTanhInner.set(color='green')


            # obtaing the corresponding thompson radial data
            data = pd.read_csv(f'../../data/radial_data_LH/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)

            # setting the time text display
            time_text.set_text(f'Transition time - t : {round(t-LHtime,3)*10**3}ms')

            # filter to outboard region
            dataOuter = data.loc[data['R'] > 1.25]

            # loading the results into list formats
            OuterR = dataOuter['R'].values
            Outerne = dataOuter['ne'].values*1e-19
            OuterneErr = dataOuter['neErr'].values*1e-19
            OuterTe = dataOuter['Te'].values*1e-3
            OuterTeErr = dataOuter['TeErr'].values*1e-3
            Outerpe = dataOuter['pe'].values*1e-3
            OuterpeErr = dataOuter['peErr'].values*1e-3

            # filter to inboard region
            dataInner = data.loc[data['R'] < 0.5]

            # loading the results into list formats
            InnerR = dataInner['R'].values
            Innerne = dataInner['ne'].values*1e-19
            InnerneErr = dataInner['neErr'].values*1e-19
            InnerTe = dataInner['Te'].values*1e-3
            InnerTeErr = dataInner['TeErr'].values*1e-3
            Innerpe = dataInner['pe'].values*1e-3
            InnerpeErr = dataInner['peErr'].values*1e-3

            # setting the raw inner pedestal data
            nePedInner.set_data(InnerR,Innerne)
            TePedInner.set_data(InnerR,InnerTe)
            pePedInner.set_data(InnerR,Innerpe)

            # setting the raw outer data
            nePedOuter.set_data(OuterR,Outerne)
            TePedOuter.set_data(OuterR,OuterTe)
            pePedOuter.set_data(OuterR,Outerpe)
            
            # using self defined optimise function
            y1 = optimize(InnerR,Innerne,InnerneErr)
            y2 = optimize(OuterR,Outerne,OuterneErr)
            y3 = optimize(InnerR,InnerTe,InnerTeErr)
            y4 = optimize(OuterR,OuterTe,OuterTeErr)
            y5 = optimize(InnerR,Innerpe,InnerpeErr)
            y6 = optimize(OuterR,Outerpe,OuterpeErr)

            # populating major radial co-ordinates with more values
            rInner = np.linspace(min(InnerR),max(InnerR),1000)
            rOuter = np.linspace(min(OuterR),max(OuterR),1000)

            # setting the inner fit data to be animated
            neTanhInner.set_data([rInner],[y1])
            TeTanhInner.set_data([rInner],[y3])
            peTanhInner.set_data([rInner],[y5])

            # setting the outer fit data to be animated
            neTanhOuter.set_data([rOuter],[y2])
            TeTanhOuter.set_data([rOuter],[y4])
            peTanhOuter.set_data([rOuter],[y6])

            # setting the time bar on the dalpha trace
            timeBar.set_xdata(t)

            return nePedOuter,TePedInner,pePedInner,neTanhOuter,TeTanhInner,peTanhInner,timeBar

        # obtianing the thompson time resolution data
        times = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')

        # animating the plot
        anim = FuncAnimation(f,animate,init_func=init,frames=times.t.values,interval=150,blit=False)
        
        # attempt to save
        try:
            anim.save(f'./figures/TanhBoth{shot}.gif')
        except:
            print(f'Check {int(shot)}!')


# using well documented mtanh function to approximate pedestal
# Arends, E. (2003) Density gradients in spherical tokamak plasmas. Technische Universiteit Eindhoven.
def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

# utilizing  curve fit module to attempt to fit the pedestal : returns curve fit
def optimize(R,param,error):
    r = np.linspace(min(R),max(R),1000)
    try:
        popt, pcov = curve_fit(mtanh,R,param,sigma=error,absolute_sigma=True)
        y = mtanh(r,*popt)
    except:
        y = np.zeros(len(r))
        y[:] = np.nan
    return y

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