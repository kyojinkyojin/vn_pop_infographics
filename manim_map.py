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

regions_df = df.copy()

# Convert geometry strings to actual Polygon objects
regions_df['geometry'] = regions_df['geometry'].apply(lambda x: wkt.loads(x))


# Convert DataFrame to GeoDataFrame
regions_gdf = gpd.GeoDataFrame(regions_df, geometry='geometry')
regions_gdf['coords'] = regions_gdf['coords'].apply(ast.literal_eval)
#regions_gdf['geometry'] = regions_gdf['geometry'].apply(lambda geom: geom.convex_hull if geom.geom_type == 'MultiPolygon' else geom) #envelope(geom)

#select_area
regions_gdf = regions_gdf[regions_gdf['region']=="HA NOI"]
print(regions_gdf)

#get_boundaries
big_polygon = envelope(regions_gdf.union_all())
polygon_border_xy = np.array(big_polygon.boundary.coords)

# Color Mapping Setup
cmap = plt.get_cmap('plasma')
norm = plt.Normalize(regions_gdf['density'].min(), regions_gdf['density'].max())

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

#need additional fixes
def calc_side_faces(points):
    side_faces = VGroup()
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        side_face = Polygon(
            points[i],
            points[next_i],
            points[next_i] + np.array([0, 0, height]),
            points[i] + np.array([0, 0, height]),
        )
        side_faces.add(side_face)
    return side_faces

# Create line and polygon (area) with color based on population density
def create_Polyhedron(axes, border_xy, density):
    color = cmap(norm(density))
    hex_color = rgb2hex(*color)
    
    # Create line graph
    line = axes.plot_line_graph(
        border_xy[:, 0], border_xy[:, 1], 
        add_vertex_dots=False,
        line_color=BLACK, 
        stroke_width=1
    )
    
    # Create polygon area
    points = axes.coords_to_point(border_xy)
    top_face = Polygon(*[points + np.array([0, 0, density])])
    bottom_face = Polygon(*points, fill_opacity=0.5, color=hex_color, stroke_width=1)


    dist_center = top_face.get_center()

    return line, polyhedron, dist_center


# Animation Class Section
# -----------------------
buff = 0.3
class Animate_pop(ThreeDScene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Set up Manim Axis
        min_x = min(polygon_border_xy[:,0]) - buff
        max_x = max(polygon_border_xy[:,0]) + buff
        min_y = min(polygon_border_xy[:,1]) - buff
        max_y = max(polygon_border_xy[:,1]) + buff
        
        axes = Axes(
            x_range=[min_x, max_x],
            y_range=[min_y, max_y],
            axis_config={"color": BLUE},
        )
        # Loop through each region in the data
        for row in regions_gdf.itertuples():
            geometry = row.geometry
            density = row.density
            district = row.dist
            border_xy = get_line_coord(geometry)
            for bor_xy in border_xy:
                region_line, region_area, center = create_Polyhedron(axes, bor_xy, density)
                self.add(region_line, region_area)
            
            region_label = Text(f"{district}", font_size=12, color=BLACK, font="montserrat") #{density:.2f} per km²
            region_label.move_to(center)
            self.add(region_label)
                
            #self.play(Create(region_line), Write(region_label), run_time=2)
            #self.play(Create(region_area), run_time=2)
            #self.play(FadeOut(region_label))