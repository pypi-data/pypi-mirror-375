"""Methods for working with Tree objects.
"""

import os
import re

import h5py

from scipy import interpolate

import requests

import networkx as nx

import numpy as np
import pandas as pd
import anytree
from anytree import search, PreOrderIter
from anytree.walker import Walker

from genepy3d.util import plot as pl
from genepy3d.io.base import CatmaidApiTokenAuth


class Tree:
    """Tree in 3D. The tree structure is constructed based on ``anytree`` package.

    We assume there are no duplicated nodes on the Tree.
    
    Attributes:
        nodes (anytree): structure of tree nodes.
        id (int): tree ID (optional).
        name (str): tree name (optional).  
    
    """
    
    def __init__(self,_nodes,_id=0,_name="GeNePy3D"):
        self.nodes = _nodes
        self.id = _id
        self.name = _name
    
    def _build_treenodes(nodes_tbl, connectors_tbl):
        """Building tree object using ``anytree`` package.

        This is the support function for classmethod.
        
        Args:
            nodes_tbl (pandas dataframe): tree nodes table.
            connectors_tbl (pandas dataframe): connectors table.
        
        """
        
        nodes = {}
        
        # get connector nodes
        conlst = []
        if connectors_tbl is not None:
            conlst = connectors_tbl.index.values.astype('int') # it may happen similar (ske,treenode) for 2 different connector id 
        
        # build treenodes
        for i in range(len(nodes_tbl)):
            nodeid = int(nodes_tbl.index[i])
            _x, _y, _z, _r, _structure_id = tuple(nodes_tbl.iloc[i][["x","y","z","r","structure_id"]])
            nodes[nodeid] = anytree.Node(nodeid,x=_x,y=_y,z=_z,r=_r,structure_id=_structure_id)
        
        # assign others features
        for i in range(len(nodes_tbl)):
            nodeid = int(nodes_tbl.index[i])
            
            # assign their parents
            parentnodeid = int(nodes_tbl.iloc[i]['parent_treenode_id'])
            if parentnodeid != -1:
                nodes[nodeid].parent = nodes[parentnodeid]
                
            # assign connectors
            if nodeid in conlst:
                _connrel = connectors_tbl.loc[nodeid]['relation_id'] # could be "pre or post synaptic"
                _connid = connectors_tbl.loc[nodeid]['connector_id'] 
            else:
                _connrel = "None"
                _connid = -1
            nodes[nodeid].connector_relation = _connrel
            nodes[nodeid].connector_id = _connid
            
        return nodes
    
    @classmethod
    def from_table(cls,nodes_tbl,connectors_tbl=None,tree_id=0,tree_name='genepy3d'):
        """Build tree from tables.
        
        Args:
            nodes_tbl (pandas dataframe): tree nodes table.
            connectors_tbl (pandas dataframe): connector table (optional).
            tree_id (int): tree ID (optional).
            tree_name (str): tree name (optional).

        Returns:
            A Tree object.

        Notes:
            -   It needs at least ``nodes_tbl`` to create the tree object. 
                The ``nodes_tbl`` stores information of nodes and their linked parent-nodes. 
                It is the same as in the SWC file specification. Please see this [1] for more detail.
                The column names must include:
                    -   treenode_id: ID of node
                    -   structure_id: ID of node structure (see the column `Structure Identifier` in [1] for the meaning).
                    -   x, y, z: coordinates of node
                    -   r: radius of node
                    -   parent_treenode_id: ID of parent node
            -   The table ``connectors_tbl`` is optional. 
                It is used to describe the synaptic connection between neuronal trees. It is the same as connector table in CATMAID [2].
                It must consist of columns:
                    -   connector_id: ID of a connector
                    -   treenode_id: ID of a treenode from a neuronal tree object
                    -   relation_id: connectomic relation, must be 'presynaptic_to' or 'postsynaptic_to' (see [3] to understand about connectomic relation in CATMAID)

        References:
            ..  [1] http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html
            ..  [2] https://catmaid.readthedocs.io/en/stable/index.html
            ..  [3] https://catmaid.readthedocs.io/en/stable/tracing_neurons.html

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot it
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)        
        
        """
        
        # check nodes_tbl
        if isinstance(nodes_tbl,pd.DataFrame):
            lbls = nodes_tbl.columns.values
            if all(lbl in lbls for lbl in ['treenode_id','structure_id','x','y','z','r','parent_treenode_id']):
                nodes_tbl_refined = nodes_tbl.dropna()
            else:
                raise Exception("can not find 'treenode_id','structure_id','x','y','z','r','parent_treenode_id' within the dataframe.")
        else: 
            raise Exception("nodes_tbl must be pandas dataframe.")
        
        # constraint some columns of nodes to int
        nodes_tbl_refined['structure_id'] = nodes_tbl_refined['structure_id'].astype('int')
        nodes_tbl_refined['treenode_id'] = nodes_tbl_refined['treenode_id'].astype('int')
        nodes_tbl_refined['parent_treenode_id'] = nodes_tbl_refined['parent_treenode_id'].astype('int')
        
        # reset index
        nodes_tbl_refined.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
        nodes_tbl_refined.set_index('treenode_id',inplace=True) # reset dataframe index
        
        # check connectors_tbl
        connectors_tbl_refined = None
        if connectors_tbl is not None:
            # check dfcon columns
            if isinstance(connectors_tbl,pd.DataFrame): 
                lbls = connectors_tbl.columns.values
                if all(lbl in lbls for lbl in ['treenode_id','connector_id','relation_id']):
                    connectors_tbl_refined = connectors_tbl.dropna()
                else:
                    raise Exception("can not find 'treenode_id','connector_id','relation_id' within the dataframe.")
            else:
                raise Exception("connectors_tbl must be pandas dataframe.")
            
            # constraint columns to int
            connectors_tbl_refined['connector_id'] = connectors_tbl_refined['connector_id'].astype('int')
            connectors_tbl_refined['treenode_id'] = connectors_tbl_refined['treenode_id'].astype('int')
            
            # reset index
            connectors_tbl_refined.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            connectors_tbl_refined.set_index("treenode_id",inplace=True) # reset dataframe index
        
        # build tree node structure
        nodes = cls._build_treenodes(nodes_tbl_refined,connectors_tbl_refined)
        
        return cls(nodes,tree_id,tree_name)
                       
    @classmethod
    def from_swc(cls,filepath):
        """Build tree from a SWC file.

        See this [1] for the description of SWC format.
        
        Args:
            filepath (str): path to swc file.

        Returns:
            A Tree object.

        References:
            ..  [1] http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html

        Examples:
            ..  code-block:: python

                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # An example of swc file can be downloaded from:
                # https://neuromorpho.org/neuron_info.jsp?neuron_name=AD1202-PMC-L-4201-fiber129
                swc_path = "file/to/swc/file"
                neu = trees.Tree.from_swc(swc_path)

                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neu.plot(ax)
        
        """
        
        data = []
        
        # extract info from file
        f = open(filepath,'r')
        for line in f:
            if line[0]!='#':
                tmp = []
                
                elemens = re.split(r'\r|\n| |\s', line)
                for ile in elemens:
                    if ile!='':
                        tmp.append(float(ile))
                
                data.append(tmp)
                
        f.close()
    
        # build dataframe and cast columns types
        if len(data)!=0:
            
            tree_name = os.path.basename(filepath).split(".swc")[0]
            tree_id = 0
            
            dfneu = pd.DataFrame(data,columns=['treenode_id', 'structure_id', 'x', 'y', 'z', 'r', 'parent_treenode_id'])            
            
            dfneu.dropna(inplace=True)
            
            # cast type
            dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
            dfneu['structure_id'] = dfneu['structure_id'].astype('int')
            dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
            
            # reset index
            dfneu.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfneu.set_index('treenode_id',inplace=True) # reset dataframe index
            # build tree node structure
            nodes = cls._build_treenodes(dfneu,None)
            return cls(nodes,tree_id,tree_name)
        else:
            raise ValueError("Errors when reading file.")
    
    @classmethod
    def from_eswc(cls,filepath):
        """Build tree from ESWC file. The ESWC is used e.g. in Vaa3D-Neuron software [1].

        ESWC is an extension of SWC with additional columns 'segment_id', 'level', 'mode', 'timestamp', 'featureval'.
        
        Args:
            filepath (str): path to eswc file.

        Returns:
            A Tree object.

        Notes:
            ESWC has extended columns compared to default SWC file, but we don't pass these extended columns into the Tree object.
            We only pass the similar columns to the Tree object as in the SWC file.

        References:
            ..  [1] https://github.com/Vaa3D/Vaa3D_Wiki/wiki/Vaa3DNeuron1.wiki

        Examples:
            Reading ESWC should be the same as reading SWC. Please see example from ``from_swc()``.
        
        """
        
        data = []
        
        # extract info from file
        f = open(filepath,'r')
        for line in f:
            if line[0]!='#':
                tmp = []
                
                elemens = re.split(r'\r|\n| |\s', line)
                for ile in elemens:
                    if ile!='':
                        tmp.append(float(ile))
                
                data.append(tmp)
                
        f.close()
        
        # build dataframe and cast columns types
        if len(data)!=0:
            
            tree_name = os.path.basename(filepath).split(".eswc")[0]
            tree_id = 0
            
            if len(data[0])==12:
                dfneu = pd.DataFrame(data,columns=['treenode_id', 'structure_id', 'x', 'y', 'z', 'r', 'parent_treenode_id','segment_id','level','mode','timestamp','featureval'])            
            elif len(data[0])==11:
                dfneu = pd.DataFrame(data,columns=['treenode_id', 'structure_id', 'x', 'y', 'z', 'r', 'parent_treenode_id','segment_id','level','mode','timestamp'])
            else:
                raise Exception('The number of columns must be 11 or 12.')
            
            dfneu = dfneu[['treenode_id', 'structure_id', 'x', 'y', 'z', 'r', 'parent_treenode_id']]
            dfneu.dropna(inplace=True)
            
            # cast type
            dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
            dfneu['structure_id'] = dfneu['structure_id'].astype('int')
            dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
            
            # reset index
            dfneu.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfneu.set_index('treenode_id',inplace=True) # reset dataframe index
            # build tree node structure
            nodes = cls._build_treenodes(dfneu,None)
            return cls(nodes,tree_id,tree_name)
        else:
            raise ValueError("Errors when reading file.")
    
    @classmethod
    def from_ims(cls,filepath):
        """Build tree from Imaris file.
        
        Args:
            filepath (str): path to ims file.

        Returns:
            A Tree object.
        
        """

        # read file
        f = h5py.File(filepath,"r")
        
        # import vertex
        item = f["Scene8"]["Content"]["Filaments0"]["Vertex"]
        item_arr = np.array([item[i].tolist() for i in range(len(item))])
        vertex = pd.DataFrame(item_arr,columns=["x","y","z","r"])
        
        # import edge
        item = f["Scene8"]["Content"]["Filaments0"]["Edge"]
        item_arr = np.array([item[i].tolist() for i in range(len(item))])
        edge = pd.DataFrame(item_arr,columns=["vertex_begin","vertex_end"])
        
        # build graph from vertices and edges
        G=nx.Graph()
        G.add_nodes_from(vertex.index.tolist())
        G.add_edges_from(edge.values.tolist())
        
        # import dendrite table
        item = f["Scene8"]["Content"]["Filaments0"]["DendriteSegment"]
        item_arr = np.array([item[i].tolist() for i in range(len(item))])
        dendrite = pd.DataFrame(item_arr,columns=["id_time","id","vertex_begin","vertex_end","edge_begin","edge_end"])
        
        # import dendrite edge index table
        item = f["Scene8"]["Content"]["Filaments0"]["DendriteSegmentEdge"]
        item_arr = np.array([item[i].tolist() for i in range(len(item))])
        dendrite_edge = pd.DataFrame(item_arr,columns=["index"])
        
        # import dendrite vertex index table
        item = f["Scene8"]["Content"]["Filaments0"]["DendriteSegmentVertex"]
        item_arr = np.array([item[i].tolist() for i in range(len(item))])
        dendrite_vertex = pd.DataFrame(item_arr,columns=["index"])
        
        # compute dendrite fragments
        parent = {}
        big_vertex_lst = []

        for ix in range(len(dendrite)):

            subdf = dendrite.iloc[ix]

            # get IDs of edge begin and pair of vertices making the edge begin
            vertex_begin = dendrite_vertex.loc[subdf["vertex_begin"]][0] # get vertex begin
            edge_begin = dendrite_edge.loc[subdf["edge_begin"]].values[0] # get edge begin
            vertices_begin = edge.loc[edge_begin].values # get pair of vertices making the edge begin
            vertex_begin_partner = np.setdiff1d(vertices_begin,vertex_begin)[0] # get the second vertex from the pair

            # get IDs of edge end and pair of vertices making the edge end
            vertex_end = dendrite_vertex.loc[subdf["vertex_end"]-1][0]
            edge_end = dendrite_edge.loc[subdf["edge_end"]-1].values[0]
            vertices_end = edge.loc[edge_end].values
            vertex_end_partner = np.setdiff1d(vertices_end,vertex_end)[0]

            # check all path starting from vertex begin to vertex end
            # then get only path containing both edge begin and edge end
            vertex_lst = []
            for path in nx.all_simple_paths(G, source=vertex_begin, target=vertex_end):
                if (vertex_begin_partner == path[1]) & (vertex_end_partner == path[-2]):
                    vertex_lst = path

            # create parent-children link
            if len(vertex_lst)!=0:
                for i in range(1,len(vertex_lst)):
                    child_vertex = vertex_lst[i]
                    parent_vertex = vertex_lst[i-1]
                    parent[child_vertex] = parent_vertex

            big_vertex_lst += vertex_lst
        
        # build dendritic dataframe
        big_vertex_lst = np.unique(big_vertex_lst)
        
        parent_vertex_lst = []
        for key in big_vertex_lst:
            if key in parent.keys():
                parent_vertex_lst.append(parent[key])
            else:
                parent_vertex_lst.append(-1)
                
        df = vertex.loc[big_vertex_lst].copy()
        df["treenode_id"] = big_vertex_lst
        df["parent_treenode_id"] = parent_vertex_lst
        df["structure_id"] = 0
        
        return cls.from_table(df)
    
    @classmethod
    def from_catmaid_server(cls,catmaid_host,token,project_id,neuron_id):
        """Build tree from CATMAID [1].

        This function queries from the CATMAID server a neuronal trace given by a ``project_id`` and ``neuron_id``. 
        The neuronal trace data is fetched using CATMAID API [2].
        
        Args:
            catmaid_host (str): address of CATMAID server
            token (str): authenticated string
            project_id (int): project ID
            neuron_id (int): neuron ID

        Returns:
            A Tree object.

        References:
            ..  [1] https://catmaid.readthedocs.io/en/stable/index.html
            ..  [2] https://catmaid.readthedocs.io/en/stable/api.html

        Examples:
            ..  code-block:: python

                from genepy3d.obj import trees

                # Replace these fake values with your own
                catmaid_host = 'https://your-catmaid-host.com'
                token = "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
                project_id = 1
                neuron_id = 1

                # Retreive neuronal tree from from CATMAID host
                neuron = trees.Tree.from_catmaid_server(catmaid_host,token,project_id,neuron_id)

        """
        
        subneu, subcon = [], []
        
        linkrequest = catmaid_host+'{}/skeleton/{}/json'.format(project_id,neuron_id)
        res = requests.get(linkrequest,auth=CatmaidApiTokenAuth(token))
        
        if res.status_code!=200:
            raise ValueError('something wrong: check again your host, token, project id or neuron id.')
        else:
            if isinstance(res.json(),dict):
                raise ValueError('something wrong: check again your project id or neuron id.')
            else: # should be a list
                res = np.array(res.json())
                
                # get neuron name
                try:
                    neuron_name = res[0]
                except:
                    neuron_name = 'genepy3d'
                
                # get neuron info
                try:
                    for iske in res[1]:
                        if iske[1] is not None:
                            iske_sub = [iske[0], 0, iske[3], iske[4], iske[5], iske[6], iske[1]]
                        else:
                            iske_sub = [iske[0], 0, iske[3], iske[4], iske[5], iske[6], -1]
                        subneu.append(iske_sub)
                except:
                    subneu = []
                
                # get connector info
                try:
                    for icon in res[3]:
                        relation_type = 'presynaptic_to'
                        if icon[2]==1:
                            relation_type = 'postsynaptic_to'
                        icon_sub = [icon[1], icon[0], relation_type]
                        subcon.append(icon_sub)
                except:
                    subcon = []
        
        # create dfneu dataframe
        if len(subneu)==0:
            raise ValueError('neuron is empty!')
        else:
            dfneu = pd.DataFrame(subneu,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])
            # remove nan
            dfneu.dropna(inplace=True)
            # cast type
            dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
            dfneu['structure_id'] = dfneu['structure_id'].astype('int')
            dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
            # reset index
            dfneu.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfneu.set_index('treenode_id',inplace=True) # reset dataframe index
        
        # create dfcon dataframe
        if len(subcon)==0:
            dfcon = None
        else:
            dfcon = pd.DataFrame(subcon,columns=['connector_id','treenode_id','relation_id'])
            # remove nan
            dfcon.dropna(inplace=True)
            # constraint columns to int
            dfcon['connector_id'] = dfcon['connector_id'].astype('int')
            dfcon['treenode_id'] = dfcon['treenode_id'].astype('int')
            # reset index
            dfcon.drop_duplicates(subset=["treenode_id"],inplace=True) # make sure unique index
            dfcon.set_index("treenode_id",inplace=True) # reset dataframe index
            
        
        # build tree node structure
        nodes = cls._build_treenodes(dfneu,dfcon)
        return cls(nodes,neuron_id,neuron_name)
    
    def get_root(self):
        """Return root node ID.
        
        Returns:
            List of root ID (list[int]).
        
        """
        
        # may contain many roots
        return list(filter(lambda nodeid: self.nodes[nodeid].parent is None, self.nodes.keys()))
    
    def get_parent(self,nodeid):
        """Return parent id of node id.

        Args:
            nodeid (int): a node ID.

        Returns:
            Node ID (int).
        
        """
        
        return self.nodes[nodeid].parent.name
    
    def get_children(self,nodeid):
        """Return children ids of nodeid.

        Args:
            nodeid (int): a node ID.

        Returns:
            List of node ID (list[int]).

        """
        
        return [node.name for node in self.nodes[nodeid].children]
    
    def get_preorder_nodes(self,rootid=None):
        """Return list of nodes in tree. The order of nodes in the list follows the preorder traversal [1].

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            List of node ID (list[int]).

        References:
            ..  [1] https://en.wikipedia.org/wiki/Tree_traversal

        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [node.name for node in PreOrderIter(self.nodes[_rootid])]
        
    def get_number_nodes(self,rootid=None):
        """Return the total number of nodes in tree.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.

        Returns:
            Total number of nodes (int).

        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        return len(self.get_preorder_nodes(_rootid))
    
    def get_leaves(self,rootid=None):
        """Return list of leaf node IDs.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            list of int.
        
        """
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [leaf.name for leaf in self.nodes[_rootid].leaves]
    
    def get_branchingnodes(self,rootid=None):
        """Return list of branching node IDs.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            list of int.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        return [n.name for n in search.findall(self.nodes[_rootid],filter_=lambda node: len(node.children)>1)]
    
    def get_connectors(self,rootid=None):
        """Return list of connector node IDs.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            Pandas dataframe whose indices are node IDs and values are corresponding connector types, connector ids.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        connector_nodes = np.array([[node.name,node.connector_relation,node.connector_id] for node in PreOrderIter(self.nodes[_rootid])])
        df = pd.DataFrame({"relation":connector_nodes[:,1],"id":connector_nodes[:,2].astype(np.int64)},
                           index=connector_nodes[:,0].astype(np.int64))
        subdf = df[(df['relation']!='None')&(df['id']!=-1)]
        
        return subdf
    
    def get_coordinates(self, nodeid=None, rootid=None):
        """Return coordinates of given nodes.
        
        Args:
            nodes (int | list of int): list of node IDs. If None, then return the coordinates of all nodes from the given root ID.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            
        Returns:
            Pandas dataframe whose indices are node IDs and values are corresponding coordinates.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if nodeid is None:
            nodelst = [node.name for node in PreOrderIter(self.nodes[_rootid])]
        elif nodeid is not None:
            if isinstance(nodeid,(int,np.integer)): # only one item.
                nodelst = [nodeid]
            elif isinstance(nodeid,(list,np.ndarray)):
                nodelst = nodeid
            else:
                raise Exception("node_id must be array-like.")
        
        coors = np.array([[self.nodes[i].x,self.nodes[i].y,self.nodes[i].z] for i in nodelst])
        df = pd.DataFrame({'nodeid':nodelst,'x':coors[:,0],'y':coors[:,1],'z':coors[:,2]})
        df.set_index('nodeid',inplace=True)
        return df    
    
    def get_features(self,features=["x","y","z"],nodeid=None,rootid=None):
        """Return list of features from given nodes.
        
        Args:
            features (list of str): list of node-wise features, e.g. "x", "y", "z", "r", "structure_id", "connector_relation". If None, then return all features.
            nodes (int | list of int): list of node IDs. If None, then return the coordinates of all nodes from the given root ID.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            
        Returns:
            Pandas dataframe whose indices are node IDs and values are corresponding features.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if nodeid is None:
            nodelst = [node.name for node in PreOrderIter(self.nodes[_rootid])]
        elif nodeid is not None:
            if isinstance(nodeid,(int,np.integer)): # only one item.
                nodelst = [nodeid]
            elif isinstance(nodeid,(list,np.ndarray)):
                nodelst = nodeid
            else:
                raise Exception("node_id must be array-like.")
        
        feats = []
        for i in nodelst:
            node = self.nodes[i]
            feats.append([i]+[getattr(node,f) for f in features])
        feats = np.array(feats)
        column_names = ["nodeid"] + features
        df = pd.DataFrame(feats,columns=column_names)
        df.set_index('nodeid',inplace=True)
        return df

    def get_bbox(self,nodeid=None,rootid=None):
        """Return bounding box coordinates covering a list of nodes from the tree. 
        
        Args:
            nodeid (list[int]): list of node IDs. If None, then return bounding box of the entire tree.
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            List of [(Xmin,Xmax),(Ymin,Ymax),(Zmin,Zmax)]
        
        """
        coors = self.get_coordinates(nodeid,rootid)
        xmin, xmax = coors['x'].min(), coors['x'].max()
        ymin, ymax = coors['y'].min(), coors['y'].max()
        zmin, zmax = coors['z'].min(), coors['z'].max()
        return [(xmin,xmax),(ymin,ymax),(zmin,zmax)]
    
    def compute_length(self,nodeid=None,rootid=None):
        """Return the total length of the tree or subpart of the tree. 
        
        Args:
            nodeid (list[int]): list of node IDs. If None, then return the total length of the entire tree.
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            int.

        Notes:
            If you provide a list of nodes. We consider it as a curve, then we return the curve length.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,5.,5.,5.,1.,1]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot it
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)
                plt.tight_layout();

                # Total length of the entire neuron
                total_length = neuron.compute_length()
                print(total_length)

                # Get a segment from root to the first branching point
                segment_lst = neuron.decompose_segments()
                print(segment_lst)
                segment = segment_lst['0_1']

                # Length of that segment
                segment_length = neuron.compute_length(segment)
                print(segment_length)
        
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        if nodeid is not None: # a list of nodes
            return Curve(self.get_coordinates(nodeid).values).compute_length()
        else:
            segments = self.decompose_segments(_rootid)
            total_length = 0
            for seg in segments.values():
                total_length += Curve(self.get_coordinates(seg).values).compute_length()
            return total_length
    
    def compute_spine(self,rootid=None):
        """Return spine node IDs (longest branch from the root to a leaf).

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            list of int.
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        segments = self.decompose_leaves(_rootid)
        segment_lengths = [self.compute_length(seg) for seg in segments.values()]
        return list(segments.values())[np.argmax(segment_lengths)]
    
    def compute_strahler_order(self, nodeid=None, rootid=None):
        """Return Strahler order for given node IDs [1].
        
        Args:
            nodeid (int|list[int]): list of node IDs. If None, return all the Strahler order for all nodes from the given root ID.
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            Pandas serie whose indices are node IDs and values are corresponding strahler orders.

        References:
            ..  [1] https://en.wikipedia.org/wiki/Strahler_number
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        try:
            # check if strahler orders already computed
            _ = self.nodes[_rootid].strahler 
        except:
            preorder_lst = np.array([node.name for node in PreOrderIter(self.nodes[_rootid])])
            for i in preorder_lst[-1::-1]:
                n = self.nodes[i]
                if n.is_leaf:
                    n.strahler = 1
                else:
                    children_strahler = np.array([[k.name, k.strahler] for k in n.children])
                    if len(children_strahler)==1:
                        n.strahler = children_strahler[0,1]
                    else:
                        nbmax = len(np.argwhere(children_strahler[:,1]==np.max(children_strahler[:,1])).flatten())
                        if nbmax>=2:
                            n.strahler = np.max(children_strahler[:,1]) + 1
                        else:
                            n.strahler = np.max(children_strahler[:,1])

        if nodeid is None:
            nodelst = [node.name for node in PreOrderIter(self.nodes[_rootid])]
        elif nodeid is not None:
            if isinstance(nodeid,int): # only one item.
                nodelst = [nodeid]
            elif isinstance(nodeid,(list,np.ndarray)):
                nodelst = nodeid
            else:
                raise Exception("nodeid must be array-like.")
                
        strahler_orders = [self.nodes[i].strahler for i in nodelst]
        
        return pd.Series(strahler_orders,name='strahler_order',index=nodelst)
    
    # def compute_orientation(self,nodeid=None,nb_avg=1,rootid=None):
    #     """Compute orientation vectors at given nodes.
        
    #     The orientation vector depends on node type (e.g. root, branching node, leaf, normal node).
        
    #     Args:
    #         nodeid (int|array of int): list of node IDs.
    #         nb_avg (int): number of neighboring nodes used to average the orientation.     
    #     """
        
    #     # internal funcs
    #     def walk_to_parent(_nid,nb_steps,_rootid):
    #         target = _nid
    #         target_lst = []
    #         it = 0
    #         while(it < nb_steps):
    #             it = it + 1
    #             target = self.get_parent(target)
    #             if target is not None:
    #                 target_lst.append(target)
    #             else:
    #                 break
    #             if target in self.get_branchingnodes(_rootid):
    #                 break
    #         return target_lst
        
    #     def walk_to_children(_nid,nb_steps):
    #         target = [_nid]
    #         target_lst = []
    #         it = 0
    #         while(it < nb_steps):
    #             it = it + 1
    #             target = self.get_children(target[0])
    #             if len(target)==1:
    #                 target_lst.append(target[0])
    #             else:
    #                 break
    #         return target_lst
        
    #     if rootid is None:
    #         _rootid = self.get_root()[0]
    #     else:
    #         _rootid = rootid
        
    #     # get list of nodes
    #     if nodeid is None:
    #         nodeidlst = self.get_preorder_nodes(_rootid)
    #     elif isinstance(nodeid,(int,np.integer)):
    #         nodeidlst = [nodeid]
    #     else:
    #         nodeidlst = nodeid
            
    #     dic = {}
            
    #     for nid in nodeidlst:
    #         item = {}
    #         source_coors = self.get_coordinates(nid,_rootid).values.flatten()
            
    #         if nid==_rootid: # root
                
    #             # vectors toward children
    #             children = self.get_children(nid)
    #             for child in children:
    #                 target_lst = [child]
    #                 target_lst = target_lst + walk_to_children(child,nb_avg-1)
    #                 target_coors = self.get_coordinates(target_lst,_rootid).values
    #                 mean_target_coors = np.mean(target_coors,axis=0)
    #                 item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
            
    #         elif nid in self.get_branchingnodes(_rootid): # branchingnodes
                
    #             # vector toward parent
    #             target_lst = walk_to_parent(nid,nb_avg,_rootid)                
    #             target_coors = self.get_coordinates(target_lst,_rootid).values
    #             mean_target_coors = np.mean(target_coors,axis=0)
    #             item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
                
    #             # vectors toward children
    #             children = self.get_children(nid)
    #             for child in children:
    #                 target_lst = [child]
    #                 target_lst = target_lst + walk_to_children(child,nb_avg-1)
    #                 target_coors = self.get_coordinates(target_lst,_rootid).values
    #                 mean_target_coors = np.mean(target_coors,axis=0)
    #                 item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)
            
    #         else: # leaf or normal node
                
    #             # vector toward parent
    #             target_lst = walk_to_parent(nid,nb_avg,_rootid)                
    #             target_coors = self.get_coordinates(target_lst,_rootid).values
    #             mean_target_coors = np.mean(target_coors,axis=0)
    #             item[str(nid)+"-"+str(target_lst[0])] = geo.vector2points(source_coors,mean_target_coors)

    #         dic[nid] = item
        
    #     return dic
    
    def path(self,target,source=None,rootid=None):
        """Find list of nodes going from source node to target node.
        
        Args:
            target (int): target node ID.
            source (int): source node ID. If None, then we take root as the source.
            rootid (int): root node ID. If None, then the first rootid will be taken.

        Returns:
            list of traveled node IDs included source and target node IDs.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,5.,5.,5.,1.,1]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Get ID of a leaf
                leaf_node = neuron.get_leaves()[0]
                print(leaf_node)

                # Path from root to the leaf
                print(neuron.path(leaf_node))
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if source==None:
            source = _rootid
            
        w = Walker()
        res = w.walk(self.nodes[source],self.nodes[target])
        return [n.name for n in res[0]] + [res[1].name] + [n.name for n in res[2]] 
    
    def extract_subtrees(self,nodeid,to_children=True,separate_children=False,rootid=None):
        """Extract a sub tree from the given node.
        
        Args:
            nodeid (int): node ID from that we extract the subtree. It becomes new root node in the subtree.
            to_children (bool): if False, then extract upper subtree (toward parent). Otherwise, lower subtrees are extracted (toward children).
            separate_children (bool): if True, then each subtree is extracted for each child. This parameter only works when setting ``to_children = True``.
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            list of Tree objects.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot it
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)
                plt.tight_layout();

                # Get a branching node
                brnode = neuron.get_branchingnodes()[0]
                print(brnode)

                # Extract a subtree from the branching node toward its children
                subtree = neuron.extract_subtrees(brnode,to_children=True,separate_children=False)

                # Plot it
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                subtree.plot(ax)
                plt.tight_layout();

                # Extract list of subtress from the branching node toward its children
                # Each subtree is extracted from each child
                subtree_lst = neuron.extract_subtrees(brnode,to_children=True,separate_children=True)

                # Plot first subtree
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                subtree_lst[0].plot(ax)
                plt.tight_layout();

                # Plot second subtree
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                subtree_lst[1].plot(ax)
                plt.tight_layout();
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        # list of nodes to be extracted by default
        nodelst = [nodeid] + [item.name for item in self.nodes[nodeid].descendants]
        
        if to_children == False: # then, getting nodes above the nodeid, i.e. subtree toward root node.
            fullnodelst = [_rootid] + [item.name for item in self.nodes[_rootid].descendants]
            nodelst = np.setdiff1d(fullnodelst,nodelst)
            subnodes = {}
            # first copy node properties
            for nid in nodelst:
                ref_node = self.nodes[nid]
                new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                        connector_relation=ref_node.connector_relation,
                                        r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                        structure_id=ref_node.structure_id)
                subnodes[nid] = new_node
            # second assign node relationship
            for nid in nodelst:
                try:
                    parent_id = self.nodes[nid].parent.name
                    subnodes[nid].parent = subnodes[parent_id]
                except:
                    subnodes[nid].parent = None # root node
            
            # copynodes = copy.deepcopy(self.nodes) # dict copy
            # copynodes[nodeid].parent = None
            # subnodes = {nid:copynodes[nid] for nid in nodelst}
            
            return Tree(subnodes,self.id,self.name)
        
        else: # get nodes starting from nodeid, i.e. subtrees toward its children.
            if separate_children==True:
                mychildren = [item.name for item in self.nodes[nodeid].children]
                if len(mychildren)>1: # more than one children
                    data = []
                    for mychild in mychildren:
                        subnodelst = [nodeid, mychild] + [item.name for item in self.nodes[mychild].descendants]
                        subnodes = {}
                        # first copy node properties
                        for nid in subnodelst:
                            ref_node = self.nodes[nid]
                            new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                                    connector_relation=ref_node.connector_relation,
                                                    r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                                    structure_id=ref_node.structure_id)
                            subnodes[nid] = new_node  
                        # second assign node relationship
                        for nid in subnodelst:
                            if nid != nodeid:
                                parent_id = self.nodes[nid].parent.name
                                subnodes[nid].parent = subnodes[parent_id]
                            else:
                                subnodes[nid].parent = None # set nodeid as new root

                        # copynodes = copy.deepcopy(self.nodes) # dict copy
                        # others = np.setdiff1d(mychildren,mychild)
                        # for otherid in others:
                        #     copynodes[otherid].parent = None
                        # copynodes[nodeid].parent = None
                        # subnodes = {nid:copynodes[nid] for nid in subnodelst}
                        
                        data.append(Tree(subnodes,self.id,self.name))
                        
                    return data
            
            # in case of only one child
            subnodes = {}
            
            # first copy node properties
            for nid in nodelst:
                ref_node = self.nodes[nid]
                new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                        connector_relation=ref_node.connector_relation,
                                        r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                        structure_id=ref_node.structure_id)
                subnodes[nid] = new_node  
            # second assign node relationship
            for nid in nodelst:
                if nid != nodeid:
                    parent_id = self.nodes[nid].parent.name
                    subnodes[nid].parent = subnodes[parent_id]
                else:
                    subnodes[nid].parent = None
            
            # copynodes = copy.deepcopy(self.nodes) # dict copy
            # subnodes = {nid:copynodes[nid] for nid in nodelst}
            # subnodes[nodeid].parent = None       
            
            return Tree(subnodes,self.id,self.name) 
    
    def copy(self,rootid=None):
        """Make a copy of the tree.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.

        Returns:
            A Tree object.

        """
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        return self.extract_subtrees(nodeid=_rootid,rootid=_rootid)
    
    def prune_leaves(self,nodeid=None,length=None,rootid=None):
        """Prune leaf branches based on its length.
        
        Args:
            nodeid (list [int]): list of leaves IDs used to examine the pruning. If None, then take all leaves into account.
            length (float): length threshold for pruning the leaf branches from the leaves given by nodeid. If None, then we eliminate all the leaf branches.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            
        Returns:
            A new Tree object after pruning.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot it
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)
                plt.tight_layout();

                # Prune all the leaf branches
                neuron_pruned = neuron.prune_leaves()

                # Plot pruned tree
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron_pruned.plot(ax)
                plt.tight_layout();

                # Prune only leaf branches whose length < 5 microns
                neuron_pruned = neuron.prune_leaves(length=5)

                # Plot pruned tree
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron_pruned.plot(ax)
                plt.tight_layout();
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if length is None:
            _length = np.inf
        else:
            _length = length
        
        segments = self.decompose_segments(_rootid)
        
        if nodeid is None:
            leafnodes = self.get_leaves(_rootid)
        else:
            leafnodes = nodeid
        
        subnodes = {}
        nodelst = []
        
        for seg in segments.values():
            contain_leaf = (np.sum([leaf in seg for leaf in leafnodes])>=1)
            seg_len = self.compute_length(seg)
            if (~contain_leaf) | (contain_leaf & (seg_len >= _length)):
                # copy node properties
                for nid in seg:
                    if nid not in nodelst:
                        ref_node = self.nodes[nid]
                        new_node = anytree.Node(nid, connector_id=ref_node.connector_id, 
                                                connector_relation=ref_node.connector_relation,
                                                r=ref_node.r, x=ref_node.x, y=ref_node.y, z=ref_node.z,
                                                structure_id=ref_node.structure_id)
                        subnodes[nid] = new_node
                        nodelst.append(nid)
        
        # assign node relationship
        for nid in nodelst:
            try:
                parent_id = self.nodes[nid].parent.name
                subnodes[nid].parent = subnodes[parent_id]
            except:
                subnodes[nid].parent = None # root node
        
        return Tree(subnodes,self.id,self.name)

    
    def decompose_segments(self,rootid=None):
        """Decompose tree in segments separating by the branching nodes.

        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.            
        
        Returns:
            A dictionary whose each item is a decomposed segment, where
                - key is a string represents the first node and the last node of the decomposed segment.
                - value is a list of nodes IDs of the decomposed segment.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)

                # Plot node ID
                coors = neuron.get_coordinates()
                for nodeid in coors.index:
                    tmp = coors.loc[nodeid]
                    ax.text(tmp.x-0.5,tmp.y+0.1,tmp.z+0.1,nodeid,fontsize=12)

                ax.axis('off');
                plt.tight_layout();

                # Decompose into segments separating by branching nodes
                print(neuron.decompose_segments())

                # The output should be as follows:
                # {'2_4': [2, 4], '2_6': [2, 5, 6], '1_3': [1, 3], '0_1': [0, 1], '1_2': [1, 2]}                  
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        segments = {}
        controlnodes = self.get_leaves(_rootid) + self.get_branchingnodes(_rootid) + [_rootid]
        for it in range(len(controlnodes)):
            nodeid = controlnodes[it]
            branch = [n.name for n in self.nodes[nodeid].path]
            idx = len(branch)-2
            while(idx != -1):
                if branch[idx] in controlnodes:
                    subbranch = branch[idx:]
                    segments[str(branch[idx])+"_"+str(nodeid)] = subbranch
                    break
                idx = idx - 1
        
        return segments
    
    def decompose_leaves(self,rootid=None):
        """Decompose tree into segments starting from root to every leaf.
        
        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            A dictionary whose each item is a decomposed segment, where            
                - key is a string represents the leaf node of the decomposed segment.
                - value is a list of nodes IDs of the decomposed segment.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)

                # Plot node ID
                coors = neuron.get_coordinates()
                for nodeid in coors.index:
                    tmp = coors.loc[nodeid]
                    ax.text(tmp.x-0.5,tmp.y+0.1,tmp.z+0.1,nodeid,fontsize=12)

                ax.axis('off');
                plt.tight_layout();

                # Decompose into segments from root to every leaves
                print(neuron.decompose_leaves())

                # The output should be as follows:
                # {4: [0, 1, 2, 4], 6: [0, 1, 2, 5, 6], 3: [0, 1, 3]} 
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        dic = {}
        for leaf in self.get_leaves(_rootid):
            dic[leaf] = self.path(target=leaf,source=_rootid)
        
        return dic
    
    def decompose_spines(self,rootid=None):
        """Decompose tree into list of spines (longest branches) starting from the root node.

        We first extract the longest branch from the root to a leaf. 
        Then for every branching node on that longest branch, we extract the subtree from that, and repeat the process by extracting the longest branch of that subtree.
        The process is repeated until no branch can be extracted.
        
        Args:
            rootid (int): root node ID. If None, then the first rootid will be taken.
        
        Returns:
            A dictionary whose each item is a decomposed segment, where            
                - key is a string represents the first node and the last node of the decomposed segment.
                - value is a list of nodes IDs of the decomposed segment.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax)

                # Plot node ID
                coors = neuron.get_coordinates()
                for nodeid in coors.index:
                    tmp = coors.loc[nodeid]
                    ax.text(tmp.x-0.5,tmp.y+0.1,tmp.z+0.1,nodeid,fontsize=12)

                ax.axis('off');
                plt.tight_layout();

                # Decompose into segments of longest branches
                print(neuron.decompose_spines())

                # The output should be as follows:
                # {'0_6': [0, 1, 2, 5, 6], '1_3': [1, 3], '2_4': [2, 4]}
        
        """
        # maximal number of recursions using in deepcopy()
        # sys.setrecursionlimit(recursion_limit)
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        data = {}
        
        # first check if there're many branches at root
        mychildren = [item.name for item in self.nodes[_rootid].children]
        if len(mychildren)>1: # more than one children
            subtrees = self.extract_subtrees(nodeid=_rootid,separate_children=True,rootid=_rootid)
            for subtree in subtrees:
                subdata = subtree.decompose_spines()
                data = {**data, **subdata}
        else:
            spinenodes = self.compute_spine(_rootid)
            spinename = str(spinenodes[0])+'_'+str(spinenodes[-1])
            data[spinename] = spinenodes
            branchingnodes = self.get_branchingnodes(_rootid)
            if len(branchingnodes)!=0:
                spinebranchingnodes = list(filter(lambda node : node in spinenodes, branchingnodes))
                
                for node in spinebranchingnodes:
                    subtrees = self.extract_subtrees(nodeid=node,separate_children=True,rootid=_rootid)
                    for subtree in subtrees:
                        firstchild = subtree.nodes[node].children[0].name
                        if firstchild not in spinenodes:
                            subdata = subtree.decompose_spines()
                            data = {**data, **subdata}
                
        return data
    
    def resample(self,sampling_length=None,rootid=None,spline_order=1,spline_smoothness=0,decompose_method="branching"):
        """Resample the tree by a given sampling length. Spline interpolation is used for resampling.

        The tree is first decomposed into segments either by "branching" (``decompose_segments()``) or by "spine" (``decompose_spines()``).
        Then, each segment is resampled by the given sampling length.
        
        Args:
            sampling_length (float): sampling length. If None, then we resample the tree by the same number of nodes.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            spline_order (uint): Spline order. value of 1 means linear interpolation.
            spline_smoothness (float or None): Parameter to control the smoothness of spline interpolation. The parameter is similar to the ``s`` parameter from this [1].
            decompose_method (str): choose the mode of decomposition: "branching" or "spine".
            
        Returns:
            A new Tree object with resampled nodes.

        References:
            ..  [1] https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.splprep.html

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron, only showing the node points
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax,show_nodes=True,show_leaves=False,show_root=False,show_branchingnodes=False)

                print("Nb. of nodes before resampling:",neuron.get_number_nodes())

                # Resampling by sampling length = 1 micron
                neuron_resampled = neuron.resample(sampling_length=1)

                # Plot resampled neuron, only showing the node points
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron_resampled.plot(ax,show_nodes=True,show_leaves=False,show_root=False,show_branchingnodes=False)

                print("Nb. of nodes after resampling:",neuron_resampled.get_number_nodes())
        
        """
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        branching_nodes = self.get_branchingnodes(_rootid)
        
        newnodes = {} # new resampled nodes
        
        # TODO: smatter handling of ID (e.g. remove ancient IDs, new_ID_generator reuse free ancient IDs)
        nodeid_max = max(self.nodes.keys()) # for now new node ID is counted from old maximal ID
        newnodeid = nodeid_max + 1
        
        if decompose_method=="branching":
            segments = self.decompose_segments(rootid=_rootid)
        elif decompose_method=="spine":
            segments = self.decompose_spines(rootid=_rootid)
            brnode_link = [] # contain link between branching node and new closest resampled node.
        else:
            raise Exception("accept only 'branching' or 'spine' decomposition")
        
        for seg in segments.values():
            # print(seg)
            try:
                # get segment coordinates
                coors = self.get_coordinates(seg,rootid).values

                # try to remove duplicates before interpolation
                _, uix = np.unique(coors,axis=0,return_index=True)
                unique_coors = coors[np.sort(uix)]
                unique_seg = np.array(seg)[np.sort(uix)]
                
                # # interpolate coordinates
                # if spline_smoothness==True:
                #     s = None
                # else:
                #     s = 0
                    
                if unique_coors.shape[0]<(spline_order+1): # linear interpolation
                    coefcoors, to = interpolate.splprep(unique_coors.T.tolist(),k=1,s=spline_smoothness)
                else:
                    coefcoors, to = interpolate.splprep(unique_coors.T.tolist(),k=spline_order,s=spline_smoothness)

                # interpolate radius
                r = [self.nodes[nodeid].r for nodeid in unique_seg]
                coefr = interpolate.splrep(to,r,k=1,s=0)
            except:
                return None
                
                # # print("ok");
                # # simply copy nodes to new nodes
                # for i in range(len(seg)):
                #     if seg[i] not in newnodes.keys():
                #         node = self.nodes[seg[i]]
                #         newnodes[seg[i]] = anytree.Node(seg[i],connector_id=node.connector_id, 
                #                                         connector_relation=node.connector_relation, r=node.r, 
                #                                         x=node.x, y=node.y, z=node.z, structure_id=node.structure_id)
                #     if i != 0:
                #         newnodes[seg[i]].parent = newnodes[seg[i-1]]

                # continue # go to next segment

            # in case of success interpolation
            if sampling_length == None:
                n = len(seg)
            else:
                n = max(int(np.round(self.compute_length(unique_seg)/sampling_length)),2) + 1 # new sampled points, must have at least 2 points
            tn = np.linspace(0,1,n)
            xn, yn, zn = interpolate.splev(tn,coefcoors)
            rn = interpolate.splev(tn,coefr)
            
            # in case of spine decomposition
            if decompose_method=="spine":
                newix_flag = np.ones(len(tn))*-1
                # newix_supp = []
                for node in branching_nodes:
                    # index start from "1" not "0" since we don't consider branching node at begin.
                    idx = np.argwhere(node==np.array(unique_seg)[1:]).flatten()
                    if len(idx)!=0:
                        oldix = idx[0]+1
                        newix = np.argwhere(tn<to[oldix]).flatten()[-1]
                        newix_flag[newix] = node
                        # newix_supp.append([node,oldix,to[oldix],newix,tn[newix]])
                    
            # print(newix_flag)
            # print(newix_supp)

            # add two end nodes to newnodes
            for iseg in [unique_seg[-1],unique_seg[0]]:
                if iseg not in newnodes.keys():
                    node = self.nodes[iseg]
                    newnodes[iseg] = anytree.Node(iseg,connector_id=node.connector_id,
                                                  connector_relation=node.connector_relation,
                                                  r=node.r, x=node.x, y=node.y, z=node.z, structure_id=node.structure_id)

            # add resampled nodes and link to parent
            check_node = newnodes[unique_seg[-1]]   
            i = n - 2
            while i != -1:
   
                if i == 0:
                    if decompose_method=="spine":
                        if newix_flag[i]!=-1:
                            brnode_link.append([int(newix_flag[i]),unique_seg[0]])
                    
                    new_node = newnodes[unique_seg[0]]
                else:
                    if decompose_method=="spine":
                        if newix_flag[i]!=-1:
                            brnode_link.append([int(newix_flag[i]),newnodeid])
                    
                    
                    new_node = anytree.Node(newnodeid, connector_id=-1, connector_relation='None',
                                            r=rn[i], x=xn[i], y=yn[i], z=zn[i], structure_id=0)
                    
                    newnodes[newnodeid] = new_node
                    # if (newnodeid==696):
                    #     print(unique_seg)

                check_node.parent = new_node

                check_node = new_node
                newnodeid = newnodeid + 1
                i = i - 1

        if decompose_method=="spine":
            for link in brnode_link:
               mychildren = [item.name for item in newnodes[link[0]].children]
               try:
                   for mychild in mychildren:
                       newnodes[mychild].parent = newnodes[link[1]]
               except:
                   print(link)
                   print(mychildren)
                   print(newnodes[link[1]])
                   raise Exception("failed, segment {}".format(unique_seg))
                   
            for brnode in branching_nodes:
                if((brnode != _rootid) & (newnodes[brnode].parent == None)):
                    del newnodes[brnode]
        
        # new resampled neuron
        return Tree(newnodes) 
    
    def compute_angles(self,decomposed_method="branching",sigma=0,rootid=None):
        """Return angle of each tree node.

        The tree is decomposed into segments. Then, the angle of node N is the angle between two vectors (N => N-1) and (N => N+1).
        One node can have multiple angle values depending on the decomposition mode.
        
        Args:
            decomposed_method (str): "leaf", "spine" or "branching", method for decomposing the neuronal trace.
            sigma (float): sigma used in Gaussian function for smoothing the tree branches.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            
        Returns:
            Pandas dataframe containing angles at every nodes.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron, only showing the node points
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax,show_nodes=True,show_leaves=False,show_root=False,show_branchingnodes=False)

                # Plot node ID
                coors = neuron.get_coordinates()
                for nodeid in coors.index:
                    tmp = coors.loc[nodeid]
                    ax.text(tmp.x-0.5,tmp.y+0.1,tmp.z+0.1,nodeid,fontsize=12)

                plt.tight_layout();

                # Compute the node angles with x, y and z axes
                # The default decomposition is "branching"
                neuron.compute_angle()

        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        nodeid_lst, segkey_lst = [],[]
        # vecx_lst, vecy_lst, vecz_lst = [], [], []
        # thetax_lst, thetay_lst, thetaz_lst = [], [], []
        thetas_lst = []
        
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():
            
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # smooth if need
            if sigma > 0:
                crv = crv.convolve_gaussian(sigma)
                
            thetas = crv.compute_angles()
            thetas_lst = thetas_lst + thetas.tolist()
            
            # vecx_lst = vecx_lst + vecs[:,0].tolist()
            # vecy_lst = vecy_lst + vecs[:,1].tolist()
            # vecz_lst = vecz_lst + vecs[:,2].tolist()
            
            # thetax_lst = thetax_lst + thetas[:,0].tolist()
            # thetay_lst = thetay_lst + thetas[:,1].tolist()
            # thetaz_lst = thetaz_lst + thetas[:,2].tolist()
            
        # making dataframe
        df = pd.DataFrame({"seg_key":segkey_lst,
                           "nodeid":nodeid_lst,                           
                           "theta":thetas_lst})
        
        df.set_index(["seg_key","nodeid"],inplace=True)            
        return df
    
    def compute_angles_vector(self,decomposed_method="branching",sigma=0,rootid=None):
        """Return angles of each tree node with x, y and z axes.

        Angle at at a node N is the angle between vector (N => N + 1) and three unit vectors of x, y and z axes.
        The tree is decomposed into segments. Then, the angles of nodes on each segment are computed.
        One node can have multiple angle values depending on the decomposition mode.
        
        Args:
            decomposed_method (str): "leaf", "spine" or "branching", method for decomposing the neuronal trace.
            sigma (float): sigma used in Gaussian function for smoothing the tree branches.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            
        Returns:
            Pandas dataframe containing angles at every nodes.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Plot neuron, only showing the node points
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax,show_nodes=True,show_leaves=False,show_root=False,show_branchingnodes=False)

                # Plot node ID
                coors = neuron.get_coordinates()
                for nodeid in coors.index:
                    tmp = coors.loc[nodeid]
                    ax.text(tmp.x-0.5,tmp.y+0.1,tmp.z+0.1,nodeid,fontsize=12)

                plt.tight_layout();

                # Compute the node angles with x, y and z axes
                # The default decomposition is "branching"
                neuron.compute_angle_axes()

        """

        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
            
        nodeid_lst, segkey_lst = [],[]
        vecx_lst, vecy_lst, vecz_lst = [], [], []
        thetax_lst, thetay_lst, thetaz_lst = [], [], []
        
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():
            
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # smooth if need
            if sigma > 0:
                crv = crv.convolve_gaussian(sigma)
                
            thetas = crv.compute_angles_vector()
            
            thetax_lst = thetax_lst + thetas[:,0].tolist()
            thetay_lst = thetay_lst + thetas[:,1].tolist()
            thetaz_lst = thetaz_lst + thetas[:,2].tolist()
            
        # making dataframe
        df = pd.DataFrame({"seg_key":segkey_lst,
                           "nodeid":nodeid_lst,
                           "thetax":thetax_lst,
                           "thetay":thetay_lst,
                           "thetaz":thetaz_lst})
        
        df.set_index(["seg_key","nodeid"],inplace=True)            
        return df 
    
    def compute_local_3d_scale_sigma(self,sig_lst,dim_param=None,decomposed_method="leaf",rootid=None,postprocess='mean'):
        """Compute local 3d scale of neuron from a list of sigma of Gaussian.

        The tree is decomposed into segments. Then, local 3d scale is computed for each segment.
        Each segment is considered as a Curve object. Please see ``compute_local_3d_scale_sigma()`` from ``Curve`` class for more detail.
        One node can have multiple local 3d scales due to the decomposition. You can specify the ``postprocess`` to return e.g. the mean local 3d scale of the node.
        
        Args:
            sig_lst (list of float): list of sigma values of Gaussian.
            dim_param (dic): parameters for dimension decomposition. If None, default parameters are used. See parameters of ``compute_local_3d_scale_sigma()`` from ``Curve`` class for the meaning.
            decomposed_method (str): "leaf", "spine" or "branching", method for decomposing the neuronal tree.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            postprocess (str): support "mean", "std", "max", "min" or None.
            
        Returns:
            Pandas dataframe containing local 3D scale and additional information: 1D, 2D, 3D flags, curvature and torsion.

        Notes:
            If ``postprocess = None``, then a Pandas dataframe containing local 3d scale and additional features (curvature, torsion, etc) of each decomposed segment is returned.
            Otherwise, a Pandas serie containing only the local 3d scale of each node is returned.

        Examples:
            ..  code-block:: python

                import pandas as pd
                from genepy3d.obj import trees
                import matplotlib.pyplot as plt

                # Generate a dummy nodes data
                data = [[0,0,0.,0.,0.,1.,-1],
                        [1,0,1.,2.,3.,1.,0],
                        [2,0,4.,5.,6.,1.,1],
                        [3,0,7.,2.,2.,1.,1],
                        [4,0,6.,6.,6.,1.,2],
                        [5,0,3.,7.,6.,1.,2],
                        [6,0,5.,5.,9.,1.,5]]

                # Dataframe from nodes data
                node_tbl = pd.DataFrame(data,columns=['treenode_id','structure_id','x','y','z','r','parent_treenode_id'])

                # Create a dummy neuron from node_tbl
                neuron = trees.Tree.from_table(node_tbl)

                # Resample the neuron with sampling length = 1 simply to get more points
                neuron = neuron.resample(sampling_length=1)

                # Plot neuron, only showing the node points
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax,show_nodes=True,show_leaves=False,show_root=False,show_branchingnodes=False)
                plt.tight_layout();

                # Averaged local 3D scale of each node for sigma from 0 => 100
                l3ds_tbl = neuron.compute_local_3d_scale_sigma(sig_lst=np.arange(100),postprocess='mean');

                # Plot neuron whose nodes are colored by the local 3d scale
                fig = plt.figure()
                ax = fig.add_subplot(111,projection='3d')
                neuron.plot(ax,weights=l3ds_tbl,
                            show_cbar=True,point_args={"cmap":"rainbow"},
                            show_nodes=False,show_leaves=False,show_root=False,show_branchingnodes=False)
                plt.tight_layout();
        
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        nodeid_lst, ls_lst, plane_line_lst, line_lst, threed_lst = [], [], [], [], []
        curvature_lst, torsion_lst = [], []
        segkey_lst = []
    
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():

            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # intrinsic dimension decomposition
            try:
                if dim_param is not None:
                    dim_param["return_dim_results"] = True
                    ls_res, intrinsic_res = crv.compute_local_3d_scale_sigma(sig_lst,**dim_param)
                else: # use default params
                    ls_res, intrinsic_res = crv.compute_local_3d_scale_sigma(sig_lst,return_dim_results=True)
            except:
                raise Exception(seg)
    
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # curvature and torsion
            curvature_lst += crv.compute_curvature().tolist()
            torsion_lst += crv.compute_torsion().tolist()
    
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # local 3D scale
            ls_lst = ls_lst + list(ls_res)
    
    #         if(len(np.argwhere(np.array(ls_res)>=70).flatten())==len(ls_res)):
    #             print(seg)
    
            # 1D, 2D, 3D flags
            pl_flag = np.zeros((len(seg),len(sig_lst)))
            l_flag = np.zeros((len(seg),len(sig_lst)))
            for i in range(len(sig_lst)):
                res = intrinsic_res[i]
                for plids in res["planeline_pred"]:
                    pl_flag[plids[0]:plids[1]+1,i]=1.
                for lids in res["line_pred"]:
                    l_flag[lids[0]:lids[1]+1,i]=1.
            threed_flag = (pl_flag + np.ones(pl_flag.shape))%2 # xor bit (3D is the opposite of planeline)
    
            plane_line_lst = plane_line_lst + pl_flag.tolist()
            line_lst = line_lst + l_flag.tolist()
            threed_lst = threed_lst + threed_flag.tolist()
        
        # making dataframe
        df = pd.DataFrame({"nodeid":nodeid_lst,
                           "seg_key":segkey_lst, 
                           "local_scale":ls_lst,
                           "plane_line_flag":plane_line_lst,
                           "line_flag":line_lst,
                           "threed_flag":threed_lst,
                           "curvature":curvature_lst,"torsion":torsion_lst})
        
    #     df.drop_duplicates("nodeid",keep=False) # drop branching nodes
        df.set_index("nodeid",inplace=True)       

        if postprocess == "mean":
            return df.groupby("nodeid")['local_scale'].mean()
        elif postprocess == "std":
            return df.groupby("nodeid")['local_scale'].std()
        elif postprocess == "min":
            return df.groupby("nodeid")['local_scale'].min()
        elif postprocess == "max":
            return df.groupby("nodeid")['local_scale'].max()
        else:
            return df
    
    def compute_local_3d_scale_radius(self,r_lst,dim_param=None,decomposed_method="leaf",rootid=None,postprocess='mean'):
        """Compute local 3d scale of neuron from a list of radius of curvatures. 
        
        This is the advanced approach to compute the local 3d scale. Please see this [1] for more detail.        

        The tree is decomposed into segments. Then, local 3d scale is computed for each segment.
        Each segment is considered as a Curve object. Please see ``compute_local_3d_scale_radius()`` from ``Curve`` class for more detail.
        One node can have multiple local 3d scales due to the decomposition. You can specify the ``postprocess`` to return e.g. the mean local 3d scale of the node.
        
        Args:
            r_lst (list of float): list of radius of curvatures. The radius must be > 0.
            dim_param (dic): parameters for dimension decomposition. If None, default parameters are used. See parameters of ``compute_local_3d_scale_radius()`` from ``Curve`` class for the meaning.
            decomposed_method (str): "leaf", "spine" or "branching", method for decomposing the neuronal tree.
            rootid (int): root node ID. If None, then the first rootid will be taken.
            postprocess (str): support "mean", "std", "max", "min" or None.
            
        Returns:
            Pandas dataframe containing local 3D scale and additional information: 1D, 2D, 3D flags, curvature and torsion.

        Notes:
            -   If ``postprocess = None``, then a Pandas dataframe containing local 3d scale and additional features (curvature, torsion, etc) of each decomposed segment is returned. Otherwise, a Pandas serie containing only the local 3d scale of each node is returned.
            -   Running this method is much longer than ``compute_local_3d_scale_sigma()``.

        References:
            ..  [1] Phan MS, Matho K, Beaurepaire E, Livet J, Chessel A.
                    nAdder: A scale-space approach for the 3D analysis of neuronal traces. 2022.
                    PLOS Computational Biology 18(7): e1010211. DOI: 10.1371/journal.pcbi.1010211
                
        """
        
        from genepy3d.obj.curves import Curve
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        nodeid_lst, ls_lst, plane_line_lst, line_lst, threed_lst = [], [], [], [], []
        curvature_lst, torsion_lst = [], []
        segkey_lst = []
    
        # decompose tree into segments
        if decomposed_method=="spine":
            segments = self.decompose_spines(_rootid)
        elif decomposed_method=="leaf":
            segments = self.decompose_leaves(_rootid)
        else:
            segments = self.decompose_segments(_rootid)
        
        for key,seg in segments.items():

            # create curve
            coors = self.get_coordinates(seg).values
            crv = Curve(coors)
            
            # intrinsic dimension decomposition
            try:
                if dim_param is not None:
                    dim_param["return_dim_results"] = True
                    ls_res, intrinsic_res = crv.compute_local_3d_scale_radius(r_lst,**dim_param)
                else: # use default params
                    ls_res, intrinsic_res = crv.compute_local_3d_scale_radius(r_lst,return_dim_results=True)
            except:
                raise Exception(seg)
    
            # save segment keys
            segkey_lst += [key for _ in range(len(seg))]
            
            # curvature and torsion
            curvature_lst += crv.compute_curvature().tolist()
            torsion_lst += crv.compute_torsion().tolist()
    
            # save node IDs
            nodeid_lst = nodeid_lst + list(seg)
            
            # local 3D scale
            ls_lst = ls_lst + list(ls_res)
    
    #         if(len(np.argwhere(np.array(ls_res)>=70).flatten())==len(ls_res)):
    #             print(seg)
    
            # 1D, 2D, 3D flags
            pl_flag = np.zeros((len(seg),len(r_lst)))
            l_flag = np.zeros((len(seg),len(r_lst)))
            for i in range(len(r_lst)):
                res = intrinsic_res[i]
                for plids in res["planeline_pred"]:
                    pl_flag[plids[0]:plids[1]+1,i]=1.
                for lids in res["line_pred"]:
                    l_flag[lids[0]:lids[1]+1,i]=1.
            threed_flag = (pl_flag + np.ones(pl_flag.shape))%2 # xor bit (3D is the opposite of planeline)
    
            plane_line_lst = plane_line_lst + pl_flag.tolist()
            line_lst = line_lst + l_flag.tolist()
            threed_lst = threed_lst + threed_flag.tolist()
        
        # making dataframe
        df = pd.DataFrame({"nodeid":nodeid_lst,
                           "seg_key":segkey_lst, 
                           "local_scale":ls_lst,
                           "plane_line_flag":plane_line_lst,
                           "line_flag":line_lst,
                           "threed_flag":threed_lst,
                           "curvature":curvature_lst,"torsion":torsion_lst})
        
    #     df.drop_duplicates("nodeid",keep=False) # drop branching nodes
        df.set_index("nodeid",inplace=True)            
        
        if postprocess == "mean":
            return df.groupby("nodeid")['local_scale'].mean()
        elif postprocess == "std":
            return df.groupby("nodeid")['local_scale'].std()
        elif postprocess == "min":
            return df.groupby("nodeid")['local_scale'].min()
        elif postprocess == "max":
            return df.groupby("nodeid")['local_scale'].max()
        else:
            return df

    # def compute_local_3d_scale(self,r_lst,dim_param=None,decomposed_method="leaf",rootid=None):
    #     """Compute 3d local scale of neuron.
        
    #     This function is **DEPRECATED**. Use compute_local_3d_scale_radius().
        
    #     Args:
    #         r_lst (list): list of scales (radius of curvature)
    #         dim_param (dic): parameters for dimension decomposition
    #         decomposed_method (str): "leaf", "spine" or "branching", method for cutting neuronal trace
    #         rootid (int): ID of root
            
    #     Returns:
    #         Pandas dataframe containing local 3D scale, 1D, 2D, 3D flags, curvature and torsion
        
    #     """
        
    #     from genepy3d.obj.curves import Curve
        
    #     if rootid is None:
    #         _rootid = self.get_root()[0]
    #     else:
    #         _rootid = rootid
        
    #     nodeid_lst, ls_lst, plane_line_lst, line_lst, threed_lst = [], [], [], [], []
    #     curvature_lst, torsion_lst = [], []
    #     segkey_lst = []
    
    #     # decompose tree into segments
    #     if decomposed_method=="spine":
    #         segments = self.decompose_spines(_rootid)
    #     elif decomposed_method=="leaf":
    #         segments = self.decompose_leaves(_rootid)
    #     else:
    #         segments = self.decompose_segments(_rootid)
        
    #     for key,seg in segments.items():

    #         # create curve
    #         coors = self.get_coordinates(seg).values
    #         crv = Curve(coors)
            
    #         # intrinsic dimension decomposition
    #         try:
    #             if dim_param is not None:
    #                 ls_res, intrinsic_res = crv.compute_local_3d_scale(r_lst,
    #                                                                    dim_param["eps_seg_len"],
    #                                                                    dim_param["eps_crv_len"],
    #                                                                    dim_param["sig_step"],
    #                                                                    dim_param["eps_kappa"],
    #                                                                    dim_param["eps_tau"],
    #                                                                    return_dim_results=True)
    #             else: # use default params
    #                 ls_res, intrinsic_res = crv.compute_local_3d_scale(r_lst,return_dim_results=True)
    #         except:
    #             raise Exception(seg)
    
    #         # save segment keys
    #         segkey_lst += [key for _ in range(len(seg))]
            
    #         # curvature and torsion
    #         curvature_lst += crv.compute_curvature().tolist()
    #         torsion_lst += crv.compute_torsion().tolist()
    
    #         # save node IDs
    #         nodeid_lst = nodeid_lst + list(seg)
            
    #         # local 3D scale
    #         ls_lst = ls_lst + list(ls_res)
    
    # #         if(len(np.argwhere(np.array(ls_res)>=70).flatten())==len(ls_res)):
    # #             print(seg)
    
    #         # 1D, 2D, 3D flags
    #         pl_flag = np.zeros((len(seg),len(r_lst)))
    #         l_flag = np.zeros((len(seg),len(r_lst)))
    #         for i in range(len(r_lst)):
    #             res = intrinsic_res[i]
    #             for plids in res["planeline_pred"]:
    #                 pl_flag[plids[0]:plids[1]+1,i]=1.
    #             for lids in res["line_pred"]:
    #                 l_flag[lids[0]:lids[1]+1,i]=1.
    #         threed_flag = (pl_flag + np.ones(pl_flag.shape))%2 # xor bit (3D is the opposite of planeline)
    
    #         plane_line_lst = plane_line_lst + pl_flag.tolist()
    #         line_lst = line_lst + l_flag.tolist()
    #         threed_lst = threed_lst + threed_flag.tolist()
        
    #     # making dataframe
    #     df = pd.DataFrame({"nodeid":nodeid_lst,
    #                        "seg_key":segkey_lst, 
    #                        "local_scale":ls_lst,
    #                        "plane_line_flag":plane_line_lst,
    #                        "line_flag":line_lst,
    #                        "threed_flag":threed_lst,
    #                        "curvature":curvature_lst,"torsion":torsion_lst})
        
    # #     df.drop_duplicates("nodeid",keep=False) # drop branching nodes
    #     df.set_index("nodeid",inplace=True)            
    #     return df
    
    def summary(self):
        """Return a brief summary of the tree.
        
        Returns:
            A Pandas Serie contains
                - number of nodes
                - number of leaves
                - number of branching nodes
                - number of connectors
        
        """
        
        index = ['id',
                 'name',
                 'root',
                 'nb_nodes',
                 'nb_leaves',
                 'nb_branchingnodes',
                 'nb_connectors']
        
        data = [self.id,
                self.name,
                self.get_root(),
                [len(self.get_preorder_nodes(_rootid)) for _rootid in self.get_root()],
                # len(list(PreOrderIter(self.nodes[self.get_root()]))),
                [len(self.get_leaves(_rootid)) for _rootid in self.get_root()],
                [len(self.get_branchingnodes(_rootid)) for _rootid in self.get_root()],
                [len(self.get_connectors(_rootid)) for _rootid in self.get_root()]]
        
        return pd.Series(data,index=index)
    
    def to_curve(self,nodeid=None):
        """Convert a segment of tree given by the list of node ID to a Curve object.

        Args:
            nodeid (list of int): List of node ID. If None, then consider all nodes of the tree.

        Returns:
            A Curve object.

        """
        from genepy3d.obj.curves import Curve
        return Curve(self.get_coordinates(nodeid).values)
    
    def to_points(self,nodeid=None):
        """Convert a segment of tree given by the list of node ID to a Points object.

        Args:
            nodeid (list of int): List of node ID. If None, then consider all nodes of the tree.

        Returns:
            A Points object.

        """
        
        from genepy3d.obj.points import Points
        return Points(self.get_coordinates(nodeid).values)
    
    def plot(self,ax,projection='3d',rootid=None,spine_only=False,
             show_root=True,show_leaves=True,show_branchingnodes=True,show_connectors=True,show_nodes=False,
             root_args={},leaves_args={},branchingnodes_args={},connectors_args={},
             weights=None,weights_display_type="c",point_args = {},show_cbar=False,cbar_args={},
             line_args={},scales=(1.,1.,1.),equal_axis=True):
        """Plot tree using matplotlib.
        
        Args:
            ax: plot axis.
            projection (str): we support *3d, xy, xz, yz* modes.
            spine_only (bool): if True, then only plot tree spine.
            show_root (bool): if True, then display root node.
            show_leaves (bool): if True, then display leaves nodes.
            show_branchingnodes (bool): if True, then display branching nodes.
            show_connectors (bool): if True, then display connector nodes.
            show_nodes (bool): if True, then display all nodes.
            root_args (dic): plot params for root node.
            leaves_args (dic): plot params for leaves nodes.
            branchingnodes_args (dic): plot params for branching nodes.
            connectors_args (dic): plot params for connectors nodes.
            weights (pandas serie): serie indexed by node ID and contains corresponding weights
            weights_display_type (str): "s" for point size or "c" for point color.
            point_args (dic): point plot params.
            line_args (dic): line plot params.
            scales (tuple of float): use to set x, y and z scales.
            equal_axis (bool): fix equal axes.
        
        """
        
        _root_args={'s':50,'c':'red'}
        for key,val in root_args.items():
            _root_args[key] = val
        
        _leaves_args={'s':8,'c':'blue'}
        for key,val in leaves_args.items():
            _leaves_args[key] = val
        
        _branchingnodes_args={'s':20,'c':'magenta'}
        for key,val in branchingnodes_args.items():
            _branchingnodes_args[key] = val
        
        _connectors_args={'s':70,'c':'red','alpha':0.7}
        for key,val in connectors_args.items():
            _connectors_args[key] = val
        
        _point_args = {"s":10,"alpha":0.8,"c":"k","cmap":"viridis"}
        for key,val in point_args.items():
            _point_args[key] = val
        
        _line_args={'alpha':0.8,'c':'k'}
        for key,val in line_args.items():
            _line_args[key] = val
        
        if rootid is None:
            _rootid = self.get_root()[0]
        else:
            _rootid = rootid
        
        if show_root==True:
            coors = self.get_coordinates(_rootid).values
            x, y, z = coors[:,0], coors[:,1], coors[:,2]
            pl.plot_point(ax,projection,x,y,z,scales,_root_args)
        
        if show_nodes==True:
            coors = self.get_coordinates().values
            x, y, z = coors[:,0], coors[:,1], coors[:,2]
            pl.plot_point(ax,projection,x,y,z,scales,_point_args)
            
        if spine_only==True:
            
            spine_nodes = self.compute_spine(_rootid)
            
            coors = self.get_coordinates(spine_nodes).values
            x, y, z = coors[:,0], coors[:,1], coors[:,2]
            pl.plot_line(ax,projection,x,y,z,scales,_line_args)
            
            if weights is not None:
                weight_args = _point_args.copy()
                weight_args[weights_display_type] = weights.loc[spine_nodes]
                if "vmin" not in weight_args.keys():
                    weight_args["vmin"] = weights.min()
                if "vmax" not in weight_args.keys():
                    weight_args["vmax"] = weights.max()
                plo = pl.plot_point(ax,projection,x,y,z,scales,weight_args)
                if (show_cbar == True):
                    if "shrink" in cbar_args:
                        shrink = cbar_args["shrink"]
                    else:
                        shrink = 0.7
                    cbar = ax.figure.colorbar(plo,shrink=shrink)
                    
                    if "ticks" in cbar_args:
                        cbar.set_ticks(cbar_args["ticks"])
                    if "ticklabels" in cbar_args:
                        cbar.set_ticklabels(cbar_args["ticklabels"])
            
            if show_leaves==True:
                coors = self.get_coordinates(spine_nodes[-1]).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                pl.plot_point(ax,projection,x,y,z,scales,_leaves_args)
        
        else:
            
            segments = self.decompose_segments(_rootid)
            cbar_flag = True
            for seg_nodes in segments.values():
                coors = self.get_coordinates(seg_nodes).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                segment_args = _line_args.copy()
                
                pl.plot_line(ax,projection,x,y,z,scales,segment_args)
                
                if weights is not None:
                    weight_args = _point_args.copy()
                    weight_args[weights_display_type] = weights.loc[seg_nodes]
                    if "vmin" not in weight_args.keys():
                        weight_args["vmin"] = weights.min()
                    if "vmax" not in weight_args.keys():
                        weight_args["vmax"] = weights.max()
                    plo = pl.plot_point(ax,projection,x,y,z,scales,weight_args)
                    if (show_cbar == True) & (cbar_flag == True):
                        if "shrink" in cbar_args:
                            shrink = cbar_args["shrink"]
                        else:
                            shrink = 0.7
                        cbar = ax.figure.colorbar(plo,shrink=shrink)
                        
                        if "ticks" in cbar_args:
                            cbar.set_ticks(cbar_args["ticks"])
                        if "ticklabels" in cbar_args:
                            cbar.set_ticklabels(cbar_args["ticklabels"]);
                        cbar_flag = False
            
            if show_leaves==True:
                leaves_nodes = self.get_leaves(_rootid)
                coors = self.get_coordinates(leaves_nodes).values
                x, y, z = coors[:,0], coors[:,1], coors[:,2]
                pl.plot_point(ax,projection,x,y,z,scales,_leaves_args)
                
            if show_branchingnodes==True:
                inter_nodes = self.get_branchingnodes(_rootid)
                if len(inter_nodes)!=0:
                    coors = self.get_coordinates(inter_nodes).values
                    x, y, z = coors[:,0], coors[:,1], coors[:,2]
                    pl.plot_point(ax,projection,x,y,z,scales,_branchingnodes_args)
                    
            if show_connectors==True:
                connectors_nodes = self.get_connectors(_rootid).index.values
                if len(connectors_nodes)!=0:
                    coors = self.get_coordinates(connectors_nodes).values
                    x, y, z = coors[:,0], coors[:,1], coors[:,2]
                    pl.plot_point(ax,projection,x,y,z,scales,_connectors_args)
                
        if equal_axis==True:
            if projection != '3d':
                ax.axis('equal')
            else:
                param = pl.fix_equal_axis(self.get_coordinates(rootid=_rootid).values / np.array(scales))
                ax.set_xlim(param['xmin'],param['xmax'])
                ax.set_ylim(param['ymin'],param['ymax'])
                ax.set_zlim(param['zmin'],param['zmax'])
                
        if projection != '3d':
            if projection=='xy':
                xlbl, ylbl = 'X', 'Y'
            elif projection=='xz':
                xlbl, ylbl = 'X', 'Z'
            else:
                xlbl, ylbl = 'Y', 'Z'
            ax.set_xlabel(xlbl)
            ax.set_ylabel(ylbl)
        else:
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            

    
                
            
            
            
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
