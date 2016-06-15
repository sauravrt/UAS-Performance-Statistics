import  math
import numpy as np

d2r = math.pi / 180

# parameters of the system plane need to be change to match the scenarios
pot_x = 4105.0
pot_y = 1211.3125
conf_radius = 3438.703125
pot_geod_lat =39.859166666667 * d2r
pot_lon = -75.266666666667 * d2r
ecc = 0.081819190842622;
eq_rad = 6378137.0 / 1852.0; #3444.053988 * nmi2km - Earth's equatorial radius (semi major axis)
second_ecc_sqr = 0.00673949674228

RHO = 0
THETA = 1
H = 2
ELE = 2

EAST = 0
NORTH = 1
UP = 2

LAT = 0
LON = 1
ALT = 2

X = 0
Y = 1
Z = 2


def geod2system( geod ) :
    conf_lat = geod2conf( geod[ LAT ] )
    pot_conf_lat = geod2conf( pot_geod_lat )
    delta_lon = geod[ LON ] - pot_lon
    denom = 1 + math.sin( conf_lat ) * math.sin( pot_conf_lat ) + \
        math.cos( conf_lat ) * math.cos( delta_lon ) * math.cos( pot_conf_lat )

    sys_x = 2 * conf_radius * math.sin( delta_lon ) * math.cos( conf_lat ) / denom

    sys_y = 2 * conf_radius * ( math.sin( conf_lat ) * math.cos( pot_conf_lat ) - \
                      math.cos( conf_lat ) * math.cos( delta_lon ) * math.sin( pot_conf_lat ) ) / denom
    sys_x = sys_x + pot_x
    sys_y = sys_y + pot_y

    return np.array( [ sys_x, sys_y, geod.alt ] )

def geod2conf( geod_lat ) :
    temp1 = math.tan( math.pi / 4 + geod_lat / 2 )
    temp2 = ( 1.0 - ecc * np.sin( geod_lat ) ) / ( 1.0 + ecc * np.sin( geod_lat ) )
    return 2 * math.atan( temp1 * math.pow( temp2, ecc / 2 ) ) - math.pi / 2

def geod2ecef( geod ) :
    ddiv = math.sqrt( 1.0 - ( ecc ** 2 ) * math.sin( geod[ LAT ] ) * math.sin( geod[ LAT ] ) )
    u = eq_rad * math.cos( geod[ LAT ] ) / ddiv + geod[ ALT ] * math.cos( geod[ LAT ] )
    v = eq_rad * ( 1.0 - ecc ** 2 ) * math.sin( geod[ LAT ] ) / ddiv + geod[ ALT ] * math.sin( geod[ LAT ] )
    return np.array( [ u * math.cos( geod[ LON ] ), u * math.sin( geod[ LON ] ), v ] )

def geod2enu( refGeod, tgtGeod ):

    if refGeod.ndim > 1 :
        res = np.zeros( refGeod.shape )
        for i in range( refGeod.shape[ 0 ] ) :
            res[ i, : ] = geod2enu( refGeod[ i, : ], tgtGeod[ i, : ] )
        return res

    refEcef = geod2ecef( refGeod )
    tgtEcef = geod2ecef( tgtGeod )

    T = ecef2enu_rotation( refGeod )
    v = np.dot( T, np.transpose( tgtEcef - refEcef ) )
    return v.transpose()

def ecef2enu_rotation( geod ) :
    return np.array( [ [ -math.sin( geod[ LON ] ), math.cos( geod[ LON ] ), 0 ],
                       [ -math.sin( geod[ LAT ] ) * math.cos( geod[ LON ] ), -math.sin( geod[ LAT ] ) * math.sin( geod[ LON ] ), math.cos( geod[ LAT ] ) ],
                       [ math.cos( geod[ LAT ] ) * math.cos( geod[ LON ] ), math.cos( geod[ LAT ] ) * math.sin( geod[ LON ] ), math.sin( geod[ LAT ] ) ] ] )

def enu2ecef_rotation( geod ) :
    return np.transpose( ecef2enu_rotation( geod ) )

