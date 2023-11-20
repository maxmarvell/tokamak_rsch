import pandas as pd
import matplotlib.pyplot as plt

def main():

    # loading the recorded transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # getting prop cycle colours to annotate later
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    # looping over every shot
    for shot in transition_data.index:

        # obtaining key features of the shot
        LH = transition_data.at[shot,'LH']
        HL = transition_data.at[shot,'HL']
        xlim = (transition_data.at[shot,'start'],transition_data.at[shot,'end'])
        set = transition_data.at[shot,'SET']
        powlim = (transition_data.at[shot,'powlimStart'],transition_data.at[shot,'powlimEnd'])
        divertor = transition_data.at[shot,'Divertor']
        
        # initilizing the figure
        f,axes = plt.subplots(figsize=(9,4))

        # annotation showing forward and backward transition
        axes.annotate('-- transition to H mode',xy=(0.005,1.08),xycoords='axes fraction',fontsize=11,color='tab:green')
        axes.annotate('-- transition to L mode',xy=(0.005,1.02),xycoords='axes fraction',fontsize=11,color='tab:red')

        # obtain corresponding psol time trace
        psol = pd.read_csv(f'../../data/time_trace_data/psol{int(shot)}.csv')

        # Labelling the plots
        axes.set_title(f'#{int(shot)}-{set}\n{divertor} configuration',fontweight='bold')
        axes.set_xlabel('Time [s]',fontsize=12)

        # annotating a legend using prop cycle colors
        axes.annotate('$P_{loss} [MW]$',xy=(-0.145,0.92),xycoords='axes fraction',fontsize=12,color=colors[0])
        axes.annotate('$P_{OHM} [MW]$',xy=(-0.145,0.82),xycoords='axes fraction',fontsize=12,color=colors[1])
        axes.annotate('$P_{NBI} [MW]$',xy=(-0.145,0.72),xycoords='axes fraction',fontsize=12,color=colors[2])
        axes.annotate('$P_{rad} [MW]$',xy=(-0.145,0.62),xycoords='axes fraction',fontsize=12,color=colors[3])

        # plotting the ploss time traces
        axes.plot(psol['t'],psol['psol']*1e-6)
        axes.plot(psol['t'],psol['pohm']*1e-6)
        axes.plot(psol['t'],(psol['pss']+psol['psw'])*1e-6)
        axes.plot(psol['t'],psol['prad_core']*1e-6)

        # setting the axes limits
        axes.set_ylim(powlim)
        axes.set_xlim(xlim)

        # plotting the transition time bar
        axes.axvline(LH, color='tab:green', linestyle='--')
        axes.axvline(HL, color='tab:red', linestyle='--')

        # saving the plot
        f.savefig(f'./figures/timeTrace{int(shot)}_{set}.png')

if __name__ == '__main__':
    main()