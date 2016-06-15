import math
import CoordTrans as ct
import numpy as np

def normalizeAngle( x ) :
    x += math.pi
    x = ( x - 2 * math.pi * math.floor( x / ( 2 * math.pi ) ) )
    x -= math.pi
    return x

# divides errors into the range bins
class HistErrors( object ):
    N = 15
    hpos_sqrd = []
    vpos = []
    hspeed = []
    vspeed = []
    azi = []
    heading = []

    grid = []
    ind = []

    def __init__( self ) :
        self.grid = np.array( [ i for i in range( self.N ) ] )
        self.hpos_sqrd = [ [] for _ in range( self.N ) ]
        self.vpos = [ [] for _ in range( self.N ) ]
        self.hspeed = [ [] for _ in range( self.N ) ]
        self.vspeed = [ [] for _ in range( self.N ) ]
        self.azi = [ [] for _ in range( self.N ) ]
        self.heading = [ [] for _ in range( self.N ) ]

    def setErrors( self, hp, vp, hs, vs, az, hd, rho ) :
        self.ind = []
        for i in range( rho.shape[ 0 ] ) :
            k = -1
            for j in range( self.N ) :
                if rho[ i ] < self.grid[ j ] :
                    k = j - 1
                    break
            self.ind.append( k )

        self.hpos_sqrd = self.breakErrorsIntoRangeBins( hp )
        self.vpos = self.breakErrorsIntoRangeBins( vp )
        self.hspeed = self.breakErrorsIntoRangeBins( hs )
        self.vspeed = self.breakErrorsIntoRangeBins( vs )
        self.azi = self.breakErrorsIntoRangeBins( az )
        self.heading = self.breakErrorsIntoRangeBins( hd )

    def breakErrorsIntoRangeBins( self, err ) :
        h = [ [] for _ in self.grid ]
        for i in range( err.shape[ 0 ] ) :
            if self.ind[ i ] != - 1 :
                h[ self.ind[ i ] ].append( err[ i ] )

        return h

    def __add__( self, right ) :
        hist_errors = HistErrors()
        for i, val in enumerate( self.grid ):
            hist_errors.hpos_sqrd[ i ] = self.hpos_sqrd[ i ] + right.hpos_sqrd[ i ]
            hist_errors.vpos[ i ] =  self.vpos[ i ] + right.vpos[ i ]
            hist_errors.hspeed[ i ] = self.hspeed[ i ] + right.hspeed[ i ]
            hist_errors.vspeed[ i ] = self.vspeed[ i ] + right.vspeed[ i ]
            hist_errors.azi[ i ] = self.azi[ i ] + right.azi[ i ]
            hist_errors.heading[ i ] = self.heading[ i ] + right.heading[ i ]

        return hist_errors

