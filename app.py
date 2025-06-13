import requests
import time
import json

def query_overpass():
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json][timeout:50];
    (
      node["tourism"="attraction"](40.4774,-74.2591,40.9176,-73.7004);
      node["historic"](40.4774,-74.2591,40.9176,-73.7004);
      node["amenity"="theatre"](40.4774,-74.2591,40.9176,-73.7004);
    );
    out body;
    """
    print("Querying Overpass API for landmarks in NYC bounding box...")
    response = requests.post(overpass_url, data={'data': query})
    response.raise_for_status()
    data = response.json()
    landmarks = []
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name')
        lat = element.get('lat')
        lon = element.get('lon')
        if name and lat and lon:
            landmarks.append({'name': name, 'latitude': lat, 'longitude': lon})
    print(f"Found {len(landmarks)} landmarks from Overpass.")
    return landmarks

def search_wikimedia_image(title):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': title,
        'gsrlimit': 1,
        'gsrnamespace': 6,  # File namespace (images)
        'prop': 'imageinfo',
        'iiprop': 'url'
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        pages = res.get('query', {}).get('pages', {})
        for page in pages.values():
            imageinfo = page.get('imageinfo', [])
            if imageinfo:
                return imageinfo[0].get('url')
    except Exception as e:
        print(f"Error searching image for {title}: {e}")
    return None

def main():
    landmarks = query_overpass()
    print("Searching images on Wikimedia Commons...")
    for i, landmark in enumerate(landmarks, 1):
        image_url = search_wikimedia_image(landmark['name'])
        landmark['image_url'] = image_url if image_url else None
        print(f"{i}/{len(landmarks)} - {landmark['name']}: {'Image found' if image_url else 'No image'}")
        time.sleep(0.5)  # polite delay
    landmarks_with_images = [lm for lm in landmarks if lm['image_url']]
    print(f"\nTotal landmarks with images: {len(landmarks_with_images)}")
    with open('nyc_landmarks_full.json', 'w', encoding='utf-8') as f:
        json.dump(landmarks_with_images, f, ensure_ascii=False, indent=2)
    print("Saved landmarks with images to nyc_landmarks_full.json")

if __name__ == "__main__":
    main()