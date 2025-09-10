"""Methods for working with Points objects.
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import re
import numpy as np
import pandas as pd
import scipy.stats as scs

from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from genepy3d.util import plot as pl, geo

class Points:
    """Points cloud in 3D.
    
    Attributes:
        coors (array | tuple): list of 3d points.

            - if ``array`` is given, then each column is the x, y, z coordinates.
            - if ``tuple`` is given, then the items are the three arrays of x, y and z coordinates.

    Examples:
        ..  code-block:: python

            from genepy3d.obj import points
            from sklearn.datasets import make_blobs
            import matplotlib.pyplot as plt

            # Generate two clusters of 3D points
            coors, _ = make_blobs(n_features=3, centers = [(0, 0, 0), (5, 5, 5)])

            # Create Points object
            pnts = points.Points(coors)

            # Plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            pnts.plot(ax)            
    
    """
    def __init__(self, _coors):
        
        if isinstance(_coors,np.ndarray):
            self.coors = _coors
        elif isinstance(_coors,(tuple,list)):
            self.coors = np.array(_coors).T
    
    @property
    def size(self):
        """Number of points.
        """
        return len(self.coors)
    
    @classmethod
    def from_csv(cls,filepath,column_names=["x","y","z"],scales=(1.,1.,1.),args={}):
        """Create Points object from x, y and z coordinates in the csv file.
        
        Args:
            filepath (str): path of the csv file.
            column_names (list of str): coordinates columns in the csv file.
            scales (tuple of float): scales in x, y and z.
            args (dict): overried parameters of pandas.read_csv().
        
        Returns:
            A Points object.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import points

                filepath = "path/to/your/csv/file.csv"

                # Create Points object from column "x", "y", "z" in the given csv file
                pnts = points.Points.from_csv(filepath)
        
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
        """Create Points object from x, y, z coordinates in the text file (e.g. txt, xyz).

        Args:
            filepath (str): path to the text file.

        Returns:
            A Points object.
        
        Notes:
            We assume that the first three columns correspond to the x, y, z coordinates.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import points

                filepath = "path/to/your/text/file.txt"

                # Create Points object from  the given text file
                pnts = points.Points.from_text(filepath)
                
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
    
    def center(self):
        """Center the cloud to the mean of each coordinates.

        The coordinates of points will be updated. Nothing is returned.
                                                
        """
        self.coors[:,1]=self.coors[:,1]-self.coors[:,1].mean()
        self.coors[:,2]=self.coors[:,2]-self.coors[:,2].mean()
    
    def append(self,new_points):
        """Append a new points cloud to the current points cloud.
        
        Args: 
            new_points (Points): a Points object to be appended.

        Notes:
            The coordinates of the current Points object will be updated.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import points
                from sklearn.datasets import make_blobs
                import matplotlib.pyplot as plt

                # Create Points object from blob cluster centered at (0,0,0)
                coors, _ = make_blobs(n_features=3, centers = [(0, 0, 0)])
                pnts_1 = points.Points(coors)

                # Plot the pnts_1
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                pnts_1.plot(ax)

                # Create Points object from blob cluster centered at (5,5,5)
                coors, _ = make_blobs(n_features=3, centers = [(5, 5, 5)])
                pnts_2 = points.Points(coors)

                # Append pnts_2 into pnts_1
                pnts_1.append(pnts_2)

                # Plot the pnts_1 after appending the pnts_2
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                pnts_1.plot(ax)


        
        """
        self.coors=np.vstack((self.coors,new_points.coors))
    
    def transform(self,phi=0,theta=0,psi=0,dx=0,dy=0,dz=0,zx=1,zy=1,zz=1):
        """Transform the points cloud.
        
        Args:
            phi (float): rotation in x (in rad).
            theta (float): rotation in y (in rad).
            psi (float): rotation in z (in rad).
            dx (float): translation in x.
            dy (float): translation in y.
            dz (float): translation in z.
            zx (float): zoom in x.
            zy (float): zoom in y.
            zz (float): zoom in z.
        
        Returns:
            A Points object.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import points
                from sklearn.datasets import make_blobs
                import matplotlib.pyplot as plt

                # Generate 3D points cloud contains two clusters
                coors, _ = make_blobs(n_features=3, centers = [(0, 0, 0), (5, 5, 5)])
                pnts = points.Points(coors)

                # Plot the points cloud
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                pnts.plot(ax)

                # Rotate points cloud around z by 90 degrees.
                pnts_transformed = pnts.transform(psi=np.pi/2.)

                # Plot the rotated points
                pnts_transformed.plot(ax,point_args={'color':'r'})
        
        """
        Pnew = self.coors.copy()
        Pnew = np.append(Pnew,np.ones((Pnew.shape[0],1)),axis=1) # add additional column for 3d transformation => [n, 4]
        Pnew = Pnew[:,:,np.newaxis] # add additional dimension for propagation of all points => [n, 4, 1]
        
        # translation
        Rt = np.array([
            [1., 0., 0., dx],
            [0., 1., 0., dy],
            [0., 0., 1., dz],
            [0., 0., 0., 1.],
        ])
        
        Pt = np.matmul(Rt,Pnew)
        
        # rotation in z
        Rpsi = np.array([
            [np.cos(psi), -np.sin(psi), 0., 0.],
            [np.sin(psi), np.cos(psi), 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.],
        ])
        
        Pt = np.matmul(Rpsi,Pt)
        
        # rotation in y
        Rtheta = np.array([
            [np.cos(theta), 0, np.sin(theta), 0.],
            [0., 1., 0., 0.],
            [-np.sin(theta), 0., np.cos(theta), 0.],
            [0., 0., 0., 1.],
        ])
        
        Pt = np.matmul(Rtheta,Pt)
        
        # rotation in x
        Rphi = np.array([
            [1., 0., 0., 0.],
            [0., np.cos(phi), -np.sin(phi), 0.],
            [0., np.sin(phi), np.cos(phi), 0.],
            [0., 0., 0., 1.],
        ])
        
        Pt = np.matmul(Rphi,Pt)
        
        # zoom
        Rz = np.array([
            [zx, 0., 0., 0.],
            [0., zy, 0., 0.],
            [0., 0., zz, 0.],
            [0., 0., 0., 1.],
        ])
        
        Pt = np.matmul(Rz,Pt)
        
        return Points(Pt[:,:3,0])
    
    def bbox(self):
        """Return bounding box covered the point cloud

        Returns:
            x0 (float): top-left x
            y0 (float): top-left y
            z0 (float): top-left z
            xlen (float): length in x
            ylen (float): length in y
            zlen (float): length in z

        """

        x0, y0, z0 = np.min(self.coors,axis=0)
        xn, yn, zn = np.max(self.coors,axis=0)

        return (x0,y0,z0,xn-x0,yn-y0,zn-z0)
    
    def fit_plane(self):
        """Fit a hyperplane to the points cloud.
            
        Returns:
            Tuple containing
                - c (float): intercept scalar.
                - normal (1d array): normal vector.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import points
                from sklearn.datasets import make_blobs
                import matplotlib.pyplot as plt

                # Generate 3D points cloud contains two clusters
                coors, _ = make_blobs(n_features=3, centers = [(0, 0, 0), (5, 5, 5)])
                pnts = points.Points(coors)

                # Plot
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                pnts.plot(ax)

                # Compute the z-intercept and the normal vector of the hyperplane that fit the point cloud
                z0, normal = pnts.fit_plane()
        
        """
        (rows, cols) = self.coors.shape
        G = np.ones((rows, 3))
        G[:, 0] = self.coors[:, 0]  #X
        G[:, 1] = self.coors[:, 1]  #Y
        Z = self.coors[:, 2]
        (a, b, c),resid,rank,s = np.linalg.lstsq(G, Z, rcond=None)
        normal = (a, b, -1)
        nn = np.linalg.norm(normal)
        normal = normal / nn
        
        return (c, normal)
    
    def pca(self):
        """Compute principal components analysis from the points cloud.
        
        Returns:
            Tuple containing
                - (1d array): empirical mean of points cloud.
                - (2d array): component vectors sorted by explained variances.
                - (2d array): explained variances.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import points
                import matplotlib.pyplot as plt

                # Generate random points on the surface of a 3D ellipsoid
                pnts = points.gen_ellipsoid(axes_length=(1.5,1.,0.5),n=500)

                # PCA 
                means, components, variances = pnts.pca()

                # Plot
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                pnts.plot(ax,point_args={"alpha":0.3})
                ax.quiver(means[0], means[1], means[2], components[0,0], components[0,1], components[0,2], length=2*variances[0], color='red')
                ax.quiver(means[0], means[1], means[2], components[1,0], components[1,1], components[1,2], length=2*variances[1], color='red')
                ax.quiver(means[0], means[1], means[2], components[2,0], components[2,1], components[2,2], length=2*variances[2], color='red')
            
        
        """
        
        pca=PCA(n_components=3)
        pca.fit(self.coors)
        return (pca.mean_,pca.components_,pca.explained_variance_)
    
    def test_isotropy(self,n_iter=500):
        """Test if the points distribution is isotropic using bootstraping.
        
        Args:
            n_iter (int) : number of bootstraping iterations.
        
        Returns:
            p_value.
        
        """
        
        # PCA to collect explained variance        
        _, _, var = self.pca()
        vp1,vp2,vp3 = var
        
        # vp1/(vp1+vp2+vp3) proportion is near to 1/3 if the points cloud is isotropic.
        # Another proportion of the same type can be calculated with a spherical points
        # cloud which is a model of isotropic points cloud.
        # Simulating and calculating the second proportion several times allows to know
        # how much the studied sample is near to the model.
        t = vp1/(vp1+vp2+vp3)
        n_isotrop = 0.0
        
        for m in range(n_iter):
            n = len(self.coors)
            sphere = gen_sphere(n,1)
            _, _, svar = sphere.pca()
            ev1,ev2,ev3 = svar
            tprime = ev1/(ev1+ev2+ev3)
            if t <= tprime :
                n_isotrop += 1
        
        p_value = n_isotrop/n_iter
        
        return p_value
    
    # def kmeans(self,**kwargs):
    #     """Clustering points cloud using kmeans in scikitlearn.
        
    #     Link: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html 
        
    #     Args:
    #         **kwargs : kmeans arguments (read scikitlearn docs).
                                
    #     Returns:
    #         Tuple containing
    #             - labels (1d array): the integer label of each sample's point.
    #             - centers (2d array): the center of each cluster.
                
    #     Examples:
    #         kmeans(n_clusters=2) # run kmeans with 2 clusters
            
        
    #     """
        
    #     kmeans=KMeans(**kwargs)
    #     kmeans.fit(self.coors)
    #     labels=kmeans.predict(self.coors)
    #     centers=kmeans.cluster_centers_
        
    #     return (labels,centers)
    
    def export_to_VTK(self,filepath):
        """Export to VTK file format.

        This is the wrapper of the ``pointsToVTK(``) in ``pyevtk`` package.
        
        Args:
            filepath (str): full path of file to save, without extention.

        Returns:
            A VTK object.
                                        
        """

        from pyevtk.hl import pointsToVTK

        pointsToVTK(filepath, np.ascontiguousarray(self.coors[:,0]),  np.ascontiguousarray(self.coors[:,1]),  np.ascontiguousarray(self.coors[:,2]),data=None)

    def to_curve(self):
        """Convert to Curve under the assumption that the points are listed in order
        
        Returns:
            A Curve object.
        """
        
        from genepy3d.obj.curves import Curve
        return Curve(self.coors)
    
    def to_surface_qhull(self):
        """Convert to Surface by computing the convex hull of the points cloud.
        
        Returns:
            A Surface object.

        """
        from genepy3d.obj.surfaces import Surface
        return Surface.from_points_qhull(self.coors)
    
    def to_surface_alphashape(self,alpha=None):
        """Convert to Surface by computing the alpha shape, i.e. the 'concave up to concavities of size alpha' hull. Assume a relatively homogeneous repartition of the points.

        Please see ``surfaces.Surface.from_points_alpha_shape()``.
        
        Returns:
            a Surface object.
        
        """
        from genepy3d.obj.surfaces import Surface
        return Surface.from_points_alpha_shape(self.coors,alpha)
    
    def plot(self, ax, projection='3d', point_args={}, equal_aspect=True):
        """Plot points cloud using matplotlib.
        
        Args:
            ax: axis to be plotted.
            projection (str): support '3d'|'xy'|'xz'|'yz' plot.
            point_args (dic): matplotlib arguments of scatter().
            equal_aspect (bool): make equal aspect for both axes.
        
        """

        _point_args = {'color':'blue', 'alpha':0.9}
        for key, val in point_args.items():
            _point_args[key] = val            

        x, y, z = self.coors[:,0], self.coors[:,1], self.coors[:,2]
        
        if projection == '3d':
            ax.scatter(x,y,z,**_point_args)
            if equal_aspect == True:
                param = pl.fix_equal_axis(self.coors)
                ax.set_xlim(param['xmin'],param['xmax'])
                ax.set_ylim(param['ymin'],param['ymax'])
                ax.set_zlim(param['zmin'],param['zmax'])
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
        elif projection == 'xy':
            ax.scatter(x,y,**_point_args)
            if equal_aspect == True:
                ax.axis('equal')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
        elif projection == 'xz':
            ax.scatter(x,z,**_point_args)
            if equal_aspect == True:
                ax.axis('equal')
            ax.set_xlabel('X')
            ax.set_ylabel('Z')
        else:
            ax.scatter(y,z,**_point_args)
            if equal_aspect == True:
                ax.axis('equal')
            ax.set_xlabel('Y')
            ax.set_ylabel('Z')

