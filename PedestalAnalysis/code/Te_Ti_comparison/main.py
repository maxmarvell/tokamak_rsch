import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():

    # obtain the transition data for each shot
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # looping over each shot from the transition data
    for shot in transition_data.index:

        # initialising subfigure layout
        f = plt.figure(figsize=(6, 9))
        subf = f.subfigures(2,1,height_ratios=[4,1])

        # allocating the subfigures
        axes1 = subf[0].subplots(3,1,sharex=True,sharey=True)
        axes2 = subf[1].subplots()
        subf[0].subplots_adjust(hspace=0)
        subf[1].subplots_adjust(top=1.1,bottom=0.3)

        # store all pertinent shot informations
        set = transition_data.at[shot,'SET']
        current = transition_data.at[shot,'Ip']
        Bt = transition_data.at[shot,'BT']
        divertor = transition_data.at[shot,'Divertor']
        LHtime = transition_data.at[shot,'LH']
        Pth = transition_data.at[shot,'Pth_LH']

        # obtain the time trace data for last closed flux surface
        LCFS = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['LCFS','LCFSTime'],index_col='LCFSTime')
        LCFS.dropna(inplace=True)

        # setting the figure aesthetics
        axes1[0].set(xlim=(1.25,1.5),ylim=(-0.1,0.45))
        axes1[0].set_title(f'#{int(shot)}-{set}\n{divertor} configuration',fontweight='bold')
        axes1[0].annotate('$T_{e}$ [keV]', xy=(0.02,1.04),xycoords='axes fraction',fontsize=10,color='tab:red')
        axes1[0].annotate('$T_{i}$ [keV]', xy=(0.02,1.14),xycoords='axes fraction',fontsize=10,color='tab:blue')
        axes1[0].annotate(f'$I_p$={current}kA \n$B_t$={abs(Bt)}T'+'\n$P_{th}$='+f'{round(Pth,3)}MW', xy=(0.86,1.04),xycoords='axes fraction',fontsize=9)
        axes1[2].set_xlabel('Major Radius [m]')
        axes2.annotate(r'$D_{\alpha}[V]$',xy=(0.02,1.04),xycoords='axes fraction',fontsize=10)
        axes2.set_xlabel('Time [s]')

        # loading the time resolution data for thompson scattering and CXRS
        ThomTimes = pd.read_csv(f'../../data/radial_data_LH/{shot}/ThompsonTime.csv')
        CXTimes = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRSTime.csv')

        # selecting the times to plot
        times = ThomTimes.loc[(ThomTimes['t']-(LHtime)).abs().argsort()[0:3]]
        times.sort_index(inplace=True)
        times = times['t'].values

        # looping over times
        for i,t in enumerate(times):

            # obtaining the thompson scattering data
            ThomData = pd.read_csv(f'../../data/radial_data_LH/{shot}/Thompson-{t}s.csv')

            # obtain the radial profile for ion temperature via interpolation
            Ti,R = data_interpolatr(t,ThomTimes,CXTimes,shot,'Ti')
            TiErr,R = data_interpolatr(t,ThomTimes,CXTimes,shot,'TiErr')

            # interpolate for the LCFS
            LCFS.loc[t] = np.nan
            LCFS.sort_index(inplace=True)
            LCFS.interpolate(inplace=True)

            # plot the errorbar comparison
            axes1[i].errorbar(R,Ti,yerr=TiErr,fmt='x',color='tab:blue',ms=4,alpha=0.8)
            axes1[i].errorbar(ThomData['R'],ThomData['Te']*1e-03,yerr=ThomData['TeErr']*1e-03,fmt='x',color='tab:red',ms=4,alpha=0.8)
            axes1[i].axvline(LCFS.at[t,'LCFS'],c='k',linestyle='--')
            axes1[i].annotate(f't = {round(t,3)*1e+3}ms',xy=(0.02,0.92),xycoords='axes fraction',fontsize=9,fontweight='bold')

            # plotting the corresponding time on dalpha trace
            axes2.axvline(t,linestyle='--',color='k')

        # loading the dalpha trace for the desired shot
        dAlpha = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',
        usecols=['DalphaSP','DalphaSPTime'],index_col='DalphaSPTime')

        # plotting the second subfigure with dalpha time trace
        axes2.plot(dAlpha)
        axes2.set_xlim(transition_data.at[shot,'start'],
        transition_data.at[shot,'end'])

        # save the figure in this directory
        f.savefig(f'./figures/Ti_Te_compare-{shot}.png')


# function to interpolate pedestal profile at same temporal location as thompson data
def data_interpolatr(time,ThomTimes,CXTimes,shot,param):

    t = ThomTimes.iloc[(ThomTimes['t']-(time)).abs().argsort()[0]]
    pair = CXTimes.iloc[(CXTimes['t']-t[0]).abs().argsort()[:2]]
    pair.sort_values('t',inplace=True)
    pair = pair['t'].values

    try:
        CXtLow1 = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{pair[0]}s.csv')
        CXtLow2 = pd.read_csv(f'../../data/radial_data_LH/{shot}/CXRS-{pair[1]}s.csv')
        interp = pd.DataFrame(index=[pair[0],pair[1],t[0]],columns=CXtLow1['R'])
        interp.loc[pair[0],:] = CXtLow1[param].values
        interp.loc[pair[1],:] = CXtLow2[param].values
        interp.sort_index(inplace=True)

    except:
        print(f'no data for {shot}') 
        return np.nan,np.nan

    else: 
        for col in interp:
            interp[col] = pd.to_numeric(interp[col],errors='coerce')
        interp.interpolate(inplace=True,axis=0)
        return interp.iloc[1].values*1e-03,CXtLow1['R'].values


if __name__ == '__main__':
    main()   