import math
from matplotlib import pyplot as plt
from matplotlib import gridspec
import OutputFile
import TruthFile
import TrkErrors
import glob, os
import numpy as np

output_folders = ( 'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\Radar_3D_1',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Software\\Tracker\\Radar_3D_4'
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\Maneuver',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\\Straight',
                   #'C:\\Users\\pkhomchuk\\My Projects\\UAS - FAA Delivery\\UAS - FAA Software\\Tracker\s\55',
                   '' )

TGT_BEACON = 2332
NMI2FT = 6076.11548

def listFilesInDir( dir, ext ) :
    os.chdir( dir )
    return glob.glob( '*.' + ext )

errors = []
for ind, folder in enumerate( output_folders ) :
    if folder != '' :
        residual_rng_rate = []

        output_file_names = listFilesInDir( folder, 'txt' )
        truth_ind = 0
        for filename in output_file_names :
            output = OutputFile.read( folder + "\\" + filename )
            trk = OutputFile.Track( output, beacon = TGT_BEACON, sensor = 'radar' );
            if trk.dataIsGood :
                residuals = np.ndarray.tolist( NMI2FT * np.transpose( trk.residuals ))
                residual_rng_rate += residuals[ 0 ]

plt.figure( 1 )
plt.boxplot( residual_rng_rate )

plt.show()