from manim import *
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("./cleaned/vietnam_adm_lvl2.csv", index_col=0)
#df = gpd.GeoDataFrame(df, geometry="geometry")

regions_df = df.copy()

# Convert geometry strings to actual Polygon objects
regions_df['geometry'] = regions_df['geometry'].apply(gpd.GeoSeries.from_wkt)

# Convert DataFrame to GeoDataFrame
regions_gdf = gpd.GeoDataFrame(regions_df, geometry='geometry')

# Color Mapping Setup
cmap = plt.get_cmap('viridis')
norm = plt.Normalize(regions_gdf['density'].min(), regions_gdf['density'].max())

# Helper Functions Section
# ------------------------

# Extract coordinates from a Polygon geometry
def get_line_coord(polygon):
    border_xy = np.array(polygon.boundary.coords)
    return border_xy

# Create line and polygon (area) with color based on population density
def get_line_and_area(axes, border_xy, density):
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
    area = Polygon(*points, fill_opacity=0.5, color=hex_color, stroke_width=1)
    dist_center = area.get_center()

    return line, area, dist_center

# Animation Class Section
# -----------------------

class Animate_pop(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Set up Manim Axis
        min_x = min([coord[0] for coord in regions_df['coords']]) - 2.5
        max_x = max([coord[0] for coord in regions_df['coords']]) + 2.5
        min_y = min([coord[1] for coord in regions_df['coords']])
        max_y = max([coord[1] for coord in regions_df['coords']])
        
        axes = Axes(
            x_range=[min_x, max_x],
            y_range=[min_y, max_y],
            axis_config={"color": BLUE},
        )
        
        # Plot the boundary of the first region (assumed to be representative)
        first_polygon = regions_gdf.iloc[0].geometry
        boundary_line = axes.plot_line_graph(
            get_line_coord(first_polygon)[:, 0], get_line_coord(first_polygon)[:, 1], 
            add_vertex_dots=False, 
            line_color=BLACK,
            stroke_width=5
        )
        self.play(Create(boundary_line, run_time=1))
        self.wait(0.5)
        
        # Loop through each region in the data
        for row in regions_gdf.itertuples():
            geometry = row.geometry
            density = row.density
            district = row.dist
            
            border_xy = get_line_coord(geometry)
            region_line, region_area, center = get_line_and_area(axes, border_xy, density)
            
            region_label = Text(f"{district}: {density:.2f} per km²", font_size=25, color=BLACK)
            region_label.move_to(UP + 2.3 * UP)
            
            self.play(Create(region_line), Write(region_label), run_time=2)
            self.play(Create(region_area), run_time=2)
            self.play(FadeOut(region_label))
print(df.head())