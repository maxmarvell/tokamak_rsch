import pyuda
import numpy as np
import pandas as pd
import os
from mast.mast_client import ListType
from mastu_exhaust_analysis import *

def main():

    cwd = os.getcwd()

    data_traces = {
        'Ip':'/AMC/PLASMA_CURRENT', # Plasma core
        'TeCore':'/ayc/t_e_core', # Core electron temperature
        'neCore':'/ane/density', # Core electron line density
        'Dalpha_upper_SXD_chamber':'/xim/da/hu10/sxd', # D-alpha upper super-X-divertor chamber
        'DalphaSP':'/xim/da/hu10/osp', # D-alpha strike point
        'Bt':'/epm/output/globalParameters/bphiRmag', #Toroidal field at magnetic axis
        'PSS':'/xnb/ss/beampower', # SS beam injector power
        'PSW':'/xnb/sw/beampower', # SW beam injector power
        'W':'/epm/output/globalParameters/plasmaEnergy', # Stored plasma energy
        'LCFS':'/epm/output/separatrixGeometry/rmidplaneOut', # LCFS from EFIT
    }

    TransitionData = pd.read_excel('./LHdata.ods',engine='odf')
    TransitionData = TransitionData.set_index('ShotNumber')

    for shot in TransitionData.index:
        
        LHdata = LH_data(shot,data_traces)

        dt = 0.015
        psol = pd.DataFrame(calc_psol(shot, smooth_dt=dt))
        ne_bar = pd.DataFrame(calc_ne_bar(shot))

        LHdata.to_csv(cwd+f'/LHdata/traces{shot}.csv',index=False)
        psol.to_csv(cwd+f'/LHdata/psol{shot}.csv',index=False)
        ne_bar.to_csv(cwd+f'/LHdata/ne_bar{shot}.csv',index=False)

def LH_data(shot, data_columns):

    client = pyuda.Client()
    data_store = pd.DataFrame()

    for signal in data_columns.keys():
        try:
            signalName = data_columns[signal]
            tag = signalName[1:4]
            latest_pass = 0
            signal_info = client.list(ListType.SIGNALS, shot=shot, alias=tag)

            for info in signal_info:

                if info.pass_ > latest_pass:

                    latest_pass = info.pass_

                    print("latest pass number is: ", latest_pass)

            data = client.get(signalName, f'{shot}/{latest_pass}')

            data_store = data_store.append(
                pd.Series(
                    data.data, name=signal
                )
            )
        except:
            print(signal + ' is Not available')
        else:
            data_store = data_store.append(
            pd.Series(
                data.time.data, name=signal+'Time'
                )
            )
            
    data_store = data_store.transpose()

    return data_store   

if __name__ == '__main__':
    main()