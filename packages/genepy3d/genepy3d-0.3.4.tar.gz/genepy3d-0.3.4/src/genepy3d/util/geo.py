"""Support functions for geometrical calculus.
"""

import numpy as np

def l2(p1, p2):
    """L2 distance between two points p1, p2.

    Args:
        p1 (ndarray): first point.
        p2 (ndarray): second point.

    Returns:
        a float.

    """
    return np.sqrt(np.sum((p1-p2)**2))

def norm(p):
    """Norm of vectors.
    
    Args:
        p (ndarray): a vector or an array of vectors.
            each vector is at one row of the array, the array columns are the vector positions.
        
    Returns:
        an array of float.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.util import geo
            vecarr = np.array([[1,2,3],[1,2,3]]) # two vectors with similar values
            geo.norm(vecarr)
    
    """
    
    if len(p.shape)==2: # list of points
        return np.sqrt(np.sum(p**2,axis=1))
    elif len(p.shape)==1: # only one point
        return np.sqrt(np.sum(p**2))
    else:
        raise ValueError('Accept only vector or array of vectors.')

def vector2points(p1,p2,normalize=True):
    """Calculate the vector from point p1 to point p2 with/without normalization.

    Args:
        p1 (ndarray): first point.
        p2 (ndarray): second point.
        normalized (bool): if True, then normalize the vector.

    Returns:
        an ndarray.
    
    """
    
    v = p2 - p1
    if((normalize==True)&(norm(v)!=0)):
        return v/norm(v)
    else:
        return v
    
def vector_axes_angles(v):
    """Calculate the angles between vector v and the three axes x, y and z.

    Args:
        v (ndarray): a vector.

    Returns:
        tuple of floats of the angles between v and axes x, y and z respectively.

    """
    
    if norm(v)!=0:
        vx = np.array([1.,0.,0.])
        vy = np.array([0.,1.,0.])
        vz = np.array([0.,0.,1.])
        
        thetax = np.arccos(np.dot(v,vx)/(norm(v)*norm(vx)))
        thetay = np.arccos(np.dot(v,vy)/(norm(v)*norm(vy)))
        thetaz = np.arccos(np.dot(v,vz)/(norm(v)*norm(vz)))
        
        return (thetax, thetay, thetaz)
    
    else:
        return (np.nan,np.nan,np.nan)

def vector_spherical_angles(v):
    """Spherical angles of vector.

    Args:
        v (ndarray): a vector.
        
    Returns:
        a list [theta, phi] of spherical angles.

    Notes:
        The spherical coordinates are specified by
        
        - azimuthal angle (theta) between the orthogonal projection of the vector v (on xy plane) and the x-vector.
        - polar angle (phi) between the vector v and the z-vector.
       
    """
    
    orientations=[]

    if np.abs(v[0])<0.1 :
        if np.abs(v[1])<0.1 :
            phi=0
            # If phi equals to zero then the component is collinear to Oz axis and
            # theta has no numerical value
            theta=None
        else :
            theta=np.pi/2
            phi=np.arccos(v[2])
    else :
        phi=np.arccos(v[2])
        theta=np.arctan(v[1]/v[0])
    orientations.append([theta,phi])

    return orientations

def angle2vectors(a,b):
    """Return angle between two vectors a and b.

    Args:
        a (ndarray): a vector.
        b (ndarray): a vector.

    Returns:
        a float.

    """
    if (norm(a) == 0) | (norm(b)==0):
        return np.nan
    else:
        return np.arccos(np.dot(a,b)/(norm(a)*norm(b)))

def angle3points(a,b,c):
    """Return angle between three points where b is the center point. It is the angle between two vectors (b->a) and (b->c).
    
    Args:
        a (ndarray): a point.
        b (ndarray): a point.
        c (ndarray): a point.
        
    Returns:
        a float.
    
    """
    ab = b - a
    bc = c - b

    if (norm(ab)==0)|(norm(bc)==0):
        return np.nan
    else:
        cosine_angle = np.dot(ab, bc) / (norm(ab) * norm(bc))
        return np.arccos(cosine_angle)

def geo_len(P):
    """Return geodesic length of a curve defined from an array of points. The first point and the last point are the begin and the end of the curve.
    
    Args:
        P (ndarray): array of points.
        
    Returns:
        a float.    

    Examples:
        ..  code-block:: python
            
            import numpy as np
            from genepy3d.util import geo
            P = np.array([[1,1,1],[2,2,2],[3,3,3]]) # curve with three points (1,1,1), (2,2,2) and (3,3,3)
            geo.geo_len(P)
    
    """
    n = P.shape[0]
    s = 0
    for i in range(n-1):
        p1, p2 = P[i], P[i+1]
        s = s + l2(p1,p2)
    return s

def active_brownian_2d(n,v=1e-6,omega=0.,p0=[0,0],dt=1e-3,R=1e-6,T=300.,eta=1e-3,seed_point=None):
    """Generate an active Brownian motion in 2D. We implemented the algorithm from the Volpe et al. paper [1].
    
    Args:
        n (int): number of positions generated from the simulation.
        p0 (ndarray): init position.
        v (float): translation speed.
        omega (float): rotation speed.
        dt (float): time step.
        R (float): particle radius.
        T (float): environment temperature.
        eta (float): fluid viscocity.
    
    Returns:
        A tuple containing
            - P (array of float): list of 2D positions.
            - t (array of float): corresponding times.

    References:
        ..  [1] Volpe, G., Gigan, S., & Volpe, G. (2014). Simulation of the active Brownian motion of a microswimmer. 
                American Journal of Physics, 82(7), 659-664. DOI:10.1119/1.4870398.
        
    """
    if seed_point is not None:
        np.random.seed(seed_point)
    
    kB = 1.38e-23 # Boltzmann constant [J/K]
    gamma = 6*np.pi*R*eta # friction coefficient [Ns/m]
    DT = (kB*T)/gamma # translational diffusion coefficient [m^2/s]
    DR = (6*DT)/(8*R**2) # rotational diffusion coefficient [rad^2/s]
    
    P = np.zeros((n,2))
    P[0] = p0 # init point
    
    theta = 0 # init angle
    
    for i in range(n-1):
        # translational diffusion step
        P[i+1] = P[i] + np.sqrt(2*DT*dt)*np.random.randn(1,2)
    
        # rotational diffusion step
        theta = theta + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        
        # torque step
        theta = theta + dt*omega

        # drift step
        P[i+1] = P[i+1] + dt*v*np.array([np.cos(theta), np.sin(theta)])
    
    t = np.arange(0,n*dt,dt)
    
    return (P,t)

