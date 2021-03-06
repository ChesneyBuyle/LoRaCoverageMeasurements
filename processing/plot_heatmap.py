"""
    ____  ____      _    __  __  ____ ___
   |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
   | | | | |_) |  / _ \ | |\/| | |  | | | |
   | |_| |  _ <  / ___ \| |  | | |__| |_| |
   |____/|_| \_\/_/   \_\_|  |_|\____\___/
                             research group
                               dramco.be/

    KU Leuven - Technology Campus Gent,
    Gebroeders De Smetstraat 1,
    B-9000 Gent, Belgium

           File: plt_heatmap.py
        Created: 2018-10-26
         Author: Gilles Callebaut
        Version: 1.0
    Description:
"""

import json
import math
import os

import folium
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from folium.map import Marker
from folium.plugins import HeatMap, MarkerCluster

import util as util

PLOT_SNR = True
PLOT_RSS = not PLOT_SNR

RSS_SERIES = "rssi"
SNR_SERIES = "snr"
LAT_SERIES = "lat"
LON_SERIES = "lon"
LAT_GRID_SERIES = "lat_discrete"
LON_GRID_SERIES = "lon_discrete"

CENTER = [51.0606959, 3.7070895]

#HEADER = ["time", "sat", "satValid", "hdopVal", "hdopValid", "vdopVal", "pdopVal", "lat", "lon", "locValid", "age", "ageValid", "alt","altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError",  "sf", "isPacket"]

HEADER = ["time", "sat", "satValid", "hdopVal", "hdopValid", "lat", "lon", "locValid", "age", "ageValid", "alt",
          "altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError",  "sf", "isPacket"]

currentDir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.abspath(os.path.join(
    currentDir, '..', 'data', "PACKETS.TXT"))
output_file_name = "heatmap_SNR.html" if PLOT_SNR else "heatmap_RSS.html"
output_file = os.path.abspath(os.path.join(
    currentDir, '..', 'result', output_file_name))

grid_size = 25

for_map = pd.read_csv(data_file, sep=',', header=None,
                      names=HEADER)

for_map = util.sort(for_map)
print(for_map)

for_map_gps = for_map.copy()

for_map = for_map[for_map.isPacket > 0]


util.addDistanceTo(for_map, CENTER)
util.addPathLossTo(for_map)

print(for_map)

for_map.plot.scatter(x='distance', y='pl_db', c='sf',  colormap='viridis')
plt.show()


max_lat = for_map[LAT_SERIES].max()
max_lon = for_map[LON_SERIES].max()

min_lat = for_map[LAT_SERIES].min()
min_lon = for_map[LON_SERIES].min()


hmap = folium.Map(location=CENTER, zoom_start=18, )  # tiles="Stamen Toner")


folium.Circle(
    radius=1,
    location=CENTER,
    color='crimson',
    fill=True,
    fill_color='crimson'
).add_to(hmap)


grid, colormap = util.get_geojson_grid(
    for_map, grid_size, PLOT_SNR)
hmap.add_child(colormap)

for i, geo_json in enumerate(grid):
    gj = folium.GeoJson(geo_json,
                        style_function=lambda feature: {
                            'fillColor': colormap(feature["properties"]["val"]),
                            'weight': 1,
                            'opacity': 0,
                            'fillOpacity': 0.55 if feature["properties"]["show"] else 0,
                            'color': 'white'
                        }, overlay=True)

    hmap.add_child(gj)

folium.PolyLine(list(zip(for_map_gps.lat.values, for_map_gps.lon.values)),
                color="red", weight=2, opacity=0.4).add_to(hmap)

hmap.save(output_file)
