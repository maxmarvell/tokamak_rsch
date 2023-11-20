import pandas as pd
from scipy import interpolate

def main():

    # load the transition data
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # loop over every shot and set
    for shot in transition_data.index:

        # obtain corresponding transition times
        LH = transition_data.at[shot,'LH']
        HL = transition_data.at[shot,'HL']

        # obtain the time trace data and ne bar data
        psol = pd.read_csv(f'../../data/time_trace_data/psol{int(shot)}.csv',index_col='t')
        ne_bar = pd.read_csv(f'../../data/time_trace_data/ne_bar{int(shot)}.csv',index_col='t')

        # using a liner interpolation to predict pth at any point
        pth = interpolate.interp1d(psol.index,psol.psol.values)
        pth_rad = interpolate.interp1d(psol.index,psol.prad_core.values)
        ne = interpolate.interp1d(ne_bar.index,ne_bar.data.values)

        # looping over forward and backward transition and find Pth and ne at each time
        for t,mode in zip([LH,HL],['LH','HL']):
            transition_data.at[shot,'Pth_'+mode] = (pth(t) + pth_rad(t))*1e-6
            transition_data.at[shot,'Pth_'+mode+'_rad'] = (pth(t))*1e-6
            transition_data.at[shot,'ne_'+mode] = ne(t)

    # initializing an excel writer
    writer = pd.ExcelWriter('../../data/transition_data.xlsx',engine='xlsxwriter')
    transition_data.to_excel(writer,sheet_name='MAST-U_transitions',index=True)  

    # saving the excel file
    writer.save()

if __name__ == '__main__':
    main()
