import CoordTrans as ct
import numpy as np

# Columns of the tracker output file
TRACK_ID = 0
TIME = 1
SENSOR = 2
BEACON = 3
POS_LAT = 4
POS_LON = 5
POS_ALT = 6
VEL_E = 7
VEL_N = 8
VEL_U = 9
SYS_X = 10
SYS_Y = 11
SYS_Z = 12
FUSED_TRACK_ID = 21
TRACK_TYPE = 22
BEACON_CODE = 23
ICAO = 24

MEAS_RNG = 31
MEAS_AZI = 32
MEAS_ELE = 33
MEAS_ALT = 34
MEAS_RNG_RATE = 35
EST_RNG = 39
EST_AZI = 40
EST_ELE = 41

MEAS_OWN_FRAME_RNG = 36
MEAS_OWN_FRAME_AZI = 37
MEAS_OWN_FRAME_ALT = 38
EST_OWN_FRAME_RNG = 39
EST_OWN_FRAME_AZI = 40

OWN_LAT = 44
OWN_LON = 45
OWN_ALT = 46
OWN_VEL_E = 47
OWN_VEL_N = 48
OWN_VEL_U = 49

RES_RNG = 52
RES_AZI = 53
RES_ELE = 54
RES_RNG_RATE = 55


SENSOR_TRACK = 1

OWN = 1
RADAR = 2
ADSB = 3
AST = 4

key_column_map = { 'time' : ( TIME, ), 
                   'beacon' : ( BEACON, ),
                   'geodetic position' : ( POS_LAT, POS_LON, POS_ALT ),
                   'enu velocity' : ( VEL_E, VEL_N, VEL_U ),
                   'system position' : ( SYS_X, SYS_Y, SYS_Z ),
                   'ownship position' : ( OWN_LAT, OWN_LON, OWN_ALT ),
                   'ownship velocity' : ( OWN_VEL_E, OWN_VEL_N, OWN_VEL_U ),
                   'radar measurements' : ( MEAS_RNG, MEAS_AZI, MEAS_ELE, MEAS_RNG_RATE ),
                   'ast measurements' : ( MEAS_RNG, MEAS_AZI, MEAS_ALT ),
                   'residuals' : (RES_RNG, RES_AZI, RES_ELE, RES_RNG_RATE) }

sensor_map = { 'radar' : set( [ RADAR, ] ),
               'adsb' : set( [ ADSB, ] ),
               'ast' : set( [ AST, ] ) }

def read( filename ) :
    with open( filename, 'r' ) as file :
        lines = file.readlines()
    file.close()

    if '\n' in lines : 
        lines.remove( '\n' )

    data = [ [ float( x ) for x in line.strip().split( ',' ) ] for line in lines ]
    #return np.array( data[ :-1 ] , dtype = float )
    return [ [ float( x ) for x in line.strip().split( ',' ) ] for line in lines ]


def get( data, **kwargs ) :
    if kwargs is not None :
        for key, value in kwargs.iteritems() :
            if key == 'item' :
                item = value

    if item == 'measurements' :
        item = self.sensor + ' ' + item;

    return data[ :, key_column_map[ item ] ]

class Track( object ) :
    dataIsGood = False

    def __init__( self, data,  **kwargs ) :
        if kwargs is not None :
            for key, value in kwargs.iteritems() :
                if key == 'sensor' :
                    sensor = value
                if key == 'beacon' :
                    beacon = value

        data = [ x for x in data if x[ BEACON ] == beacon and x[ TRACK_TYPE ] == SENSOR_TRACK and x[ SENSOR ] in sensor_map[ sensor ] ]
        #data = data[ ( data[ :, BEACON ] == beacon ) * ( data[ :, TRACK_TYPE ] == SENSOR_TRACK ), : ]
        #f = np.array( [ True if x in sensor_map[ sensor ] else False for x in data[ :, SENSOR ] ] )
        #data = data[ f ]
        if data :
            data = np.array( data )
            self.dataIsGood = True
            self.sensor = sensor
            self.beacon = beacon
            self.time = get( data, item = 'time' )
            self.pos_geod = get( data, item = 'geodetic position' )
            self.vel_enu = get( data, item = 'enu velocity' )
            self.pos_sys = get( data, item = 'system position' )
            self.own_pos_geod = get( data, item = 'ownship position' )
            self.own_vel_enu = get( data, item = 'ownship velocity' )

            #if sensor == 'radar' :
            #    self.residuals = get( data, item = 'residuals' )
            #    self.measurements = get( data, item = 'radar measurements' )
