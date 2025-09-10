"""Methods for working with tracks.
"""

import numpy as np
from numbers import Number
from scipy.interpolate import splev, splrep
from genepy3d.obj import curves
from genepy3d.util import geo

def merge(tracklst):
    """Merge tracks. They must be placed in the increasing order of times.

    Args:
        tracklst (array of SimpleTrack): a list of SimpleTrack objects.

    Returns:
        A merged SimpleTrack object.

    """

    if len(tracklst)==1:
        return tracklst[0]
    else:
        coors, t = [], []
        coors.append(tracklst[0].coors) # initialize by the first track
        t.append(tracklst[0].time)
        for ix in range(1,len(tracklst)):
            if (tracklst[ix-1].time[-1] < tracklst[ix].time[0]): # check time order
                coors.append(tracklst[ix].coors)
                t.append(tracklst[ix].time)
            else:
                raise Exception("Time between tracks {} and {} is not in increasing order".format(ix-1,ix))
        
        coors = np.concatenate(coors,axis=0)
        t = np.concatenate(t,axis=0)
        return SimpleTrack(coors,t)

class SimpleTrack(curves.Curve):
    """A simple track object. 
    
    It's simple because it has no division or merge. 
    We can consider it as a Curve object with time attribute.
    
    Work in 3D but also support 2D tracks. Please check the documentation of each function to see if it supports 2D.

    Attributes:
        coors (array | tuple): array of points. See ``Curve`` for more detail.
        time (numeric): array of time.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.objext.simpletracks import SimpleTrack
            
            # Create SimpleTrack from array of points and time
            coors = np.array([[1,2,3],[1,2,3],[1,2,3]])
            t = np.array([1,2,3])
            track = SimpleTrack(coors,t)
    
    """

    def __init__(self, coors, t):
        super().__init__(coors)
        self.time = np.array(t)

    def compute_time_gap(self):
        """Compute the difference between two consecutive times.

        Work in 3D and 2D.

        Returns:
            Array of time gap whose i element is the time gap between (ti, ti-1).

        Notes:
            The first element has no time gap and is set as np.nan.

        """

        time_shift = self.time[1:] - self.time[:-1]
        return np.array([np.nan] + list(time_shift))

    def split(self,max_gap):
        """Split track if the gap between two consecutive times is larger than max_gap.

        Work in 3D and 2D.

        Args:
            max_gap (float): maximual gap allowed between two consecutive times.

        Returns:
            List of subtracks.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.objext.simpletracks import SimpleTrack
                
                # Create SimpleTrack from array of points and time
                coors = np.array([[0,0,0],[1,1,1],[2,2,2],[1,1,1],[0,0,0]])
                t = np.array([0,1,2,10,11])
                track = SimpleTrack(coors,t)
                subtracks = track.split(max_gap=5) # the track is splitted in two tracks.

        """

        frameshift = self.compute_time_gap()
        breakidlst = np.argwhere(frameshift>max_gap).flatten()
        checkidlst = [0] + list(breakidlst) + [self.nb_of_points]
        
        subtracks = []
        for i in range(len(checkidlst)-1):
            sub = SimpleTrack(self.coors[checkidlst[i]:checkidlst[i+1]],self.time[checkidlst[i]:checkidlst[i+1]])
            sub.dim = self.dim # make sure the subtraj has the same dim with the mother traj
            subtracks.append(sub)
        
        return subtracks
    
    def convolve_gaussian(self, sigma, mo="nearest", kerlen=4):
        """Overlay convolve_gaussian() of Curve object. 

        See more details of this function in ``Curve`` class.

        Work in 3D and 2D.

        Returns:
            SimpleTrack object.

        """
        crv_smoothed = super().convolve_gaussian(sigma, mo, kerlen)
        if self.dim == 2:
            return SimpleTrack(crv_smoothed.coors[:,[0,1]],self.time)
        else:
            return SimpleTrack(crv_smoothed.coors,self.time)
        
    def denoise(self,sigma_step=.25,max_iter=None,return_sigma=False):
        """Override the denoise() from Curve.

        Details see ``Curve.denoise()``.

        """
        res = super().denoise(sigma_step,max_iter,return_sigma)
        if res is None:
            raise Exception("Failed to denoise the curve")
        else:
            if return_sigma:
                crv_denoised = res[0]
                sigmalst = res[1]
                trk = SimpleTrack(crv_denoised.coors,self.time)
                trk.dim = self.dim
                return (trk,sigmalst)
            else:
                trk = SimpleTrack(res.coors,self.time)
                trk.dim = self.dim
                return trk
        
    
    def resample(self, dt, spline_order=1, return_old_indices=False, return_interp_param=False):
        """The track is resampled by the new time step.

        Work in 3D and 2D.

        Args:
            dt (float|int): resampled time step.
            spline_order (int): degree of spline interpolation.
            return_old_indices (bool): if True, return the indices of new sampled time array correspond to the old time array.
            return_interp_param (bool): if True, return spline parameters.

        Returns:
            Resampled SimpleTrack object.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.objext.simpletracks import SimpleTrack
                
                # Create SimpleTrack from array of points and time
                coors = np.array([[0,0,0],[1,1,1],[2,2,2],[1,1,1],[0,0,0]])
                t = np.array([0,1,2,10,11])
                track = SimpleTrack(coors,t)
                track_new = track.resample(dt=1) # resample with time step = 1

        """

        # New number of spots
        n = int((self.time[-1]-self.time[0])/dt) + 1

        # New time
        time_new = np.linspace(self.time[0],self.time[-1],n)

        # Find from the new time the indices corresponding to the old time if possible
        if return_old_indices:
            old_ids = np.ones(len(self.time))*np.nan
            for ix in range(len(self.time)):
                ix2 = np.argwhere(self.time[ix]==time_new).flatten()
                if len(ix2)>0:
                    old_ids[ix] = ix2[0]

        # Compute spline parameters
        splx = splrep(self.time,self.coors[:,0],k=spline_order,s=0)
        sply = splrep(self.time,self.coors[:,1],k=spline_order,s=0)
        splz = splrep(self.time,self.coors[:,2],k=spline_order,s=0)

        # Compute new coordinates
        x_new = splev(time_new,splx)
        y_new = splev(time_new,sply)
        z_new = splev(time_new,splz)

        # New SimpleTrack
        track_resampled = SimpleTrack(np.array([x_new,y_new,z_new]).T,time_new)

        track_resampled.dim = self.dim # make sure the resampled one has the same dim property.
        
        # Handle returns
        if (return_old_indices == False) & (return_interp_param == False):
            return track_resampled
        else:
            return_lst = [track_resampled]
            if return_old_indices:
                return_lst.append(old_ids)
            if return_interp_param:
                return_lst.append((splx,sply,splz))
            return return_lst

    
    def is_moving(self,num_neighbor,displ_tol):
        """Check if the object is moving at each point.

        Work in 3D and 2D.

        Args:
            num_neighbor (int): number of neighbor frames. The frames are used to check the movement at a frame n are [n-k,n-k-1,...,n,...,n+k-1,n+k], where k is the number of neighbors frames.
            displ_tol (float): if the displacement between neighbor points is larger than this value, then it's considered as no moving.

        Returns:
            Array of boolean with 0 = no moving, 1 = moving.

        """

        imflag = []
        frame_ids = np.arange(self.nb_of_points)

        for ix in frame_ids:
            
            ids = np.argwhere((frame_ids>=ix-num_neighbor)&(frame_ids<=ix+num_neighbor)).flatten()
            x = self.coors[ids,0]
            y = self.coors[ids,1]
            z = self.coors[ids,2]

            # compare min/max versus mean displacement in x, y and z
            dxmin = np.mean(x) - np.min(x)
            dxmax = np.max(x) - np.mean(x)

            dymin = np.mean(y) - np.min(y)
            dymax = np.max(y) - np.mean(y)

            dzmin = np.mean(z) - np.min(z)
            dzmax = np.max(z) - np.mean(z)

            flag = 0 # is immobile
            if (dxmin>displ_tol) | (dymin>displ_tol) | (dzmin>displ_tol) | (dxmax>displ_tol) | (dymax>displ_tol) | (dzmax>displ_tol):
                flag = 1 # is mobile  
            imflag.append(flag)

        return np.array(imflag)
    
    def compute_velocity(self):
        """Velocity at every point of the track.

        Work in 3D and 2D.

        Returns:
            Array of velocities.

        Notes:
            The first point has no velocity and is set as np.nan

        """

        velolst = [np.nan] # first frame has no velocity
        for ix in np.arange(1,self.nb_of_points):
            delta_t = self.time[ix] - self.time[ix-1]
            displacement = np.sqrt(np.sum((self.coors[ix] - self.coors[ix-1])**2))
            if delta_t == 0:
                velolst.append(np.nan)
            else:
                velolst.append(displacement/delta_t)

        return np.array(velolst)

    def compute_acceleration(self):
        """Acceleration at every point of the track.

        Work in 3D and 2D.

        Returns:
            Array of acceleration.

        Notes:
            The first two points have no acceleration and are set as np.nan
        """

        velocity = self.compute_velocity()
        accelst = [np.nan, np.nan]
        for ix in np.arange(2,self.nb_of_points):
            delta_t = self.time[ix] - self.time[ix-1]
            delta_v = velocity[ix] - velocity[ix-1]
            if delta_t == 0:
                accelst.append(np.nan)
            else:
                accelst.append(delta_v/delta_t)

        return np.array(accelst)

    def compute_msd(self):
        """Mean square displacement.

        Adapt from this post: https://colab.research.google.com/github/kaityo256/zenn-content/blob/main/articles/msd_fft_python/msd_fft_python.ipynb#scrollTo=z7KpcUd8ddZ2
        
        Work in 3D and 2D.
        
        Returns:
            Array of MSD.

        """

        msd = [np.nan] # no msd for the first time
        r = geo.norm(self.coors)
        for s in np.arange(1,self.nb_of_points):
            delta = r[s:] - r[:-s]
            msd.append(np.average(delta**2))
        return np.array(msd)

    def filter_by_time_interval(self,duration,t_begin=None):
        """Filter the track starting from a `t_begin` and with a given `duration`.

        If `t_begin` is None, then the first time point is taken. 
        Otherwise, the time point corresponding to the lower bound of the `t_begin` is chosen.

        When computing the time point corresponding to the duration, it's the time point corresponds to the upper bound of (t_begin + duration).

        Work in 3D and 2D.

        Args:
            duration (numeric, list): duration starting from t_begin.
            t_begin (numeric): time begin, if None, then take the first time point.
        
        Returns:
            A subtrack.

        Notes:
            Duration can be a single value or a list of durations. 
            If the latter one is provided, then return the track with the maximal duration from the list.

        """

        # compute the first time index
        if t_begin is None:
            i0 = 0
        else:
            ids = np.argwhere(self.time <= t_begin).flatten()
            if len(ids) == 0:
                raise Exception("t_begin is not valid.")
            i0 = ids[-1] # the lower bound index

        # check duration input
        if isinstance(duration,Number):
            duration_lst = np.array([duration])
        elif isinstance(duration,(list,np.ndarray)):
            duration_lst = np.array(duration)
        else:
            raise Exception("duration must be a number of a list/array")
        
        # sort duration lst
        duration_lst = np.sort(duration_lst)
        
        # find the last time index
        i1 = None
        for item in duration_lst[-1::-1]: # check the longest duration first
            if t_begin is None:
                t_end = self.time[0]+item
            else:
                t_end = t_begin + item
            
            ids = np.argwhere(self.time >= t_end).flatten()
            if len(ids) == 0:
                continue
            else:
                i1 = ids[0] # the upper bound index
                break

        if i1 is None:
            return None # can not find subtrack satisfying the given duration
        else:
            sub = SimpleTrack(self.coors[i0:i1+1],self.time[i0:i1+1])
            sub.dim = self.dim
            return sub
        
    def filter_by_distance(self,d,t_begin=None):
        """Filter from a time `t_begin`, a subtrack that is inside a distance `d`.

        If `t_begin` is None, then the first time point is taken. 
        Otherwise, the time point corresponding to the lower bound of the `t_begin` is chosen.
        
        Assuming the track intersects the ball `B` with center given by the position `p` at the time `t_begin` and with radius `d`.
        The function returns a subtrack starting from `p` and end at the first position intersecting the ball.

        Work in 3D and 2D.

        Args:
            d (numeric): a distance.
            t_begin (numeric): time begin, if None, then take the first time point.
        
        Returns:
            A subtrack.

        Notes:
            The function only returns the portion starting from the time `t_begin`.
            All the time points within the ball but before `t_begin` are not counted.
            It must have a least 1 position intersecting the ball. Otherwise it returns None.

        """

        # compute the first time index
        if t_begin is None:
            i0 = 0
        else:
            ids = np.argwhere(self.time <= t_begin).flatten()
            if len(ids) == 0:
                raise Exception("t_begin is not valid.")
            i0 = ids[-1] # the lower bound index

        # compute distances
        i_target = np.arange(i0,self.nb_of_points)
        # print(i_target)
        p_target = self.coors[i_target]

        i_src = np.ones(len(i_target),dtype=int) * i0
        p_src = self.coors[i_src]     

        dlst = np.sum((p_target - p_src)**2,axis=1)**0.5

        ilst = np.argwhere(dlst >= d).flatten()
        if len(ilst)==0:
            return None
        else:
            i1 = i_target[ilst[0]] # the upper bound index
            # print(i1)
            sub = SimpleTrack(self.coors[i0:i1+1],self.time[i0:i1+1])
            sub.dim = self.dim
            return sub

    def filter_by_length(self,l,t_begin=None,tolerance=0.5):
        """Filter the track starting from a `t_begin` having a given length `l`.

        If `t_begin` is None, then the first time point is taken. 
        Otherwise, the time point corresponding to the lower bound of the `t_begin` is chosen.

        Work in 3D and 2D.

        Args:
            l (numeric): a length.
            t_begin (numeric): time begin, if None, then take the first time point.
            tolerance (numeric): allow to accept the result if it is within [l-tolerance,l+tolerance]. This make faster search given provided error.
        
        Returns:
            A subtrack.

        """

        # compute the first time index
        if t_begin is None:
            i0 = 0
        else:
            ids = np.argwhere(self.time <= t_begin).flatten()
            if len(ids) == 0:
                raise Exception("t_begin is not valid.")
            i0 = ids[-1] # the lower bound index

        actual_l = curves.Curve(self.coors[i0:]).compute_length() 

        if (actual_l < (l - tolerance)):
            return None # actual length is too small to reach the queried length `l`

        # if (actual_l + tolerance) < l:
        #     return None # queried lenght `l` is greater than actual length
        
        # build distances table
        idlst = np.arange(i0,self.nb_of_points)
        dlst = np.sum((self.coors[idlst[1:]] - self.coors[idlst[:-1]])**2,axis=1)**0.5
        
        # query length by binary search
        stop = False
        i_lb = 0
        i_ub = len(idlst) - 1
        i1 = None

        while(not stop):

            # print(i_lb,i_ub)

            i_query = int((i_lb + i_ub)/2)
            l_query = np.sum(dlst[:i_query])

            if (l_query >= (l - tolerance)) & (l_query <= (l + tolerance)):
                i1 = idlst[i_query]
                stop = True
            elif (l_query > (l + tolerance)):
                i_ub = i_query
            else:
                i_lb = i_query
                
            if (i_lb >= (i_ub-1)):
                i1 = None
                stop = True            

        if i1 is None:
            return None
        else:
            sub = SimpleTrack(self.coors[i0:i1+1],self.time[i0:i1+1])
            sub.dim = self.dim
            return sub




            
        

        

        


        




