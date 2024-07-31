from manim import *
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from colormap import rgb2hex
from shapely import wkt, envelope
import shapely
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
#regions_gdf = regions_gdf[regions_gdf['region'].isin(select_regions)].sort_values(by=query, ascending=False)
regions_gdf = regions_gdf.sort_values(by=query, ascending=False)
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

# Helper Functions Section
# ------------------------

# Extract coordinates from a Polygon geometry, updated to handle Multigon
def get_line_coord(polygon) -> list:
    if polygon.geom_type == "MultiPolygon":
        p_list = list(polygon.geoms)
        border_xy = [np.array(p.boundary.coords) for p in p_list]
    else:
        border_xy = [np.array(polygon.boundary.coords)]
    return border_xy

# Create line and polygon (area) with color based on population density
def create_Polyhedron(axes, border_xy, height):
    color = cmap(norm(height))
    hex_color = rgb2hex(*color)
    
    # Create polygon area
    points = axes.c2p(border_xy)
    top_face = Polygon(*[point + np.array([0, 0, height]) for point in points], fill_opacity=1, color=hex_color, stroke_width=1)
    bottom_face = Polygon(*points, fill_opacity=1, color=hex_color, stroke_width=1)
    top_center = top_face.get_center()

    return top_face, bottom_face, top_center

#need additional fixes
def calc_side_faces(polygon, height):
    color = cmap(norm(height-0.2))
    hex_color = rgb2hex(*color)
    side_faces = VGroup()
    points = polygon.get_vertices()
    #z_level = min([y for x,y,z in points]) + 10
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        side_face = Polygon(*[
            points[i],
            points[next_i],
            points[next_i] + np.array([0, 0, height]),
            points[i] + np.array([0, 0, height]),
        ], fill_opacity=1, color=hex_color, stroke_width=1, stroke_opacity=1)
        side_faces.add(side_face)
    return side_faces


# Animation Class Section
# -----------------------

class Animate_pop(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=10 * DEGREES, theta=-100 * DEGREES)
        self.camera.set_focal_distance(100000)
        self.begin_ambient_camera_rotation(rate=30*DEGREES, about='theta')
    
        axes = Axes(
            x_range=[min_x, max_x],
            y_range=[min_y, max_y],
            axis_config={"color": WHITE},
        ).scale(.5).set_z_index(0)
        x_label = Tex("x").next_to(axes.x_axis.get_end(), RIGHT)
        y_label = Tex("y").next_to(axes.y_axis.get_end(), UP)
        self.add(axes)
        self.add(x_label, y_label)
        # Loop through each region in the data
        count = 0
        for idx, row in regions_gdf.iterrows(): #sort_values(by='coords', ascending=True).
            geometry = row.geometry
            height = row[query]/dfac
            count += 1
            border_xy = get_line_coord(geometry)
            for bor_xy in border_xy:
                region_topface, region_bottomface, center = create_Polyhedron(axes, bor_xy, height)
                side_faces = calc_side_faces(region_bottomface, height).set_z_index(count)
                polyh = VGroup(region_bottomface, side_faces, region_topface).set_shade_in_3d(True)
                print(self.camera.is_in_frame(side_faces))
                print(count)
                self.add(polyh)
                #print(polyh.get_z_index_reference_point)

        #self.wait(3)
            #region_label = Text(f"{district}", font_size=12, color=BLACK, font="Arial") #{density:.2f} per km²
            #region_label.move_to(center)
            #self.add(region_label)
                
            #self.play(Create(region_line), Write(region_label), run_time=2)
            #self.play(Create(region_area), run_time=2)
            #self.play(FadeOut(region_label))