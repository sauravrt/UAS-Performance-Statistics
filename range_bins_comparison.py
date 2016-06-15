import math
from matplotlib import pyplot as plt
from matplotlib import gridspec
import OutputFile
import TruthFile
import TrkErrors
import glob, os
import numpy as np

#output_folders = ( "C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\RadarMC_4D_NoSkip",
#                   "C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\RadarMC_3D_NoSkip", '' )

output_folders = ( #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\Uncorrelated Hale',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\Radar_4D_1',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\Radar_3D_1',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\Maneuver',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\Straight',
                   'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\3D',
                   'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\4D',
                   '' )

truth_folders = ( #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\Uncorrelated HALE',
                  #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\55',
                  #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\55',
                  #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\Maneuver',
                  #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\Straight',
                  #'C:\\Users\\pkhomchuk\\My Projects\\UAS encounters\\MIT_LL\\55',
                  'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\TruthServer\\scenario_files',
                  'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\TruthServer\\scenario_files',
                  '' )

#titles = ( 'Maneuver', 'Straight', '55', '' )
titles = ( '3D', '4D', '' )
#itles = ( 'Uncorrelated HALE', '' )

NMI2FT = 6076.11548
KNOTS2FT_PER_MIN = NMI2FT / 60


OWN_BEACON = 2331
TGT_BEACON = 2332
N_MONTE_CARLO = 1

def listFilesInDir( dir, ext ) :
    os.chdir( dir )
    return glob.glob( '*.' + ext )

def percentile( x, q ) :
    if x :
        a = np.array( x )
        return np.percentile( a, q )
    else :
        return 0

tgt_true = []
own_true = []

for ind, folder in enumerate( truth_folders ) :
    if folder != '':
        tgt_true.append( [] )
        own_true.append( [] )

        truth_file_names = listFilesInDir( folder, 'txt' )
        for filename in truth_file_names :
            truth = TruthFile.read( folder + '\\' + filename )
            tgt_true[ ind ].append( TruthFile.Aircraft( truth, beacon = TGT_BEACON ) )
            own_true[ ind ].append( TruthFile.Aircraft( truth, beacon = OWN_BEACON ) )

errors = []
for ind, folder in enumerate( output_folders ) :
    if folder != '' :
        hist_errors = TrkErrors.HistErrors()

        output_file_names = listFilesInDir( folder, 'txt' )
        truth_ind = 0
        for filename in output_file_names :
            output = OutputFile.read( folder + "\\" + filename )
            trk = OutputFile.Track( output, beacon = TGT_BEACON, sensor = 'radar' );
            if trk.dataIsGood :
                truth_ind = int( math.floor( ( int( filename.split( '.' )[ 0 ][ 3: ] ) - 1 ) / N_MONTE_CARLO ) )
                err = TrkErrors.Errors( own_true[ ind ][ truth_ind ], tgt_true[ ind ][ truth_ind ], trk, True )
                hist_errors = hist_errors + err.hist_errors
            #if ind % N_MONTE_CARLO == 0 and ind > 0 :
            #    truth_ind += 1
        errors.append( hist_errors )

n = len( errors )

# Plot horizontal position error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 1 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    hpos_err = [ [ [ math.sqrt( x ) * NMI2FT ] for x in y ] for y in errors[ i ].hpos_sqrd ]
    plt.boxplot( hpos_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper95 = [ percentile( x, 95 ) for x in hpos_err ]
    plt.plot( errors[ i ].grid, upper95, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Horizontal position error [feet]' )
    plt.title( titles[ i ] )
    plt.ylim( 0, 3000 )
    plt.grid()

# Plot vertical position error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 2 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    vpos_err = [ [ [ x * NMI2FT ] for x in y ] for y in errors[ i ].vpos ]
    plt.boxplot( vpos_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper97_5 = [ percentile( x, 97.5 ) for x in vpos_err ]
    plt.plot( errors[ i ].grid, upper97_5, 'go' )

    lower2_5 = [ percentile( x, 2.5 ) for x in vpos_err ]
    plt.plot( errors[ i ].grid, lower2_5, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Vertical position error [feet]' )
    plt.title( titles[ i ] )
    plt.ylim( -3000, 1000 )
    plt.grid()

# Plot horizontal speed error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 3 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    hspeed_err  =[ [ [ x * KNOTS2FT_PER_MIN ] for x in y ] for y in errors[ i ].hspeed ] 
    plt.boxplot( hspeed_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper97_5 = [ percentile( x, 97.5 ) for x in hspeed_err ]
    plt.plot( errors[ i ].grid, upper97_5, 'go' )

    lower2_5 = [ percentile( x, 2.5 ) for x in hspeed_err ]
    plt.plot( errors[ i ].grid, lower2_5, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Horizontal speed error [feet/min]' )
    plt.title( titles[ i ] )
    plt.ylim( -6000, 6000 )
    plt.grid()

# Plot vertical speed error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 4 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    vspeed_err  =[ [ [ x * KNOTS2FT_PER_MIN ] for x in y ] for y in errors[ i ].vspeed ] 
    plt.boxplot( vspeed_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper97_5 = [ percentile( x, 97.5 ) for x in vspeed_err ]
    plt.plot( errors[ i ].grid, upper97_5, 'go' )

    lower2_5 = [ percentile( x, 2.5 ) for x in vspeed_err ]
    plt.plot( errors[ i ].grid, lower2_5, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Vertical speed error [feet/min]' )
    plt.title( titles[ i ] )
    plt.ylim( -6000, 6000 )
    plt.grid()

# Plot azimuth error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 5 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    azi_err = [ [ [ 180 * x / math.pi ] for x in y ] for y in errors[ i ].azi ]
    plt.boxplot( azi_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper97_5 = [ percentile( x, 97.5 ) for x in azi_err ]
    plt.plot( errors[ i ].grid, upper97_5, 'go' )

    lower2_5 = [ percentile( x, 2.5 ) for x in azi_err ]
    plt.plot( errors[ i ].grid, lower2_5, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Azimuth error [deg]' )
    plt.title( titles[ i ] )
    plt.ylim( -4, 4 )
    plt.grid()


# Plot heading error
gs = gridspec.GridSpec( 1, n ) 
plt.figure( 6 )
for i in range( n ) :
    plt.subplot( gs[ i ] )
    heading_err = [ [ [ 180 * x / math.pi ] for x in y ] for y in errors[ i ].heading ]
    plt.boxplot( heading_err, labels = errors[ i ].grid, positions = errors[ i ].grid )

    upper97_5 = [ percentile( x, 97.5 ) for x in heading_err ]
    plt.plot( errors[ i ].grid, upper97_5, 'go' )

    lower2_5 = [ percentile( x, 2.5 ) for x in heading_err ]
    plt.plot( errors[ i ].grid, lower2_5, 'go' )

    plt.xlabel( 'Range [nmi]' )
    plt.ylabel( 'Heading error [deg]' )
    plt.title( titles[ i ] )
    plt.ylim( -50, 50 )
    plt.grid()

plt.show()