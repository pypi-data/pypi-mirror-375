"""Methods for working with Surface objects.
"""

import numpy as np
from scipy import interpolate
from scipy.ndimage import morphology
from skimage import measure

import alphashape

from genepy3d.util import plot as pl

from pyevtk.hl import unstructuredGridToVTK
from pyevtk.vtk import VtkTriangle
import vtk

import trimesh

class Surface(trimesh.Trimesh):
    """Triangulated surface in 3D; inherits from Trimesh and thus is triangulated upon creation if the mesh is not a triangulation.

    The Trimesh library is here: https://trimsh.org/trimesh.html.
    
    Attributes:
        vertices (ndarray (float)): vertices coordinates.
        faces (ndarray (float)): index of the vertices of each of the simplices.
    
    """
   
    @classmethod
    def from_points_qhull(cls,points):
        """Create surface object from point cloud via the convex hull algorithms.
      
        Args:
            points (nx3 array of float): coordinates of point cloud.
        
        Returns:
            a Surface object.            

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import surfaces
                import matplotlib.pyplot as plt

                # coors = np.array(...): array whose columns are x, y and z coordinates
                
                surf = surfaces.Surface.from_points_qhull(coors) # surface from convex hull

                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                surf.plot(ax);

        """               

        # Notes
        # We used ConvexHull from scipy, but the result seems to contain crossed triangulation.
        # We employed convex_hull property from TriMesh for better estimation. See self.get_qhull() for more detail.

        from scipy.spatial import ConvexHull
        hull = ConvexHull(points)
        # Becasue hull.simplices are in the context of the full point list, not just Qhull vertexes
        simplices=np.reshape(np.stack([np.where(hull.vertices==i)[0] for i in hull.simplices.flat]),hull.simplices.shape) 
        return cls(hull.points[hull.vertices,:], simplices).get_qhull()
    
    @classmethod
    def from_points_alpha_shape(cls,points,alpha=None):
        """Create surface object from point cloud via the alpha-shape algorithms. 
        
        The result is the set triangles part of tetrahedrals with a circumsphere of radius less that alpha that face outward. 
      
        Args:
            points (nx3 array of float): coordinates of point cloud.
            alpha (float): value of alpha.
        
        Returns:
            a Surface instace.

        Notes:
            There is no guarantee on the topology of the resulting mesh.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import surfaces
                from genepy3d.util import geo
                import matplotlib.pyplot as plt

                # coors = np.array(...): array whose columns are x, y and z coordinates

                # Diagonal distance of the bounding box of the point cloud
                # Alpha value can be set relatively to this distance
                # Larger value of alpha produces surface closer to the convex hull
                min_coors = np.min(coors,axis=0)
                max_coors = np.max(coors,axis=0)
                diadst = geo.l2(min_coors,max_coors) # diagonal distance
                alpha = diadst/3. # alpha value

                # Surface from the alpha shape
                surf = surfaces.Surface.from_points_alpha_shape(coors,alpha)

                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                surf.plot(ax)

        """

        if alpha == None:
            mesh = alphashape.alphashape(points)
        else:
            mesh = alphashape.alphashape(points,alpha)

        return cls(mesh.vertices,mesh.faces)

    
#     @classmethod
#     def from_points_alpha_shape(cls,points,alpha):
#         """Create surface object from point cloud via the alpha-shape algorithms. 
        
#         The result is the set triangles part of tetrahedrals with a circumsphere of radius less that alpha that face outward. 
#         Python implementation from https://stackoverflow.com/questions/26303878/alpha-shapes-in-3d
      
#         Args:
#             points (nx3 array of float): coordinates of point cloud.
#             alpha (float): value of alpha.
        
#         Returns:
#             a Surface instace.

#         Notes:
#             There is no guarantee on the topology of the resulting mesh.

#         Examples:
#             ..  code-block:: python

#                 import numpy as np
#                 from genepy3d.obj import surfaces
#                 from genepy3d.util import geo
#                 import matplotlib.pyplot as plt

