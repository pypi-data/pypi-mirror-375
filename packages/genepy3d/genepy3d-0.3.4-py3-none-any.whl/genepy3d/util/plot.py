"""Plot objects using matplotlib.

This module contains basic plotting functions using the matplotlib library.

"""

import numpy as np

def plot_line(ax,projection,x,y,z,scales=(1.,1.,1.),line_args={}):
    """Wrapper for plot() in matplotlib. Support 3D, xy, xz and yz projections.
    
    Args:
        ax: axis to be plotted.
        projection (str): support *3d, xy, xz, yz*.
        x (ndarray): x coordinates.
        y (ndarray): y coordinates.
        z (ndarray): z coordinates.
        scales (tuple): axis scales.
        line_args (dic): matplotlib args for plot() func.

    Returns:
        matplotlib plot object.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.util import plot as mypl
            import matplotlib.pyplot as plt

            # coordinates
            x = np.array([1.,2.,3.])
            y = np.array([1.,2.,3.])
            z = np.array([1.,2.,3.])

            # 3D plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            mypl.plot_line(ax,'3d',x,y,z)

            # 2D plot (XY projection)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            mypl.plot_line(ax,'xy',x,y,z)
    
    """
    
    x = x / scales[0]
    y = y / scales[1]
    z = z / scales[2]
    
    if projection=='3d':
        pl = ax.plot(x,y,z,**line_args)
    else:
        if projection=='xy':
            _x, _y = x, y
        elif projection=='xz':
            _x, _y = x, z
        else:
            _x, _y = y, z
            
        pl = ax.plot(_x,_y,**line_args)
        
    return pl
    
def plot_point(ax,projection,x,y,z,scales=(1.,1.,1.),point_args={}):
    """Wrapper for scatter() in matplotlib. Support 3D, xy, xz and yz projections.
    
    Args:
        ax: axis to be plotted.
        projection (str): support *3d, xy, xz, yz*.
        x (ndarray): x coordinates.
        y (ndarray): y coordinates.
        z (ndarray): z coordinates.
        scales (tuple): axis scales.
        point_args (dic): matplotlib args for scatter() func.

    Returns:
        matplotlib scatter object.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.util import plot as mypl
            import matplotlib.pyplot as plt

            # coordinates
            x = np.array([1.,2.,3.])
            y = np.array([1.,2.,3.])
            z = np.array([1.,2.,3.])

            # 3D plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            mypl.plot_point(ax,'3d',x,y,z)

            # 2D plot (XY projection)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            mypl.plot_point(ax,'xy',x,y,z)
    
    """
    
    x = x / scales[0]
    y = y / scales[1]
    z = z / scales[2]
    
    if projection=='3d':
        pl = ax.scatter(x,y,z,**point_args)
    else:
        if projection=='xy':
            _x, _y = x, y
        elif projection=='xz':
            _x, _y = x, z
        else:
            _x, _y = y, z
            
        pl = ax.scatter(_x,_y,**point_args)
        
    return pl


def fix_equal_axis(data):
    """Fix unequal axis bug in matplotlib 3d plot.

    The option ax.axis('equal') doesn't seem to work in 3D. Assuming a plot of 3D point cloud. This function attemps to fix this issue.
    
    Args:
        data (ndarray): 3D points.
        
    Returns:
        min and max values in each axis.  

    Notes:
        The returned values are then used in ax.set_xlim(), ax.set_ylim(), ax.set_zlim() to correct the unequal axis.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.util import plot as mypl
            import matplotlib.pyplot as plt

            # Coordinates
            x = np.array([1.,50.,100.])
            y = np.array([1.,50.,100.])
            z = np.array([1.,50.,100.])

            # 3D plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            mypl.plot_point(ax,'3d',x,y,z)

            # Fix unequal axis
            data = np.array([x,y,z]).T # array of points whose columns are x, y and z positions
            param = mypl.fix_equal_axis(data)
            ax.set_xlim(param['xmin'],param['xmax']);
            ax.set_ylim(param['ymin'],param['ymax']);
            ax.set_zlim(param['zmin'],param['zmax']);
    
    """
    x, y, z = data[:,0], data[:,1], data[:,2]
    scalex = x.max()-x.min()
    scaley = y.max()-y.min()
    scalez = z.max()-z.min()
    maxscale = np.round(np.max(np.array([scalex,scaley,scalez])))/2
    xmed,ymed,zmed = np.median(x),np.median(y),np.median(z)
    scale_params = {}
    scale_params['xmin'] = xmed-maxscale
    scale_params['xmax'] = xmed+maxscale
    scale_params['ymin'] = ymed-maxscale
    scale_params['ymax'] = ymed+maxscale
    scale_params['zmin'] = zmed-maxscale
    scale_params['zmax'] = zmed+maxscale
    
    return scale_params