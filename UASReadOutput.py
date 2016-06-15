import math
import numpy as np

BEACON_CODE = 1
TIME = 1
FUSED_TRACK_ID = 21
TRACK_TYPE = 22

SYSTEM_TRACK = 2

def UASReadOutput( filename ) :
    file = open( filename, 'r' )
    data = []
    for line in file :
        if len( line ) > 1 :
            line = line.strip()
            columns = line.split( "," )
            columns = [ float( x ) for x in columns ]
            if columns[ TRACK_TYPE ] == SYSTEM_TRACK :
                data.append( columns )
    file.close()
    data = np.array( data )
    tracks = np.unique( data[ :, FUSED_TRACK_ID ] )
    tracks = np.delete( tracks, [ 0 ] )
    return ( data, tracks )