from .config import CHAR_MAP, CATEGORY_KEYWORDS, DISCOVERY_KEYWORDS, DESC_BLACKLIST, STOP_WORDS, SIMPLE_QUERY, BASE_QUERY
from http.server import BaseHTTPRequestHandler
import json
import requests
import spacy
import urllib.parse
from datetime import datetime, timedelta
from collections import Counter
import unicodedata
import csv
import re
import os

nlp = spacy.load("en_core_web_sm")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_name(name):
    """Normalize location names"""
    name = name.strip()
    name = re.sub(r'^[Tt]he\s+', '', name)

    for suffix in [" Province", " State", " Peninsula", " Desert", " Mountains", " Island", " Islands", " Region", " District", " County", " Department", " Territory"]:
        name = name.replace(suffix, "")

    for character, replacement in CHAR_MAP.items():
        name = name.replace(character, replacement)

    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')

    return name.lower()

with open(os.path.join(BASE_DIR, "../data/cities.csv")) as f:
    reader = csv.DictReader(f)
    CITY_TO_COUNTRY = {}
    for row in reader:
            city = clean_name(row["city"])
            country = clean_name(row["country"])

            if city not in CITY_TO_COUNTRY:
                CITY_TO_COUNTRY[city] = { country }
            else:
                CITY_TO_COUNTRY[city].add(country)

    CITIES = set(CITY_TO_COUNTRY.keys())

with open(os.path.join(BASE_DIR, "../data/states.csv")) as f:
    reader = csv.DictReader(f)
    STATE_TO_COUNTRY = {}
    
    for row in reader:
        state = clean_name(row["name"])
        country = clean_name(row["country_name"])

        if state not in STATE_TO_COUNTRY:
            STATE_TO_COUNTRY[state] = { country }
        else:
            STATE_TO_COUNTRY[state].add(country)

    STATES = set(STATE_TO_COUNTRY.keys())

with open(os.path.join(BASE_DIR, "../data/countries.csv")) as f:
    rows = list(csv.DictReader(f))
    COUNTRIES_RAW = [row["name"] for row in rows]
    COUNTRIES = {clean_name(row["name"]) for row in rows}

def extract_loc(text):
    """Extract location entities from text"""
    doc = nlp(text)

    #ents = []
    locs = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            if ent.text not in locs:
                locs.append(clean_name(ent.text))
        #ents.append("|"+ent.text)

    if len(locs) == 0:
        return None

    # locs_string = " ".join(locs) 
    # ents_string = " ".join(ents) 
    # print("\tLOCS:"+locs_string)
    # print("\tENTS:"+ents_string)

    chosen_loc = None
    loc_context = None

    for loc in locs:
        if loc in CITIES and loc not in STATES and loc not in COUNTRIES:
            chosen_loc = loc
            break
        
    for loc in locs:
        if loc in STATES and loc not in COUNTRIES:
            if not chosen_loc:
                chosen_loc = loc
            elif not loc_context and loc != chosen_loc:
                loc_context = loc
            break

    for loc in locs:
        if loc in COUNTRIES:
            if not chosen_loc:
                chosen_loc = loc
            elif not loc_context and loc != chosen_loc: 
                if chosen_loc in CITIES and loc in CITY_TO_COUNTRY[chosen_loc]:
                    loc_context = loc
                    break
                elif chosen_loc in STATES and loc in STATE_TO_COUNTRY[chosen_loc]:
                    loc_context = loc
                    break
                else: 
                    continue
            break
    
    if not chosen_loc:
        return None
        
    return chosen_loc, loc_context

def loc_to_geocode(loc, context):
    """Convert location entity to coordinates""" 
    token = os.environ.get("MAPBOX_TOKEN")
    query = f"{loc}, {context}" if context else loc
    #print("\tquery to mapbox: "+ query)

    encoded = urllib.parse.quote(query)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded}.json?access_token={token}&limit=1"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data["features"]:
            feature = data["features"][0]
            coords = {
                "lat": feature["center"][1],
                "lon": feature["center"][0],
                "loc": feature["place_name"]
            }
            return coords

    except Exception as e:
        print(f"Geocoding error for {loc}: {e}")
        return None
    
def is_relevant(article):
    """Return whether an article is relevant to the categories"""
    heading = f"{article.get('title', '')} {article.get('description', '')}".lower()
    body = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()

    heading_words = set(heading.split())
    discovery_hits = heading_words & DISCOVERY_KEYWORDS

    body_words = set(body.split())
    all_keywords = {keyword for keywords in CATEGORY_KEYWORDS.values() for keyword in keywords}
    category_hits = body_words & all_keywords

    return len(discovery_hits) > 0 and len(category_hits) > 0

