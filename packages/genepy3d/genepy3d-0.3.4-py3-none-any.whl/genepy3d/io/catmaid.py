import requests
import numpy as np
import pandas as pd

from genepy3d.io.base import CatmaidApiTokenAuth
from genepy3d.obj import trees

class Catmaid:
    """Support reading neuron data from Catmaid [1].
    
    Attributes:
        dfneu (pandas dataframe): neuron table.
        dfcon (pandas dataframe): connector table.

    References:
        ..  [1] https://catmaid.readthedocs.io/en/stable/index.html
    
    """
    
    def _assign_dfneu(self,dfneu):
        """Check and assign neuron data to class attribute.
        """
        if dfneu is None:
            raise Exception("need to provide neuron table.") 
        # remove nan
        dfneu.dropna(inplace=True)
        # cast type
        dfneu['neuron_id'] = dfneu['neuron_id'].astype('int')
        dfneu['treenode_id'] = dfneu['treenode_id'].astype('int')
        dfneu['structure_id'] = dfneu['structure_id'].astype('int')
        dfneu['parent_treenode_id'] = dfneu['parent_treenode_id'].astype('int')
        self.dfneu = dfneu
        
    def _assign_dfcon(self,dfcon):
        """Check and assign connector data to class attribute.
        """
        if dfcon is None:
            self.dfcon = None
        # remove nan
        dfcon.dropna(inplace=True) # drop invalid rows
        # constraint columns to int
        dfcon['connector_id'] = dfcon['connector_id'].astype('int')
        dfcon['neuron_id'] = dfcon['neuron_id'].astype('int')
        dfcon['treenode_id'] = dfcon['treenode_id'].astype('int')
        self.dfcon = dfcon
        
    def _compute_dfsyn(self):
        """Compute synaptic relationship from connector data.
        """
        if self.dfcon is not None:
            # getting synapse detail
            syninfo = []
            
            conidlist = self.dfcon['connector_id'].unique()
            for conid in conidlist:
                pre = self.dfcon[(self.dfcon['connector_id']==conid)&(self.dfcon['relation_id']=='presynaptic_to')][['neuron_id','treenode_id']].values.tolist()
                posts = self.dfcon[(self.dfcon['connector_id']==conid)&(self.dfcon['relation_id']=='postsynaptic_to')][['neuron_id','treenode_id']].values.tolist()
                
                if len(pre)==0:
                    continue
                elif len(pre)>1:
                    raise ValueError('unknown situation: multiple presynaptic_to')
                    break
                else:
                    if len(posts)==0:
                        continue
                    else:
                        for post in posts:
                            syninfo.append(pre[0]+post)
        
            # check syninfo
            if len(syninfo)==0:
                self.dfsyn = None
            else:
                self.dfsyn = pd.DataFrame(syninfo,columns=['pre_neuron_id','pre_treenode_id','post_neuron_id','post_treenode_id'])
    
    def __init__(self,dfneu,dfcon=None):
        self._assign_dfneu(dfneu)
        self._assign_dfcon(dfcon)
        self._compute_dfsyn()
    
    @classmethod
    def from_csv(cls, neuronfile, confile=None):
        """Read neuron data from Catmaid csv files.
        
        Args:
            neuronfile (str): path to neuron csv file.
            confile (str): path to connector csv file.   

        Returns:
            Catmaid object.   
        
        """
        
        # read neuronfile
        try:
            dfneu = pd.read_csv(neuronfile)
        except:
            raise Exception('Failed to load neuron file.')
        
        labels = dfneu.columns.values
        refined_labels = []
        for lbl in labels:
            refined_labels.append(lbl.split()[0].lower()) # extract all column names, remove irregular characters
        if all(lbl in refined_labels for lbl in ['neuron_name','neuron_id','treenode_id','structure_id','x','y','z','r','parent_treenode_id']):
            dfneu.columns = refined_labels
            dfneu = dfneu[['neuron_name','neuron_id','treenode_id','structure_id','x','y','z','r','parent_treenode_id']] # select only conventional columns
        
        elif all(lbl in refined_labels for lbl in ['neuron','skeleton_id','treenode_id','parent_treenode_id','x','y','z','r']):
            dfneu.columns = refined_labels
            dfneu['structure_id'] = 0 # add structure_id column
            dfneu.rename(columns={'neuron':'neuron_name','skeleton_id':'neuron_id'},inplace=True) # rename following the convention
            dfneu = dfneu[['neuron_name','neuron_id','treenode_id','structure_id','x','y','z','r','parent_treenode_id']] # select only conventional columns
            dfneu['parent_treenode_id'].fillna(-1,inplace=True) # replace NaN by -1
        else:
            raise ValueError("The file must contain columns 'neuron','skeleton_id','treenode_id','parent_treenode_id','x','y','z','r'.")
        
        # read connector file
        dfcon = None
        if confile is not None:
            try:
                dfcon = pd.read_csv(confile)
            except:
                raise Exception ('Failed to load connector file.')
            
            labels = dfcon.columns.values
            refined_labels = []
            for lbl in labels:
                refined_labels.append(lbl.split()[0].lower())
            if all(lbl in refined_labels for lbl in ['connector_id','neuron_id','treenode_id','relation_id']):
                dfcon.columns = refined_labels
                dfcon = dfcon[['connector_id','neuron_id','treenode_id','relation_id']]
            elif all(lbl in refined_labels for lbl in ['connector_id','skeleton_id','treenode_id','relation_id']):
                dfcon.columns = refined_labels
                dfcon.rename(columns={'skeleton_id':'neuron_id'},inplace=True) # rename some columns
                dfcon = dfcon[['connector_id','neuron_id','treenode_id','relation_id']]
            else:
                raise ValueError("The file must contain columns 'connector_id','skeleton_id','treenode_id','relation_id'.")

        return cls(dfneu,dfcon)
            
    @staticmethod
    def get_neuron_id_from_server(host,token,project_id):
        """Return list of neuron IDs from given project ID.
        
        Args:
            host (str): address of CATMAID server.
            token (str): authenticated string.
            project_id (int): project ID.
            
        Returns:
            array of int.
        
        """

        # restful request
        linkrequest = host+'{}/skeletons/'.format(project_id)
        res = requests.get(linkrequest,auth=CatmaidApiTokenAuth(token))
        
        if res.status_code!=200:
            raise ValueError('something wrong: check again your host, token or project id.')
        else:
            if isinstance(res.json(),dict):
                raise ValueError('something wrong: check again your project id.')
            else: # should be a list
                return np.array(res.json())
    
    @classmethod
    def from_server(cls,host,token,project_id,neuron_id=None):
        """Import neuron data from Catmaid server.
        
        Args:
            host (str): Catmaid host address.
            token (str): authentication token.
            project_id (int): project ID.
            neuron_id (int|list of int): list of neuron IDs.

        Returns:
            Catmaid object.
        
        """
        
        if neuron_id is None:
            neuronlst = cls.get_neuron_id_from_server(host,token,project_id)
        elif isinstance(neuron_id,(int,np.integer)):
            neuronlst = [neuron_id]
        else:
            neuronlst = neuron_id
        
        neuinfo, coninfo = [], []
        
        # query data from catmaid
        for neuid in neuronlst:
            
            linkrequest = host+'{}/skeleton/{}/json'.format(project_id,neuid)
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
        #                neuname = res[0].encode('ascii','ignore') # hdf5 does not support unicode
                        neuname = res[0]
                    except:
                        neuname = 'genepy3d'
                    
                    subneu, subcon = [], []
                    
                    # get neuron info
                    try:
                        for iske in res[1]:
                            if iske[1] is not None:
                                iske_sub = [neuname, neuid, iske[0], 0, iske[3], iske[4], iske[5], iske[6], iske[1]]
                            else:
                                iske_sub = [neuname, neuid, iske[0], 0, iske[3], iske[4], iske[5], iske[6], -1]
                            subneu.append(iske_sub)
                    except:
                        subneu = []
                    
                    # get connector info
                    try:
                        for icon in res[3]:
                            relation_type = 'presynaptic_to'
                            if icon[2]==1:
                                relation_type = 'postsynaptic_to'
                            icon_sub = [icon[1], neuid, icon[0], relation_type]
                            subcon.append(icon_sub)
                    except:
                        subcon = []
                    
                    neuinfo = neuinfo + subneu
                    coninfo = coninfo + subcon
                
        # create dataframe from data
        if len(neuinfo)==0:
            raise Exception("neuron table is empty.")
        else:
            dfneu = pd.DataFrame(neuinfo,columns=['neuron_name','neuron_id','treenode_id','structure_id','x','y','z','r','parent_treenode_id'])
        
        if len(coninfo)==0:
            dfcon = None
        else:
            dfcon = pd.DataFrame(coninfo,columns=['connector_id','neuron_id','treenode_id','relation_id'])
            
        return cls(dfneu,dfcon)
    
    def get_neuron_id(self,neuron_name=None):
        """Return neuron IDs from neuron names.
        
        Args:
            neuron_name (str | array of str): list of neuron names.
 
        Returns:
            pandas Series whose index is name and value is ID.
        
        """
        
        if neuron_name is None:
            subdf = self.dfneu[['neuron_id','neuron_name']].drop_duplicates().copy() # get all neuron ids
            subdf.set_index("neuron_name",inplace=True)
            return subdf
        else:
            if isinstance(neuron_name,str): # only one neuron name
                try:
                    subdf = self.dfneu[self.dfneu['neuron_name']==neuron_name][['neuron_id','neuron_name']].drop_duplicates().copy()
                    subdf.set_index("neuron_name",inplace=True)
                    return subdf
                except:
                    return None
            else: 
                try:
                    subdf = self.dfneu[self.dfneu['neuron_name'].isin(neuron_name)][['neuron_id','neuron_name']].drop_duplicates().copy()
                    subdf.set_index("neuron_name",inplace=True)
                    return subdf
                except:
                    return None
    
    def get_neuron_name(self,neuron_id=None):
        """Return neuron names from neuron IDs.
        
        Args:
            neuron_id (int | array of int): list of neuron names.
 
        Returns:
            pandas Series whose index is ID and value is name.
        
        """
        
        if neuron_id is None:
            subdf = self.dfneu[['neuron_id','neuron_name']].drop_duplicates().copy() # get all neuron ids
            subdf.set_index("neuron_id",inplace=True)
            return subdf
        else:
            if isinstance(neuron_id,(int,np.integer)): # only one neuron name
                try:
                    subdf = self.dfneu[self.dfneu['neuron_id']==neuron_id][['neuron_id','neuron_name']].drop_duplicates().copy()
                    subdf.set_index("neuron_id",inplace=True)
                    return subdf
                except:
                    return None
            else: 
                try:
                    subdf = self.dfneu[self.dfneu['neuron_id'].isin(neuron_id)][['neuron_id','neuron_name']].drop_duplicates().copy()
                    subdf.set_index("neuron_id",inplace=True)
                    return subdf
                except:
                    return None
    
    def get_synaptic_relation(self,relation_id="presynaptic_to",nb_connectors=1):
        """Return neurons and corresponding treenodes filtered by their synaptic relations.
        
        A neuron can have multiple presynaptic gates (for receiving signals from others neurons),
        and only one postsynaptic gate (for sending signal).
        
        Args:
            relation_id (str): presynaptic_to or postsynaptic_to.
            nb_connectors (uint): number of connectors. If None, then return all neurons regardess their number of connectors.
        
        Returns:
            Dictionary whose keys are neuron_id, values are treenode_ids.
        
        """
        
        subdf = self.dfcon[self.dfcon['relation_id']==relation_id].copy()
        subdf_counts = subdf.groupby(['neuron_id'])['treenode_id'].count()
        dic = {}
        if nb_connectors is None:
            neulst = subdf_counts.index.values
        else:
            neulst = subdf_counts[subdf_counts==nb_connectors].index.values
        
        for neuron_id in neulst:
            dic[neuron_id] = list(subdf[subdf["neuron_id"]==neuron_id]["treenode_id"].values)
        
        return dic
        
    def get_innervation_relation(self,nb_innervations=1):
        """Return neurons filtered by innervation relation.
        
        Innervation: a neuron receives signals from one (mono) or many (multi) other neurons via its presynaptic gates.
        We assume innervated neuron as postsynaptic neuron, the ones who make innervation are presynaptic neurons.
                
        Args:
            nb_innervations (int): number innervated presynaptic neurons. If None, then return all neurons.
            
        Returns:
            dictionary whose key is postsynaptic neuron, value is innervating presynaptic neurons.
        
        """
        
        dic = {}
        
        if self.dfsyn is not None:
            subdf = self.dfsyn.sort_values(['post_neuron_id'])
            subdf_counts = subdf.groupby(['post_neuron_id'])['pre_neuron_id'].count()
            if nb_innervations is None:
                neulst = subdf_counts.index.values
            else:
                neulst = subdf_counts[subdf_counts==nb_innervations].index.values
            for neuron_id in neulst:
                dic[neuron_id] = subdf[subdf["post_neuron_id"]==neuron_id][["pre_neuron_id","pre_treenode_id"]].values.tolist()
        
        return dic
    
    def get_neurons(self,neuron_id=None,scales=(1.,1.,1.)):
        """Return neurons (Tree object) of a given list of neuron IDs.
        
        Args:
            neuron_id (int | array of int): list of neuron IDs.
            scales (tuple (float)): define x, y, z scales
        
        Returns:
            list of neurons (``tree.Tree``)
            
        """
        
        # check neuron_id
        if neuron_id is None:
            neuronlst = self.get_neuron_id().values.flatten()
        else:
            if isinstance(neuron_id,(int,np.integer)): # only one item.
                neuronlst = [neuron_id]
            elif isinstance(neuron_id, (list, np.ndarray)): # array-like
                neuronlst = neuron_id
            else:
                raise Exception('neuron_id must be int or array-like.')
                
        dic = {}
        for neuid in neuronlst:
            
            subdfneu = self.dfneu[self.dfneu['neuron_id']==neuid].copy()
            if len(subdfneu)==0:
                raise ValueError("check again neuron id.")
            else:
                neuname = self.get_neuron_name(neuid).values.flatten()[0]
                
                subdfcon = None
                if self.dfcon is not None:
                    subdfcon = self.dfcon[self.dfcon['neuron_id']==neuid].copy()
                    if len(subdfcon)==0:
                        subdfcon = None
                        
                # scale x, y and z
                subdfneu["x"] = subdfneu["x"]*scales[0]
                subdfneu["y"] = subdfneu["y"]*scales[1]
                subdfneu["z"] = subdfneu["z"]*scales[2]
                
                dic[neuid] = trees.Tree.from_table(subdfneu,subdfcon,neuid,neuname)
                
        if len(neuronlst)==1: #only 1 tiem
            return dic[neuid]
        else:
            return dic
    
    def to_csv(self,neuron_file="dfneu.csv",connector_file="dfcon.csv",neuron_id=None):
        """Export the neuron table and connector table into csv files.

        We can extract for a subset of neuron given by ``neuron_id``.

        Args:
            neuron_file (str): file path to save the neuron table.
            connector_file (str): file path to save the connector table.
            neuron_id (list of int): list of neuron IDs to be exported. If None, then all neurons were exported.            

        """
        
        if neuron_id is None:
            neulst = self.get_neuron_id().values.flatten()
        elif isinstance(neuron_id,(int,np.integer)):
            neulst = [neuron_id]
        else:
            neulst = neuron_id
        
        conidlst = self.dfcon[self.dfcon["neuron_id"].isin(neulst)]["connector_id"].unique()
        subdfcon = self.dfcon[self.dfcon["connector_id"].isin(conidlst)].copy()
        fullneulst = subdfcon["neuron_id"].unique()
        subdfneu = self.dfneu[self.dfneu["neuron_id"].isin(fullneulst)].copy()
        
        try:
            subdfneu.to_csv(neuron_file)
            subdfcon.to_csv(connector_file)
        except:
            raise Exception("Fail when exporting to csv.")

















































    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
