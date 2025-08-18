import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load the CSV from Step 1
df = pd.read_csv("accident_prone_zones_2021.csv")

# Create geocoder object
geolocator = Nominatim(user_agent="accident_locator")

# Lists to store coordinates
latitudes = []
longitudes = []

for zone in df["Accident Prone Zone"]:
   
    try:
        # Add ", Delhi, India" to help geocoding accuracy
        location = geolocator.geocode(f"{zone}, Delhi, India", timeout=10)

        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except Exception as e:
        print(f"Error for {zone}: {e}")
        latitudes.append(None)
        longitudes.append(None)

    time.sleep(2)  # safer, reduces risk of blocking
  # to avoid API rate limit

# Add new columns
df["Latitude"] = latitudes
df["Longitude"] = longitudes

# Save new CSV
df.to_csv("accident_prone_zones_with_coords.csv", index=False)
print("✅ accident_prone_zones_with_coords.csv created successfully!")
