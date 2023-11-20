import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def main():

    # obtaining recorded data of transition times
    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    # loop over forward and backward transitions
    for transition in ['LH','HL']:

        # loop over every shot
        for shot in transition_data.index:

            # try obtain the thompaons radial time
            try:
                times = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/ThompsonTime.csv')
            except:
                print(f'No {transition} for {shot}!')
                continue

            # set the columns of the data frame - corresponds to mtanh
            cols = ['position','width','height','core_slope','offset']

            # initialize the date frames over every loop
            peDf = neDf = TeDf = pd.DataFrame(columns=cols)

            for t in times.t.values:

                # read the corresponding thompson radial data
                data = pd.read_csv('../../data/radial_data_'+transition+f'/{shot}/Thompson-{t}s.csv')              
                data.replace([np.inf, -np.inf], np.nan, inplace=True)
                data.dropna(inplace=True)

                # filtering to only the inboard region
                data = data.loc[data['R'] < 0.4]

                # store the calues from the data frame to be plotted
                R = data.R.values
                ne = data['ne'].values*1e-19
                neErr = data.neErr.values*1e-19
                Te = data.Te.values*1e-3
                TeErr = data.TeErr.values*1e-3
                pe = data.pe.values*1e-3
                peErr = data.peErr.values*1e-3

                # try optimize the parameters
                nePopt = optimize(R,ne,neErr)
                TePopt = optimize(R,Te,TeErr)
                pePopt = optimize(R,pe,peErr)

                # append ne to dataframe
                neDf = neDf.append(
                    pd.Series(nePopt,index=cols),ignore_index=True
                )

                # append Te to dataframe
                TeDf = TeDf.append(
                    pd.Series(TePopt,index=cols),ignore_index=True
                )

                # append pe to dataframe
                peDf = peDf.append(
                    pd.Series(pePopt,index=cols),ignore_index=True
                )

            # appending the time to each dataframe
            neDf.loc[:,'time'] = times.t.values
            TeDf.loc[:,'time'] = times.t.values
            peDf.loc[:,'time'] = times.t.values

            # initialize the excelwriter
            writer = pd.ExcelWriter('../../data/pedestal_fit/'+transition+f'/inboard_{shot}.xlsx',engine='xlsxwriter')

            # adding each dataframe to a different sheet
            neDf.to_excel(writer,sheet_name='ne',index=False)
            TeDf.to_excel(writer,sheet_name='Te',index=False)
            peDf.to_excel(writer,sheet_name='pe',index=False)

            # saving the excel file
            writer.save()

# utilizing  curve fit module to attempt to fit the pedestal : returns optimal params
def optimize(R,param,error):
    try:
        popt, pcov = curve_fit(mtanh,R,param,sigma=error,absolute_sigma=True)
    except:
        popt = np.empty(5)
        popt = popt.fill(np.nan) 
    return popt

# using well documented mtanh function to approximate pedestal
# Arends, E. (2003) Density gradients in spherical tokamak plasmas. Technische Universiteit Eindhoven.
def mtanh(x, position, width, height, core_slope, offset):
    r = ((position - x)/(2*width))
    A = ((height-offset)/2)
    numerator = (((1 + (core_slope*r))*np.exp(r)) - np.exp(-1*r))
    denominator = (np.exp(r) + np.exp(-1*r))
    mtanh = A*((numerator/denominator) + 1) + offset
    return mtanh

if  __name__ == '__main__':
    main()