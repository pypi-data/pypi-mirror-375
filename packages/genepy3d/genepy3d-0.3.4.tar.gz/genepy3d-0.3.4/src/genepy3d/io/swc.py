import os
import glob
import fnmatch
import numpy as np
import pandas as pd

from genepy3d.obj import trees

class SWC:
    """Support reading neuron data from swc files [1].
    
    References:
        ..  [1] http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html
    
    """
    
    def __init__(self,filepath,recursive=False):
        
        filelst = [] # file with full path
        neuronnamelst = [] # file name
        
        # check input
        if os.path.isdir(filepath): # if directory
            
            if recursive==False:
                filepattern = os.path.join(filepath,"*.swc")
                for file in glob.glob(filepattern):
                    neuronnamelst.append(os.path.basename(file).split(".swc")[0])
                    filelst.append(file)
            
            else: # searching recursively from the parent directory
                for root, dirnames, filenames in os.walk(filepath):
                    for file in fnmatch.filter(filenames, '*.swc'):
                        neuronnamelst.append(os.path.basename(file).split(".swc")[0])
                        filelst.append(os.path.join(root,file))
        
        elif os.path.isfile(filepath): # if a file
            neuronnamelst.append(os.path.basename(filepath).split(".swc")[0])
            filelst.append(filepath)
        
        else:  
            raise ValueError("do not support special files (socket, FIFO, device file).")
            
        self.filelst = filelst
        self.neuronidlst = range(len(filelst))
        self.neuronnamelst = neuronnamelst
        
    def get_neuron_id(self):
        """Return neuron IDs.
        
        Returns:
            A pandas serie of (name,id).
        
        """
        
        return pd.Series(self.neuronidlst,index=self.neuronnamelst)
    
    def get_neurons(self,neuron_id=None):
        """Return list of neurons (Tree object) identified by IDs.
        
        Returns:
            A dictionary where key is the neuron ID and value is the Tree object.
                
        """
        
        # check neuron_id
        if neuron_id is None:
            neuronlst = range(len(self.filelst))
        else:
            if isinstance(neuron_id,(int,np.integer)): # only one item.
                neuronlst = [neuron_id]
            elif isinstance(neuron_id, (list, np.ndarray)): # array-like
                neuronlst = neuron_id
            else:
                raise Exception('neuron_id must be int or array-like.')
        
        dic = {}
        
        
        for i in neuronlst:
            file = self.filelst[i]
            # filename = self.neuronnamelst[i]
            fileid = self.neuronidlst[i]
            dic[fileid] = trees.Tree.from_swc(file)
            
        if len(neuronlst)==1: # only 1 item
            return list(dic.values())[0]
        else:
            return dic
            
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    