def ecef2geod( ecef ) :

    ecc_sqr = ecc ** 2
    b = eq_rad * math.sqrt( ( 1.0 - ecc_sqr ) )

    Z_sqr = ecef[ Z ] ** 2
    r_sqr = ecef[ X ] ** 2 + ecef[ Y ] ** 2
    r = math.sqrt( r_sqr )
    E_sqr = eq_rad ** 2 - b ** 2
    F = 54 * b * b * Z_sqr
    G = r_sqr + ( 1.0 - ecc_sqr ) * Z_sqr - ecc_sqr * E_sqr
    C = ecc_sqr * ecc_sqr * F *  r_sqr / ( G ** 3 )
    temp = math.sqrt( C ** 2 + 2 * C )
    temp = temp + 1 + C
    S = math.pow( temp, 1.0 / 3.0 )
    temp = S + 1.0 / S + 1.0
    P = F / ( 3 * ( temp ** 2 ) * ( G ** 2 ) )
    temp = 1 + 2 * ( ecc_sqr ** 2 ) * P
    Q = math.sqrt( temp )
    temp = ( eq_rad ** 2 ) * ( 1.0 + 1.0 / Q ) / 2.0 - P * ( 1.0 - ecc_sqr ) * Z_sqr / ( Q * ( 1.0 + Q ) ) - P * r_sqr / 2
    r_0 = math.sqrt( temp ) - P * ecc_sqr * r / ( 1.0 + Q )
    temp = r - ecc_sqr * r_0
    temp = temp ** 2
    U = math.sqrt( ( temp + Z_sqr ) )
    V = math.sqrt( ( temp + ( 1 - ecc_sqr ) * Z_sqr ) )
    Z_0 = ( b ** 2 ) * ecef[ Z ] / ( eq_rad * V )
    temp = ecef[ Z ] + second_ecc_sqr * Z_0
    phi = math.atan2( temp, r )
    l = math.atan2( ecef[ Y ], ecef[ X ] )
    h = U * ( 1.0 - ( b ** 2 ) / ( eq_rad * V ) )
    
    return np.array( [ phi, l, h ] )

def enu2geod( enu_pos, ref_geod ) :
    ref_ecef = geod2ecef( ref_geod )
    rot_matrix = enu2ecef_rotation( ref_geod )
    ecef_pos = np.dot( rot_matrix, enu_pos.v.transpose() )
    ecef_pos = EcefCoords( np.asscalar( ecef_pos[ X ] ) + ref_ecef[ X ], \
                           np.asscalar( ecef_pos[ Y ] ) + ref_ecef[ Y ], \
                           np.asscalar( ecef_pos[ Z ] ) + ref_ecef[ Z ] )

    return ecef2geod( ecef_pos )

# meas in cylindrical, ownship in geodetic
def cyl2enu( meas, own ):
    up = meas[ H ] - own[ ALT ]
    grndrng = math.sqrt( meas[ RHO ] ** 2 - up ** 2 )
    east = math.sin( meas[ THETA ] ) * grndrng
    north = math.cos( meas[ THETA ] ) * grndrng
    return np.array( [ east, north, up ] )

def sph2enu( meas ):
    east = math.sin( meas[ THETA ] ) * math.cos( meas[ ELE ] ) * meas[ RHO ];
    north = math.cos( meas[ THETA ] ) * math.cos( meas[ ELE ] ) * meas[ RHO ];
    up = math.sin( meas[ ELE ] ) * meas[ RHO ];
    return np.array( [ east, north, up ] )

def enu2sph( meas ):
    if meas.ndim > 1 :
        res = np.zeros( meas.shape )
        for i in range( meas.shape[ 0 ] ) :
            res[ i, : ] = enu2sph( meas[ i, : ] )
        return res

    rho = math.sqrt( meas[ EAST ] ** 2 + meas[ NORTH ] ** 2 + meas[ UP ] ** 2 )
    azi = math.atan2( meas[ EAST ], meas[ NORTH ] )
    ele = math.sin( meas[ UP ] / rho )
    return np.array( [ rho, azi, ele ] )


# meas in spherical, ownship in geodetic
# Use this function to convert the radar measurement to the system plane
def sph2sys( meas, own ):
    enu_pos = sph2enu( meas )
    geod_pos = enu2geod( enu_pos, own )
    return geod2system( geod_pos )

def enu2enu_rotation( oldgeod, newgeod, v ) :
    if v.ndim > 1 :
        res = np.zeros( v.shape )
        for i in range( v.shape[ 0 ] ) :
            res[ i, : ] = enu2enu_rotation( oldgeod[ i, : ], newgeod[ i, : ], v[ i, : ] )
        return res

    T1 = enu2ecef_rotation( oldgeod );
    T2 = ecef2enu_rotation( newgeod );
    w = np.dot( T2, np.dot( T1, v.transpose() ) )
    return w.transpose()
