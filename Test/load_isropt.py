from __future__ import division, absolute_import
from glob import glob
from os.path import expanduser
#
from GeoData import GeoData
from GeoData import utilityfuncs

def revpower(x1,x2):
    return x2**x1

def load_risromti(risrName,omtiName=None,isrparams=['nel']):
    #creating GeoData objects of the 2 files, given a specific parameter
    if omtiName:
        omti = GeoData.GeoData(utilityfuncs.readOMTI,(omtiName, ['optical']))
    else:
        omti = None

    risr = GeoData.GeoData(utilityfuncs.readMad_hdf5,(risrName, isrparams))
    #converting logarthmic electron density (nel) array into electron density (ne) array
    risr.changedata('nel','ne',revpower,[10.0])

    return risr,omti

def load_pfisr_hst(isrName,optName=None,azelfn=None,heightkm=None,isrparams=['nel'],treq=None):
    """
    Loads Mishap, DMC and HST data stored in HDF5 format.
    Michael Hirsch
    """
    if optName and azelfn and treq:
        cam = GeoData.GeoData(utilityfuncs.readNeoCMOS,(optName,azelfn,heightkm,treq))
    else:
        cam = None

    pfisr = GeoData.GeoData(utilityfuncs.readMad_hdf5,(isrName,isrparams))

    pfisr.changedata('nel','ne',revpower,[10.])

    return pfisr,cam

def load_pfisr_dasc(isrName,optStem=None,azelfn=None,heightkm=None,isrparams=['nel'],treq=None):
    """
    Loads Mishap, DMC and HST data stored in HDF5 format.
    Michael Hirsch
    """
    if optStem and azelfn and treq:
        flist = glob(expanduser(optStem)+'*.FITS') #FIXME make case insensitive
        cam = GeoData.GeoData(utilityfuncs.readAllskyFITS,(flist,azelfn,heightkm,treq))
    else:
        cam = None

    pfisr = GeoData.GeoData(utilityfuncs.readMad_hdf5,(isrName,isrparams))

    pfisr.changedata('nel','ne',revpower,[10.])

    return pfisr,cam