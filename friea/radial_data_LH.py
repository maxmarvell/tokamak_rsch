import pyuda
import pandas as pd
import numpy as np
from equilibrium import *

def main():

    data_traces = {
        '/ayc/t_e':'Te', # Thompson scattering Te
        'ayc/dT_e':'TeErr',
        '/ayc/n_e':'ne', # Thompson scattering ne
        'ayc/dn_e':'neErr',
        '/ayc/p_e':'pe',
        'ayc/dp_e': 'peErr',
        '/ayc/r':'R1', # Thompson radial data
        '/act/ss/act_ss_temperature':'Ti', # CXRS Ti
        '/act/ss/act_ss_temperature_error':'TiErr', # CXRS TiErr
        '/act/ss/act_ss_velocity':'vTorr', # CXRS vTorr
        '/act/ss/act_ss_velocity_error':'vTorrErr', # CXRS vTorrErr
        '/act/ss/major_radius':'R2' # CXRS radial data
        } 

    pedData = pedData = pd.read_excel('./transition_data/forward_transition_data.ods',engine='odf')
    pedData = pedData.set_index('ShotNumber')
    client = pyuda.Client()
    signals = {}

    for shot in pedData.index:

        Thomdf = pd.DataFrame()
        CXdf = pd.DataFrame()
        ThomTime = pd.DataFrame()
        CXTime = pd.DataFrame()

        for signal in data_traces.keys():
            try:
                signals[data_traces[signal]] = client.get(signal,int(shot))
            except:
                print(f'{signal} not available for shot {int(shot)}!')
        
        time = signals['Te'].time.data
        LHtime = pedData.loc[shot]['LH']

        timeIndices = np.where(np.logical_and(
            time >= LHtime-0.1, time <= LHtime+0.1
        ))

        timeIndices = np.ravel(timeIndices)

        ThomTime.loc[:,'t'] = np.around(time[timeIndices],6)
        ThomTime.to_csv(f'./radialData_LH/{shot}/ThompsonTime.csv',index=False)

        R = Te = ne = pe = TeErr = neErr = peErr = []

        for k in timeIndices:

            R = signals['R1'].data[k]
            Te = signals['Te'].data[k]
            TeErr = signals['TeErr'].data[k]
            ne = signals['ne'].data[k]
            neErr = signals['neErr'].data[k]
            pe = signals['pe'].data[k]
            peErr = signals['peErr'].data[k]

            Thomdf.loc[:,'R'] = R
            Thomdf.loc[:,'Te'] = Te
            Thomdf.loc[:,'TeErr'] = TeErr
            Thomdf.loc[:,'ne'] = ne
            Thomdf.loc[:,'neErr'] = neErr
            Thomdf.loc[:,'pe'] = pe
            Thomdf.loc[:,'peErr'] = peErr

            Thomdf.to_csv(f'./radialData_LH/{shot}/Thompson-{round(time[k],6)}s.csv',index=False)
        
        time = signals['Ti'].time.data
        LHtime = pedData.loc[shot]['LH']

        timeIndices = np.where(np.logical_and(
            time >= LHtime-0.1, time <= LHtime+0.1
        ))

        timeIndices = np.ravel(timeIndices)

        CXTime.loc[:,'t'] = np.around(time[timeIndices],6)
        CXTime.to_csv(f'./radialData_LH/{shot}/CXRSTime.csv',index=False)

        for k in timeIndices:

            R = signals['R2'].data
            Ti = signals['Ti'].data[k]
            TiErr = signals['TiErr'].data[k]
            Vtorr = signals['vTorr'].data[k]
            VtorrErr = signals['vTorrErr'].data[k]

            CXdf.loc[:,'R'] = R
            CXdf.loc[:,'Ti'] = Ti
            CXdf.loc[:,'TiErr'] = TiErr
            CXdf.loc[:,'vTorr'] = Vtorr
            CXdf.loc[:,'vTorrErr'] = VtorrErr
            CXdf.to_csv(f'./radialData_LH/{shot}/CXRS-{round(time[k],6)}s.csv',index=False)

if __name__ == "__main__":
    main()