import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():

    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    for shot in transition_data.index:

        # initialising subfigure layout
        f = plt.figure(figsize=(7, 9))
        subf = f.subfigures(2,1,height_ratios=[4,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(3,2,sharex='col',sharey='row')
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.2)

        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']
        Pth = transition_data.at[shot,'Pth_LH']

        times = pd.read_csv(f'../../data/radial_data/{shot}/ThompsonTime.csv')
        LHtime = transition_data.at[shot,'LH']

        timePair = times.iloc[(times['t [s]']-LHtime).abs().argsort()[2:4]]
        timePair.sort_values('t [s]',inplace=True)
        timePair = timePair['t [s]'].values

        axes1[0][0].set(xlim=(0.25,0.5),ylim=(-0.5,5))
        axes1[0][1].set(xlim=(1.25,1.5))
        axes1[1][0].set(ylim=(-0.1,0.6))
        axes1[2][0].set(ylim=(0,0.8))

        axes1[0][0].annotate(f'$LH_t$={LHtime}s', xy=(0.02,1.04),xycoords='axes fraction',fontsize=10)
        axes1[0][0].annotate(f'#{int(shot)}-{set}\n{divertor} configuration', xy=(1.12,1.04),xycoords='axes fraction',fontsize=13,fontweight='bold',ha='center')
        axes1[0][1].annotate(f'$t_L$={round(timePair[0],3)}s', xy=(0.67,0.85),xycoords='axes fraction',fontsize=9,color='tab:blue')
        axes1[0][1].annotate(f'$t_H$={round(timePair[1],3)}s', xy=(0.67,0.75),xycoords='axes fraction',fontsize=9,color='tab:red')
        axes1[0][0].annotate('$n_{e}$ [$10^{-19}$m$^{-3}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[0][1].annotate(f'$I_p$={current}kA \n$B_t$= {abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=9)
        axes1[1][0].annotate('$T_{e}$ [keV]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)
        axes1[2][0].annotate('$p_{e}$ [$kNm^{-2}$]', xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        axes2.annotate(r'$D_{\alpha} [V]$',xy=(0.02,0.85),xycoords='axes fraction',fontsize=9)

        spliner(axes1[0])
        spliner(axes1[1])
        spliner(axes1[2])

        for t,c in zip(timePair, ['tab:blue','tab:red']):

            data = pd.read_csv(f'../../data/radial_data/{shot}/Thompson-{t}s.csv')
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.dropna(inplace=True)

            dataOuter = data.loc[data['R'] > 1.3]
            dataInner = data.loc[data['R'] < 0.6]

            axes1[0][0].errorbar(dataInner['R'],dataInner['ne']*1e-19,fmt='x',yerr=dataInner['neErr']*1e-19,color=c)
            axes1[0][1].errorbar(dataOuter['R'],dataOuter['ne']*1e-19,fmt='x',yerr=dataOuter['neErr']*1e-19,color=c)
            axes1[1][0].errorbar(dataInner['R'],dataInner['Te']*1e-3,fmt='x',yerr=dataInner['TeErr']*1e-3,color=c)
            axes1[1][1].errorbar(dataOuter['R'],dataOuter['Te']*1e-3,fmt='x',yerr=dataOuter['TeErr']*1e-3,color=c)
            axes1[2][0].errorbar(dataInner['R'],dataInner['pe']*1e-3,fmt='x',yerr=dataInner['peErr']*1e-3,color=c)
            axes1[2][1].errorbar(dataOuter['R'],dataOuter['pe']*1e-3,fmt='x',yerr=dataOuter['peErr']*1e-3,color=c)

            # plotting the corresponding time on dalpha trace
            axes2.axvline(t,linestyle='--',color=c)

        # loading the dalpha trace for the desired shot
        dAlpha = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['DalphaSP','DalphaSPTime'],index_col='DalphaSPTime')

        # plotting the second subfigure with dalpha time trace
        axes2.plot(dAlpha)
        axes2.set_xlim(transition_data.at[shot,'start'],
        transition_data.at[shot,'end'])

        f.savefig(f'./figures/shot{shot}.png')

def spliner(axes):

    axes[0].spines['right'].set_visible(False)
    axes[1].spines['left'].set_visible(False)
    axes[0].yaxis.tick_left()
    axes[1].yaxis.tick_right()

    d = .025

    kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False)
    axes[0].plot((1-d,1+d), (-d,+d), **kwargs)
    axes[0].plot((1-d,1+d),(1-d,1+d), **kwargs)

    kwargs.update(transform=axes[1].transAxes)
    axes[1].plot((-d,+d), (1-d,1+d), **kwargs)
    axes[1].plot((-d,+d), (-d,+d), **kwargs)

if __name__ == '__main__':
    main()       