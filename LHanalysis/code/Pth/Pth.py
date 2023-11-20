import matplotlib.pyplot as plt
import pandas as pd

def main():

    transition_data = pd.read_excel('../../data/transition_data.xlsx',index_col='Shot Number')

    f1,axes1 = plt.subplots(2,1,figsize=(9,7),sharex=True)
    f2,axes2 = plt.subplots(2,1,figsize=(9,7),sharex=True)

    f1.subplots_adjust(hspace=0)
    f2.subplots_adjust(hspace=0)

    conventional = transition_data.loc[(transition_data['Divertor'].values=='Conventional')]
    conventional_600 = conventional.loc[(conventional['Ip'].values==600)]
    conventional_750 = conventional.loc[(conventional['Ip'].values==750)]
    superX = transition_data.loc[(transition_data['Divertor'].values=='SUPER-X')]

    for ax in [axes1,axes2]:
        ax[1].set_xlabel('Averaged electron line density $[10^{19}m^{-3}]$',fontsize=12)
        ax[0].annotate('SUPER-X:$I_{p}=600kA$',xy=(0.02,0.04),xycoords='axes fraction',fontsize=9,color='tab:red',fontweight='bold')
        ax[0].annotate('Conventional:$I_{p}=750kA$',xy=(0.02,0.13),xycoords='axes fraction',fontsize=9,color='tab:blue',fontweight='bold')
        ax[0].annotate('Conventional:$I_{p}=600kA$',xy=(0.02,0.22),xycoords='axes fraction',fontsize=9,color='tab:purple',fontweight='bold')
        ax[0].annotate('Forward and backward transitions',xy=(0.02,0.92),xycoords='axes fraction',fontsize=10,fontweight='bold')
        ax[1].annotate('Forward transitions',xy=(0.02,0.92),xycoords='axes fraction',fontsize=10,fontweight='bold')
        ax[0].set_xlim(0,3.75)
        ax[0].set_ylim(0,4.)
        ax[1].set_ylim(0,3.4)

    axes1[1].annotate('$P_{th}[MW]$',xy=(-0.08,1.0),xycoords='axes fraction',fontsize=12,rotation=90)
    axes2[1].annotate('$P_{th-rad}[MW]$',xy=(-0.08,1.0),xycoords='axes fraction',fontsize=12,rotation=90)
    axes2[0].set_title('Accounting for radiative power loss',fontweight='bold')
    colors = ['tab:purple','tab:blue','tab:red']

    for div,col in zip([conventional_600,conventional_750,superX],colors):

        axes1[0].errorbar(div['ne_LH'].dropna().values*1e-19,div['Pth_LH'].dropna().values,yerr=div['Pth_LH_SD'].dropna().values,fmt='^',color=col)
        axes1[0].errorbar(div['ne_HL'].dropna().values*1e-19,div['Pth_HL'].dropna().values,yerr=div['Pth_HL_SD'].dropna().values,fmt='v',color=col,markerfacecolor='none')

        axes2[0].errorbar(div['ne_LH'].dropna().values*1e-19,div['Pth_LH_rad'].dropna().values,yerr=div['Pth_LH_SD_rad'].dropna().values,fmt='^',color=col)
        axes2[0].errorbar(div['ne_HL'].dropna().values*1e-19,div['Pth_HL_rad'].dropna().values,yerr=div['Pth_HL_SD_rad'].dropna().values,fmt='v',color=col,markerfacecolor='none')

        axes1[1].errorbar(div['ne_LH'].dropna().values*1e-19,div['Pth_LH'].dropna().values,yerr=div['Pth_LH_SD'].dropna().values,fmt='^',color=col)

        axes2[1].errorbar(div['ne_LH'].dropna().values*1e-19,div['Pth_LH_rad'].dropna().values,yerr=div['Pth_LH_SD_rad'].dropna().values,fmt='^',color=col)


    f1.savefig('./figures/Pth.png')
    f2.savefig('./figures/Pth_rad.png')


if __name__ == '__main__':
    main()
     