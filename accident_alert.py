import pandas as pd
import folium
import osmnx as ox
import networkx as nx
from shapely.geometry import LineString, Point
import webbrowser
import os

# --------------------------
# 1. Load accident data (remove missing coords)
# --------------------------
accident_df = pd.read_csv("accident_data.csv")
accident_df = accident_df.dropna(subset=["Latitude", "Longitude"])

# --------------------------
# 2. Ask user for start & end coordinates
# --------------------------
print("Enter START location coordinates:")
start_lat = float(input("Latitude: "))
start_lon = float(input("Longitude: "))

print("\nEnter DESTINATION location coordinates:")
end_lat = float(input("Latitude: "))
end_lon = float(input("Longitude: "))

start_point = (start_lat, start_lon)
end_point = (end_lat, end_lon)

# --------------------------
# 3. Get road network and shortest path
# --------------------------
print("\nDownloading road network from OpenStreetMap...")
G = ox.graph_from_point(start_point, dist=30000, network_type='drive')
G = ox.project_graph(G)  # convert to meters so no scikit-learn needed

orig_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
dest_node = ox.distance.nearest_nodes(G, end_lon, end_lat)


# Get shortest driving route
route_nodes = nx.shortest_path(G, orig_node, dest_node, weight='length')
route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route_nodes]  # lat, lon

# Create shapely LineString for route
route_line = LineString([(lon, lat) for lat, lon in route_coords])

# --------------------------
# 4. Filter accidents within 500 meters of route
# --------------------------
filtered_accidents = []
for _, row in accident_df.iterrows():
    accident_point = Point(row['Longitude'], row['Latitude'])
    if route_line.distance(accident_point) <= 0.005:  # ~500m
        filtered_accidents.append(row)

filtered_df = pd.DataFrame(filtered_accidents)

# --------------------------
# 5. Create map
# --------------------------
mid_lat = (start_lat + end_lat) / 2
mid_lon = (start_lon + end_lon) / 2
m = folium.Map(location=(mid_lat, mid_lon), zoom_start=13)

# Add road route
folium.PolyLine(route_coords, color="blue", weight=4, opacity=0.7, popup="Road Route").add_to(m)

# Start & end markers
folium.Marker((start_lat, start_lon), popup="Start", icon=folium.Icon(color='green')).add_to(m)
folium.Marker((end_lat, end_lon), popup="End", icon=folium.Icon(color='red')).add_to(m)

# Accident markers
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=(row['Latitude'], row['Longitude']),
        radius=5,
        color='orange',
        fill=True,
        fill_color='orange',
        popup=f"{row['Accident Prone Zone']}"
    ).add_to(m)

if route_coords and len(route_coords) > 1:
    route_line = LineString([(lon, lat) for lat, lon in route_coords])
else:
    print("❌ No route found between the given points.")
    exit()


# --------------------------
# 6. Save & open map
# --------------------------
map_file = "accident_map_roadroute.html"
m.save(map_file)
webbrowser.open('file://' + os.path.realpath(map_file))

print("✅ Map generated with road route and nearby accidents.")


