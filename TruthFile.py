import CoordTrans as ct
import numpy as np

# Columns of the truth file
TIME = 0
BEACON = 1
ICAO = 2
POS_LAT = 3
POS_LON = 4
POS_ALT = 5
VEL_E = 7
VEL_N = 8
VEL_U = 9
TGT_SYS_X = 14
TGT_SYS_Y = 15
TGT_SYS_Z = 16
TGT_SYS_DOT = 17
TGT_SYS_Y_DOT = 18
TGT_SYS_Z_DOT = 19
ADSB_ON = 20
RADAR_ON = 21
AST_ON = 22

key_column_map = { 'time' : ( TIME, ), 
                   'beacon' : ( BEACON, ),
                   'geodetic position' : ( POS_LAT, POS_LON, POS_ALT ),
                   'enu velocity' : ( VEL_E, VEL_N, VEL_U ),
                   'system position' : ( TGT_SYS_X, TGT_SYS_Y, TGT_SYS_Z ) }

def read( filename ):

    with open( filename, 'r' ) as file :
        lines = file.readlines()
    file.close()

    return np.array( [ [ float( x ) for x in line.strip().split() ] for line in lines ], dtype = float )

def get( data, **kwargs ) :
    if kwargs is not None :
        for key, value in kwargs.iteritems() :
            if key == 'item' :
                item = value

    return data[ :, key_column_map[ item ] ]


class Aircraft( object ) :

    def __init__( self, data, **kwargs ) :
        if kwargs is not None :
            for key, value in kwargs.iteritems() :
                if key == 'beacon' :
                    beacon = value
        data = data[ data[ :, BEACON ] == beacon, : ]

        self.time = get( data, item = 'time' )
        self.pos_geod = get( data, item = 'geodetic position' )
        self.vel_enu = get( data, item = 'enu velocity' )
