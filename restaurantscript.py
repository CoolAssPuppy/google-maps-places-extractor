import requests
import csv
import os

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if not API_KEY:
    raise ValueError("No Google Maps API key found in environment variables!")

def extract_name_from_url(url):
    # Extract the name from the Google Maps URL.
    parts = url.split("/place/")
    if len(parts) > 1:
        return parts[1].split("/")[0].replace("+", " ")
    return None

def search_place(name):
    endpoint_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={name}&inputtype=textquery&key={API_KEY}"
    response = requests.get(endpoint_url)
    results = response.json().get('candidates', [])

    if results:
        return results[0]['place_id']
    return None

def get_place_details(place_id):
    endpoint_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}"
    response = requests.get(endpoint_url)
    result = response.json()

    if result['status'] != 'OK':
        print(f"Error fetching details for place_id {place_id}: {result['status']}")
        return None

    place = result['result']
    
    # Extracting required details
    name = place.get('name', '')
    city = ''
    country = ''
    for component in place.get('address_components', []):
        if 'locality' in component['types']:
            city = component['long_name']
        if 'country' in component['types']:
            country = component['long_name']
    phone_number = place.get('formatted_phone_number', '')
    rating = place.get('rating', '')
    website = place.get('website', '')
    google_maps_url = place.get('url', '')

    return name, city, country, phone_number, rating, website, google_maps_url

def main():
    with open('Restaurants.csv', 'r') as infile, open('RestaurantsDetail.csv', 'w') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['Name', 'City', 'Country', 'Phone Number', 'Google Star Rating', 'Website', 'Google Maps URL']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            name = extract_name_from_url(row['URL'])
            print(f"fetching {name}")
            place_id = search_place(name)
            if place_id:
                details = get_place_details(place_id)
                if details:
                    writer.writerow({
                        'Name': details[0],
                        'City': details[1],
                        'Country': details[2],
                        'Phone Number': details[3],
                        'Google Star Rating': details[4],
                        'Website': details[5],
                        'Google Maps URL': details[6]
                    })

if __name__ == '__main__':
    main()
