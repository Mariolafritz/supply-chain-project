import pandas as pd
import networkx as nx
import random
from faker import Faker
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopy
import folium
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='geopy')

# --- Configuration ---
RETAILER_LOCATION = "Gelsenkirchen"
WHOLESALER_LOCATION = "Düsseldorf"
WINERY_MOSEL_LOCATION = "Bernkastel-Kues"
WINERY_RHEINGAU_LOCATION = "Rüdesheim am Rhein"
N_CUSTOMERS = 25

# --- Geocoder setup ---
geolocator = Nominatim(user_agent="supply_chain_app", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=5.0, max_retries=2, swallow_exceptions=False)

def get_coordinates(city_name):
    try:
        location = geocode(city_name + ", Deutschland")
        if location:
            if "Sea" in location.address or "Meer" in location.address or "water" in location.raw.get("type", "").lower():
                print(f"⚠️ '{city_name}' is likely a sea → marked as WATER.")
                return "WATER"
            else:
                return (location.latitude, location.longitude)
        else:
            print(f"⚠️ No coordinates for {city_name} → marked as WATER.")
            return "WATER"
    except Exception as e:
        print(f"❌ Geocoding error for {city_name}: {e}")
        return "WATER"

# --- Geocode key locations ---
print("📍 Geocoding important locations...")
locations = {
    "Retailer": (RETAILER_LOCATION, get_coordinates(RETAILER_LOCATION)),
    "Wholesaler": (WHOLESALER_LOCATION, get_coordinates(WHOLESALER_LOCATION)),
    "Winery_Mosel": (WINERY_MOSEL_LOCATION, get_coordinates(WINERY_MOSEL_LOCATION)),
    "Winery_Rheingau": (WINERY_RHEINGAU_LOCATION, get_coordinates(WINERY_RHEINGAU_LOCATION)),
}

for name, (city, coords) in locations.items():
    if coords == "WATER":
        print(f"❌ ERROR: Critical location '{city}' is invalid. Exiting.")
        exit()

# --- Generate customers ---
print("👥 Generating customer data...")
common_german_cities = [
    'Berlin', 'Hamburg', 'München', 'Köln', 'Frankfurt am Main', 'Stuttgart',
    'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig', 'Bremen', 'Dresden',
    'Hannover', 'Nürnberg', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld',
    'Bonn', 'Münster', 'Karlsruhe', 'Mannheim', 'kassel', 'Wiesbaden'
]

customer_data = []
customer_cities = random.choices(common_german_cities, k=N_CUSTOMERS)

for i in range(N_CUSTOMERS):
    customer_id = f"Customer_{i+1}"
    city = customer_cities[i]
    demand = random.randint(1, 12)
    coords = get_coordinates(city)
    if coords != "WATER":
        customer_data.append({
            "id": customer_id,
            "city": city,
            "demand": demand,
            "latitude": coords[0],
            "longitude": coords[1]
        })
    else:
        print(f"🚫 Skipping customer {city} (invalid/water location)")

customers_df = pd.DataFrame(customer_data)
print(f"✅ {len(customers_df)} customers added to the network.")

# --- Build graph ---
G = nx.DiGraph()

for key in ["Winery_Mosel", "Winery_Rheingau", "Wholesaler", "Retailer"]:
    city, coords = locations[key]
    G.add_node(key, type=key.split('_')[0], city=city, pos=(coords[1], coords[0]))

for _, cust in customers_df.iterrows():
    G.add_node(cust['id'], type="Customer", city=cust['city'], demand=cust['demand'], pos=(cust['longitude'], cust['latitude']))

G.add_edge("Winery_Mosel", "Wholesaler", percentage=0.2)
G.add_edge("Winery_Rheingau", "Wholesaler", percentage=0.8)
G.add_edge("Wholesaler", "Retailer")
for cust_id in customers_df['id']:
    G.add_edge("Retailer", cust_id)

print(f"📦 Network graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

# --- Folium Map with blue sea tiles ---
print("🌐 Creating interactive map...")
m = folium.Map(location=[51.1657, 10.4515], zoom_start=6, tiles="OpenStreetMap")

node_colors = {
    "Winery": "red",
    "Wholesaler": "orange",
    "Retailer": "blue",
    "Customer": "greeng"
}
node_icons = {
    "Winery": "industry",
    "Wholesaler": "truck",
    "Retailer": "shopping-cart",
    "Customer": "user"
}

for node, data in G.nodes(data=True):
    lon, lat = data['pos']
    ntype = data.get("type", "Unknown")
    popup = f"{node} ({ntype})<br>City: {data.get('city')}"
    if ntype == "Customer":
        popup += f"<br>Demand: {data.get('demand')} bottles"

    folium.Marker(
        location=[lat, lon],
        popup=popup,
        tooltip=node,
        icon=folium.Icon(color=node_colors.get(ntype, "gray"), icon=node_icons.get(ntype, "info-sign"), prefix='fa')
    ).add_to(m)

for u, v in G.edges():
    pos_u = G.nodes[u]['pos']
    pos_v = G.nodes[v]['pos']
    folium.PolyLine([(pos_u[1], pos_u[0]), (pos_v[1], pos_v[0])],
                    color="black", weight=1.5, opacity=0.6).add_to(m)

map_filename = "liefernetz_karte_with_blue_sea.html"
m.save(map_filename)
print(f"✅ Map saved: {map_filename}")
