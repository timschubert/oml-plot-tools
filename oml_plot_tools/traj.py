#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is a part of IoT-LAB oml-plot-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""
usage: plot_oml_traj [-h] [-i DATA] [-c CIRCUIT] [-m MAP_INFOS] [-l TITLE]
                     [-b BEGIN] [-e END] [-t] [-a] [-ti]

Plot iot-lab trajectory oml files

optional arguments:
  -h, --help            show this help message and exit
  -i DATA, --input DATA
                        Robot trajectory values
  -c CIRCUIT, --circuit CIRCUIT
                        Robot circuit file
  -m MAP_INFOS, --maps MAP_INFOS
                        Map and elements
  -l TITLE, --label TITLE
                        Graph title
  -b BEGIN, --begin BEGIN
                        Sample start
  -e END, --end END     Sample end

plot:
  Plot selection

  -t, --traj            Plot robot trajectory
  -a, --angle           Plot robot angle
  -ti, --time           Plot time verification
"""


import os
import sys
import argparse
# Issues with numpy and matplotlib.cm
# pylint:disable=no-member
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from collections import namedtuple

from . import common

# http://stackoverflow.com/a/26605247/395687
# pip install --no-index -f http://dist.plone.org/thirdparty/ -U PIL
# or 'apt-get install python-imaging'
from PIL import Image
import csv

import json
import matplotlib.patches as patches


MEASURES_D = common.measures_dict(
    ('x', float, 'X'),
    ('y', float, 'Y'),
    ('theta', float, 'yaw angle (rad)'),
)

Deco = namedtuple('Deco', ['marker', 'color', 'size', 'x', 'y'])
Map = namedtuple('Map', ['marker', 'file', 'ratio', 'sizex', 'sizey',
                         'offsetx', 'offsety'])


def oml_load(filename):
    """ Load consumption oml file """
    data = common.oml_load(filename, 'robot_pose', MEASURES_D.values())
    return data


def maps_load(filename):
    """ Load iot-lab om file

    Parameters:
    ------------
    filename: string
              filename

    Returns:
    -------
    data_map : numpy array
    ['f' 'filename' ratio sizex sizey ofx ofy]

    data_deco : numpy array
    [[mark color size x y] [mark1 color1 size1 x1 y1]...]

    """
    map_dir = os.path.dirname(filename)

    try:
        datafile = open(filename, 'r')
        datareader = csv.reader(datafile, delimiter=' ')
        # Skip empty lines and comments
        rows = (d for d in datareader if len(d) and d[0] != '#')
    except IOError as err:
        sys.stderr.write("Error opening map file:\n{0}\n".format(err))
        sys.exit(2)
    except (ValueError, StopIteration) as err:
        sys.stderr.write("Error reading map file:\n{0}\n".format(err))
        sys.exit(3)

    # Search if there is a map and split with other elements (data_deco)
    sitemap = None
    data_deco = []

    for row in rows:
        # float conversion for rows 2 to -1
        for index in range(2, len(row)):
            row[index] = float(row[index])

        if row[0] == 'f':  # map file
            row[1] = os.path.join(map_dir, row[1])
            sitemap = Map(*row)
        else:  # firts column is marker for printing
            data_deco.append(Deco(*row))

    # Rescale, noop if map is None
    decos = []
    for ditem in data_deco:
        posx, posy = scale_with_map(ditem.x, ditem.y, sitemap)
        dec = ditem._replace(x=posx, y=posy)  # pylint:disable=protected-access
        decos.append(dec)

    return sitemap, decos


def circuit_load(filename):
    """ Load robot circuit file

    Parameters:
    ------------
    filename: string
              filename

    Returns:
    -------
    circuit: json object
    {
       "coordinates": [
       {
         "name": "0",
         "x": 9.5036359876481,
         "y": -0.8644077467101,
         "z": 0,
         "w": -2.4504422620417
       },
       {
         "name": "1",
         "x": 0.88773354001121,
         "y": 9.750401138047,
         "z": 0,
         "w": 0.46435151843117
       }
      ],
      "points":[
                "0",
                "1"
      ]
    }
    """

    with open(filename, 'rb') as json_file:
        return json.load(json_file)


PARSER = argparse.ArgumentParser(
    prog='plot_oml_traj', description="Plot iot-lab trajectory oml files")
PARSER.add_argument('-i', '--input', dest='data', type=oml_load,
                    help="Robot trajectory values")
PARSER.add_argument('-c', '--circuit', dest='circuit', type=circuit_load,
                    help="Robot circuit file")
PARSER.add_argument('-m', '--maps', dest='map_infos', type=maps_load,
                    default=(None, ()), help="Map and elements")

PARSER.add_argument('-l', '--label', dest='title', default="Robot",
                    help="Graph title")
PARSER.add_argument('-b', '--begin', default=0, type=int, help="Sample start")
PARSER.add_argument('-e', '--end', default=-1, type=int, help="Sample end")

_PLOT = PARSER.add_argument_group('plot', "Plot selection")
_PLOT.add_argument('-t', '--traj', dest='plot', const='traj',
                   action='append_const', help="Plot robot trajectory")
_PLOT.add_argument('-a', '--angle', dest='plot', const='angle',
                   action='append_const', help="Plot robot angle")
_PLOT.add_argument('-ti', '--time', dest='plot', const='time',
                   action='append_const', help="Plot time verification")


def trajectory_plot(data, title,  # pylint:disable=too-many-arguments
                    decos, img_map, circuit, selection):
    """ Plot trajectories infos """

    if 'traj' in selection:
        oml_plot_map(data, title, decos, img_map, circuit)

    # Figure angle initialization
    if 'angle' in selection:
        oml_plot_angle(data, title)

    # Clock verification
    if 'time' in selection:
        common.oml_plot_clock(data)

    try:
        plt.tight_layout()
    except ValueError:
        pass
    plt.show()


def scale_with_map(posx, posy, sitemap=None):
    """ Scale `posx` and `posy` with `sitemap` scaling informations """
    if sitemap is None:
        return posx, posy
    scaled_x = (posx - sitemap.offsetx) / sitemap.ratio
    scaled_y = sitemap.sizey - (posy - sitemap.offsety) / sitemap.ratio
    return scaled_x, scaled_y


def scale_points_with_map(coordinates, sitemap):
    """ Scale circuit coordinates with `sitemap` scaling informations """
    checkpoints = []
    for coord in coordinates:
        point = scale_with_map(coord['x'], coord['y'], sitemap)
        checkpoints.append(point)
    return checkpoints


def oml_plot_angle(data, title, xlabel=common.TIMESTAMP_LABEL):
    """ Plot data 'angel' field """
    ylabel = MEASURES_D['theta'].label
    title = '%s %s' % (title, 'angle')

    plt.figure()
    plt.title(title)
    plt.grid()
    plt.plot(data['timestamp'], data['theta'])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def oml_plot_map(data, title, decos, sitemap,  # pylint:disable=too-many-locals
                 circuit=None):
    """ Plot iot-lab oml data

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    title: string
       title of the plot
    decos: array
       [marker, color, size,  x, y]
       for marker see http://matplotlib.org/api/markers_api.html
       for color  see http://matplotlib.org/api/colors_api.html
    sitemap: array (size 1)
       [marker, filename_img, ratio, sizex, sizey]
       plot point item for trajectory with filename_img in background
    circuit:
       TODO
    """

    if not (sitemap or decos or data or circuit):
        return  # nothing to graph
    # Figure trajectory initialization
    circuit_fig = plt.figure()
    plt.title(title + ' trajectory')
    plt.grid()

    # Plot map image in background
    if sitemap:
        try:
            image = Image.open(sitemap.file).convert("L")
        except IOError as err:
            sys.stderr.write("Cannot open image map file:\n{0}\n".format(err))
            sys.exit(2)
        arr = np.asarray(image)
        plt.imshow(arr, cmap=cm.Greys_r)

    # Plot elements for decoration
    for deco in decos:
        plt.scatter(deco.x, deco.y, marker=deco.marker,
                    color=deco.color, s=deco.size)

    # Plot robot trajectory
    if data is not None:
        data_x, data_y = scale_with_map(data['x'], data['y'], sitemap)
        unit = 'm' if sitemap else 'pixels'  # scaled or not

        plt.plot(data_x, data_y)
        plt.xlabel('X (%s)' % unit)
        plt.ylabel('Y (%s)' % unit)

    # Plot circuit
    if circuit is not None:
        checkpoints = scale_points_with_map(circuit['coordinates'], sitemap)

        checkpoint_lines = patches.Polygon(checkpoints, linestyle='dashed',
                                           linewidth=2, edgecolor='red',
                                           fill=False)
        a_x = circuit_fig.add_subplot(111)
        a_x.add_patch(checkpoint_lines)
        coord_x = [c[0] for c in checkpoints]
        coord_y = [c[1] for c in checkpoints]
        plt.plot(coord_x, coord_y, 'ro')

    return


def main():  # pylint:disable=too-many-statements
    """ Main command """
    opts = PARSER.parse_args()
    # default to plot traj/map
    selection = opts.plot or ('traj')
    # select samples
    data = opts.data[opts.begin:opts.end] if opts.data else None
    map_img, map_decos = opts.map_infos

    trajectory_plot(data, opts.title, map_decos, map_img,
                    opts.circuit, selection)


if __name__ == "__main__":
    main()
