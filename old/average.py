import numpy as np


def azimuth(angles, azimuth=True):
    """ numpy version of above"""
    rads = np.deg2rad(angles)
    av_sin = np.mean(np.sin(rads))
    av_cos = np.mean(np.cos(rads))
    ang_rad = np.arctan2(av_sin, av_cos)
    ang_deg = np.rad2deg(ang_rad)
    # if azimuth:
    #     ang_deg = np.mod(ang_deg, 360.)

    # return ang_rad, ang_deg
    return np.mod(ang_deg, 360.)