#                 # coors = np.array(...): array whose columns are x, y and z coordinates

#                 # Diagonal distance of the bounding box of the point cloud
#                 # Alpha value can be set relatively to this distance
#                 # Larger value of alpha produces surface closer to the convex hull
#                 min_coors = np.min(coors,axis=0)
#                 max_coors = np.max(coors,axis=0)
#                 diadst = geo.l2(min_coors,max_coors) # diagonal distance
#                 alpha = diadst/3. # alpha value

#                 # Surface from the alpha shape
#                 surf = surfaces.Surface.from_points_alpha_shape(coors,alpha)

#                 fig = plt.figure()
#                 ax = fig.add_subplot(111,projection='3d')
#                 surf.plot(ax)

#         """

#         from scipy.spatial import Delaunay
#         import numpy as np
#         from collections import defaultdict

# #        def alpha_shape_3D(pos, alpha):

#         tetra = Delaunay(points)

#         # Find radius of the circumsphere.
#         # By definition, radius of the sphere fitting inside the tetrahedral needs 
#         # to be smaller than alpha value
#         # http://mathworld.wolfram.com/Circumsphere.html

#         tetrapos = np.take(points,tetra.simplices,axis=0)
#         normsq = np.sum(tetrapos**2,axis=2)[:,:,None]
#         ones = np.ones((tetrapos.shape[0],tetrapos.shape[1],1))
#         a = np.linalg.det(np.concatenate((tetrapos,ones),axis=2))
#         Dx = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[1,2]],ones),axis=2))
#         Dy = -np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,2]],ones),axis=2))
#         Dz = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,1]],ones),axis=2))
#         c = np.linalg.det(np.concatenate((normsq,tetrapos),axis=2))
        
#         # Remove zero determinant
#         ids = np.argwhere(a!=0).flatten()
#         Dx = Dx[ids]
#         Dy = Dy[ids]
#         Dz = Dz[ids]
#         a = a[ids]
#         c = c[ids]
#         tetra_vertices = tetra.simplices[ids]
        
#         # Radius of circumshpere
#         r = np.sqrt(Dx**2+Dy**2+Dz**2-4*a*c)/(2*np.abs(a))

#         try:
        
#             # Find tetrahedrals
#             tetras = tetra_vertices[r<alpha,:]
#             # triangles
#             TriComb = np.array([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
#             Triangles = tetras[:,TriComb].reshape(-1,3)
#             Triangles = np.sort(Triangles,axis=1)
#             # Remove triangles that occurs twice, because they are within shapes
#             TrianglesDict = defaultdict(int)
#             for tri in Triangles:TrianglesDict[tuple(tri)] += 1
#             Triangles=np.array([tri for tri in TrianglesDict if TrianglesDict[tri] ==1])
#             #edges
#             EdgeComb=np.array([(0, 1), (0, 2), (1, 2)])
#             Edges=Triangles[:,EdgeComb].reshape(-1,2)
#             Edges=np.sort(Edges,axis=1)
#             Edges=np.unique(Edges,axis=0)

#             Vertices = np.unique(Edges)
#             simplices=np.reshape(np.stack([np.where(Vertices==i)[0] for i in Triangles.flat]),Triangles.shape) 
#             return Surface(points[Vertices,:], simplices)
        
#         except:
#             return None # can not compute the surface from the given alpha value
        
#    @classmethod
#    def from_OFF(cls,afile): #TODO
#        """Create surface object from OFF file. Does no check on the loaded mesh.
        
#       TODO
       
#        Args:
#            afile (string): path to load
        