def emd(ps1, ps2, return_flows=False):
    """Compute the Earth Mover's Distance (EMD) [1] between two points clouds ps1, ps2.
    
    Args:
        ps1 (Points): point cloud.
        ps2 (Points): point cloud.
        return_flows (bool): if True then return maching flows between ps1 and ps2.
        
    Returns:
        EMD distance between ps1 and ps2 and if return_flows is True, then return array of matching flows.

    References:
        ..  [1] https://en.wikipedia.org/wiki/Earth_mover%27s_distance

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.obj import points
            import matplotlib.pyplot as plt

            # Generate two points clouds
            x = np.arange(10)
            y = x
            z = np.zeros(10)
            pnt1 = points.Points((x,y,z))
            pnt2 = pnt1.transform(dx=20) # translate in x

            # EMD
            dist, flows = points.emd(pnt1,pnt2,return_flows=True)
            print(dist)
            print(flows)

            # Plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            pnt1.plot(ax)
            pnt2.plot(ax)
    
    """
    
    return geo.emd(ps1.coors, ps2.coors, return_flows)

def gen_ellipsoid(axes_length=[1.,1.,1.],n=100):
    """Generate random uniform points cloud on the surface of an ellipsoid. 
    
    Args:
        axes_length (list of float): half lengths of the major, median and minor axis.
        n (int): number of points to be generated.
    
    Returns:
        A Points object.

    Examples:
        ..  code-block:: python

            from genepy3d.obj import points
            import matplotlib.pyplot as plt

            # Generate random points on the surface of 3D ellipsoid
            pnts = points.gen_ellipsoid(axes_length=(1.5,1.,0.5),n=500)

            # Plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            pnts.plot(ax)
    
    """

    a=axes_length[0]
    b=axes_length[1]
    c=axes_length[2]
  
    # Simulation with spherical coordinates
    thetas=np.arccos(-2*np.random.random_sample(n)+1)  
    phis=2*np.pi*np.random.random_sample(n)
    pts=np.zeros((n,3))
    # theta polar angle
    # phi azimuthal angle
    for theta,phi,i in zip(thetas,phis,np.arange(n)):
        pts[i]=[a*np.sin(theta)*np.cos(phi),b*np.sin(theta)*np.sin(phi),c*np.cos(theta)]
    
    return Points(pts)
 
