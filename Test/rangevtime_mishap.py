#!/usr/bin/env python3
"""
load isr data vs time and altitude
"""
from __future__ import division,absolute_import
import logging
from matplotlib.pyplot import subplots, show,figure,draw,pause
from dateutil.parser import parse
from pytz import UTC
from datetime import datetime
from scipy.spatial import cKDTree
import numpy as np
#
from GeoData.plotting import rangevstime,plotbeamposGD
#
from load_isropt import load_pfisr_neo

epoch = datetime(1970,1,1,tzinfo=UTC)

vbnd = ((0.5e9,5e11),
        (10,2500),(10,2500),(-200,200))
#beamazel = [[-154.3, 77.5],
#            [-149.69,78.56],
#            [-159.5, 78.],
#            [-154.3, 79.5],
#            [-154.3, 78.5]]
beamazel = np.asarray([[-154.3,77.5]])
cmap = (None,None,None,'bwr')
#titles=('$N_e$','$T_i$','$T_e$','$V_i$')
titles=(None,)*4

def makeplot(isrName,optName,azelfn,tbounds,isrparams,showbeam):

    #treq = (datetime(2011,3,2,8,20,20,tzinfo=UTC),
    #          datetime(2011,3,2,8,20,21,tzinfo=UTC))

    #treq = [(t-epoch).total_seconds() for t in treq]
    treq=None

    #load radar data into class
    isr,opt = load_pfisr_neo(isrName,optName,azelfn,isrparams=isrparams,treq=treq)

#%% plot data
    #setup subplot to pass axes handles in to be filled with individual plots
    fg,axs = subplots(beamazel.shape[0],4,sharex=True,sharey=True,figsize=(16,10))
    axs = np.atleast_2d(axs) #needed for proper sharex in one row case

    for j,ae in enumerate(beamazel):
        for i,(b,p,c,tt,ax) in enumerate(zip(vbnd,isrparams,cmap,titles,axs.ravel())):
            rangevstime(isr,ae,b,p[:2],tbounds=tbounds,title=tt,cmap=c,
                        ax=ax,fig=fg,ic=i==0,ir=j==axs.shape[0]-1,it=j==0)
#%% plot beams on their own plot
    plotbeamposGD(isr,minel=75.,elstep=5.)
#%%
    if opt is not None:
        try:
            #setup figure
            fg = figure()
            ax = fg.gca()
            hi=ax.imshow(opt.data['optical'][0,...],vmin=50,vmax=250,
                         interpolation='none',origin='lower')
            fg.colorbar(hi,ax=ax)
            ht = ax.set_title('')
#%% plot beams over top of video
            if showbeam:  # find indices of closest az,el
                print('building K-D tree for beam scatter plot, takes several seconds')
                kdtree = cKDTree(opt.dataloc[:,1:]) #az,el
                for b in beamazel:
                    i = kdtree.query([b[0]%360,b[1]],k=1, distance_upper_bound=0.1)[1]
                    y,x = np.unravel_index(i,opt.data['optical'].shape[1:])
                    ax.scatter(y,x,s=80,facecolor='none',edgecolor='b')
#%% play video
            for t,im in zip(opt.times[:,0],opt.data['optical']):
                hi.set_data(im)
                ht.set_text(datetime.fromtimestamp(t,tz=UTC))
                draw(); pause(0.1)
        except Exception as e:
            logging.error('problem loading images  {}'.format(e))

if __name__ == "__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(description='range vs. time plots of key ISR and optical video during March 2011 events')
    p.add_argument('-b','--showbeams',help='superimpose radar beams on video (takes several seconds)',action='store_true')
    p.add_argument('-d','--date',help='date of study event (to auto load files)',required=True)
    p.add_argument('--isr',help='ISR parameters to select',nargs='+',default=['nel','ti','te','vo'])
    p = p.parse_args()

#%% date / event select
    if p.date == '2011-03-02':
        tbounds=(datetime(2011,3,2,7,30,tzinfo=UTC),
                 datetime(2011,3,2,9,0,tzinfo=UTC))

        flist=('~/data/2011-03-02/ISR/pfa110302.002.hdf5',
               '~/data/2011-03-02/110302_0819.h5',
               '~/data/2011-03/calMishap2011Mar.h5')

    elif p.date == '2013-04-11':
        tbounds=(datetime(2013,4,11,9,tzinfo=UTC),
                 datetime(2013,4,11,12,tzinfo=UTC))

        flist = ('~/data/2013-04-11/ISR/pfa130411.002.hdf5',None,None)

    elif p.date == '2013-04-14':
        tbounds=(datetime(2013,4,14,8,tzinfo=UTC),
                 datetime(2013,4,14,10,tzinfo=UTC))

        flist = ('~/data/2013-04-14/ISR/pfa130413.004.hdf5',None,None)

    elif p.date=='2013-03-01':
        tbounds=(parse('2011-03-01T10:13Z'),
                 parse('2011-03-01T11:13Z'))

        flist = ('~/data/2011-03-01/ISR/pfa110301.003.hdf5',None,None)


    makeplot(flist[0],flist[1],flist[2],tbounds,p.isr,p.showbeams)
#%%
    show()
