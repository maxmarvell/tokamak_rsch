import pandas as pd
import matplotlib.pyplot as plt

def main():

    # loading the recorded transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # looping over every shot
    for shot in transition_data.index:

        # obtaining key features of the shot
        LH = transition_data.at[shot,'LH']
        HL = transition_data.at[shot,'HL']
        xlim = (transition_data.at[shot,'start'],transition_data.at[shot,'end'])
        set = transition_data.at[shot,'SET']
        divertor = transition_data.at[shot,'Divertor']
        
        # initilizing the figure
        f,axes = plt.subplots(figsize=(9,4))

        # annotation showing forward and backward transition
        axes.annotate('-- transition to H mode',xy=(0.005,1.08),xycoords='axes fraction',fontsize=11,color='tab:green')
        axes.annotate('-- transition to L mode',xy=(0.005,1.02),xycoords='axes fraction',fontsize=11,color='tab:red')

        # loading the corresponding time trace data
        timeTrace = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv')

        # Labelling the plots
        axes.set_title(f'#{int(shot)}-{set}\n{divertor} configuration',fontweight='bold')
        axes.set_xlabel('Time [s]',fontsize=12)
        axes.set_ylabel(r'$D_{\alpha} [V]$',fontsize=12)

        # plotting the Dalpha time trace
        axes.plot(timeTrace['DalphaSPTime'], timeTrace['DalphaSP'])
        axes.set_ylim(0,12)
        axes.set_xlim(xlim)

        # plotting the transition time bar
        axes.axvline(LH, color='tab:green', linestyle='--')
        axes.axvline(HL, color='tab:red', linestyle='--')

        # saving the plot
        f.savefig(f'./figures/timeTrace{int(shot)}_{set}.png')

if __name__ == '__main__':
    main()