import math
import numpy as np

def UASReadInput( filename ) :
    file = open( filename, 'r' )
    data = []
    for line in file :
        line = line.strip()
        columns = line.split()
        columns = [ float( x ) for x in columns ]
        #if columns[ BEACON_CODE ] == beacon :
        data.append( columns )
    file.close()
    data = np.array( data )

    return data