def classify_news(article):
    """Classify an article based on title and description"""
    heading = f"{article.get('title', '')}".lower()
    body = f"{article.get('description', '')} {article.get('content', '')}".lower()
    scores = Counter()

    heading_doc = nlp(heading)
    heading_lemmas = {token.lemma_.lower() for token in heading_doc if not token.is_punct and not token.is_space }

    body_doc = nlp(body)
    body_lemmas = {token.lemma_.lower() for token in body_doc if not token.is_punct and not token.is_space }

    for lemma in heading_lemmas:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if lemma in keywords:
                scores[category] += 2

    for lemma in body_lemmas:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if lemma in keywords:
                scores[category] += 1

    if scores:
        return scores.most_common(1)[0][0]
    else:
        return "Unknown"

def clean_desc(desc):
    """Removes or strips spammy descriptions"""
    if not desc:
        return None
    
    desc_stripped = desc.strip()

    for phrase in DESC_BLACKLIST:
        if phrase in desc_stripped.lower():
            return None
        
    sentences = re.split(r'(?<=[.!?])\s+', desc_stripped)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    if len(sentences) <= 1:
        return desc_stripped

    last_sentence = sentences[-1]
    if last_sentence.endswith("...") or last_sentence.endswith("…") or len(last_sentence) < 30:
        sentences = sentences[:-1]
    
    cleaned = " ".join(sentences)
    return cleaned

def get_keywords(text):
    """Extract content words from text"""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    words = text.split()
    return { word for word in words if word not in STOP_WORDS and len(word) > 2 }

def keyword_similarity(a, b):
    """Jaccard similarity for keywords"""
    A = get_keywords(a)
    B = get_keywords(b)

    if not A or not B:
        return 0

    return len(A & B) / len(A | B)

def dedup_news(articles, jaccard_threshold=0.2, overlap_threshold=2):
    """Deduplicate articles"""
    deduped = []

    for A in articles:
        is_dup = False
        title_a = A["title"]
        loc_a = A["location"]
        for B in deduped:
            title_b = B["title"]
            loc_b = B["location"]
            sim = keyword_similarity(title_a, title_b)
            keywords_a = get_keywords(title_a)
            keywords_b = get_keywords(title_b)
            overlap = keywords_a & keywords_b

            if loc_a == loc_b and ((sim >= jaccard_threshold) or len(overlap) >= overlap_threshold):
                is_dup = True
                break
            elif ((sim >= jaccard_threshold + 0.05) or len(overlap) >= (overlap_threshold + 1)):
                is_dup = True
                break
        if not is_dup:
            deduped.append(A)
    
    return deduped

def process_news(articles):
    """Extract and geocode locations from articles"""
    processed = []

    for article in articles:
        if len(processed) >= 100:
            break
        if not is_relevant(article):
            continue
        else:
            category = classify_news(article)
            text = f"{article.get('title')} {article.get('description')} {article.get('content')}"
            result = extract_loc(text)

            if result:
                loc, context = result
                coords = loc_to_geocode(loc, context)

                if coords:
                    desc = clean_desc(article.get("description"))
                    processed.append({
                        "title": article.get("title"),
                        "description": desc,
                        "url": article.get("url"), 
                        "source": article.get("source"),
                        "latitude": coords["lat"], 
                        "longitude": coords["lon"],
                        "location": coords["loc"],
                        "date": article.get("publishedAt"),
                        "category": category
                    })

    deduped = dedup_news(processed)
    return deduped

def fetch_news(api_key, from_date, to_date, country):
    """Fetch news"""
    url = "https://newsapi.org/v2/everything"

    query = SIMPLE_QUERY + f" AND {country}" if country != "" else BASE_QUERY

    params = {
        "q": query,
        "excludeDomains": "freerepublic.com",
        "from": from_date,
        "to": to_date,
        "sortBy": "relevancy",
        "apiKey": api_key 
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["articles"]
    
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def get_sample_data():
    """Return sample data"""
    return [
        {
            "title": "Shipwreck Examined on Canada’s Sable Island",
            "description":
            "According to a Halifax City News report, Parks Canada archaeologists and a Mi’kmaw archaeological technician examined a well-preserved shipwreck exposed on the North Beach of Sable Island.",
            "url": "https://archaeology.org/news/2026/03/17/shipwreck-examined-on-canadas-sable-island/",
            "source": {
                "id": None,
                "name": "Archaeology",
            },
            "latitude": 44.6509,
            "longitude": -63.5923,
            "location": "Halifax",
            "category": "Shipwreck",
        }
    ]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        api_key = os.environ.get("NEWS_API_KEY")
        mapbox_token = os.environ.get("MAPBOX_TOKEN")
        
        if not api_key:
            response = {
                "articles": get_sample_data(),
                "count": len(get_sample_data()),
                "timestamp": datetime.now().isoformat(),
                "mode": "sample"
            }
        else:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            from_date = params.get("from", [None])[0]
            to_date = params.get("to", [None])[0]
            country = params.get("country", [None])[0]

            if not from_date:
                from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")
            if not country:
                country = ""

            articles = fetch_news(api_key, from_date, to_date, country)
            processed = process_news(articles)
            
            response = {
                "articles": processed,
                "count": len(processed),
                "timestamp": datetime.now().isoformat(),
                "mode": "live",
                "mapboxToken": mapbox_token
            }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return