import numpy as np
import pandas as pd
from scipy import interpolate

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # Looping over each type of transition
    for transition in ['LH','HL']:
   
        # looping over every shot in the transition data
        for shot in transition_data.index:

            # load the corresponding time trace data for SW beampower
            PSW_data = pd.read_csv(f'../../data/time_trace_data/traces{int(shot)}.csv',usecols=['PSW','PSWTime'],
            index_col=['PSWTime'])
            
            # Filter to only when the beams are on
            PSW_data = PSW_data.loc[PSW_data['PSW']>0]
            BeamON = min(PSW_data.index)
            BeamOFF = max(PSW_data.index)

            # obtaining the cahrge exchange time resolution data
            try:
                times = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/CXRSTime.csv')
            except:
                print(f'No {transition} for {shot}!')
                continue

            # filter charge exchange diagnostic to only when the beams are onto remove erroneous results
            times = times.loc[(times['t']>BeamON)&(times['t']<BeamOFF)]
            
            # reading the pedestal data of the most relaible fitted signal aka electron density
            ped = pd.read_excel('../../data/pedestal_fit/'+transition+f'/outboard_{shot}.xlsx',index_col='time',sheet_name='ne',
            usecols=['position','width','time'])  
            ped.dropna(inplace=True)
            ped = ped.loc[(ped['position']<1.45) & (ped['position']>1.325)]

            # initialising an output data frame for the pedestal parameters to be sent to
            output = pd.DataFrame()

            # loop over time data
            for t in times['t'].values:

                # check whether pedestal position is already recorded if not interpolate to estimate a value
                try:
                    pos = ped.at[t,'position']-ped.at[t,'width']/2   
                except:
                    ped.loc[t] = [np.nan,np.nan,]
                    ped.sort_index(inplace=True)
                    ped.interpolate(inplace=True)
                    pos = ped.at[t,'position']-ped.at[t,'width']/2   

                try:
                    
                    # load the corresponding time data
                    data = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/CXRS-{t}s.csv',index_col='R',
                    usecols=['Ti','vTorr','R'])

                    # filter infinities and nans
                    data.replace([np.inf, -np.inf], np.nan, inplace=True)
                    data.dropna(inplace=True)

                # report to user that data is missing
                except:
                    print(f'No charge exchange for {int(shot)}!')
                    break

                else:
                    # interpolate to find corresponding value in charge exchange diagnostic
                    vTorr = interpolate.interp1d(data.index,data['vTorr'].values)
                    Ti = interpolate.interp1d(data.index,data['Ti'].values)

                    # add the interpolated values to the output
                    output.at[pos,'vTorr'] = vTorr(pos)
                    output.at[pos,'Ti'] = Ti(pos)
                    output.at[pos,'t'] = t
            
                # save the interpolation for the charge exchange
                writer = pd.ExcelWriter('../../data/interpolations/'+transition+f'/CXRS/outboard_{shot}.xlsx',engine='xlsxwriter')
                output.to_excel(writer,sheet_name='interpolated',index=False)

                # dave the interpolated data
                writer.save()


if __name__ == '__main__':
    main()