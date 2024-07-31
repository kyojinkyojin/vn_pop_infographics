from manim import *
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from colormap import rgb2hex
from shapely import wkt, envelope
from shapely import buffer
import ast

df = pd.read_csv("./cleaned/vietnam_adm_lvl2.csv", index_col=0)

regions_df = df.copy().fillna(0)

# Convert geometry strings to actual Polygon objects
regions_df['geometry'] = regions_df['geometry'].apply(lambda x: wkt.loads(x))


# Convert DataFrame to GeoDataFrame
regions_gdf = gpd.GeoDataFrame(regions_df, geometry='geometry')
regions_gdf['coords'] = regions_gdf['coords'].apply(ast.literal_eval)

#select_area
select_regions = ["HA NOI"]
query = "population"
regions_gdf = regions_gdf[regions_gdf['region'].isin(select_regions)].sort_values(by=query, ascending=False)
#regions_gdf = regions_gdf.sort_values(by=query, ascending=False)
len_df = len(regions_gdf)
#print(regions_gdf)

#get_boundaries
big_polygon = envelope(regions_gdf.union_all())
polygon_border_xy = np.array(big_polygon.boundary.coords)
min_x = min(polygon_border_xy[:,0])
max_x = max(polygon_border_xy[:,0])
min_y = min(polygon_border_xy[:,1])
max_y = max(polygon_border_xy[:,1])
buff_x = (max_x-min_x)/2
buff_y = (max_y-min_y)/2

# Color Mapping Setup'
dfac = 2*10**5
cmap = plt.get_cmap('plasma')
norm = plt.Normalize(regions_gdf[query].quantile(0.05)/dfac, regions_gdf[query].quantile(0.98)/dfac)

def shrink_or_swell_shapely_polygon(my_polygon, factor=0.10, swell=False):
    ''' returns the shapely polygon which is smaller or bigger by passed factor.
        If swell = True , then it returns bigger polygon, else smaller '''
    from shapely import geometry

    #my_polygon = mask2poly['geometry'][120]

    shrink_factor = 0.10 #Shrink by 10%
    xs = list(my_polygon.exterior.coords.xy[0])
    ys = list(my_polygon.exterior.coords.xy[1])
    x_center = 0.5 * min(xs) + 0.5 * max(xs)
    y_center = 0.5 * min(ys) + 0.5 * max(ys)
    min_corner = geometry.Point(min(xs), min(ys))
    max_corner = geometry.Point(max(xs), max(ys))
    center = geometry.Point(x_center, y_center)
    shrink_distance = center.distance(min_corner)*0.10

    if swell:
        my_polygon_resized = my_polygon.buffer(shrink_distance) #expand
    else:
        my_polygon_resized = my_polygon.buffer(-shrink_distance) #shrink
    return my_polygon_resized

# Extract coordinates from a Polygon geometry, updated to handle Multigon
def get_line_coord(polygon) -> list:
    if polygon.geom_type == "MultiPolygon":
        p_list = list(polygon.geoms)
        p_list = [buffer(p, 0.01) for p in p_list]
        border_xy = [np.array(p.boundary.coords) for p in p_list]
    else:
        polygon = buffer(polygon, 0.01)
        border_xy = [np.array(polygon.boundary.coords)]
    return border_xy

# Create line and polygon (area) with color based on population density
def create_Polyhedron(axes, border_xy, h_tracker):
    height = 0
    color = cmap(norm(height))
    hex_color = rgb2hex(*color)
    
    # Create polygon area
    points = axes.c2p(border_xy)
    z_level = min([y for x, y, z in points]) + 3
    top_face = Polygon(*[point + np.array([0, 0, height]) for point in points], fill_opacity=1, color=hex_color, stroke_width=1).set_shade_in_3d(True)
    top_face.add_updater(lambda p, ht=h_tracker: p.become(
        Polygon(*[point + np.array([0, 0, h_tracker.get_value()]) for point in points], fill_opacity=1, color=rgb2hex(*cmap(norm(ht.get_value()))), stroke_width=1).set_shade_in_3d(True)
    ))
    bottom_face = Polygon(*points, fill_opacity=1, color=hex_color, stroke_width=1).set_shade_in_3d(True)
    bottom_face.add_updater(lambda p, ht=h_tracker: p.become(
        Polygon(*points, fill_opacity=1, color=rgb2hex(*cmap(norm(ht.get_value()))), stroke_width=1).set_shade_in_3d(True)
    ))
    top_center = top_face.get_center()

    return top_face, bottom_face, top_center

#need additional fixes
def calc_side_faces(polygon, h_tracker):
    height = 0
    color = cmap(norm(0))
    hex_color = rgb2hex(*color)
    side_faces = VGroup()
    points = polygon.get_vertices()
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        side_face = Polygon(*[
            points[i],
            points[next_i],
            points[next_i] + np.array([0, 0, height]),
            points[i] + np.array([0, 0, height]),
        ], fill_opacity=1, color=hex_color, stroke_width=1, stroke_opacity=1)
        side_face.add_updater(lambda p, i=i, next_i=next_i, ht=h_tracker: p.become(
        Polygon(*[points[i],
            points[next_i],
            points[next_i] + np.array([0, 0, ht.get_value()]),
            points[i] + np.array([0, 0, ht.get_value()])], fill_opacity=1, color=rgb2hex(*cmap(norm(ht.get_value()-.2))), stroke_width=1)
        ))
        side_faces.add(side_face)
        side_faces.set_shade_in_3d(True)
    return side_faces


# Animation Class Section
# -----------------------

class Animate_pop(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=30 * DEGREES, theta=-100 * DEGREES)
        self.camera.shading_factor = .3
        self.camera.default_distance = 20
        self.camera.set_focal_distance(10000)
        #self.begin_ambient_camera_rotation(rate=30*DEGREES, about='theta')
        #print(self.camera.get_position())
        axes = ThreeDAxes(
            x_range=[min_x, max_x],
            y_range=[min_y, max_y],
            z_range=[0, 4],
            axis_config={"color": WHITE},
        ).scale(.3).shift(DOWN*2)
        x_label = Tex("x").next_to(axes.x_axis.get_end(), RIGHT)
        y_label = Tex("y").next_to(axes.y_axis.get_end(), UP)
        self.add(axes)
        self.add(x_label, y_label)
        # Loop through each region in the data
        count = 0
        animations = []
        for idx, row in regions_gdf.sort_values(by='coords', ascending=False).iterrows(): #
            geometry = row.geometry
            height_goal = row[query]/dfac
            h_tracker = ValueTracker(height_goal)
            count += 1
            border_xy = get_line_coord(geometry)
            for bor_xy in border_xy:
                region_topface, region_bottomface, center = create_Polyhedron(axes, bor_xy, h_tracker)
                side_faces = calc_side_faces(region_bottomface, h_tracker)
                polyh = VGroup(region_bottomface, side_faces, region_topface)
                self.add(polyh)
                #animations.append(h_tracker.animate.set_value(height_goal))
        
        #self.play(LaggedStart(*animations, lag_ratio=0.3), rate_func=rate_functions.ease_in_out_cubic, run_time=8)


        #self.wait(3)