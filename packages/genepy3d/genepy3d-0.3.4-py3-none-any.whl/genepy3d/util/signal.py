"""Support functions for 1D signal.
"""

import numpy as np
from scipy.ndimage import label
from skimage.filters import gaussian

def smooth(arr,sigma):
    """Smooth a 1D signal arr by gaussian with given sigma. 
    
    The array is split into subarrays if there are NaN.

    Args:
        arr (array): numpy array.
        sigma: gaussian parameter.

    Returns:
        smoothed array with the same dimension.

    """
    
    non_nan_flag = ~np.isnan(arr)
    # print(non_nan_flag)

    # extract interval which not nan
    lbls, n = label(non_nan_flag)
    # print(lbls)

    new_arr = np.ones(len(arr))*np.nan
    # print(new_arr)

    # only apply gaussian on not nan regions
    for ic in range(1,n+1):
        ids = np.argwhere(lbls==ic).flatten()
        # print(ids)
        tmps = gaussian(arr[ids],sigma=sigma)
        # print(tmps)
        new_arr[ids] = tmps

    # print(new_arr)    
    
    return new_arr