class Errors( object ) :
    hpos_err_sqrd = []
    vpos_err = []
    hspeed_err = []
    vspeed_err = []
    azi_err = []
    heading_err = []

    range = []

    def __init__( self, own_truth, tgt_truth, track, absolute ) :
        t_ind = self.match_times( track.time, tgt_truth.time )

        # Positions
        own_true_pos_geod = own_truth.pos_geod[ t_ind, : ]
        tgt_true_pos_geod = tgt_truth.pos_geod[ t_ind, : ]
        trk_est_pos_geod = track.pos_geod
        own_est_pos_geod = track.own_pos_geod

        # Velocities
        own_true_vel_enu = own_truth.vel_enu[ t_ind, : ]
        tgt_true_vel_enu = tgt_truth.vel_enu[ t_ind, : ]
        trk_est_vel_enu = 3600 * track.vel_enu
        own_est_vel_enu = 3600 * track.own_vel_enu

        # all ENU positions and velocities are calculated wrt the coordinate system local to the true position of the own ship
        tgt_true_pos_enu = ct.geod2enu( own_true_pos_geod, tgt_true_pos_geod )
        trk_est_pos_enu = ct.geod2enu( own_true_pos_geod, trk_est_pos_geod )
        own_est_pos_enu = ct.geod2enu( own_true_pos_geod, own_est_pos_geod )

        if not absolute :
            tgt_est_relative_pos = trk_est_pos_enu - own_est_pos_enu
        else :
            tgt_est_relative_pos = trk_est_pos_enu

        delta = tgt_true_pos_enu - tgt_est_relative_pos

        # Horizontal position error
        self.hpos_err_sqrd = np.apply_along_axis( lambda x : x[ ct.EAST ] ** 2 + x[ ct.NORTH ] ** 2, axis = 1, arr = delta )

        # Vertical position errors
        self.vpos_err = delta[ :, ct.UP ]
        true_azi = np.apply_along_axis( lambda x : math.atan2( x[ ct.EAST ], x[ ct.NORTH ] ), axis = 1, arr = tgt_true_pos_enu )
        est_azi = np.apply_along_axis( lambda x : math.atan2( x[ ct.EAST ], x[ ct.NORTH ] ), axis = 1, arr = tgt_est_relative_pos )
        vfunc = np.vectorize( normalizeAngle )
        self.azi_err = vfunc( true_azi - est_azi )
        
        trk_est_vel_enu_in_true_own = ct.enu2enu_rotation( trk_est_pos_geod, own_true_pos_geod, trk_est_vel_enu )
        tgt_true_vel_enu_in_true_own = ct.enu2enu_rotation( tgt_true_pos_geod, own_true_pos_geod, tgt_true_vel_enu )
        own_est_vel_enu_in_true_own = ct.enu2enu_rotation( own_est_pos_geod, own_true_pos_geod, own_est_vel_enu )

        if not absolute :
            tgt_est_relative_vel = trk_est_vel_enu_in_true_own - own_est_vel_enu_in_true_own
        else :
            tgt_est_relative_vel = trk_est_vel_enu_in_true_own

        if not absolute :
            tgt_true_relative_vel = tgt_true_vel_enu_in_true_own - own_true_vel_enu
        else :
            tgt_true_relative_vel = tgt_true_vel_enu_in_true_own

        # Estimated horizontal speed
        hspeed_est = np.apply_along_axis( lambda x : math.sqrt( x[ ct.EAST ] ** 2 + x[ ct.NORTH ] ** 2 ), axis = 1, arr = tgt_est_relative_vel )
        # True horizontal speed
        hspeed_true = np.apply_along_axis( lambda x : math.sqrt( x[ ct.EAST ] ** 2 + x[ ct.NORTH ] ** 2 ), axis = 1, arr = tgt_true_relative_vel )
        # Horizontal speed error
        self.hspeed_err = hspeed_true - hspeed_est

        # Vertical speed error
        self.vspeed_err = tgt_true_relative_vel[ :, ct.UP ] - tgt_est_relative_vel[ :, ct.UP ]

        heading_est = np.apply_along_axis( lambda x : math.atan2( x[ ct.EAST ], x[ ct.NORTH ] ), axis = 1, arr = tgt_est_relative_vel )
        heading_true = np.apply_along_axis( lambda x : math.atan2( x[ ct.EAST ], x[ ct.NORTH ] ), axis = 1, arr = tgt_true_relative_vel )
        self.heading_err = vfunc( heading_true - heading_est )

        self.range = np.apply_along_axis( lambda x : math.sqrt( x[ ct.EAST ] ** 2 + x[ ct.NORTH ] ** 2 + x[ ct.UP ] ** 2 ), axis = 1, arr = tgt_true_pos_enu )

        self.hist_errors = HistErrors( )
        self.hist_errors.setErrors( self.hpos_err_sqrd, self.vpos_err, self.hspeed_err,\
                                       self.vspeed_err, self.azi_err, self.heading_err, self.range )

    def match_times( self, t1, t2 ) :
        # t1 is shorter
        ind = []
        for t in t1 :
            ind.append( np.argmin( abs( t2 - t ) ) )

        return ind
