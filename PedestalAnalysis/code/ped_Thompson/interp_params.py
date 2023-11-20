import numpy as np
import pandas as pd

def main():

    # obtaining recorded data of transition times
    transitionData = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')
    
    # looping over forward and backward transitions
    for transition in ['LH','HL']:

        # looping over every shot in the transition data
        for shot in transitionData.index:

            # obtaining the thompson time resolution data
            try:
                times = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/ThompsonTime.csv')
            except:
                print(f'No {transition} for {shot}!')
                continue

            # reading the pedestal data of the most relaible fitted signal aka electron density
            ped = pd.read_excel('../../data/pedestal_fit/'+transition+f'/outboard_{shot}.xlsx',index_col='time',sheet_name='ne',
            usecols=['position','width','time'])  
            ped.dropna(inplace=True)
            ped = ped.loc[(ped['position']<1.45) & (ped['position']>1.325)]

            # initialising an output data frame for the pedestal parameters to be sent to
            output = pd.DataFrame()

            # looping over time data to obtain solution at every time
            for t in times['t'].values:

                # check whether pedestal position is already recorded if not interpolate to estimate a value
                try:
                    pos = ped.at[t,'position']-ped.at[t,'width']/2   
                except:
                    ped.loc[t] = [np.nan,np.nan,]
                    ped.sort_index(inplace=True)
                    ped.interpolate(inplace=True)
                    pos = ped.at[t,'position']-ped.at[t,'width']/2  
                
                # load the corresponding radial data
                data = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/Thompson-{t}s.csv',
                usecols=['ne','Te','pe','R'])

                # filter infinities and nans
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # obtain a window for where the pedestal should form
                pedel = data.iloc[(data['R']-(pos)).abs().argsort()[0:5]]

                # select the maximum as an apporoximation for the pedestal height
                output.at[pos,'ne'] = max(pedel['ne'].values)
                output.at[pos,'Te'] = max(pedel.Te.values)
                output.at[pos,'pe'] = max(pedel.pe.values)
                output.at[pos,'t'] = t
            
            # save the interpolation for the Thompson Scattering
            writer = pd.ExcelWriter('../../data/interpolations/'+transition+f'/thompson/outboard_{shot}.xlsx',engine='xlsxwriter')
            output.to_excel(writer,sheet_name='interpolated',index=False)

            # save the excel spreadsheet
            writer.save()

if  __name__ == '__main__':
    main()