# def gen_gaussian_points(n=1000,center=[0,0,0],scales=[1.,1.,1.],orientation=[0,np.pi/2]):
#     """Generate point cloud by Gaussian sampling. 
    
#     Args:
#         n (int) : sample's size.
#         center (list of float): center of points cloud.
#         scales (float | array of float) : standard deviations along the three main axis.
#         orientation (array) : spherical coordinates of the first axis.
    
#     Returns:
#         Points.
    
#     """
    
    
#     # Simulation of a gaussian sample whose components are exactly
#     # the canonical vectors
#     X = scs.norm.rvs(loc=center,scale=scales,size=(n,3))
    
#     theta, phi = orientation
    
#     # Getting the asked orientation after some rotations
#     R=geo.rotation_matrix([0,0,1],theta)
#     v=np.cross(np.dot(R,[1,0,0]),[0,0,1])
#     R=np.dot(geo.rotation_matrix(v,np.pi/2-phi),R)
    
#     return Points(np.dot(X,R.transpose()))

def gen_sphere(r=1,n=1000):
    """Generate random uniform points cloud on a sphere.
    
    Args:
        r (float): sphere's radius.
        n (int): number of points.        
        
    Returns:
        A Points object.

    Examples:
        ..  code-block:: python

            from genepy3d.obj import points
            import matplotlib.pyplot as plt

            # Generate random points on the surface of 3D sphere
            pnts = points.gen_sphere(r=1,n=500)

            # Plot
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            pnts.plot(ax)
    
    """
    
    return gen_ellipsoid(axes_length=[r,r,r],n=n)

# def gen_blobs(**kwargs):
#     """Generate isotropic gaussian blobs for clustering. Convenience function around sklearn.
    
#     Args:
#         **kwargs : make_blobs keyword agruments in scikitlearn.
        
#     Returns:
#         Tuple containing
#             - Points.
#             - labels (array) : point label.
    
#     """
    
#     pts,labels=make_blobs(**kwargs)
#     return (Points(pts),labels)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