#        Returns:
#            a Surface object
#        """       
#        return
    
    @classmethod
    def from_stl(cls,afile,xy2zratio=None,center=False): 
        """Create surface object from STL file.

        This function is *DEPRECATED*. use ``Surface.from_file()`` instead.
        
        Args:
            afile (string): filepath to load the surface.
            xy2zratio (float): in case of anisotromic measurement, ratio to apply to z coordinates w.r.t. x and y.
            center (bool): center the mesh.
        
        Returns:
            a Surface object.

        """
         
        # from stl import mesh
        
        # your_mesh = mesh.Mesh.from_file(afile)
        # points=np.reshape(your_mesh.data['vectors'],[3*your_mesh.data['vectors'].shape[0],3])
        # points=np.unique(points,axis=0)
 
        # inds=[]
        # for i in range(your_mesh.data['vectors'].shape[0]):
        #     for j in range(your_mesh.data['vectors'].shape[1]):
        #         inds.append(np.where([(points[k,:]==your_mesh.data['vectors'][i][j]).all() for k in range(len(points))])[0])
        # inds=np.reshape(np.stack(inds),your_mesh.data['vectors'].shape[0:2])  
        # #points_centered=preprocessing.scale(points,with_std=False)    
        
        # Load file using load() in trimesh
        try:
            your_mesh = trimesh.load(afile)
        except:
            raise Exception("Failed to load stl file.")
        
        points = your_mesh.vertices
        inds = your_mesh.faces
        
        if center:
            points[:,0]=points[:,0]-np.mean(points[:,0])
            points[:,1]=points[:,1]-np.mean(points[:,1])
            points[:,2]=points[:,2]-np.mean(points[:,2])
        if xy2zratio:
            points[:,2]=points[:,2]*xy2zratio
            
        
        return cls(points,inds)
    
    @classmethod
    def from_ply(cls,afile,xy2zratio=None,center=False): 
        """Create surface object from PLY file.

        This function is DEPRECATED. use ``Surface.from_file()`` instead.
        
        Args:
            afile (string): filepath to load the surface.
            xy2zratio (float): in case of anisotromic measurement, ratio to apply to z coordinates w.r.t. x and y.
            center (bool): center the mesh.
        
        Returns:
            a Surface object.

        """

        # Since from_STL() use trimesh.load() func, it is also convenient to load ply file
        return cls.from_stl(afile,xy2zratio,center)

    @classmethod
    def from_file(cls,afile,xy2zratio=None,center=False): 
        """Wrapper of trimesh.load() to load a surface from file.

        To see which file formats are supported. Use ``surfaces.available_formats()``.
        
        Args:
            afile (string): filepath to load the surface.
            xy2zratio (float): in case of anisotromic measurement, ratio to apply to z coordinates w.r.t. x and y.
            center (bool): center the mesh.
        
        Returns:
            a Surface object.

        Examples:
            ..  code-block:: python

                from genepy3d.obj import surfaces
                import matplotlib.pyplot as plt

                filepath = "path/to/file"
                surf = surfaces.Surface.from_file(filepath)

                fig = plt.figure()
                ax = fig.add_subplot(111,projection="3d")
                surf.plot(ax)

        """
        
        # Load file using load() in trimesh
        try:
            your_mesh = trimesh.load(afile)
        except:
            raise Exception("Failed to load file.")
        
        points = your_mesh.vertices
        inds = your_mesh.faces
        
        if center:
            points[:,0]=points[:,0]-np.mean(points[:,0])
            points[:,1]=points[:,1]-np.mean(points[:,1])
            points[:,2]=points[:,2]-np.mean(points[:,2])
        if xy2zratio:
            points[:,2]=points[:,2]*xy2zratio
        
        return cls(points,inds)
    
    
    @classmethod
    def from_volume(cls,vol,lbl,spacing=(1.,1.,1.),step_size=1,level=0.5,opening=False,fillholes=False):
        """Create isosurface of a 3D voxels volume from image stack using marching cubes.

        We assume that the image stack contains multiple volumic objects specified by integer labels.
        This function extracts the volume of a given label, then estimates the outlined surface using marching cubes from scikit-image.
        
        Args:
            vol (3D ndarray): 3D volume.
            lbl (int): voxel label of the volume to be extracted from the image stack.
            spacing (tuple (float)): voxel spacing using in marching cubes.
            step_size (int): parameter defining the mesh resolution (higher step_size yields coarser mesh).
            level (float): between 0 and 1, determine proportion between background (0.) and foreground (1.) in volume.
            opening (bool): preprocess volumne by morphology opening.
            fillholes (bool): preprocess volumne by morphology fillholes.
            
        Returns:
            a Surface object.

        Examples:
            ..  code-block:: python

                import numpy as np
                from genepy3d.obj import surfaces
                import matplotlib.pyplot as plt
                
                stack = np.zeros((100,100,100)) # an image stack of size 100x100x100
                stack[20:40,20:40,20:40] = 1 # a volume of label = 1

                surf = surfaces.Surface.from_volume(stack,1) # outline surface of volume

                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                surf.plot(ax);
        
        """
        
        # extend volume shape to avoid missing faces at border
        ext = 2*step_size + 1
        extvol = np.zeros((vol.shape[0]+2*ext,vol.shape[1]+2*ext,vol.shape[2]+2*ext))
        extvol[ext:ext+vol.shape[0],ext:ext+vol.shape[1],ext:ext+vol.shape[2]] = vol
        
        if isinstance(lbl,int):
            extvol[extvol!=lbl]=0.
        else:
            for lev in lbl:
                extvol[extvol!=lev] = 0.
        extvol[extvol!=0] = 1.
            
        if opening == True:
            extvol = morphology.binary_opening(extvol,iterations=3).astype(float)
        
        if fillholes == True:
            extvol = morphology.binary_fill_holes(extvol).astype(float)
        
        # get isosurface by lewiner algorithm
        verts, faces, _, _ = measure.marching_cubes(extvol, level=level, spacing=spacing, step_size=step_size)
        
        # get vertice coordinates back to the origin
        verts = verts - ext
        
        return cls(verts[:,[2,1,0]],faces)
    
    def get_qhull(self):
        """Return the Convex Hull of the surface.

        Returns:
            a Surface object.
        
        """

        # from scipy.spatial import ConvexHull
        # hull = ConvexHull(self.vertices)
        # #becasue hull.simplices are in the context of the full point list, not just Qhull vertexes
        # simplices=np.reshape(np.stack([np.where(hull.vertices==i)[0] for i in hull.simplices.flat]),hull.simplices.shape) 
        
        qhull = self.convex_hull
        return Surface(qhull.vertices, qhull.faces)

    def get_bbox(self):
        """Return the bounding box of the surface.

        Returns:
            a Surface object.

        """

        return Surface(self.bounding_box.vertices,self.bounding_box.faces)
    
    def get_obbox(self):
        """Return the oriented bounding box of the surface.

        Returns:
            a Surface object.

        """
        
        return Surface(self.bounding_box_oriented.vertices,self.bounding_box_oriented.faces)

    def get_obbox_axes(self):
        """Return the three basic axis-vectors covered the oriented bounding box. 

        Returns:
            Tuple contains:
            
            - coordinates of the three axes.
            - lengths of the three axes.
        
        """

        # Get oriented bounding box
        obbox = self.get_obbox()

        # Compute the angles between adjacent faces
        theta = np.round(obbox.face_adjacency_angles,3)

        # Find inplane edges (should be excluded from the measurement)
        inplane_edges = obbox.face_adjacency_edges[theta==0]

        # Exclude inplane edges
        edges_axis = []
        edges_len = []
        for i in range(len(obbox.edges_unique)):

            query = len(np.argwhere(np.array([len(np.setdiff1d(item,obbox.edges_unique[i])) for item in inplane_edges])==0).flatten())==0
            if query is True: # not inplane edge
                # print("Included",obbox.edges_unique[i],np.round(obbox.edges_unique_length[i],3))
                edges_len.append(np.round(obbox.edges_unique_length[i],3))
                edges_axis.append(obbox.edges_unique[i])
            # else:
            #     print("Excluded",obbox.edges_unique[i])
        
        # Get only on triple of edges with a common point
        uix = [0]
        for i in range(1,len(edges_axis)):
            candidate_ix = np.intersect1d(edges_axis[i], edges_axis[0]).flatten()
            if len(candidate_ix)>0:
                if candidate_ix == edges_axis[0][0]:
                    uix.append(i)
        edges_len = np.array(edges_len)[uix]
        edges_axis = np.array(edges_axis)[uix]

        # Sort by lengths
        six = np.argsort(edges_len)
        edges_len = edges_len[six]
        edges_axis = edges_axis[six]

        return obbox.vertices[edges_axis], edges_len

    def compute_sphericity(self):
        """Compute the sphericity index of the surface.

        The sphericity formula is from this paper: https://www.sciencedirect.com/science/article/pii/S1877750318304757#bib0205

        Sphericity = ((minor**2) / (median*major))**(1/3),

        where minor, median and major are lengths of the elliposoid fitting the surface.
        These lengths can be found from the orient bounding box of the surface.

        Returns:
            a float.

        """

        # Get edges lengths of the oriented bounding boxes
        _, edges_len = self.get_obbox_axes()

        if len(edges_len)!=3:
            raise Exception("Failed to determine minor, medium, major lengths of bounding box.")
        else:
            sphericity_index = (edges_len[0]**2 / (edges_len[1]*edges_len[2]))**(1./3)
        
        return sphericity_index
    
    def _find_projected_face(self,edges_axis):
        """Support function for get_paraboloid_centroid().

        Args:
            edges_axis (array): coordinates of 3 basic lines of the oriented bounding box.

        """

        best_dist = np.inf
        best_i, best_j = None, None
        best_crv, best_center = None, None

        # iterate each face of the oriented bounding box
        # find the intersection with surface
        # selection the center of the face the touch the head of the paraboiloid.
        for i in [0,1,2]:
            for j in [0,1]:

                # compute intersection between surface the face of the oriented bounding box.
                k = np.bitwise_xor(j,1)
                normal = edges_axis[i][k] - edges_axis[i][j]
                origin = edges_axis[i][j]
                crv = self.section(normal,origin)

                # get center of the face of the oriented bounding box.
                if i == 0:
                    l,m=1,2
                elif i == 1:
                    l,m=0,2
                else:
                    l,m=0,1
                c0 = edges_axis[i][j]
                c1 = edges_axis[l][1] + (edges_axis[m][1] - edges_axis[m][0])
                if j == 1:
                    c1 += (edges_axis[i][1] - edges_axis[i][0])
                center = np.mean(np.array([c0,c1]),axis=0)

                # compute distance of intersected positions to the center
                dist_lst = []
                for iv in range(crv.vertices.shape[0]):
                    dist = np.sum((crv.vertices[iv] - center)**2)**0.5
                    dist_lst.append(dist)

                # get the face with the minimal distance
                mean_dist = np.mean(dist_lst)
                if mean_dist < best_dist:
                    best_dist = mean_dist
                    best_i = i
                    best_j = j
                    best_crv = crv
                    best_center = center
        
        return best_i, best_j, best_dist, best_crv, best_center
    
    def get_paraboloid_centroid(self):
        """Find the centroid lying on the paraboloid.

        Assuming the surface has a paraboloid form. This function estimate the centroid lying on the surface.
        It's not similar to the centroid computed by averaging faces positions.

        """

        # Three axes of the oriented bounding box
        edges_axis, _ = self.get_obbox_axes()

        best_i, best_j, best_dist, best_crv, best_center = self._find_projected_face(edges_axis)

        return best_center

    
    def split(self):
        """Override split() by casting Trimesh to Surface.

        If the surface consists of distinct subsurfaces, then the function split() returns these subsurfaces.

        Returns:
            a list of distinct subsurfaces.

        """
        surface_splits = []
        trimesh_splits = super(Surface,self).split() # call split() from Trimesh
        
        # cast Trimesh obj to Surface obj
        if len(trimesh_splits)!=0:
            for m in trimesh_splits:
                surface_splits.append(Surface(m.vertices,m.faces))
        return surface_splits
    
    def to_points(self):
        """Convert to Points object.
        
        Returns:
            a Points object, consisting of the vertices of the mesh.
        
        """
        from genepy3d.obj.points import Points
        return Points(self.vertices)
    
    def export_to_VTK(self,filepath,kind='PolyData'):
        """Export surface in VTK fileformat, either as PolyData or unstructuredGrid.
        
        Args:
            filepath (string): path to export the file to, *with no extention*
            kind (string): one of 'PolyData' or 'UnstructuredGrid' (default:'PolyData').

        Returns:
            a VTK fileformat.
        
        """
        
        if kind == 'PolyData':
            
            Points = vtk.vtkPoints()
            Triangles = vtk.vtkCellArray()
            
            for p in self.vertices:
                Points.InsertNextPoint(p[0],p[1],p[2])

            for s in self.faces:            
                Triangle = vtk.vtkTriangle()
            
                Triangle.GetPointIds().SetId(0, s[0])
                Triangle.GetPointIds().SetId(1, s[1])
                Triangle.GetPointIds().SetId(2, s[2])
                Triangles.InsertNextCell(Triangle)
        
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(Points)
            polydata.SetPolys(Triangles)
            polydata.Modified()
        
            writer = vtk.vtkPolyDataWriter()
            writer.SetFileName(filepath)
            writer.SetInputData(polydata)
            writer.Write()

        if kind== 'UnstructuredGrid':
            offset=[]
            conn=[]
            for s in self.faces:
                conn.extend(s)
                offset.append(3)
            offset=np.array(offset)
            conn=np.array(conn)
    
            celltype=np.ones(len(self.faces))*VtkTriangle.tid      
    
            unstructuredGridToVTK(filepath, np.ascontiguousarray(self.vertices[:,0]),  np.ascontiguousarray(self.vertices[:,1]),  np.ascontiguousarray(self.vertices[:,2]), connectivity = conn, offsets = offset, cell_types = celltype, cellData = None, pointData = None)
    
    def plot(self,ax,**kwds):
        """Plot outline in 3D or 2D-projection (xy, xz and yz) using matplotlib.
        
        Args:
            ax: axis to be plotted.
            projection (str): support '3d'|'xy'|'xz'|'yz'.
            scales: (tuples [float]): scales in x y and z.
            args_3d (dic): matplotlib arguments to plot 3d boundary (set of 3d polygons). 
            args_2d (dic): matplotlib arguments to plot 2d boundary.
            equal_aspect (bool): make equal aspect for both axes.

        """
        if 'projection' in kwds.keys():
            projection = kwds['projection']
        else:
            projection = '3d'

        if 'scales' in kwds.keys():
            scales=kwds['scales']
        else:
            scales=(1.,1.,1.)
            
        if 'args_2d' in kwds.keys():
            args_2d = kwds['args_2d']
        else:
            args_2d = {'edgecolor':'yellow','edgewidth':1,'facecolor':None,'alpha':0.5,'divby':'row','ndiv':1}
            
        if 'args_3d' in kwds.keys():
            args_3d = kwds['args_3d']
        else:
            args_3d = {'edgecolor':'none','color':'yellow','alpha':0.5,'linewidths':0.1}
            
        if 'equal_aspect' in kwds.keys():
            equal_aspect = kwds['equal_aspect']
        else:
            equal_aspect = True
            
        vertices_scale = np.zeros(self.vertices.shape)            
        vertices_scale[:,0] = 1.*self.vertices[:,0]/scales[0]
        vertices_scale[:,1] = 1.*self.vertices[:,1]/scales[1]
        vertices_scale[:,2] = 1.*self.vertices[:,2]/scales[2]

        
        if projection=='3d':
            self._plot3d(ax,vertices_scale,args_3d)
            if equal_aspect == True:
                param = pl.fix_equal_axis(vertices_scale)
                ax.set_xlim(param['xmin'],param['xmax'])
                ax.set_ylim(param['ymin'],param['ymax'])
                ax.set_zlim(param['zmin'],param['zmax'])
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            
        else:
            if projection=='xy':
                coors2d = vertices_scale[:,[0,1]]
            elif projection=='xz':
                coors2d = vertices_scale[:,[0,2]]
            else:
                coors2d = vertices_scale[:,[1,2]]
            
            self._plot2d(ax,coors2d,**args_2d)
            
            if equal_aspect==True:
                ax.axis('equal')
                
    def _plot3d(self,ax,coors,args_3d={'edgecolor':'none','color':'yellow','alpha':0.5,'linewidths':0.1}):
        """Support 3d plot outline.
        
        Args:
            ax: axis to be plotted.
            coors (2d numpy array [float]): 3d coordinates of outline.
            edgecolor (str): edge color.
            facecolor (str): face color.
            alpha (float): transparent.
        
        """
        
        ax.plot_trisurf(coors[:, 0], coors[:,1], self.faces, coors[:, 2],**args_3d)
        
        #for simplex in self.faces:
        #    tri = mplot3d.art3d.Poly3DCollection([coors[simplex,:].tolist()],**args_3d)
        #    # tri.set_color(facecolor)
        #    # tri.set_edgecolor(edgecolor)
        #    ax.add_collection3d(tri)
                
    
    def _plot2d(self,ax,coors,edgecolor='yellow',edgewidth=1,facecolor=None,alpha=0.5,divby='row',ndiv=1):
        """Support 2d plot of outline.
        
        Allow plotting outline in different divisions along a specific axis.
        
        Args:
            ax: axis to be plotted.
            coors (2d numpy array [float]): 2d coordinates of outline.
            edgecolor (str): edge color.
            edgewidth (float): edge width.
            facecolor (str|list|matplotlib_colormap): face color.
            alpha (float): transparent.
            divby (str): axis of division, support 'row'|'col'.
            ndiv (int): number of division along specific axis.
        
        """
        
        # boundary = np.array(self.vertices.tolist()+[self.vertices[0]])
        
        from scipy.spatial import ConvexHull
        hull = ConvexHull(coors)
        
        xbound = list(coors[hull.vertices,0])+[coors[hull.vertices[0],0]]
        ybound = list(coors[hull.vertices,1])+[coors[hull.vertices[0],1]]
        
        if ndiv==1:
            if facecolor is None:
                ax.plot(xbound,ybound,c=edgecolor,lw=edgewidth,alpha=alpha)
            else:
                ax.fill(xbound,ybound,ec=edgecolor,lw=edgewidth,fc=facecolor,alpha=alpha)
        else:
            coef, t = interpolate.splprep([xbound, ybound], k=1)
            tnew = np.linspace(0,1,500)
            xnew, ynew = interpolate.splev(tnew,coef) # generate xnew, ynew which fill inside of outline
            if divby=='row':
                slices = np.linspace(ynew.min(),ynew.max(),ndiv+1)
                vals = ynew
            else:
                slices = np.linspace(xnew.min(),xnew.max(),ndiv+1)
                vals = xnew
            
            for i in range(len(slices)-1):
                idx = np.argwhere((vals>=slices[i])&(vals<=slices[i+1])).flatten()
                if facecolor is not None:
                    
                    if type(facecolor) is list:
                        _fc = facecolor[i]
                    elif type(facecolor) is str:
                        _fc = facecolor
                    else: # color map
                        _fc = facecolor(i*1.0/(len(slices)-1))

                    ax.fill(xnew[idx],ynew[idx],fc=_fc,ec=edgecolor,lw=edgewidth,alpha=alpha)
                else:
                    ax.plot(xnew[idx],ynew[idx],c=edgecolor,lw=edgewidth,alpha=alpha)
        
def available_formats():
    """Return file formats that support by Trimesh for loading the surface.

    Returns:
        list of support file formats.

    """
    return trimesh.available_formats()

        