def active_brownian_3d(n,v=1e-6,omega=0.,p0=[0,0,0],dt=1e-3,R=1e-6,T=300.,eta=1e-3,seed_point=None):
    """Generate an active Brownian motion in 3D. We adapted the algorithm of active brownian motion in 2D from the paper of Volpe et al. [1] for 3D case.
    
    Args:
        n (int): number of positions generated from the simulation.
        p0 (ndarray): init position.
        v (float): translation speed.
        omega (float): rotation speed.
        dt (float): time step.
        R (float): particle radius.
        T (float): environment temperature.
        eta (float): fluid viscocity.
    
    Returns:
        A tuple containing
            - P (array of float): list of 3D positions.
            - t (array of float): corresponding times.

    References:
        ..  [1] Volpe, G., Gigan, S., & Volpe, G. (2014). Simulation of the active Brownian motion of a microswimmer. 
                American Journal of Physics, 82(7), 659-664. DOI:10.1119/1.4870398.
        
    """
    
    if seed_point is not None:
        np.random.seed(seed_point)
    
    kB = 1.38e-23 # Boltzmann constant [J/K]
    DT = (kB*T)/(6*np.pi*eta*R) # translational diffusion coefficient [m^2/s]
    DR = (kB*T)/(8*np.pi*eta*R**3) # rotational diffusion coefficient [rad^2/s]
    
    P = np.zeros((n,3))
    P[0] = p0 # init point
    
    theta = 0 # init angle
    phi = 0 # init angle
    
    for i in range(n-1):
        # translational diffusion step
        P[i+1] = P[i] + np.sqrt(2*DT*dt)*np.random.randn(1,3)
    
        # rotational diffusion step
        theta = theta + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        phi = phi + np.sqrt(2*DR*dt)*np.random.randn(1,1)[0,0]
        
        # torque step
        if omega != 0:
            theta = theta + dt*np.sin(omega)
            phi = phi + dt*np.cos(omega)

        # drift step
        P[i+1] = P[i+1] + dt*v*np.array([np.cos(theta)*np.sin(phi), np.sin(theta)*np.sin(phi), np.cos(phi)])
    
    t = np.arange(0,n*dt,dt)
    
    return (P,t)

def emd(X,Y,return_flows=False):
    """Compute the Earth Mover's Distance (EMD) [1] between two point clouds X and Y. 
    We used the emd func from POT library. Detail is here: https://pythonot.github.io/all.html#ot.emd
    
    Args:
        X (ndarray): array of points.
        Y (ndarray): array of points.
        return_flows (bool): if True return travelled flows between X and Y.
        
    Returns:
        if return_flows is False, then only the emd distance is returned, otherwise a tuple of distance and array of flows.

    References:
        ..  [1] https://en.wikipedia.org/wiki/Earth_mover%27s_distance

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.util import geo
            X = np.array([[1,1,1],[2,2,2]])
            Y = np.array([[3,3,3],[4,4,4]])
            loss = geo.emd(X,Y)
    
    """
    import ot # optimal transport lib
    
    n = X.shape[0]
    M = ot.dist(X, Y)
    a, b = np.ones((n,)) / n, np.ones((n,)) / n  # uniform distribution on samples
    loss = ot.emd2(a, b, M)
    if return_flows==True:
        F = ot.emd(a, b, M)
        return (loss,F)
    else:
        return loss
    
# def emd(X,Y,return_flows=False):
#     """Compute Earth Mover's Distance (EMD) between two nD points X and Y.
    
#     Args:
#         X (nD array): nD points.
#         Y (nD array): nD points.
#         return_flows (bool): if True return matching flows between X and Y.
        
#     Returns:
#         if return_flows is False, then only distance value else a tuple of distance and array of flows.
    
#     """
#     from emd import emd as emddev
    
#     return emddev(X,Y,return_flows=return_flows)


def rotation_matrix(u,theta):
    """Calculate the rotation matrix corresponding to a rotation of angle theta around a vector u in 3D.

    Args:
        u (ndarray) : 3D vector for rotation direction.
        theta (float) : rotation angle in radians.

    Returns:
        (ndarray of shape (3,3)) : rotation matrix.

    Examples:
        ..  code-block:: python
            
            import numpy as np
            from genepy3d.util import geo
            u = np.array([1.,0.,0.]) # unit x-vector
            theta = np.pi/2. # rotation of 90 degrees
            M = geo.rotation_matrix(u,theta) # rotation matrix of 90 degrees around the unit x-vector

    """
    P=np.kron(u,u).reshape(3,3)
    Q=np.diag([u[1]],k=2)+np.diag([-u[2],-u[0]],k=1)+np.diag([u[2],u[0]],k=-1)+np.diag([-u[1]],k=-2)
    return P+np.cos(theta)*(np.eye(3)-P)+np.sin(theta)*Q



























