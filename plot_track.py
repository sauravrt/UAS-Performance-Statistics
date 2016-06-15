import OutputFile
import TruthFile
import TrkErrors
import CoordTrans as ct
from matplotlib import pyplot as plt
from matplotlib import gridspec
import math

truth_file_name = 'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\55\\truth_mit_ll_19235.txt'
output_file_name = 'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\Radar_4D_1\\out4.txt'

NMI2FT = 6076.11548
KNOTS2FT_PER_MIN = NMI2FT / 60

OWN_BEACON = 2331
TGT_BEACON = 2332

truth = TruthFile.read( truth_file_name )
tgt_true = TruthFile.Aircraft( truth, beacon = TGT_BEACON )
own_true = TruthFile.Aircraft( truth, beacon = OWN_BEACON )

output = OutputFile.read( output_file_name )
trk = OutputFile.Track( output, beacon = TGT_BEACON, sensor = 'radar' );

tgt_true_pos_own_enu = ct.geod2enu( own_true.pos_geod, tgt_true.pos_geod )
tgt_true_pos_sph = ct.enu2sph( tgt_true_pos_own_enu )

plt.figure( 1 )
plt.plot( tgt_true_pos_own_enu[ :, ct.EAST ], tgt_true_pos_own_enu[ :, ct.NORTH ], 'g-' )
plt.xlabel( 'East [nmi]' )
plt.ylabel( 'North [nmi]' )
plt.grid()

gs = gridspec.GridSpec( 1, 2 ) 
plt.figure( 2 )
plt.subplot( gs[ 0 ] )
plt.plot( trk.time, 3600 * trk.residuals[ :, 3 ], 'g-' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Range rate residual [nmi/sec]' )

plt.subplot( gs[ 1 ] )
plt.plot( trk.time, trk.measurements[ :, 3 ], 'g-' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Range rate [nmi/sec]' )


gs = gridspec.GridSpec( 1, 2 ) 
plt.figure( 3 )
plt.subplot( gs[ 0 ] )
plt.plot( trk.time, trk.residuals[ :, 0 ], 'g-' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Range residual [nmi]' )

plt.subplot( gs[ 1 ] )
plt.plot( trk.time, trk.measurements[ :, 0 ], 'g-' )
plt.plot( tgt_true.time, tgt_true_pos_sph[ :, 0 ], 'b--' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Range [nmi]' )

gs = gridspec.GridSpec( 1, 2 ) 
plt.figure( 4 )
plt.subplot( gs[ 0 ] )
plt.plot( trk.time, 180 * trk.residuals[ :, 1 ] / math.pi, 'g-' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Azimuth residual [deg]' )

plt.subplot( gs[ 1 ] )
plt.plot( trk.time, trk.measurements[ :, 1 ], 'g-' )
plt.plot( tgt_true.time, tgt_true_pos_sph[ :, 1 ], 'b--' )
plt.xlabel( 'Time [seconds]' )
plt.ylabel( 'Azimuth [rad]' )

plt.show()
