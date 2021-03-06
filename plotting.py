import matplotlib.pyplot as plt
from matplotlib import dates
import numpy as np

from copy import deepcopy
from collections import Counter


def lts_array_plot(st, stdict, t, mdccm, LTSvel, LTSbaz):
    '''
    Least-trimmed squares array processing plot, including
        flagged element pairs.
    Plots first channel waveform, trace-velocity, back-azimuth,
        and LTS-flagged element pairs.

    Args:
        st: filtered obspy stream. Assumes response has been removed.
        stdict: dictionary of flagged element pairs
        t: array processing time vector
        mdccm: median cross-correlation maxima
        LTSvel: least-trimmed squares trace velocity
        LTSbaz: least-trimmed squares back-azimuth

    Returns:
        fig1: Output figure
        axs1: Output figure axes

    Usage:
        fig1,axs1=lts_array_plot(st,stdict,t,mdccm,LTSvel,LTSbaz)
    '''

    # datenum time vector
    tvec = dates.date2num(st[0].stats.starttime.datetime)+st[0].times()/86400

    cm = 'RdYlBu_r'   # colormap
    cax = 0.2, 1          # colorbar/y-axis for mdccm

    # The waveform subplot
    fig1, axarr1 = plt.subplots(4, 1, sharex='col')
    fig1.set_size_inches(9, 12)
    axs1 = axarr1.ravel()
    axs1[0].plot(tvec, st[0].data, 'k')
    axs1[0].axis('tight')
    axs1[0].set_ylabel('Pressure [Pa]')
    # s = 'f = '+str(np.around(fmin, 4))+' - '+str(np.around(fmax, 4))+' Hz'
    # axs1[0].text(0.90, 0.93, s, horizontalalignment='center',
    #             verticalalignment='center', transform=axs1[0].transAxes)
    axs1[0].text(0.15, 0.93, st[0].stats.station, horizontalalignment='center',
                 verticalalignment='center', transform=axs1[0].transAxes)
    cbaxes = fig1.add_axes(
        [0.9, axs1[2].get_position().y0, 0.02,
         axs1[1].get_position().y1 - axs1[2].get_position().y0])

    # The trace velocity subplot
    sc = axs1[1].scatter(t, LTSvel, c=mdccm,
                         edgecolors='gray', lw=0.1, cmap=cm)
    axs1[1].set_ylim(0.15, 0.60)
    axs1[1].set_xlim(t[0], t[-1])
    axs1[1].plot([t[0], t[-1]], [0.25, 0.25], '-', color='grey')
    axs1[1].plot([t[0], t[-1]], [0.45, 0.45], '-', color='grey')
    sc.set_clim(cax)
    axs1[1].set_ylabel('Trace Velocity\n [km/s]')
    axs1[1].grid(b=1, which='major', color='gray', linestyle=':', alpha=0.5)

    # The back-azimuth subplot
    sc = axs1[2].scatter(t, LTSbaz, c=mdccm,
                         edgecolors='gray', lw=0.1, cmap=cm)
    axs1[2].set_ylim(0, 360)
    axs1[2].set_xlim(t[0], t[-1])
    sc.set_clim(cax)
    axs1[2].set_ylabel('Back-azimuth\n [deg]')
    axs1[2].grid(b=1, which='major', color='gray', linestyle=':', alpha=0.5)
    hc = plt.colorbar(sc, cax=cbaxes, ax=[axs1[1], axs1[2]])
    hc.set_label('MdCCM')

    # The sausage plot of flagged station pairs
    t1 = t[0]
    t2 = t[-1]
    ndict = deepcopy(stdict)
    n = ndict['size']
    ndict.pop('size', None)
    tstamps = list(ndict.keys())
    tstampsfloat = [float(ii) for ii in tstamps]

    # set the second colormap
    cm2 = plt.get_cmap('binary', (n-1))
    initplot = np.empty(len(t))
    initplot.fill(1)

    axs1[3].scatter(np.array([t1, t2]), np.array([0.01, 0.01]), c='w')
    axs1[3].axis('tight')
    axs1[3].set_ylabel('Element [#]')
    axs1[3].set_xlabel('UTC Time')
    axs1[3].set_xlim(t1, t2)
    axs1[3].set_ylim(0.5, n+0.5)
    axs1[3].xaxis_date()
    axs1[3].tick_params(axis='x', labelbottom='on')

    # Loop through the stdict for each flag
    for jj in range(len(tstamps)):
        z = Counter(list(ndict[tstamps[jj]]))
        keys, vals = z.keys(), z.values()
        keys, vals = np.array(list(keys)), np.array(list(vals))
        pts = np.tile(tstampsfloat[jj], len(keys))
        sc = axs1[3].scatter(pts, keys, c=vals, edgecolors='k',
                             lw=0.1, cmap=cm2, vmin=1-0.5, vmax=n-1+0.5)

    p3 = axs1[3].get_position().get_points().flatten()
    cbaxes2 = fig1.add_axes([p3[0], 0.05, p3[2]-p3[0], 0.02])
    hc = plt.colorbar(sc, orientation="horizontal", cax=cbaxes2, ax=axs1[3])
    hc.set_label('Number of Flagged Element Pairs')
    plt.subplots_adjust(right=0.87, hspace=0.12)

    return fig1, axs1
