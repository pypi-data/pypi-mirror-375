"""Methods for working with Curve objects.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import re
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.ndimage import gaussian_filter1d
from scipy.ndimage import label
from scipy.signal import argrelextrema

from PyAstronomy import pyasl

from sklearn import metrics

from genepy3d.util.geo import active_brownian_2d, active_brownian_3d, geo_len, norm, angle3points, vector2points, vector_axes_angles, angle2vectors
from genepy3d.util import plot as pl

from matplotlib.colors import ListedColormap

class Curve:
    """Curve in 3D. Also work with 2D curve.
    
    Please check the documentation of each function to see if it supports 2D curve.
    We assumme that curve is a parametric function g(t) = (x(t),y(t),z(t)).
    If 2D points are passed then we consider only X and Y coordinates and set Z = 0.

    The Curve is assumed open and with no duplicated positions.
    
    Attributes:
        coors (array | tuple): list of 3d points.
        
            - if ``array`` is given, then each column is the x, y, z coordinates of a specific point.
            - if ``tuple`` is given, then the items are the three arrays of x, y and z coordinates.
    
    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.obj.curves import Curve
            
            # Curve from array input
            coors = np.array([[1,2,3],[1,2,3],[1,2,3]])
            crv = Curve(coors)

            # Curve from tuple input
            coors = ([1,1,1],[2,2,2],[3,3,3])
            crv = Curve(coors)
            
    """
    def __init__(self, coors):
        
        if isinstance(coors,np.ndarray):
            self.coors = coors
        elif isinstance(coors,(tuple,list)):
            self.coors = np.array(coors).T
            
        self.dim = 3 # default is 3D
        
        # check 2D input
        if self.coors.shape[1]==2:
            z = np.zeros(self.coors.shape[0])
            newcoors = np.array([self.coors[:,0],self.coors[:,1],z]).T
            self.coors = newcoors
            self.dim = 2 # mark this curve is 2D
            
        
        self.nb_of_points = self.coors.shape[0]
        
    
    @property
    def size(self):
        """Number of points on the curve.
        """
        return len(self.coors)
    
    @classmethod
    def from_csv(cls,filepath,column_names=["x","y","z"],scales=(1.,1.,1.),args={}):
        """Constructor from csv file.
        
        Args:
            filepath (str): csv file.
            column_names (list of str): coordinates columns in csv file. 
                Default column names to look for is "x", "y" and "z".
            scales (tuple of float): scales in x, y and z.
            args (dict): overried parameters of pandas.read_csv().
        
        Returns:
            a Curve object.

        Examples:
            ..  code-block:: python
          
                from genepy3d.obj.curves import Curve
                filepath = 'path/to/csv/file'
                crv = Curve.from_csv(filepath)
                
        """
        
        # read file
        df = pd.read_csv(filepath,**args)
        
        # make lower case
        refined_column_names = [name.lower() for name in column_names]
        
        
        # extract all column names, remove irregular characters (e.g. space)
        # treat upper and lower cases as the same
        labels = df.columns.values
        refined_labels = []
        for lbl in labels:
            refined_labels.append(lbl.split()[0].lower())
        
        df.columns = refined_labels
            
        if all(lbl in refined_labels for lbl in refined_column_names):
            coors = df[refined_column_names].values / np.array(scales)
            return cls(coors)
        else:
            raise Exception("can not find column names in file.")
    
    @classmethod
    def from_text(cls,filepath):
        """Read from text-liked file (.txt, .xyz).

        Args:
            filepath (str): text file.

        Returns:
            a Curve object.
        
        Notes:
            Assuming the first three columns correspond to x, y, z coordinates.

        Examples:
            ..  code-block:: python
          
                from genepy3d.obj.curves import Curve
                filepath = 'path/to/text/file'
                crv = Curve.from_text(filepath)
        
        """
        
        try:
            data = []
            f = open(filepath,'r')
            for line in f:
                tmp = []
                elements = re.split(r'\r|\n| |\s', line)
                for ile in elements:
                    if ile!='':
                        tmp.append(float(ile))
                data.append(tmp)
            f.close()
            data = np.array(data)
            return cls(data[:,:3])
        except:
            raise Exception("failed when importing from text file")
    
    def compute_derivative(self,deg,dt=1):
        """Derivative using np.gradient.
        
        Also support 2D. If in 2D, then return 0 for the derivative of Z.
        
        Args:
            deg (int): derivative degree.
            dt (float): delta t.
            
        Returns:
            array of float where each row is the derivative in x, y and z at a specific point.
        
        """
        
        dx, dy, dz = self.coors[:,0].copy(), self.coors[:,1].copy(), self.coors[:,2].copy()
        for i in range(deg):
            dx = np.gradient(dx,dt,edge_order=1)
            dy = np.gradient(dy,dt,edge_order=1)
            dz = np.gradient(dz,dt,edge_order=1)

        return np.array([dx, dy, dz]).T
    
    # def get_norm(self):
    #     """Norms of points on curve.
        
    #     NOTE not useful, will remove.
        
    #     Returns:
    #         array of float.
        
    #     """
        
    #     if self.norm is None:
    #         self.norm = norm(self.coors)

    #     return self.norm

    def compute_length(self):
        """Return the length of curve.

        It is the sum of L2 distances of curve segments.
        
        Also support 2D.
        
        Returns:
            a float.
        
        """
        
        return geo_len(self.coors)
        
    def compute_direction_change(self):
        """Compute the angle (directional change) at a give point and its orientation (CW or CCW).
        
        Assume three points A => B => C. The direction change at B is the angle between two vectors
        (A->B) and (B->C). The sign of angle indicates CW (negative) or CCW (positive) rotation (only work in 2D).

        Support 2D: YES.

        Returns:
            Array of angles.

        Notes:
            - I compute the angle using this suggestion: https://stackoverflow.com/questions/14066933/direct-way-of-computing-the-clockwise-angle-between-two-vectors
            - The CW/CCW is only worked under 2D case.


        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves

                # 3D curve from a helix
                t = np.arange(50)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Angles w.r.t. x-vector
                crv.compute_direction_change()

        """

        if self.nb_of_points == 1:
            return np.array([np.nan])
        elif self.nb_of_points == 2:
            return np.array([np.nan,np.nan])
        else:
            angles_lst = []
            for i in range(1,self.nb_of_points-1):
                vec1 = self.coors[i] - self.coors[i-1]
                vec2 = self.coors[i+1] - self.coors[i]
                if self.dim == 3: # 3D curve
                    if (norm(vec1)==0) | (norm(vec2)==0):
                        angles_lst.append(np.nan)
                    else:
                        costheta = np.sum(vec1 * vec2) / (norm(vec1)*norm(vec2))
                        costheta = np.round(costheta,3) # avoid numerical errors
                        theta = np.arccos(costheta) # in radian                        
                        angles_lst.append(theta)
                else: # 2D curve
                    dot = np.sum(vec1 * vec2) 
                    det = vec1[0] * vec2[1] - vec1[1] * vec2[0]
                    theta = np.arctan2(det,dot) # theta in [-pi, pi]
                    angles_lst.append(theta)

            angles_lst = [np.nan] + angles_lst + [np.nan] # first and last points are not counted => put as nan
            return np.array(angles_lst)
    
    def compute_angles(self):
        """Angle between two vectors from two nearby points of a given point.

        The first and last points are not counted.

        Assumming three consecutive nodes A, B, C, the angle at node B is the angle between two vector (B=>A) and (B=>C).

        Support 2D: YES.

        Returns:
            Array of angles.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves

                # 3D curve from a helix
                t = np.arange(50)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Angles w.r.t. x-vector
                crv.compute_angles()
        
        """

        if self.nb_of_points == 1:
            return np.array([np.nan])
        elif self.nb_of_points == 2:
            return np.array([np.nan,np.nan])
        else:
            angles_lst = []
            for i in range(1,self.nb_of_points-1):
                vec1 = self.coors[i-1] - self.coors[i]
                vec2 = self.coors[i+1] - self.coors[i]
                if (norm(vec1)==0) | (norm(vec2)==0):
                    angles_lst.append(np.nan)
                else:
                    costheta = np.sum(vec1 * vec2) / (norm(vec1)*norm(vec2))
                    costheta = np.round(costheta,3) # avoid numerical errors
                    theta = np.arccos(costheta) # in radian
                    angles_lst.append(theta)

            angles_lst = [np.nan] + angles_lst + [np.nan] # first and last points are not counted => put as nan
            return np.array(angles_lst)

    def compute_angles_vector(self,u=None):
        """Angles between vector at a node on the curve and a vector u.

        Assuming two consecutive nodes A, B, the angle at the node A is the angle between vector (A=>B) and vector u. 

        Args:
            u (array (float)): vector used to compute angles. If None, then return angles with three x, y and z axes.

        Returns:
            Array of angles.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves

                # 3D curve from a helix
                t = np.arange(50)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Angles w.r.t. x-vector
                crv.compute_angles_vector(np.array([1.,0.,0.]))

                # Angles w.r.t. three axes x, y and z
                # Return array with 3 columns for angles in x, y and z respectively
                crv.compute_angles_vector()
        
        """

        angles = []
        
        for i in range(self.coors.shape[0]-1):
            a = self.coors[i]
            b = self.coors[i+1]

            # if i==0:
            #     a = self.coors[i]
            #     b = self.coors[i+1]
            # elif i==(self.coors.shape[0]-1):
            #     a = self.coors[i-1]
            #     b = self.coors[i]
            # else:
            #     a = self.coors[i-1]
            #     b = self.coors[i+1]
            
            vec = vector2points(a, b)
            
            if u is None:
                # angles w.r.t. three axes x, y and z
                angles.append(vector_axes_angles(vec))
            else:
                angles.append(angle2vectors(vec,u))
        
        # no angle for the last point
        if u is None:
            angles.append([np.nan, np.nan, np.nan]) 
        else:
            angles.append(np.nan)
        
        return np.array(angles)
    
    def compute_curvature(self):
        """Curvatures at every point on the curve.
        
        Support 2D: YES.
        
        Returns:
            array of curvatures.

        Notes:
            Due to the side effect when computing the derivative, the curvature can be not very accurate at the extremal points of the curve. 
            The number of points affected at each of the two extremes is 2.
        
        """
        
        d1 = self.compute_derivative(1)
        d2 = self.compute_derivative(2)
        
        d1norm = norm(d1)
        cp = np.cross(d1,d2)
        cpnorm = norm(cp)
        
        res = np.ones(len(d1norm))*np.nan
        idx = np.argwhere(d1norm!=0).flatten()
        if len(idx)!=0:
            res[idx]  = cpnorm[idx]/(d1norm[idx]**3)
        
        return res
    
    def compute_torsion(self):
        """Torsions at every point on the curve.
        
        Returns:
            array of torsions.

        Notes:
            Due to the side effect when computing the derivative, the torsion can be not very accurate at the extremal points of the curve. 
            The number of points affected at each of the two extremes is 3.
        
        """
        
        d1 = self.compute_derivative(1)
        d2 = self.compute_derivative(2)
        d3 = self.compute_derivative(3)
        
        cp = np.cross(d1,d2)
        cpnorm = norm(cp)
        
        res = np.ones(len(cpnorm)) * np.nan
        idx = np.argwhere(cpnorm!=0).flatten()
        if len(idx)!=0:
            res[idx] = np.sum(cp[idx]*d3[idx],axis=1)/(cpnorm[idx]**2)
        
        return res
    
    def compute_wiggliness(self):
        """Wiggliness at every point on the curve.
        
        Also support 2D.
        
        Wiggliness = Length / Distance
        
        Returns:
            array of wiggliness.
        
        """
        
        dist = np.sqrt(np.sum((self.coors[0]-self.coors[-1])**2))
        
        if dist == 0:
            wiggliness = np.nan
        else:
            wiggliness = self.compute_length()*1./dist
                
        return wiggliness
    
    def compute_tortuosity(self):
        """Tortuosity of every point on the curve.
        
        This function is another name of compute_wiggliness().
        
        Returns:
            array of float.
        
        """
        
        return self.compute_wiggliness()
    
    def transform(self,phi=0,theta=0,psi=0,dx=0,dy=0,dz=0,zx=1,zy=1,zz=1):
        """Apply the same rigid transformation to every point on the curve.
        
        Args:
            phi (float): rotation in x in radian.
            theta (float): rotation in y in radian.
            psi (float): rotation in z in radian.
            dx (float): translation in x.
            dy (float): translation in y.
            dz (float): translation in z.
            zx (float): zoom in x.
            zy (float): zoom in y.
            zz (float): zoom in z.
        
        Returns:
            a Curve object.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                t = np.arange(50)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Plot the curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax);

                # Rotate by 90 degree around x
                # Then, shift by 10 in y
                crv_transformed = crv.transform(phi=np.pi/2.,dy=10)

                # Plot the transformed curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv_transformed.plot(ax);
        
        """
        
        return self.to_points().transform(phi,theta,psi,dx,dy,dz,zx,zy,zz).to_curve()
    
    # def compute_curviness(self):
        # """Curviness of curve.
        
        # Curviness is computed from local maxima of curvatures.
        
        # Returns:
            # array of float.
        
        # """
            
        # kappa = self.compute_curvature()
        # extid = argrelextrema(kappa,np.greater)[0] # get indices of local maxima of curvatures
        
        # k = len(extid)
        # if k==0:
            # curviness = 0
        # else:
            # curviness = (1./(1.+abs(k)))*np.sum(kappa[extid])
                
        # return curviness
    
    
    def _extract_plane(self,cur,tor,cur_thr,tor_thr,ext_thr):
        """Compute indices where the curve is locally planar or linear based on torsions and curvatures.
        
        Used in ``scale_space()``.
        
        Args:
            cur (array of float): curvatures.
            tor (array of float): torsions.
            tor_thr (float): torsion threshold.
            cur_thr (float): curvature threshold.
            ext_thr (float): threshold for penalize extreme values of torsions (this is not useful).
            
        Returns:
            array of int where 1 indicate *planar or linear* point, and 0 otherwise.
        
        """
        
        T = np.zeros(len(tor),dtype=np.uint)

        idx0 = np.argwhere(np.isnan(tor)).flatten() # nan value in torsion array, if it's a line.
        
        # torsion condition
        ixvalid = np.setdiff1d(np.arange(len(tor)),idx0)
        idxtmp = np.argwhere((np.abs(tor[ixvalid]) <= tor_thr)|(np.abs(tor[ixvalid]) >= ext_thr)).flatten()
        idx1 = ixvalid[idxtmp]
        
        # curvature condition
        idx2 = np.argwhere(cur <= cur_thr).flatten()
        
        idx = np.union1d(idx0,np.union1d(idx1,idx2))
        
        if len(idx)!=0:
            T[idx] = 1 # plane flag
        
        return T

    def convolve_gaussian(self,sigma,mo="nearest",kerlen=4.0):
        """Get curve at a specific scale *sigma* by Gaussian convolution.
        
        Also support 2D.
        
        Args:
            sigma (float or list of floats): scale.
            mo (str): mode used to treat the border effect (see ``gaussian_filter1d()`` in scipy for detail).
            kerlen (float): specify the length of Gaussian kernel (see ``gaussian_filter1d()`` in scipy for detail).
            
        Returns:
            Curve object.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                t = np.arange(50)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Plot the curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax);

                sigma = 5
                crv_gauss = crv.convolve_gaussian(sigma)

                # Plot the smoothed curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv_gauss.plot(ax);
        
        """

        if np.issubdtype(type(sigma),np.integer) | np.issubdtype(type(sigma),np.floating):
            sigx, sigy, sigz = sigma, sigma, sigma
        else:
            try:
                sigx, sigy, sigz = sigma[0], sigma[1], sigma[2]
            except:
                raise Exception('sigma must be a single number of a list')
        
        # if sigma == 0:
        #     return self
        
        x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
        
        if sigx == 0:
            xs = x
        else:
            xs = gaussian_filter1d(x,sigx,mode=mo,truncate=kerlen)
        
        if sigy == 0:
            ys = y
        else:
            ys = gaussian_filter1d(y,sigy,mode=mo,truncate=kerlen)
        
        if sigz == 0:
            zs = z
        else:
            zs = gaussian_filter1d(z,sigz,mode=mo,truncate=kerlen)
        
        return Curve(np.array([xs,ys,zs]).T)
    
    def resample(self,unit_length=None,npoints=None,spline_order=1,return_interp_param=False):
        """Resample the curve using spline interpolation.
        
        Support 2D: YES.
        
        Args:
            unit_length (float): sampling length. If None, then the curve is resampled from the input ``npoints``.
            npoints (int): number of resampled points. If None, then the number of resampled points is equal to the current number of points on the curve (i.e. before resampling).
            spline_order (uint): if it equal 1, then the linear interpolation is used. Otherwise, spline interpolation is used. Please see ``interpolate.splprep()`` in scipy for more detail.
            return_interp_param (bool): if True then return interpolation parameters.
            
        Returns:
            Curve object.

        Notes:
            - Only choose to resample the curve by either the ``unit_length`` or ``npoints``.
            - The resampling can be failed in some cases due to the spline interpolation constraints. Please see ``interpolate.splprep()`` in scipy for more detail.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                t = np.arange(20)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Plot the curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax,point_args={"c":"r"}); # set point_args to display the points on the curve

                # Resample by 50 points
                crv_resampled = crv.resample(npoints=50)

                # Plot the resampled curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv_resampled.plot(ax,point_args={"c":"r"});

        """
        
        if unit_length is None:
            if npoints is None:
                n = int(self.coors.shape[0]*2)
            else:
                n = npoints
        else:
            n = int(np.round(self.compute_length()/unit_length))
            
        # ignore when the nb. points or resampled one are smaller than spline order
        if ((n <= spline_order) | (self.coors.shape[0] <= spline_order)):
            new_coors = self.coors
        else:
            # try to remove duplicates before interpolation
            _, uix = np.unique(self.coors,axis=0,return_index=True)
            uix = np.sort(uix)
            unique_coors = self.coors[uix]

            # interpolation
            if self.dim == 3:
                try:
                    coef, to = interpolate.splprep([unique_coors[:,0],unique_coors[:,1],unique_coors[:,2]],k=spline_order,s=0)
                except:
                    raise Exception("Given coordinates can not be interpolated by spline.")
                ti = np.linspace(0,1,n)
                xi, yi, zi = interpolate.splev(ti,coef)
                new_coors = np.array([xi,yi,zi]).T
            else: # 2D
                try:
                    coef, to = interpolate.splprep([unique_coors[:,0],unique_coors[:,1]],k=spline_order,s=0)
                except:
                    raise Exception("Given coordinates can not be interpolated by spline.")
                ti = np.linspace(0,1,n)
                xi, yi = interpolate.splev(ti,coef)
                zi = [0. for _ in xi]
                new_coors = np.array([xi,yi,zi]).T
        
        if return_interp_param==False:
            return Curve(new_coors)
        else:
            try:
                return (Curve(new_coors),to,coef,ti,uix)
            except:
                return Curve(new_coors)
    
    # def denoise(self,return_std=False):
    #     """Denoise a curve assuming a Gaussian noise. 
        
    #     Noise variances across x, y and z axes of the curve are estimated using the `beta-sigma` algorithm implemented in ``PyAstronomy`` [1]. 

    #     Args:
    #         return_std (bool): if True, then return the estimated sigma (default: False)

    #     Reurns:
    #         denoised curve (if return_std is False)
    #         (denoised curve, estimated sigma) (if return_std is True)

    #     References:
    #         ..  [1] A posteriori noise estimation in variable data sets - With applications to spectra and light curves. 
    #                 S. Czesla, T. Molle and J. H. M. M. Schmitt. A&A, 609 (2018) A39.
    #                 DOI: 10.1051/0004-6361/201730618.
        
    #     """
        
    #     with warnings.catch_warnings():
    #         warnings.filterwarnings('error')
                
    #         # estimate denoised scale
    #         try: 
    #             x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
                
    #             max_iter = self.coors.shape[0]//2

    #             beq = pyasl.BSEqSamp()
    #             N, j = 1, 1
    #             xsig, _ = beq.betaSigma(x, N, j, returnMAD=True)
    #             ysig, _ = beq.betaSigma(y, N, j, returnMAD=True)
    #             zsig, _ = beq.betaSigma(z, N, j, returnMAD=True)
    #             estsig = np.round(np.max([xsig,ysig,zsig]),2)
    #             # print(estsig)

    #             s = 0.
    #             step = 1.0
    #             ite = 0
    #             xflag, yflag, zflag = True, True, True
    #             while((xflag | yflag | zflag) & (ite < max_iter)):

    #                 crvs = self.convolve_gaussian(s)
    #                 xs, ys, zs = crvs.coors[:,0], crvs.coors[:,1], crvs.coors[:,2]
    #                 xsig = np.std(xs-x)
    #                 ysig = np.std(ys-y)
    #                 zsig = np.std(zs-z)

    #                 if xsig >= estsig:
    #                     xflag = False
    #                 if ysig >= estsig:
    #                     yflag = False
    #                 if zsig >= estsig:
    #                     zflag = False

    #                 ite = ite + 1
    #                 s = s + step

    #             est_noise_scale = s
    #             # print(est_noise_scale)

    #         except:
    #             est_noise_scale = 0
                
    #     # denoise curve
    #     if est_noise_scale != 0:
    #         crvd = self.convolve_gaussian(est_noise_scale) 
    #         # print("ok")
    #     else:
    #         crvd = self
        
    #     if return_std == False:
    #         return crvd
    #     else:
    #         return (crvd,estsig)
    
    def estimate_noise_variance(self):
        """Estimate noise variance across each axis x, y and z of the curve. Assuming noise is normal distribution.

        Returns:
            xsig, ysig and zsig the three estimated sigma for x, y and z.

        References:
            ..  [1] A posteriori noise estimation in variable data sets - With applications to spectra and light curves. 
                    S. Czesla, T. Molle and J. H. M. M. Schmitt. A&A, 609 (2018) A39.
                    DOI: 10.1051/0004-6361/201730618.

        """

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            
            x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
            
            try: # estimate sigma in x, y and z
                beq = pyasl.BSEqSamp()
                N, j = 1, 1
                xsig, _ = beq.betaSigma(x, N, j, returnMAD=True)
                ysig, _ = beq.betaSigma(y, N, j, returnMAD=True)
                zsig, _ = beq.betaSigma(z, N, j, returnMAD=True)
            except:
                return None
            
            return xsig, ysig, zsig

    def _denoise_2d(self,sigma_step=.25,max_iter=None,return_sigma=False):
        """Denoise a curve assuming a Gaussian noise.

        Only take x and y (i.e. 2D case), this is the support function for the denoise().

        Args:
            sigma_step (float): initial sigma of Gaussian used to smooth the curve.
            max_iter (int): maximal number of iteration. If None, then max_iter = number of points on the curve.
            return_sigma (bool): if True, then return the estimated sigmas in x, y and z.

        Returns:
            a denoised Curve object and list of estimated sigmas if ``return_sigma`` is True. If failed, then return None.

        References:
            ..  [1] A posteriori noise estimation in variable data sets - With applications to spectra and light curves. 
                    S. Czesla, T. Molle and J. H. M. M. Schmitt. A&A, 609 (2018) A39.
                    DOI: 10.1051/0004-6361/201730618.

        Notes:
            - We assume noise follows the normal distribution. The denoising can be ineffecient if noise follows another distribution.
            - The denoise() cannot guarantee an optimal noise removal, especially when the noise level is high.
        
        """
        
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            
            x, y = self.coors[:,0], self.coors[:,1]
            
            try: # estimate sigma in x, y
                beq = pyasl.BSEqSamp()
                N, j = 1, 1
                xsig, _ = beq.betaSigma(x, N, j, returnMAD=True)
                ysig, _ = beq.betaSigma(y, N, j, returnMAD=True)
            except:
                return None
            
            # Denoise the curve using the estimated sigma
            # Repeatly convolve the curve with an initial sigma increased over iteration.
            # Estimate the stdev between denoised curve and noisy curve at each iteraction.
            # Stop if the calculated stdev <= estimated sigma. Or the number of iteration > max_iter
            
            try:
                
                xsigs, ysigs = sigma_step, sigma_step # initial sigmas for denoising.
                xflag, yflag = True, True # flag to check when we stop the iteration.
                if max_iter is None:
                    _max_iter = self.coors.shape[0]
                else:
                    _max_iter = max_iter

                ite = 0

                while((xflag | yflag) & (ite < _max_iter)):

                    crvs = self.convolve_gaussian([xsigs,ysigs,0])
                    xs, ys = crvs.coors[:,0], crvs.coors[:,1]
                    xstd = np.std(xs-x)
                    ystd = np.std(ys-y)

                    if xstd >= xsig:
                        xflag = False
                    if ystd >= ysig:
                        yflag = False

                    ite = ite + 1
                    xsigs += sigma_step
                    ysigs += sigma_step
            
            except:
                return None
            
            if return_sigma == True:
                return (crvs,[xsig,ysig,0])
            else:
                return crvs
    
    def denoise(self,sigma_step=.25,max_iter=None,return_sigma=False):
        """Denoise a curve assuming a Gaussian noise. 

        Work for both 2D and 3D.
        
        Noise variances across x, y and z axes of the curve are estimated using the `beta-sigma` algorithm implemented in ``PyAstronomy`` [1]. 
        The curve is then denoised by Gaussian convolution of an initial sigma = ``sigma_step``.
        We repeat the denoising process by increasing ``sigma_step`` until the stdev between the denoised curve and the noisy curve approaches the estimated noise variances.
        The process will be also stopped if the number of iteration >= ``max_iter``.

        Args:
            sigma_step (float): initial sigma of Gaussian used to smooth the curve.
            max_iter (int): maximal number of iteration. If None, then max_iter = number of points on the curve.
            return_sigma (bool): if True, then return the estimated sigmas in x, y and z.

        Returns:
            a denoised Curve object and list of estimated sigmas if ``return_sigma`` is True. If failed, then return None.

        References:
            ..  [1] A posteriori noise estimation in variable data sets - With applications to spectra and light curves. 
                    S. Czesla, T. Molle and J. H. M. M. Schmitt. A&A, 609 (2018) A39.
                    DOI: 10.1051/0004-6361/201730618.

        Notes:
            - We assume noise follows the normal distribution. The denoising can be ineffecient if noise follows another distribution.
            - The denoise() cannot guarantee an optimal noise removal, especially when the noise level is high.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                n = 200 # number of points
                t = np.arange(n)
                a = 1.
                b = 1.
                sigma = 0.2 # sigma of noise to add into the curve
                x = a * np.cos(t/5) + np.random.normal(0,sigma,n)
                y = a * np.sin(t/5) + np.random.normal(0,sigma,n)
                z = b * t + np.random.normal(0,sigma,n)
                crv = curves.Curve((x,y,z))

                # Plot the noisy curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax,point_args={"c":"r"}); # set point_args to display the points on the curve

                # Denoised the curve
                crv_denoised, sigma_est = crv.denoise(return_sigma=True)
                print(sigma_est)

                # Plot the denoised curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv_denoised.plot(ax,point_args={"c":"r"});
        
        """

        if self.dim == 2:
            return self._denoise_2d(sigma_step,max_iter,return_sigma)
        
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            
            x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
            
            try: # estimate sigma in x, y and z
                beq = pyasl.BSEqSamp()
                N, j = 1, 1
                xsig, _ = beq.betaSigma(x, N, j, returnMAD=True)
                ysig, _ = beq.betaSigma(y, N, j, returnMAD=True)
                zsig, _ = beq.betaSigma(z, N, j, returnMAD=True)
            except:
                return None
            
            # Denoise the curve using the estimated sigma
            # Repeatly convolve the curve with an initial sigma increased over iteration.
            # Estimate the stdev between denoised curve and noisy curve at each iteraction.
            # Stop if the calculated stdev <= estimated sigma. Or the number of iteration > max_iter
            
            try:
                
                xsigs, ysigs, zsigs = sigma_step, sigma_step, sigma_step # initial sigmas for denoising.
                xflag, yflag, zflag = True, True, True # flag to check when we stop the iteration.
                if max_iter is None:
                    _max_iter = self.coors.shape[0]
                else:
                    _max_iter = max_iter

                ite = 0

                while((xflag | yflag | zflag) & (ite < _max_iter)):

                    crvs = self.convolve_gaussian([xsigs,ysigs,zsigs])
                    xs, ys, zs = crvs.coors[:,0], crvs.coors[:,1], crvs.coors[:,2]
                    xstd = np.std(xs-x)
                    ystd = np.std(ys-y)
                    zstd = np.std(zs-z)

                    if xstd >= xsig:
                        xflag = False
                    if ystd >= ysig:
                        yflag = False
                    if zstd >= zsig:
                        zflag = False

                    ite = ite + 1
                    xsigs += sigma_step
                    ysigs += sigma_step
                    zsigs += sigma_step
            
            except:
                return None
            
            if return_sigma == True:
                return (crvs,[xsig,ysig,zsig])
            else:
                return crvs
    
    def scale_space(self,scale_range,features={'curvature','torsion','ridge','valley','planeline','line'},eps_kappa=0.01,eps_tau=0.01,eps_seg=10,mo="nearest",kerlen=4.0):
        """Compute features of a curve across scales.

        We compute e.g. the curvatures, torsions, etc of a curve convolved by Gaussian of a given sigma.
        The process repeats over increasing sigma and produce finally a feature-scale space of the curve.
        
        Args:
            scale_range (array of float): range of scales (sigma of Gaussian).
            features (dic): list of features (detail see below).
            eps_kappa (float): curvature threshold. (for planeline feature)
            eps_tau (float): torsion threshold. (for line and planeline features)
            eps_seg (float): segment length threshold (in number of points, for line and planeline features).
            
        Returns:
            dictionary whose each item is a scale space matrix of a specific feature,
            the rows of matrix are the scale range and columns are the curve indices.
        
        Note:
            - We support following features
            
                - curvature: curvature scale space.
                - torsion: torsion scale space.
                - ridge: local maxima of curvature
                - valley: local minima of curvature
                - planeline: plane+line scale space.
                - line: line scale space.

            - The line and planeline scale space were used to compute the local 3d scale of the curve. See ``compute_local_3d_scale_sigma()`` for detail.

            - The curvature scale space was used to compute the main turns of the curve. See ``main_turns()`` for detail. 

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                t = np.arange(100)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Plot the curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax);

                scale_range = np.arange(0,50.,1) # sigma ranges
                features = crv.scale_space(scale_range,features={'curvature'}) # curvature scale space
                kappa_space = features['curvature']

                # Plot the curvature scale space
                fig = plt.figure()
                ax = fig.add_subplot(111)
                pl = ax.imshow(kappa_space)
                ax.invert_yaxis();
                fig.colorbar(pl)
        
        """
        
        x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
        xs, ys, zs = x.copy(), y.copy(), z.copy()
        
        npoints = self.coors.shape[0]
        
        # initialize data
        data = {}
        for f in features:
            data[f] = np.zeros((len(scale_range),npoints),dtype=float)
        
        for i in range(len(scale_range)):
            
            # scaled curve
            if scale_range[i]!=0:
                # smooth curve with gaussian func
                xs = gaussian_filter1d(x,scale_range[i],mode=mo,truncate=kerlen)
                ys = gaussian_filter1d(y,scale_range[i],mode=mo,truncate=kerlen)
                zs = gaussian_filter1d(z,scale_range[i],mode=mo,truncate=kerlen)
            
            scaled_curve = Curve(coors=(xs,ys,zs))
            cur = scaled_curve.compute_curvature()
            tor = scaled_curve.compute_torsion()
            
            # curvature
            if 'curvature' in features:
                data['curvature'][i,:] = cur

            # torsion                
            if 'torsion' in features:
                data['torsion'][i,:] = tor

            # ridge 
            if 'ridge' in features:
                extid = argrelextrema(cur,np.greater)[0] # the func worked with nan values
                if len(extid)>0:
                    data['ridge'][i,extid] = 1
            
            # valley
            if 'valley' in features:
                extid = argrelextrema(cur,np.less)[0] # the func worked with nan values
                if len(extid)>0:
                    data['valley'][i,extid] = 1
            
            # estimate local planes (include also lines)
            if 'planeline' in features:
                ext_thr = 1e6 # peak threshold (not useful, so make very large value) => see extract_plane()
                if((i==0)&(len(np.argwhere(self._extract_plane(cur,tor,eps_kappa,eps_tau,ext_thr)==1).flatten())==npoints)):
                    data['planeline'][i,:] = 1
                elif((i!=0)&(len(np.argwhere(data['planeline'][i-1,:]==1).flatten())==npoints)):
                    data['planeline'][i,:] = 1
                else:
                    data['planeline'][i,:] = scaled_curve._extract_plane(cur,tor,eps_kappa,eps_tau,ext_thr) # REMARK: we do not treat nan values here.
                connected_compo, nb_compo = label(data['planeline'][i,:])
                if nb_compo!=0:
                    for j in range(1,nb_compo+1):
                        connected_idx = np.argwhere(connected_compo==j).flatten()
                        if ((len(connected_idx)<npoints)&(len(connected_idx)<=eps_seg)):
                            data['planeline'][i,connected_idx] = 0  # remove plane artifacts based on segment length threshold
                        
            # estimate local lines
            if 'line' in features:
                idx = np.argwhere(cur <= eps_kappa).flatten() # REMARK: we do not treat nan values here.
                if((i==0)&(len(np.argwhere(cur <= eps_kappa).flatten())==npoints)):
                    data['line'][i,:] = 1
                elif((i!=0)&(len(np.argwhere(data["line"][i-1,:]==1).flatten())==npoints)):
                    data["line"][i,:] = 1                
                elif len(idx)!=0:
                    data['line'][i,idx] = 1
                    
                connected_compo, nb_compo = label(data['line'][i,:])
                if nb_compo!=0:
                    for j in range(1,nb_compo+1):
                        connected_idx = np.argwhere(connected_compo==j).flatten()
                        if ((len(connected_idx)<npoints)&(len(connected_idx)<=eps_seg)):
                            data['line'][i,connected_idx] = 0  # remove plane artifacts

        return data
                
    def _find_best_segments(self,I):
        """Estimate the best combination of planes or lines from indicator I.
        
        This is the support function for ``decompose_intrinsicdim()``.
        
        Args:
            I (array of float): scale space (planeline or line).
            
                This can be obtained from ``scale_space()``.
            
        Returns:
            dictionary containing estimated segments detail.
        
        """
        
        nb_seg = [] # nb of segments at each scale
        seg_info = [] # begin and end indices of each segment at each scale
        seg_len = [] # segment length at each scale
        nb_seg_groups = [] # list of various combinations of segments within the scale range
        duration = [] # number of scale each combination of segment appear within the scale range
        
        nscale, npoint = I.shape
        
        it = 0 # iterator for nb_seg_groups
        
        # check segments duration
        for il in range(nscale):
            
            # get connected components at this scale
            connected_compo, nb_compo = label(I[il])
            nb_seg.append(nb_compo)
            
            # save segment information
            if nb_compo==0:
                seg_info.append([])
                seg_len.append([])
            else:
                tmp, tmp2 = [], []
                for icompo in range(1,nb_compo+1):
                    connected_idx = np.argwhere(connected_compo==icompo).flatten()
                    tmp.append([connected_idx[0],connected_idx[-1]]) # save component indice interval
                    tmp2.append(len(connected_idx)) # save component length
                seg_info.append(tmp)
                seg_len.append(tmp2)
            
            # calculate its duration
            if len(nb_seg_groups)==0: # this first time
                nb_seg_groups.append(nb_compo)
                duration.append(1)
            elif nb_seg_groups[it]==nb_compo: # update step: compare states between the current scale with the previous scale (it)
                duration[it] = duration[it]+1
            else: # if different, reset to new combination
                it = it + 1
                nb_seg_groups.append(nb_compo)
                duration.append(1)
        
        # select the interval that show the longest seg life
        nb_seg, nb_seg_groups, duration = np.array(nb_seg),np.array(nb_seg_groups),np.array(duration)
        tmp_duration = duration.copy()
        idx = np.argwhere(nb_seg_groups==0).flatten() # check seg groups that have nothing
        if len(idx)!=0:
            tmp_duration[idx] = -1 # penalize 0 segments
        best_group = np.argmax(tmp_duration) # the best combination is the longest life
        
        # compute max, min and avg scales within the best combination
        max_level = int(np.sum(duration[:best_group+1]) - 1)
        min_level = int(np.sum(duration[:best_group]))
        avg_level = int((max_level + min_level)/2)
    
        # estimate best configuration of segments from the best combination
        # NOTE: the nb. of segments is similar across scales within the best combination but with various lengths.
        # Thus, select the subinterval of seg_len within the maximal range
        subseg = np.array(seg_len[min_level:max_level+1]) 
        max_seg_ids = np.argmax(subseg,axis=0)+min_level # get the maximal length for each component
    
        # combine all segments indices into one array
        best_seg_ids = np.zeros(npoint,dtype=np.uint)
        for iseg in range(len(max_seg_ids)):
            id1, id2 = seg_info[max_seg_ids[iseg]][iseg][0], seg_info[max_seg_ids[iseg]][iseg][1]
            best_seg_ids[id1:id2+1] = best_seg_ids[id1:id2+1] + 1
        
        # show intersected segments (marked by value > 1)
        conflit_ids = np.zeros(npoint,dtype=np.uint)
        idx = np.argwhere(best_seg_ids>1).flatten() # the intersected zones are marked by value > 1.
        conflit_ids[idx]=1
        if len(idx)!=0:
            connected_compo, nb_compo = label(conflit_ids) # get all intersected zones
            for icompo in range(1,nb_compo+1):
                connected_idx = np.argwhere(connected_compo==icompo).flatten()
                best_seg_ids[connected_idx] = 0 # first assign this zone by 0
                if len(connected_idx)>2: # if the intersected segment has a least 2 points.
                    seg_1 = connected_idx[0:len(connected_idx)//2]
                    seg_2 = connected_idx[(len(connected_idx)//2)+1:]
                    best_seg_ids[seg_1] = 1
                    best_seg_ids[seg_2] = 1
    
        # finally, extract again all segments from best_seg_ids
        pred_segs = []
        connected_compo, nb_compo = label(best_seg_ids)
        if nb_compo!=0:
            for icompo in range(1,nb_compo+1):
                connected_idx = np.argwhere(connected_compo==icompo).flatten()
                pred_segs.append([connected_idx[0],connected_idx[-1]])
        
        dic = {}
        dic['pred_segs'] = pred_segs
        dic['max_level'] = max_level
        dic['min_level'] = min_level
        dic['avg_level'] = avg_level
        dic['nb_seg'] = nb_seg
        dic['seg_info'] = seg_info
        dic['seg_len'] = seg_len
        dic['nb_seg_groups'] = nb_seg_groups
        dic['duration'] = duration
        
        return dic
    
    def decompose_intrinsicdim(self,sig_c,delta_sig=None,eps_seg_len=None,eps_crv_len=None,sig_step=1,eps_kappa=0.01,eps_tau=0.01):
        """Decompose curve into multiscale hierarchichal intrinsic segments at a given sigma ``sig_c``.

        The function decomposes the curve into portions of 1D lines, 2D planes or 3D at a given scale ``sig_c``.
        The decomposition is hierarchichal, i.e. 1D lines can be detected from a 2D plane portion.
        The detail of algorithm can be found [1].
        
        Args:
            sig_c (float): central scale of the searching region.
            delta_sig (float): width of the searching interval.
            sig_step (int): scale step within the searching region.
            eps_kappa (float): curvature threshold.
            eps_tau (float): torsion threshold.
            eps_seg_len (float): segment length threshold.
            eps_crv_len (float): curve length threshold.
            
        Returns:
            list of segment indices specifying line, plane+line.

        References:
            ..  [1] Phan MS, Matho K, Beaurepaire E, Livet J, Chessel A.
                    nAdder: A scale-space approach for the 3D analysis of neuronal traces. 2022.
                    PLOS Computational Biology 18(7): e1010211. DOI: 10.1371/journal.pcbi.1010211

        Notes:
            The decomposition can be visualized using ``plot_decomposed_table()`` and ``plot_intrinsicdim()``.
        
        """
        
        if delta_sig is None:
            search_width = 0.3*sig_c # 30% of sig_c
        else:
            search_width = delta_sig
        
        # setting scale range
        l1 = sig_c - search_width
        if l1 < 0:
            l1 = 0
        l2 = sig_c + search_width
        scale_range = np.arange(l1,l2+sig_step,sig_step)
        
        # setting minimal segment length
        if eps_seg_len is None:
            eps_seg = int(np.round(self.coors.shape[0]*0.05)) # 5% of nb. of points
        else:
            # converting eps_seg_len in nb. of points
            if self.compute_length() <= eps_seg_len:
                eps_seg = self.coors.shape[0] # all points
            else:
                eps_seg = int(np.round(self.coors.shape[0]*eps_seg_len*1./self.compute_length())) # fraction of points
        
        # compute planeline and line indicators
        data = self.scale_space(scale_range,{'planeline','line'},eps_kappa,eps_tau,eps_seg)
        
        planeline_param = self._find_best_segments(data['planeline'])
        min_pl_level = planeline_param['min_level']
        max_pl_level = planeline_param['max_level']
        
        line_param = self._find_best_segments(data['line'][min_pl_level:max_pl_level+1])
        
        # post processing for scaled curve whose length <= given threshold : esp_crv_len
        plids = planeline_param['pred_segs']
        lids = line_param['pred_segs']
        
        # setting minimal curve length
        if eps_crv_len is None:
            if eps_seg_len is not None:
                eps_crv = eps_seg_len
            else:
                eps_crv = self.compute_length()*0.01 # 1% of curve length
        else:
            eps_crv = eps_crv_len
        
        if (self.convolve_gaussian(sig_c).compute_length() <= eps_crv):
            # then we simply see the curve as a straight line
            plids = [[0, len(self.coors)-1]]
            lids = [[0, len(self.coors)-1]]       
            
        planeline_param['pred_segs'] =  plids
        line_param['pred_segs'] = lids
            
        self.intrinsic_dims = {}
        self.intrinsic_dims['scale_range'] = scale_range
        self.intrinsic_dims['planeline_scales'] = data['planeline']
        self.intrinsic_dims['line_scales'] = data['line']
        self.intrinsic_dims['planeline_param'] = planeline_param
        self.intrinsic_dims['line_param'] = line_param
        
        return {'planeline_pred':plids,'line_pred':lids}
    
    def plot_decomposed_table(self,ax,show_selection=True,show_scales=True,aspect=3,xdiv=50,ydiv=10):
        """Display decomposed intrinsic table.
        
        It is only used after running ``decompose_intrinsicdim()``.
        
        Args:
            ax : plot axis.
            show_selection (bool): if True, then display selection interval.
            show_scales (bool): if True, display scale range in y axis.
            aspect (int): aspect ratio between x and y axes.
            xdiv (int): to calculate xticks.
            ydiv (int): to calculate yticks.
        
        """
        
        newcolors = np.array([[0.,0.7,0.],[0.9,0.9,0.]])
        mycmap = ListedColormap(newcolors)
        
        npoints = len(self.coors)

        ax.imshow(self.intrinsic_dims['planeline_scales'],cmap=mycmap,aspect=aspect)
        ax.contourf(self.intrinsic_dims['line_scales'], 1, hatches=['', '//// \\\\\\\\'], alpha=0.5) # use this to mark line within plane
        
        if show_scales == True:
            ax.set_yticks(np.arange(0,len(self.intrinsic_dims['scale_range']),ydiv))
            ax.set_yticklabels((np.round(self.intrinsic_dims['scale_range'][0::ydiv],2)).astype(np.int))
        else:
            ax.set_yticks(np.arange(0,len(self.intrinsic_dims['scale_range']),ydiv))
        
        if show_selection == True:
            min_pl_level = self.intrinsic_dims['planeline_param']['min_level']
            max_pl_level = self.intrinsic_dims['planeline_param']['max_level']
            min_l_level = self.intrinsic_dims['line_param']['min_level']
            max_l_level = self.intrinsic_dims['line_param']['max_level']
            
            ax.hlines(min_pl_level,0,npoints,color='yellow',linewidth=5)
            ax.hlines(max_pl_level,0,npoints,color='yellow',linewidth=5)
            ax.hlines(min_pl_level+min_l_level,0,npoints,color='blue')
            ax.hlines(min_pl_level+max_l_level,0,npoints,color='blue')
        
        ax.set_xlim(0,npoints);
        ax.set_xticks(np.arange(0,npoints,xdiv));
        
        ax.invert_yaxis();
        ax.grid('on');
        
        ax.set_ylabel('scale')
        ax.set_xlabel('u')
        
    def plot_intrinsicdim(self,ax,projection='3d',scales=(1.,1.,1.),
                          root_args={"c":"blue","s":100},
                          dim1d_args={"c":"magenta","lw":1,"alpha":1.},
                          dim2d_args={"c":"yellow","lw":3,"alpha":0.7},
                          dim3d_args={"c":"green","lw":3,"alpha":0.7},
                          plane_color="yellow",
                          overrided_curve=None):
        """Display curve superimposed by estimated intrinsic dimensions.
        
        It is only used after running ``decompose_intrinsicdim()``.
        
        Args:
            ax : plot axis.
            projection (str): support *3d, xy, xz, yz* modes.
            scales (tuple of float): specify x, y, z scales.
            overrided_curve (Curve): superimpose estimated intrinsic dimensions on the overrided_curve.
                if None, then a scaled curve computed from ``decompose_intrinsicdim()`` is used as default.
        
        """
        
        from genepy3d.obj.points import Points        
        
        if overrided_curve is not None:
            P = overrided_curve.coors
        else:
            min_pl_level = self.intrinsic_dims['planeline_param']['min_level']
            max_pl_level = self.intrinsic_dims['planeline_param']['max_level']
            avg_pl_level = int((min_pl_level+max_pl_level)/2)
            avg_scale = self.intrinsic_dims['scale_range'][avg_pl_level]
            P = self.convolve_gaussian(avg_scale).coors
        
        pl.plot_point(ax,projection,P[0,0],P[0,1],P[0,2],scales,point_args=root_args)
        
        pl.plot_line(ax,projection,P[:,0],P[:,1],P[:,2],scales,line_args=dim3d_args)        
        
        pred_pl_ids = self.intrinsic_dims['planeline_param']['pred_segs']
        pred_l_ids = self.intrinsic_dims['line_param']['pred_segs']
        for i in pred_pl_ids:
            idx = range(i[0],i[1]+1)
            pl.plot_line(ax,projection,P[idx,0],P[idx,1],P[idx,2],scales,line_args=dim2d_args)
            if projection == '3d':
                data = P[idx]
                c, normal = Points(data).fit_plane()
                maxx = np.max(data[:,0])
                maxy = np.max(data[:,1])
                minx = np.min(data[:,0])
                miny = np.min(data[:,1])
                
                pnt = np.array([0.0, 0.0, c])
                d = -pnt.dot(normal)
                
                xx, yy = np.meshgrid([minx, maxx], [miny, maxy])
                z = (-normal[0]*xx - normal[1]*yy - d)*1. / normal[2]
                
                ax.plot_surface(xx, yy, z, color=plane_color,alpha=0.4)
            
        for i in pred_l_ids:
            idx = range(i[0],i[1]+1)
            pl.plot_line(ax,projection,P[idx,0],P[idx,1],P[idx,2],scales,line_args=dim1d_args)
            
        if projection != '3d':
                ax.axis('equal')
        else:
            param = pl.fix_equal_axis(self.coors / np.array(scales))
            ax.set_xlim(param['xmin'],param['xmax'])
            ax.set_ylim(param['ymin'],param['ymax'])
            ax.set_zlim(param['zmin'],param['zmax'])
            
    
    def compute_local_3d_scale_sigma(self,sig_lst,delta_sig=0,sig_step=1,eps_seg_len=None,eps_crv_len=None,eps_kappa=0.01,eps_tau=0.01,return_dim_results=False):
        """Computing local 3d scale of curve from the list of sigma i.e stdev of Gaussian function.
        
        Local 3D scale: scale at which point transforms from 3D to 2D/1D. 
        Detail of the algorithm can be found in [1].
        
        Args:
            sig_lst (list (float)): list of sigma values.
            delta_sig (float): width of the searching interval.
            sig_step (int|float): scale step within the searching region.
            eps_seg_len (float): segment length threshold.
            eps_crv_len (float): curve length threshold.
            eps_kappa (float): curvature threshold.
            eps_tau (float): torsion threshold.
            return_dim_results (bool): if True, then return intrinsic dim estimation of r_lst
            
        Returns:
            list of local 3d scales for every points on curve.

        References:
            ..  [1] Phan MS, Matho K, Beaurepaire E, Livet J, Chessel A.
                    nAdder: A scale-space approach for the 3D analysis of neuronal traces. 2022.
                    PLOS Computational Biology 18(7): e1010211. DOI: 10.1371/journal.pcbi.1010211
            
        """
        
        npnt = self.coors.shape[0]
        nrad = len(sig_lst)
        counter = np.zeros(npnt)
        maxlen = np.ones(npnt)*-1.
        firstid = np.ones(npnt)*(nrad-1)
        
        if return_dim_results==True:
            dim_results = []
            
        # default delta sigma
        if delta_sig is None:
            delta_sig = 3 * sig_step
        
        # intrinsic dim estimation
        for ir in range(nrad):
                
            sc = sig_lst[ir]
            res = self.decompose_intrinsicdim(sc,delta_sig,
                                             eps_seg_len,eps_crv_len,sig_step,
                                             eps_kappa,eps_tau)
            
            if return_dim_results==True:
                dim_results.append(res)
            
            dimid = []
            for item in res['planeline_pred']:
                dimid = dimid + list(range(item[0],item[1]+1))
            
            countedid = np.argwhere(counter>0).flatten()
            intersectedid = np.intersect1d(countedid,dimid)
            diffid = np.setdiff1d(countedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = counter[intersectedid] + 1.
            if len(diffid)>0:
                checkid = np.argwhere(counter[diffid]>maxlen[diffid]).flatten()
                if len(checkid)>0:
                    updateid = diffid[checkid]
                    maxlen[updateid] = counter[updateid]
                    firstid[updateid] = ir - counter[updateid]
                    counter[updateid] = 0. # reset counter

            uncountedid = np.argwhere(counter==0).flatten()
            intersectedid = np.intersect1d(uncountedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = 1.
                
        # remove peaks
        nonvalidid = np.argwhere(maxlen==1.).flatten()
        firstid[nonvalidid] = nrad-1

        # when the point has 2D/1D until the end of radius
        finalcheckid = np.argwhere((counter>maxlen)&(counter!=0)).flatten()
        if len(finalcheckid)>0:
            firstid[finalcheckid] = nrad - counter[finalcheckid]
        
        if return_dim_results==False:
            return list(sig_lst[firstid.astype(np.uint)])
        else:
            return (list(sig_lst[firstid.astype(np.uint)]),dim_results)
    
    
    def compute_local_3d_scale_radius(self,r_lst,eps_seg_len=None,eps_crv_len=None,sig_step=1,eps_kappa=0.01,eps_tau=0.01,return_dim_results=False):
        """Computing local 3d scale of curve from the list of radius of curvatures.
        
        Local 3D scale: scale at which point transforms from 3D to 2D/1D.
        Detail of the algorithm can be found in [1].
        
        Args:
            r_lst (list (float)): list of radii of curvatures. The radius must be > 0.
            eps_seg_len (float): segment length threshold.
            eps_crv_len (float): curve length threshold.
            sig_step (int): scale step within the searching region.
            eps_kappa (float): curvature threshold.
            eps_tau (float): torsion threshold.
            return_dim_results (bool): if True, then return intrinsic dim estimation of r_lst
            
        Returns:
            list of local 3d scales for every points on curve.

        References:
            ..  [1] Phan MS, Matho K, Beaurepaire E, Livet J, Chessel A.
                    nAdder: A scale-space approach for the 3D analysis of neuronal traces. 2022.
                    PLOS Computational Biology 18(7): e1010211. DOI: 10.1371/journal.pcbi.1010211
            
        """
        
        npnt = self.coors.shape[0]
        nrad = len(r_lst)
        counter = np.zeros(npnt)
        maxlen = np.ones(npnt)*-1.
        firstid = np.ones(npnt)*(nrad-1)
        
        rstbl = RadiusScaleTable(self,max(r_lst)+1)
        
        if return_dim_results==True:
            dim_results = []
            
        
        # intrinsic dim estimation
        for ir in range(nrad):
            try:
                sc, delta_sig = rstbl.compute_scales_from_radius(r_lst[ir])
            except:
                raise Exception("failed at ir={}".format(ir))
            
            res = self.decompose_intrinsicdim(sc,delta_sig,
                                             eps_seg_len,eps_crv_len,sig_step,
                                             eps_kappa,eps_tau)
            
            if return_dim_results==True:
                dim_results.append(res)
            
            dimid = []
            for item in res['planeline_pred']:
                dimid = dimid + list(range(item[0],item[1]+1))
            
            countedid = np.argwhere(counter>0).flatten()
            intersectedid = np.intersect1d(countedid,dimid)
            diffid = np.setdiff1d(countedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = counter[intersectedid] + 1.
            if len(diffid)>0:
                checkid = np.argwhere(counter[diffid]>maxlen[diffid]).flatten()
                if len(checkid)>0:
                    updateid = diffid[checkid]
                    maxlen[updateid] = counter[updateid]
                    firstid[updateid] = ir - counter[updateid]
                    counter[updateid] = 0. # reset counter

            uncountedid = np.argwhere(counter==0).flatten()
            intersectedid = np.intersect1d(uncountedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = 1.
                
        # remove peaks
        nonvalidid = np.argwhere(maxlen==1.).flatten()
        firstid[nonvalidid] = nrad-1

        # when the point has 2D/1D until the end of radius
        finalcheckid = np.argwhere((counter>maxlen)&(counter!=0)).flatten()
        if len(finalcheckid)>0:
            firstid[finalcheckid] = nrad - counter[finalcheckid]
        
        if return_dim_results==False:
            return list(r_lst[firstid.astype(np.uint)])
        else:
            return (list(r_lst[firstid.astype(np.uint)]),dim_results)
    
    
    def compute_local_3d_scale(self,r_lst,eps_seg_len=None,eps_crv_len=None,sig_step=1,eps_kappa=0.01,eps_tau=0.01,return_dim_results=False):
        """Computing local 3d scale of curve.
        
        Local 3D scale: scale at which point transforms from 3D to 2D/1D.
        This function is DEPRECATED. Use ``compute_local_3d_scale_radius()`` or ``compute_local_3d_scale_sigma()``.
        
        Args:
            r_lst (list (float)): list of radii of curvatures.
            eps_seg_len (float): segment length threshold.
            eps_crv_len (float): curve length threshold.
            sig_step (int): scale step within the searching region.
            eps_kappa (float): curvature threshold.
            eps_tau (float): torsion threshold.
            return_dim_results (bool): if True, then return intrinsic dim estimation of r_lst
            
        Returns:
            list of local 3d scales for every points on curve.
            
        """
        
        npnt = self.coors.shape[0]
        nrad = len(r_lst)
        counter = np.zeros(npnt)
        maxlen = np.ones(npnt)*-1.
        firstid = np.ones(npnt)*(nrad-1)
        
        rstbl = RadiusScaleTable(self,max(r_lst)+1)
        
        if return_dim_results==True:
            dim_results = []
            
        
        # intrinsic dim estimation
        for ir in range(nrad):
            try:
                sc, delta_sig = rstbl.compute_scales_from_radius(r_lst[ir])
            except:
                raise Exception("failed at ir={}".format(ir))
            
            res = self.decompose_intrinsicdim(sc,delta_sig,
                                             eps_seg_len,eps_crv_len,sig_step,
                                             eps_kappa,eps_tau)
            
            if return_dim_results==True:
                dim_results.append(res)
            
            dimid = []
            for item in res['planeline_pred']:
                dimid = dimid + list(range(item[0],item[1]+1))
            
            countedid = np.argwhere(counter>0).flatten()
            intersectedid = np.intersect1d(countedid,dimid)
            diffid = np.setdiff1d(countedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = counter[intersectedid] + 1.
            if len(diffid)>0:
                checkid = np.argwhere(counter[diffid]>maxlen[diffid]).flatten()
                if len(checkid)>0:
                    updateid = diffid[checkid]
                    maxlen[updateid] = counter[updateid]
                    firstid[updateid] = ir - counter[updateid]
                    counter[updateid] = 0. # reset counter

            uncountedid = np.argwhere(counter==0).flatten()
            intersectedid = np.intersect1d(uncountedid,dimid)
            if len(intersectedid)>0:
                counter[intersectedid] = 1.
                
        # remove peaks
        nonvalidid = np.argwhere(maxlen==1.).flatten()
        firstid[nonvalidid] = nrad-1

        # when the point has 2D/1D until the end of radius
        finalcheckid = np.argwhere((counter>maxlen)&(counter!=0)).flatten()
        if len(finalcheckid)>0:
            firstid[finalcheckid] = nrad - counter[finalcheckid]
        
        if return_dim_results==False:
            return list(r_lst[firstid.astype(np.uint)])
        else:
            return (list(r_lst[firstid.astype(np.uint)]),dim_results)
    
    def _find_ridge(self,idx,C,step):
        """Find ridge starting from index idx at level 0 (noiseless case) in scale space C. 
        
        The interval size to find the next closest index of upper level is specified by step.
        
        This is the support function for ``main_turns()``.
        
        Args:
            idx (int): index to start identifying the ridge.
            C (array of float): matrix of scale space where searching for the ridge.
            step (int): threshold used to search the next closest index at the upper levels.
            
        Returns:
            array specifying the indices of ridge and a warning flag.
            
        Note:
            If warning flag = 1, then there's error when finding ridge.
            It could be due to the conflicts with anothers ridges during ridge evolution.
              
        """
        check_idx = idx
        ridge_idx = []
        ridge_idx.append((0,check_idx)) # add first ridge index
    
        warning = 0
        m, n = C.shape[0], C.shape[1]
    
        for i in range(1,m):
            
            subC = np.zeros(2*step+1)
            subC_start, subC_stop = 0, 2*step
        
            C_start, C_stop = check_idx-step, check_idx+step
        
            # check border condition
            if (check_idx-step)<0:
                C_start = 0
                subC_start = 0 - (check_idx-step)
                
            if (check_idx+step)>(n-1):
                C_stop = n-1
                subC_stop = (2*step) - ((check_idx+step) - (n-1))
        
            # extract local maxima at the upper level between interval specified by step
            subC[subC_start:(subC_stop+1)] = C[i,C_start:(C_stop+1)]
        
            candidate_idx = np.argwhere(subC!=0).flatten()
        
            # select the suitable index based on distance
            if len(candidate_idx)==0:
                break
            elif len(candidate_idx)==1:
                check_idx = check_idx + candidate_idx[0] - step
                ridge_idx.append((i,check_idx))
            else:
                darr = np.abs(candidate_idx-step)
                smallest_idx = np.argwhere(darr==min(darr)).flatten()
                if len(smallest_idx)==1:
                    check_idx = check_idx + candidate_idx[smallest_idx[0]] - step
                    ridge_idx.append((i,check_idx))
                else:
                    warning = 1
                    break
    
        return (np.array(ridge_idx), warning)
    
    def _removepnt_byangle(self,breakid,angle_thr):
        """Remove indices based on angle threshold.
        
        This is support function for ``main_turns()``.
        
        Args:
            breakid (array of int): list of potential principal indices.
            angle_thr (float): angle threshold in degree.
        
        Returns:
            new break indices.
        
        """
        
        x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
        
        newbreakid = breakid.copy()
        idx = 2
        while(idx<len(newbreakid)):
            ia = newbreakid[idx-2]
            ib = newbreakid[idx-1]
            ic = newbreakid[idx]
    
            a = np.array([x[ia],y[ia],z[ia]])
            b = np.array([x[ib],y[ib],z[ib]])
            c = np.array([x[ic],y[ic],z[ic]])
            
            if np.degrees(angle3points(a,b,c))<=angle_thr:
                newbreakid = np.delete(newbreakid,(idx-1))
            else:
                idx = idx + 1
        return newbreakid
    
    def main_turns(self,sig_lst,search_step=5,eps_kappa=None,ridgelength_thr=0.1,angle_thr=20,min_dist=None):
        """Compute the main turns of curve.

        Main turns are the positions on the curve showing important changes of orientation.
        We calculate the curvature scale space of the curve across a range of sigmas (Gaussian func).
        Then, track the change of curvatures of points on the curve within the curvature scale space.
        Finally, select the points as the main turns based on some criteria.
        
        Args:
            sig_lst (list (float)): list of sigma values used to compute curvature scale space.
            search_step (int): number of neighboring points that are grouped to find the main turns.
            eps_kappa (float): curvature threshold. 
                The points whose curvatures are larger than the ``eps_kappa`` are taken as the candidates to find the main turns.
                If None, then it is set relatively to the maximal curvature of the curve.
            ridgelength_thr (float): ridge length threshold (in % compared to the longest ridge).
                ridge is a track of a point in the curvature scale space. The point whose ridge length is larger than the ``ridgelength_thr`` is considered as main turn.
            angle_thr (float): angle threshold in degree. Remove position whose angle is smaller than the ``angle_thr``.
            min_dist (float): minimal distance between two main turns. Make sure that the distance between two main turns is not smaller than ``min_dist``.
            
        Returns:
            indices of main turns.
        
        """
        
        # local maximal curvatures indices at the original scale
        # extid = argrelextrema(crvr.compute_curvature(),np.greater)[0]
        
        # scale space
        data = self.scale_space(sig_lst,features={'curvature','ridge'})
        
        # setting kappa threshold
        if eps_kappa is None:
            kappa_max = np.max(self.compute_curvature())
            kappa_thr = kappa_max*0.05 # 1/20 of maximal curvature
        else:
            kappa_thr = eps_kappa
        
        # identify ridges in curvature scale space
        ridge_lst, length_lst, warning_lst = [],[],[]
        
        try:
            start_idx = np.argwhere((data['ridge'][0,:]!=0)&(data['curvature'][0,:]>kappa_thr)).flatten()
        except:
            return [] # there is no data for ridge and curvature
        
        for idx in start_idx:
            ridge,warning = self._find_ridge(idx,data['ridge'],search_step)
            ridge_lst.append(ridge)
            length_lst.append(len(ridge))
            warning_lst.append(warning)
        length_arr = np.array(length_lst)
        
        
        if (len(length_arr)==0):
            return []
    
        # select ridges based on ridge length
        p = max(length_arr)*ridgelength_thr
        selected_ridges = length_arr>=p
        selected_idx = start_idx[selected_ridges]
        
        # print(selected_idx)
    
        # remove indices based on angle criteria
        npoints = self.coors.shape[0]
        breakid = np.sort(np.array([0]+selected_idx.tolist()+[npoints-1]))
        newbreakid = self._removepnt_byangle(breakid,angle_thr)
        
        # print(newbreakid)
        
        # remove points very close to two sides (to compensate the error? but not know where...)
        # Modify into distance threshold
        # REMARK: should check this ???
        # if len(newbreakid)>2:
        #     if(newbreakid[1]<(1/50.)*npoints):
        #         newbreakid = np.delete(newbreakid,1)
                
        # if len(newbreakid)>2:
        #     idx = len(newbreakid)-2
        #     if((npoints-1-newbreakid[idx])<(1/50.)*npoints):
        #         newbreakid = np.delete(newbreakid,idx)
                
        # selected_idx = newbreakid[1:-1]
        
        # remove turns whose distance is too small
        if (min_dist != None) & (len(newbreakid)>2):
            check_idx = 0
            while(check_idx<len(newbreakid)-1):
                ix1, ix2 = newbreakid[check_idx], newbreakid[check_idx+1]
                coors = self.coors[ix1:ix2+1]
                if(geo_len(coors)<=min_dist):
                    newbreakid = np.delete(newbreakid,check_idx+1)
                else:
                    check_idx += 1
        
        selected_idx = newbreakid[1:-1] # remove the two extremal points (first and last points that are employed to compute the main turns)
        
        # ignored_idx = np.setdiff1d(extid,selected_idx)
        
        # self.ppt = {} # main turns results
        # self.ppt['scale_range'] = scale_range
        # self.ppt['curvature_scales'] = data['curvature']
        # self.ppt['ridge_scales'] = data['ridge']
        # self.ppt['ridge_lst'] = ridge_lst
        # self.ppt['ridge_ids'] = start_idx
        # self.ppt['selected_ridge_ids'] = start_idx[selected_ridges]
        # self.ppt['ppt_ids'] = selected_idx
        # self.ppt['excluded_ids'] = ignored_idx
        
        return selected_idx
    
    def main_turns_old(self,nbscales=None,search_step=5,eps_kappa=None,ridgelength_thr=0.1,angle_thr=20,min_dist=None):
        """Compute the main turns of curve.

        Main turns are the positions on the curve showing important changes of orientation.
        We calculate the curvature scale space of the curve across a range of sigmas (Gaussian func).
        Then, track the change of curvatures of points on the curve within the curvature scale space.
        Finally, select the points as the main turns based on some criteria.

        The sigmas are defined from ``nbscales` input. sigmas = [0, 1, ..., nbscales]

        This function is DEPRECATED. Please refer to main_turns().
        
        Args:
            nbscales (int): number of scales used to compute the curvature scale space. If None, then it is set as halft of number of points of the curve.
            search_step (int): number of neighboring points that are grouped to find the main turns.
            eps_kappa (float): curvature threshold. 
                The points whose curvatures are larger than the ``eps_kappa`` are taken as the candidates to find the main turns.
                If None, then it is set relatively to the maximal curvature of the curve.
            ridgelength_thr (float): ridge length threshold (in % compared to the longest ridge).
                ridge is a track of a point in the curvature scale space. The point whose ridge length is larger than the ``ridgelength_thr`` is considered as main turn.
            angle_thr (float): angle threshold in degree. Remove position whose angle is smaller than the ``angle_thr``.
            min_dist (float): minimal distance between two main turns. Make sure that the distance between two main turns is not smaller than ``min_dist``.
            
        Returns:
            indices of main turns.
        
        """
        
        # local maximal curvatures indices at the original scale
        # extid = argrelextrema(crvr.compute_curvature(),np.greater)[0]
        
        if nbscales is None:
            _nbscales = int(self.size / 2)
        else:
            _nbscales = nbscales
        
        # scale space
        data = self.scale_space(range(int(_nbscales)),features={'curvature','ridge'})
        
        # setting kappa threshold
        if eps_kappa is None:
            kappa_max = np.max(self.compute_curvature())
            kappa_thr = kappa_max*0.05 # 1/20 of maximal curvature
        else:
            kappa_thr = eps_kappa
        
        # identify ridges in curvature scale space
        ridge_lst, length_lst, warning_lst = [],[],[]
        
        try:
            start_idx = np.argwhere((data['ridge'][0,:]!=0)&(data['curvature'][0,:]>kappa_thr)).flatten()
        except:
            return [] # there is no data for ridge and curvature
        
        for idx in start_idx:
            ridge,warning = self._find_ridge(idx,data['ridge'],search_step)
            ridge_lst.append(ridge)
            length_lst.append(len(ridge))
            warning_lst.append(warning)
        length_arr = np.array(length_lst)
        
        
        if (len(length_arr)==0):
            return []
    
        # select ridges based on ridge length
        p = max(length_arr)*ridgelength_thr
        selected_ridges = length_arr>=p
        selected_idx = start_idx[selected_ridges]
        
        # print(selected_idx)
    
        # remove indices based on angle criteria
        npoints = self.coors.shape[0]
        breakid = np.sort(np.array([0]+selected_idx.tolist()+[npoints-1]))
        newbreakid = self._removepnt_byangle(breakid,angle_thr)
        
        # print(newbreakid)
        
        # remove points very close to two sides (to compensate the error? but not know where...)
        # Modify into distance threshold
        if len(newbreakid)>2:
            if(newbreakid[1]<(1/50.)*npoints):
                newbreakid = np.delete(newbreakid,1)
                
        if len(newbreakid)>2:
            idx = len(newbreakid)-2
            if((npoints-1-newbreakid[idx])<(1/50.)*npoints):
                newbreakid = np.delete(newbreakid,idx)
                
        selected_idx = newbreakid[1:-1]
        
        # remove turns whose distance is too small
        if (min_dist != None) & (len(selected_idx)>1):
            check_idx = 0
            while(check_idx<len(selected_idx)-1):
                ix1, ix2 = selected_idx[check_idx], selected_idx[check_idx+1]
                coors = self.coors[ix1:ix2+1]
                if(geo_len(coors)<=min_dist):
                    selected_idx = np.delete(selected_idx,check_idx+1)
                else:
                    check_idx += 1
        
        # ignored_idx = np.setdiff1d(extid,selected_idx)
        
        # self.ppt = {} # main turns results
        # self.ppt['scale_range'] = scale_range
        # self.ppt['curvature_scales'] = data['curvature']
        # self.ppt['ridge_scales'] = data['ridge']
        # self.ppt['ridge_lst'] = ridge_lst
        # self.ppt['ridge_ids'] = start_idx
        # self.ppt['selected_ridge_ids'] = start_idx[selected_ridges]
        # self.ppt['ppt_ids'] = selected_idx
        # self.ppt['excluded_ids'] = ignored_idx
        
        return selected_idx
    
    def plot_ridge_map(self,ax,show_scales=True):
        """Display ridge finding from main turns computation.
        
        This is only used after running ``main_turns()``.
        
        Args:
            ax : plot axis.
            show_scales (bool): if True, display scale range in y axis.
        
        """
        
        ridge_ids = self.ppt['ridge_ids']
        ridge_lst = self.ppt['ridge_lst']
        selected_ridge_lst = self.ppt['selected_ridge_ids']
        ppt_ids = self.ppt['ppt_ids']
        scale_range = self.ppt['scale_range']
        for i in range(len(ridge_ids)):
            rid = ridge_ids[i]
            r = ridge_lst[i]
            if rid in selected_ridge_lst:
                if rid in ppt_ids:
                    ax.plot(r[:,1],r[:,0],c='green')
                else:
                    ax.plot(r[:,1],r[:,0],c='magenta')
            else:
                ax.plot(r[:,1],r[:,0],c='red')

        ax.set_ylim(0,len(scale_range))
        ax.set_yticks(range(len(scale_range)))
        
        if show_scales == True:
            ax.set_yticklabels(scale_range)
    
    def coors_to_pixel(self,dx,dy,dz):
        """Convert coordinates to pixel coordinates.

        Args:
            dx (float): pixel size in x.
            dy (float): pixel size in y.
            dz (float): pixel size in z.

        Returns:
            array of pixel coordinates.

        """

        x_px = (self.coors[:,0] / dx).astype(np.int64)
        y_px = (self.coors[:,1] / dy).astype(np.int64)
        z_px = (self.coors[:,2] / dz).astype(np.int64)

        return np.array([x_px,y_px,z_px]).T
    
    def to_points(self):
        """Convert Curve object to Points object.

        Returns:
            Points object.

        """
        from genepy3d.obj.points import Points
        
        return Points(self.coors)
    
    def plot(self,ax,projection="3d",scales=(1.,1.,1.),show_root=True,root_args={"color":"red"},line_args={'c':'blue',"lw":1},point_args=None):
        """Plot curve using matplotlib.

        Args:
            ax: matplotlib axis.
            projection (str): support '3d', 'xy', 'xz' and 'yz'.
            scales (tuple): scale in x, y and z.
            show_root (bool): If True, then show the root position (the first point).
            root_args (dic): Pass this to the scatter() in matplotlib.
            line_args (dic): Pass this to the plot() in matplotlib.
            point_args (dic): Pass this to the scatter() in matplotlib.

        Examples:
            ..  code-block:: python
                
                import numpy as np
                from genepy3d.obj import curves
                import matplotlib.pyplot as plt

                # 3D curve from a helix
                n = 200 # number of points
                t = np.arange(n)
                a = 1.
                b = 1.
                x = a * np.cos(t/5)
                y = a * np.sin(t/5)
                z = b * t
                crv = curves.Curve((x,y,z))

                # Plot the noisy curve
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                crv.plot(ax,point_args={"c":"r"}); # set point_args to display the points on the curve

        """
        
        line_pl = None
        if line_args is not None:
            line_pl = pl.plot_line(ax,projection,self.coors[:,0],self.coors[:,1],self.coors[:,2],scales,line_args=line_args)
        
        point_pl = None
        if point_args is not None:
            point_pl = pl.plot_point(ax,projection,self.coors[:,0],self.coors[:,1],self.coors[:,2],scales,point_args=point_args)
            
        root_pl = None
        if show_root == True:
            root_pl = pl.plot_point(ax,projection,self.coors[0,0],self.coors[0,1],self.coors[0,2],scales,point_args=root_args)
            
        return (line_pl, point_pl, root_pl)
        

# Default parameters for simulation model
            
DEFAULT_PARAMS_3D = {
    'n': [np.uint32(3*1e4)],
    'v': [1*1e-6],
    'omega': [2*np.pi],
    'zoom': range(5,11,1)        
}
DEFAULT_PARAMS_PLANE = {
    'n': [np.uint32(3*1e4)],
    'v': [i*1e-6 for i in range(10,12,1)],
    'omega': [0]
}
DEFAULT_PARAMS_LINE = {
    'length': range(100,151,10)    
}

class SimuIntrinsic:
    """Generate curve in 3D with random intrinsic dimension segments.
    
    The process is simulated based on 2D and 3D Brownian motion. 
    See ``active_brownian_2d()`` and ``active_brownian_3d()`` in ``genepy3d.util.geo`` module for the generation of Brownian motion.
    
    Attributes:
        seg_lbl (array of int): list of generated curve segments, ``0`` for 3d, ``1`` for 2d, ``2`` for 1d.
        npoints (int): number of points on simulated curve.
        sigma (float): for adding Gaussian noise.
        params (array of dic | dic): simulation parameters.
        random_state (int): seed number used to memorize the simulated curve.
        max_seg (int): maximal number of segments.
            if this is set, then number of simulated intrinsic segments will be <= max_seg.
        nb_seg (int): number of segments. 
            if this is set, then number of simulated intrinsic segments will be fixed at nb_seg.
        remove_zero_replica (bool): if True, then replace the '0,0,..' sequence into only one '0'.        
        
    Notes:
        specify either ``seg_lbl``, ``max_seg`` or ``nb_seg`` whose priority order is ``seg_lbl`` first, then ``max_seg`` and ``nb_seg``.

    Examples:
        ..  code-block:: python

            from genepy3d.obj import curves
            import matplotlib.pyplot as plt

            # Create a simulator to generate curve consists of 3D=>1D=>3D=>2D=>1D=>3D segments.
            simulator = curves.SimuIntrinsic(seg_lbl=[0,2,0,1,2,0]).gen()

            print("Number of points:",simulator.npoints)
            print("Line indices:",simulator.line_ids)
            print("Plane indices:",simulator.plane_ids)

            # Plot the simulated curve
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            simulator.plot(ax)
    
    """
    
    def __init__(self,seg_lbl=[0,1,2],npoints=1000,sigma=1.,random_state=None,params={},max_seg=None,nb_seg=None,remove_zero_replica=True,spline_order=1):
        
        self.npoints = npoints
        self.sigma = sigma
        self.random_state = random_state
        self.spline_order = spline_order
        
        # generate segment labels
        if nb_seg is not None:
            self.seg_lbl = self._gen_seg_lbl(nb_seg=nb_seg,remove_zero_replica=remove_zero_replica)
        elif max_seg is not None:
            self.seg_lbl = self._gen_seg_lbl(nb_seg=max_seg,is_max=True,remove_zero_replica=remove_zero_replica)
        elif seg_lbl is not None:
            if remove_zero_replica == True:
                # remove "0,0,.." pattern
                if remove_zero_replica==True:
                    ilbl = 0
                    while (ilbl<len(seg_lbl)):
                        if(seg_lbl[ilbl]!=0):
                            ilbl = ilbl + 1
                        elif(ilbl+1)<len(seg_lbl):
                            if seg_lbl[ilbl+1]==0:
                                seg_lbl.pop(ilbl)
                            else:
                                ilbl = ilbl + 1
                        else:
                            ilbl = ilbl + 1
            self.seg_lbl = seg_lbl
        else:
            raise Exception("must provide seg_lbl or nb_seg or max_seg.")
        
        # generate segments parameters
        self.seg_param = self._gen_seg_para(params)
    
    def _gen_seg_lbl(self,nb_seg,is_max=False,remove_zero_replica=True):
        """Generate a list of random segment labels: 0 is pure 3d, 1 is plane and 2 is line.
        
        This is the internal method used in ``__init__()``.
        
        Args:
            nb_seg (int): number of segments.
            is_max (bool): if True generate number of segments <= nb_seg.
            remove_zero_replica (bool): if True, then replace the '0,0,..' sequence into only one '0'.
            
        Returns:
            seg_lbl (array of int): list of intrinsic segments labels.
        
        """

        # init random seed
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        # init a random nb. of segment
        if is_max==False:
            ns = nb_seg
        else:
            ns = np.random.permutation(range(1,nb_seg+1))[0]
        
        # init a random nb. of plane and line segments <= nb_seg 
        nb_planes_lines = np.random.permutation(range(1,ns+1))[0] 
        
        seg_lbl = np.zeros(ns,dtype=np.uint8)
        ids = np.random.permutation(ns)[:nb_planes_lines] # random set of plane and line indices
        seg_lbl[ids] = np.random.randint(1,3,len(ids)) # random assign plane or line labels
        
        # convert to list
        seg_lbl = seg_lbl.tolist()
        
        # remove "0,0,.." pattern
        if remove_zero_replica==True:
            ilbl = 0
            while (ilbl<len(seg_lbl)):
                if(seg_lbl[ilbl]!=0):
                    ilbl = ilbl + 1
                elif(ilbl+1)<len(seg_lbl):
                    if seg_lbl[ilbl+1]==0:
                        seg_lbl.pop(ilbl)
                    else:
                        ilbl = ilbl + 1
                else:
                    ilbl = ilbl + 1
    
        return seg_lbl
    
    def _gen_seg_para(self,params):
        """Generate parameters for each segment from ``seg_lbl``.
        
        This is the internal method used in ``__init()__``.
        
        Args:
            params (array of dic | dic): ranges of segment parameters.
            
        Returns:
            seg_para (array of dic): list of segments parameters.
        
        """
        
        if self.random_state is not None:
            np.random.seed(self.random_state)
        
        params_3d = DEFAULT_PARAMS_3D
        params_plane = DEFAULT_PARAMS_PLANE
        params_line = DEFAULT_PARAMS_LINE
        
        if isinstance(params,dict):
            
            if '3d' in params.keys():
                params_3d = params['3d']

            if 'plane' in params.keys():
                params_plane = params['plane']
            
            if 'line' in params.keys():
                params_line = params['line']
        
        seg_para = []
        for i in range(len(self.seg_lbl)):
            ilbl = self.seg_lbl[i]
            record = {}
            
            if ilbl==0: # pure 3d segment
                
                try:
                    _para = params[i]['n']
                except:
                    _para = params_3d['n']
                idx = np.random.permutation(range(len(_para)))[0]
                record['n'] = _para[idx]
                
                try:
                    _para = params[i]['v']
                except:
                    _para = params_3d['v']
                idx = np.random.permutation(range(len(_para)))[0]
                record['v'] = _para[idx]
                
                try:
                    _para = params[i]['omega']
                except:
                    _para = params_3d['omega']
                idx = np.random.permutation(range(len(_para)))[0]
                record['omega'] = _para[idx]
                
                try:
                    _para = params[i]['zoom']
                except:
                    _para = params_3d['zoom']
                idx = np.random.permutation(range(len(_para)))[0]
                record['zoom'] = _para[idx]

            elif ilbl==1: # plane
                
                try:
                    _para = params[i]['n']
                except:
                    _para = params_plane['n']
                idx = np.random.permutation(range(len(_para)))[0]
                record['n'] = _para[idx]
                
                try:
                    _para = params[i]['v']
                except:
                    _para = params_plane['v']
                idx = np.random.permutation(range(len(_para)))[0]
                record['v'] = _para[idx]
                
                try:
                    _para = params[i]['omega']
                except:
                    _para = params_plane['omega']
                idx = np.random.permutation(range(len(_para)))[0]
                record['omega'] = _para[idx]
            
            else: # line
                
                try:
                    _para = params[i]['length']
                except:
                    _para = params_line['length']
                idx = np.random.permutation(range(len(_para)))[0]
                record['length'] = _para[idx]
                
            seg_para.append(record)
            
        return seg_para
        
    def gen(self):
        """Generate a 3D curve with specified intrinsic lines, planes and 3D.
        
        Returns:
            itself.
        
        Notes:
            generated curve for noiseless case can contain duplicata points.
            
        """
        
        from genepy3d.obj.points import Points
        
        tmp = []
        ipl, iln = 0,0
        seg_len = np.zeros(len(self.seg_param))
        
        # read each segment para
        for iseg in range(len(self.seg_lbl)):
            lbl = self.seg_lbl[iseg]
            par = self.seg_param[iseg]
            if lbl==0: # 3d segment
                # generate 3d active brownian process
                P,_ = active_brownian_3d(n=par['n'],v=par['v'],omega=par['omega'],seed_point=self.random_state)
                P = P * 1e6 # to micron
                
                # interpolation
                coef, to = interpolate.splprep([P[:,0],P[:,1],P[:,2]],k=self.spline_order,s=0)
                ti = np.linspace(0,1,1000)
                xi, yi, zi = interpolate.splev(ti,coef)
                Pi = np.array([xi,yi,zi]).T
                
                # smooth a bit
                Ps = Curve(Pi).convolve_gaussian(1.0).coors
                
                # random transformation
                phi, theta, psi = (((2*np.pi) - (0.)) * np.random.random(3) + (0.))
                zx,zy,zz = par['zoom'], par['zoom'], par['zoom']
                
                Pt = Points(Ps).transform(phi,theta,psi,0.,0.,0.,zx,zy,zz).coors
                
                tmp.append(Pt)
                seg_len[iseg] = geo_len(Pt)
                
            elif lbl==1: # plane segment
                
                ipl = ipl + 1 # plane numerator
                
                # generate 2d active brownian process
                P,_ = active_brownian_2d(n=par['n'],v=par['v'],seed_point=self.random_state)
                P = P * 1e6 # to micron
                P = np.append(P,np.zeros((P.shape[0],1)),axis=1) # add z coordinates
                
                # interpolation
                coef, to = interpolate.splprep([P[:,0],P[:,1],P[:,2]],k=self.spline_order,s=0)
                ti = np.linspace(0,1,1000)
                xi, yi, zi = interpolate.splev(ti,coef)
                Pi = np.array([xi,yi,zi]).T
                
                # random transformation
                alpha = 2*np.pi/3.
#                alpha = (((np.pi/2.) - (2*np.pi/3.)) * np.random.random(1) + (2*np.pi/3.))[0]
                beta = (((2*np.pi) - (0.)) * np.random.random(1) + (0.))[0]
                if (ipl%2)!=0:
                    phi, theta, psi = alpha,0.,beta
                else:
                    phi, theta, psi = 0.,alpha,beta
                
                Pt = Points(Pi).transform(phi,theta,psi,0.,0.,0.).coors
                
                tmp.append(Pt)
                seg_len[iseg] = geo_len(Pt)
                
            else: # line
                
                iln = iln + 1 # line numerator
                
                # a simple line in z axis
                P = np.array([np.zeros(par['length']),np.zeros(par['length']),np.arange(par['length'])]).T
                
                # random transformation
                alpha = -np.pi/3.
#                alpha = (((-np.pi/4.) - (-np.pi/3.)) * np.random.random(1) + (-np.pi/3.))[0]
                beta = (((2*np.pi) - (0.)) * np.random.random(1) + (0.))[0]
#                print(beta)
                if (iln%2)==0:
                    phi, theta, psi = alpha,0.,beta
                else:
                    phi, theta, psi = 0.,alpha,beta
                
                Pt = Points(P).transform(phi,theta,psi,0.,0.,0.).coors
                
                tmp.append(Pt)
                seg_len[iseg] = geo_len(Pt)
                
    
        # concatenate segments into curve
        Pcrv = []
        break_ids = np.zeros(len(self.seg_param)+1,dtype=np.int16)
        plane_ids = []
        line_ids = []
        
        s = 0
        full_len = np.sum(seg_len)
        for iseg in range(len(self.seg_param)):
            lbl = self.seg_lbl[iseg]
            # compute proportion of nb. of. points w.r.t. segment length
            if iseg!=(len(self.seg_param)-1):
                npoints_seg = int((seg_len[iseg]*1./full_len)*self.npoints)
                s = s + npoints_seg
            else:
                npoints_seg = self.npoints - s
            
            # interpolation
            P = tmp[iseg]
            coef, to = interpolate.splprep([P[:,0],P[:,1],P[:,2]],k=self.spline_order,s=0)
            ti = np.linspace(0,1,npoints_seg)
            xi, yi, zi = interpolate.splev(ti,coef)
            Pi = np.array([xi,yi,zi]).T
            
            # concatenation
            if iseg==0:
                Pcrv = Pcrv + Pi.tolist()
            else:
                dx, dy, dz = Pcrv[-1] - Pi[0]
                Pt = Points(Pi).transform(0.,0.,0.,dx,dy,dz).coors
                Pcrv = Pcrv + Pt.tolist()
    
            # save break index
            break_ids[iseg+1] = len(Pcrv)
            if lbl==1: # plane
                plane_ids.append([len(Pcrv)-npoints_seg,len(Pcrv)-1])
            elif lbl==2: # line
                line_ids.append([len(Pcrv)-npoints_seg,len(Pcrv)-1])
                
        # add noise to 3d curve
        Pcrv = np.array(Pcrv)
        Pcrv_noise = Pcrv + np.random.randn(len(Pcrv),3)*self.sigma
        
        self.coors = Pcrv
        self.coors_noise = Pcrv_noise
        self.break_ids = break_ids
        self.plane_ids = plane_ids
        self.line_ids = line_ids
        
        return self
                
    def add_noise(self,sigma):
        """Add Gaussian noise to curve.
        
        Args:
            sigma (float): std of Gaussian kernel.
            
        Returns:
            itself.
        
        """
        
        self.sigma = sigma
        self.coors_noise = self.coors + np.random.randn(len(self.coors),3)*self.sigma
        return self
    
    def get_curve(self,noisy=True):
        """Return curve with/without noise.
        
        Args:
            noisy (bool): if True, then return noisy curve, and False otherwise.
            
        Returns:
            Curve object.
        
        """
        if noisy==True:
            return Curve(self.coors_noise)
        else:
            return Curve(self.coors)
        
    def evaluate(self,pred_line_ids,pred_plane_ids,metric="f1"):
        """Evaluate accuracies of intrinsic dimension estimation.
        
        Args:
            pred_line_ids (list): list of predicted lines indices.
            pred_plane_ids (list): list of predicted planes indices.
            metric (str): accuracy metric, we support: *f1, jaccard, balanced* as in scikit learn.
            
        Returns:
            A tuple including
                - [line_acc, line_pre, line_rec]: line accuracy, precision and recall.
                - [plane_acc, plane_pre, plane_rec]: plane accuracy, precision and recall.
                - [nonplane_acc, nonplane_pre, nonplane_rec]: 3D accuracy, precision and recall.
        
        """
        
        true_line_ids = self.line_ids
        true_plane_ids = self.plane_ids
        n = self.npoints
        
        def _get_segs(P):
            """Get list of local planes or lines for a given scale of the planes or lines evolution data.
            """
            seg_list = []
            connected_compo, nb_compo = label(P)
            if nb_compo != 0:
                for i_compo in range(1,nb_compo+1):
                    idx = np.argwhere(connected_compo==i_compo).flatten()
                    seg_list.append([idx[0],idx[-1]])
            return seg_list
        
        # line score
        if((len(true_line_ids)==0) | (len(pred_line_ids)==0)):
            line_acc = -1 # not consider this case for simplcity
            line_pre = -1
            line_rec = -1
        else:
            acc_line = []
            pre_line, rec_line = [], []
            for true_idx in true_line_ids:
                true_tmp = np.zeros(n,dtype=np.uint)
                true_tmp[true_idx[0]:true_idx[-1]+1]=1
                acc = 0.
                pre, rec = 0., 0.
                for pred_idx in pred_line_ids:
                    pred_tmp = np.zeros(n,dtype=np.uint)
                    pred_tmp[pred_idx[0]:pred_idx[-1]+1]=1
                    
                    pre_tmp = metrics.precision_score(true_tmp,pred_tmp)
                    if pre_tmp > pre:
                        pre = pre_tmp
                    
                    rec_tmp = metrics.recall_score(true_tmp,pred_tmp)
                    if rec_tmp > rec:
                        rec = rec_tmp
                    
                    if metric=="f1":
                        acc_tmp = metrics.f1_score(true_tmp,pred_tmp)
                    elif metric=="jaccard":
                        acc_tmp = metrics.jaccard_score(true_tmp,pred_tmp)
                    else:
                        acc_tmp = metrics.balanced_accuracy_score(true_tmp,pred_tmp)
                    
                    if acc_tmp > acc:
                        acc = acc_tmp
                
                acc_line.append(acc)
                pre_line.append(pre)
                rec_line.append(rec)
            
            line_acc = np.mean(np.array(acc_line))
            line_pre = np.mean(np.array(pre_line))
            line_rec = np.mean(np.array(rec_line))
        
        # plane score
        if((len(true_plane_ids)==0) | (len(pred_plane_ids)==0)):
            plane_acc = -1 # not consider this case for simplcity
            plane_pre = -1
            plane_rec = -1
        else:
            acc_plane = []
            pre_plane, rec_plane = [], []
            for true_idx in true_plane_ids:
                true_tmp = np.zeros(n,dtype=np.uint)
                true_tmp[true_idx[0]:true_idx[-1]+1]=1
                acc = 0.
                pre, rec = 0., 0.
                for pred_idx in pred_plane_ids:
                    pred_tmp = np.zeros(n,dtype=np.uint)
                    pred_tmp[pred_idx[0]:pred_idx[-1]+1]=1
                    
                    pre_tmp = metrics.precision_score(true_tmp,pred_tmp)
                    if pre_tmp > pre:
                        pre = pre_tmp
                    
                    rec_tmp = metrics.recall_score(true_tmp,pred_tmp)
                    if rec_tmp > rec:
                        rec = rec_tmp                
                    
                    if metric=="f1":
                        acc_tmp = metrics.f1_score(true_tmp,pred_tmp)
                    elif metric=="jaccard":
                        acc_tmp = metrics.jaccard_score(true_tmp,pred_tmp)
                    else:
                        acc_tmp = metrics.balanced_accuracy_score(true_tmp,pred_tmp)
                    
                    if acc_tmp > acc:
                        acc = acc_tmp
                            
                acc_plane.append(acc)
                pre_plane.append(pre)
                rec_plane.append(rec)
            
            plane_acc = np.mean(np.array(acc_plane))
            plane_pre = np.mean(np.array(pre_plane))
            plane_rec = np.mean(np.array(rec_plane))
        
        # 3d score
        tmp = np.ones(n,dtype=np.uint)
        for ip in (true_plane_ids+true_line_ids):
            tmp[ip[0]:ip[-1]+1]=0
        true_nonplane_ids = _get_segs(tmp)
        # print(true_nonplane_ids)
        
        tmp = np.ones(n,dtype=np.uint)
        for ip in (pred_plane_ids+pred_line_ids):
            tmp[ip[0]:ip[-1]+1]=0
        pred_nonplane_ids = _get_segs(tmp)
        # print(pred_nonplane_ids)
        
        if((len(true_nonplane_ids)==0) | (len(pred_nonplane_ids)==0)):
            nonplane_acc = -1 # not consider this case for simplcity
            nonplane_pre = -1
            nonplane_rec = -1
        else:
            acc_nonplane = []
            pre_nonplane, rec_nonplane = [], []
            for true_idx in true_nonplane_ids:
                true_tmp = np.zeros(n,dtype=np.uint)
                true_tmp[true_idx[0]:true_idx[-1]+1]=1
                acc = 0.
                pre, rec = 0., 0.
                for pred_idx in pred_nonplane_ids:
                    pred_tmp = np.zeros(n,dtype=np.uint)
                    pred_tmp[pred_idx[0]:pred_idx[-1]+1]=1
                    
                    pre_tmp = metrics.precision_score(true_tmp,pred_tmp)
                    if pre_tmp > pre:
                        pre = pre_tmp
                    
                    rec_tmp = metrics.recall_score(true_tmp,pred_tmp)
                    if rec_tmp > rec:
                        rec = rec_tmp
                    
                    if metric=="f1":
                        acc_tmp = metrics.f1_score(true_tmp,pred_tmp)
                    elif metric=="jaccard":
                        acc_tmp = metrics.jaccard_score(true_tmp,pred_tmp)
                    else:
                        acc_tmp = metrics.balanced_accuracy_score(true_tmp,pred_tmp)
                    
                    if acc_tmp > acc:
                        acc = acc_tmp
                            
                acc_nonplane.append(acc)
                pre_nonplane.append(pre)
                rec_nonplane.append(rec)
            
            nonplane_acc = np.mean(np.array(acc_nonplane))
            nonplane_pre = np.mean(np.array(pre_nonplane))
            nonplane_rec = np.mean(np.array(rec_nonplane))
    
        return ([line_acc, line_pre, line_rec],
                [plane_acc, plane_pre, plane_rec],
                [nonplane_acc, nonplane_pre, nonplane_rec])
        
        
    def plot(self,ax,projection='3d',noisy=True,scales=(1.,1.,1.),show_interpoints=False):
        """Plot simulated curve with its intrinsic segments.
        
        Args:
            ax: plot axis.
            projection (str): support *3d, xy, xz, yz* modes.
            noisy (bool): plot noisy curve or noiseless curve.
            scales (tuple of float): specify x, y and z scales.
            show_interpoints (bool): if True, points in between intrinsic segments are displayed.
                    
        """
        
        from genepy3d.obj.points import Points
        
        if noisy==True:
            P = self.coors_noise
        else:
            P = self.coors
            
        pl.plot_point(ax,projection,P[0,0],P[0,1],P[0,2],scales,point_args={'c':'blue','s':50})
        
        pl.plot_line(ax,projection,P[:,0],P[:,1],P[:,2],scales,line_args={'c':'green','alpha':0.7})
        
        if show_interpoints==True:
            if len(self.break_ids)>2:
                pl.plot_point(ax,projection,P[self.break_ids[1:-1],0],P[self.break_ids[1:-1],1],P[self.break_ids[1:-1],2],scales,point_args={'c':'cyan','s':20})
        
        for pid in self.plane_ids:
            pl.plot_line(ax,projection,P[pid[0]:pid[1],0],P[pid[0]:pid[1],1],P[pid[0]:pid[1],2],scales,line_args={'c':'yellow','alpha':0.7})

            
            if projection == '3d':
            
                data = P[pid[0]:pid[1]]
                c, normal = Points(data).fit_plane()
                maxx = np.max(data[:,0])
                maxy = np.max(data[:,1])
                minx = np.min(data[:,0])
                miny = np.min(data[:,1])
                
                pnt = np.array([0.0, 0.0, c])
                d = -pnt.dot(normal)
                
                xx, yy = np.meshgrid([minx, maxx], [miny, maxy])
                z = (-normal[0]*xx - normal[1]*yy - d)*1. / normal[2]
                
                ax.plot_surface(xx, yy, z, color='yellow',alpha=0.4)
        
        for lid in self.line_ids:
            pl.plot_line(ax,projection,P[lid[0]:lid[1],0],P[lid[0]:lid[1],1],P[lid[0]:lid[1],2],scales,line_args={'c':(0.85,0.25,0.6),'alpha':1.0})
        
        if projection != '3d':
                ax.axis('equal')
        else:
            param = pl.fix_equal_axis(self.coors_noise / np.array(scales))
            ax.set_xlim(param['xmin'],param['xmax'])
            ax.set_ylim(param['ymin'],param['ymax'])
            ax.set_zlim(param['zmin'],param['zmax'])

class RadiusScaleTable:
    """Compute scales table of a curve from given radius of curvature.

    This is the support class for the function ``compute_local_3d_scale_radius()``.
    
    Attributes:
        crv (Curve): curve to compute radius scale table.
        r (float): reference radius of curvature.
        mo (str): method used in gaussian convolution to treat the extreme values.
        kerlen (float): gaussian kernel length.
    
    """
    
    def __init__(self, crv, r, mo=None, kerlen=None):
        
        self.crv = crv
        
        assert r > 0, "reference radius must be positive"
        self.kappa = 1./r
        
        if mo is None:
            self.mo = "nearest"
        else:
            self.mo = mo
            
        if kerlen is None:
            self.kerlen = 4.0
        else:
            self.kerlen = kerlen
            
        self.kappa_tbl = self.build_scales_from_radius()
            
    def build_scales_from_radius(self, max_iter=None):
        """Compute scales range from given reference radius.
        
        Support func of intrinsic dimensions decomposition.
        
        Args:
            max_iter (int): number of convolution iteration. If None, it will be set = haft of number of points.
            
        Retuns:
            kappa_tbl (array (float)): curvature table.
        
        """
        
        x, y, z = self.crv.coors[:,0], self.crv.coors[:,1], self.crv.coors[:,2]
        xs, ys, zs = x.copy(), y.copy(), z.copy()
        # npoints = self.crv.coors.shape[0]
        
        if max_iter is None:
            num_max = 1e4 # need to check this point
        else:
            num_max = max_iter
        ite = 1
        
        sig = 0
        kappa_tbl = []
        flag = True
        
        # compute kappa table
        while(flag):
                            
            if sig!=0:
                # smooth curve with gaussian func
                xs = gaussian_filter1d(x,sig,mode=self.mo,truncate=self.kerlen)
                ys = gaussian_filter1d(y,sig,mode=self.mo,truncate=self.kerlen)
                zs = gaussian_filter1d(z,sig,mode=self.mo,truncate=self.kerlen)
            
            scaled_curve = Curve(coors=(xs,ys,zs))
            cur = scaled_curve.compute_curvature()
            kappa_tbl.append(cur)
            sig += 1. # sigma step = 1
            
            ix = np.argwhere(cur > self.kappa).flatten()
            if len(ix)==0:
                flag = False
            
            if ite > num_max:
                flag = False
            else:
                ite += 1
                
        kappa_tbl = np.array(kappa_tbl).T # row is scale, col is point index
        
        return kappa_tbl
    
    def compute_scales_from_radius(self,r=None):
        """Compute scales range from given reference radius.
        
        Support func of intrinsic dimensions decomposition.
        
        Args:
            r (float): reference radius.
            
        Retuns:
            sig_c (float): central value of sigma
            delta_sig (float): std value of sigma
        
        """
        
        if r is None:
            check_kappa = self.kappa
        else:
            assert r > 0, "radius r must be positive"
            assert r <= (1./self.kappa), "radius r must be <= {}".format(1./self.kappa)
            check_kappa = 1./r # inverse of radius
            
        npoints = self.crv.coors.shape[0]
        
        # estimate sig_c and delta_sig
        if(len(self.kappa_tbl[self.kappa_tbl<=check_kappa])==0):
            raise Exception("failed to compute curvature table.")
            
        selected_sig = []
        for i in range(npoints):
            ix = np.argwhere(self.kappa_tbl[i]<=check_kappa).flatten()
            if len(ix)!=0:
                selected_sig.append(ix[0]) # take the first scale
        
        if len(selected_sig)!=0:
            sig_c = np.mean(selected_sig) # compute sig_c
            delta_sig = np.std(selected_sig) # compute delta_c
        else:
            raise Exception("failed to compute curvature table.")
        
        if sig_c == 0:
            delta_sig = 0
        
        return (sig_c, delta_sig)

def decompose_intrinsicdim_sequential(p,eps_line,eps_plane,eps_seg):
    """Decompose the curve into intrisic segments of 1D line, 2D plane and 3D.
    
    This decomposition method is implemented from the paper of J. Yang et al. [1].
    This func is only used to compare with our algorithm [2].
    
    Args:
        p (array of float): list of 3D points on curve.
        eps_line (float): line threshold.
        eps_plane (float): plane_threshold.
        eps_seg (float): segment length threshold.
        
    Returns:
        list of line and plane indices.

    References:
        ..  [1] Yang J, Yuan J, Li Y. Parsing 3D motion trajectory for gesture recognition. Journal of Visual Communication and Image Representation. 2016. Pages 627-640. DOI: 10.1016/j.jvcir.2016.04.010.

        ..  [2] Phan MS, Matho K, Beaurepaire E, Livet J, Chessel A. nAdder: A scale-space approach for the 3D analysis of neuronal traces. 2022. PLOS Computational Biology 18(7): e1010211. DOI: 10.1371/journal.pcbi.1010211
    
    """
    
    # support functions
    # ---
    
    def determinant(a,b,c,d):
        
        ab = b - a
        ac = c - a
        ad = d - a        
        m = np.array([[ab[0], ab[1], ab[2]],
                      [ac[0], ac[1], ac[2]],
                      [ad[0], ad[1], ad[2]]])
    
        return abs((1./6)*np.linalg.det(m))
    
    def label_line(p,eps,seg_len):
        n = len(p)
        lbl = np.zeros(n,dtype=np.uint)
        for i in range(1,n-1):
            p1 = p[i]-p[i-1]
            p2 = p[i+1]-p[i]
            
            if((norm(p1)==0) | (norm(p2)==0)):
                lbl[i]=0 # collapse points
            else:
                delta = 1. - ((np.dot(p1,p2)) / (norm(p1)*norm(p2)))
                if delta <= eps:
                    lbl[i] = 1 # line
                else:
                    lbl[i] = 0
                
        # remove small segment
        connected_compo, nb_compo = label(lbl)
        if nb_compo!=0:
            for j in range(1,nb_compo+1):
                connected_idx = np.argwhere(connected_compo==j).flatten()
                if len(connected_idx)<=seg_len:
                    lbl[connected_idx] = 0        
        
        return lbl
        
    def label_plane(p,lbl,eps,seg_len):
        n = len(p)
        lbl2 = lbl.copy()
        for i in range(1,n-2):
            if((lbl2[i]==0) & (lbl2[i+1]==0)):
                delta = determinant(p[i-1],p[i],p[i+1],p[i+2])                    
                if delta <= eps:
                    lbl2[i] = 2 # plane
                    lbl2[i+1] = 2
                    
        # remove small segment
        idx = np.argwhere(lbl2==2).flatten()
        lbltmp = np.zeros(n,dtype=np.uint)
        lbltmp[idx]=1
        connected_compo, nb_compo = label(lbltmp)
        if nb_compo!=0:
            for j in range(1,nb_compo+1):
                connected_idx = np.argwhere(connected_compo==j).flatten()
                if len(connected_idx)<=seg_len:
                    lbl2[connected_idx] = 0
        
        return lbl2
    
    def get_segments(lbl):
    
        data = []
        for ilbl in [0,1,2]:
            segs = []
            indicator = np.zeros(len(lbl))
            tmp = np.argwhere(lbl==ilbl).flatten()
            indicator[tmp]=1
            connected_compo, nb_compo = label(indicator)
            if nb_compo!=0:
                for j in range(1,nb_compo+1):
                    idx = list(np.argwhere(connected_compo==j).flatten())
                    if len(idx)!=0:
                        segs.append([idx[0],idx[-1]])
            
            data.append(segs)
        
        return data
    
    # ---
    
    lbl1 = label_line(p,eps_line,eps_seg)
    lbl2 = label_plane(p,lbl1,eps_plane,eps_seg)
    segs = get_segments(lbl2)
    
    return segs

def align(target, ref):
    """Align a target curve to match a reference curve.
    
    This func is used to align two curves that minimize their spatial differences.
    
    The func is useful as a preparation before computing the distance between the two curves.
    E.g. we provided ``emd()`` in the Points class to compute the Earth Mover's Distance between two point clouds.
    
    Args:
        target (Curve): target curve.
        ref (Curve): reference curve.
        
    Return:
        aligned target curve.
    
    """
    
    c1 = ref.coors
    c2 = target.coors
    
    # shifting
    c1 = c1 - c1[0]
    c2 = c2 - c2[0]
    
    # rotating based on two base lines
    v1 = c1[-1] - c1[0]
    v1 = v1 / np.sqrt(np.sum(v1**2))

    v2 = c2[-1] - c2[0]
    v2 = v2 / np.sqrt(np.sum(v2**2))

    u = np.cross(v1,v2)
    u = u / np.sqrt(np.sum(u**2))
    ux, uy, uz = u[0], u[1], u[2]
    theta = np.arccos(np.dot(v1,v2))
    stheta = np.sin(theta)
    ctheta = np.cos(theta)
    R = np.array([
        [ctheta + ux**2*(1-ctheta), ux*uy*(1-ctheta)-uz*stheta, ux*uz*(1-ctheta)+uy*stheta],
        [uy*ux*(1-ctheta)+uz*stheta, ctheta + uy**2*(1-ctheta), uy*uz*(1-ctheta)-ux*stheta],
        [uz*ux*(1-ctheta)-uy*stheta, uz*uy*(1-ctheta)+ux*stheta, ctheta + uz**2*(1-ctheta)]
    ])
    c2 = np.matmul(c2,R) # rotate c2 to c1 based on base line vectors v2 to v1
    
    c2 = c2 + ref.coors[0]
    
    return Curve(c2)
    
    
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    


        
        
