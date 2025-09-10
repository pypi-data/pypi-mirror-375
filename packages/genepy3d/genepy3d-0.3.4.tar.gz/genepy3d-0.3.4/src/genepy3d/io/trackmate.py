"""This module supports reading tracked file from `TrackMate <https://imagej.net/plugins/trackmate/>`_.
"""

import pandas as pd
import numpy as np
from genepy3d.objext.simpletracks import SimpleTrack

def read_spots(filepath):
    """Read tracked spots table exported from TrackMate.

    Args:
        filepath (str): path to the csv file.

    Returns:
        Spots object.

    """

    spotsdf = pd.read_csv(filepath)
    spotsdf = spotsdf.iloc[3:] # remove first 3 usefuless rows
    spotsdf.columns = [str.lower(col) for col in spotsdf.columns] # convert column names to lowercase
    del spotsdf['label'] # remove label column 
    spotsdf = spotsdf.apply(pd.to_numeric) # convert data to numeric type

    return Spots(spotsdf)

class Spots:
    """Handle tracked spots table.

    Attributes:
        spots (dataframe): Spots table.
        trackid_lst (numpy array): list of trackid from the Spots table.
        nb_tracks (int): number of tracks.

    Notes:
        The spots table must be imported from ``trackmate.read_spots()``.

    Examples:
        ..  code-block:: python

            import numpy as np
            from genepy3d.io import trackmate

            # Csv file of spots table from Trackmate
            spots = trackmate.read_spots("path/to/spots/csv/file")

    """

    def __init__(self,spotsdf):
        self.spots = spotsdf
        self.trackid_lst = spotsdf['track_id'].unique()
        self.nb_tracks = len(self.trackid_lst)

    def tracks_nb_spots(self,ascending=False):
        """Return number of spots per track.

        Args:
            ascending (bool): if True, sort by ascending order.
        Returns:
            A Pandas series index by trackid.

        """
        return self.spots.groupby("track_id")['id'].count().sort_values(ascending=ascending)
    
    def get_tracks(self,trackid_lst,return_type="simpletrack",x_col="position_x",y_col="position_y",z_col="position_z",t_col="frame"):
        """Return tracks data given by trackid_lst.

        Support two returns: "dataframe" as a Pandas dataframe and "simpletrack" as ``SimpleTrack`` objects.

        Args:
            trackid_lst (numpy array or int): a single trackid or list of trackid.
            return_type (str): if "dataframe" then return a Pandas dataframe, if "simpletrack" then return ``SimpleTrack`` objects.
            x_col (str): x column name.
            y_col (str): y column name.
            z_col (str): z column name.
            t_col (str): time column name.
        
        Returns:
            A Pandas dataframe or SimpleTrack objects depend on condition.

        Notes:
            The parameters `x_col`, `y_col`, `z_col` and `t_col` are only needed if return_type = "simpletrack".

        """

        if isinstance(trackid_lst,(int,np.integer)):
            trackid_lst_new = np.array([trackid_lst])
        else:
            trackid_lst_new = trackid_lst

        if return_type == "dataframe":
            tracks = self.spots[self.spots["track_id"].isin(trackid_lst_new)].copy()
            return tracks
        elif return_type == "simpletrack":
            simtrack_lst = []
            for trackid in trackid_lst_new:
                track = self.spots[self.spots["track_id"]==trackid].copy()
                track.sort_values("frame",inplace=True)
                coors = track[[x_col,y_col,z_col]].values
                t = track[t_col].values
                new_traj = SimpleTrack(coors,t)
                if np.sum(coors[:,2])==0: # 2D trajectories
                    new_traj.dim = 2
                else:
                    new_traj.dim = 3
                simtrack_lst.append(new_traj)
            if len(simtrack_lst)==1:
                return simtrack_lst[0] # no need to return list if only one item.
            else:
                return simtrack_lst
        else:
            raise Exception("return_type must be either 'dataframe' or 'simpletrack'.")
    
    def remove_tracks(self,trackid_lst_excluded):
        """Remove tracks from the table.

        Args:
            trackid_lst_excluded (numpy array): list of trackids to be removed.

        Returns:
            Itself. Tracks with given trackids will be removed from the spots table.

        """

        new_trackid_lst = np.setdiff1d(self.trackid_lst,trackid_lst_excluded)
        self.trackid_lst = new_trackid_lst
        self.nb_tracks = len(new_trackid_lst)

        spots = self.spots
        spots = spots[spots['track_id'].isin(new_trackid_lst)]
        self.spots = spots # maybe no need this line

    

    



