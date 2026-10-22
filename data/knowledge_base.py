"""
Curated knowledge base covering major Indian travel destinations across all
tiers, plus the content used to build itineraries and destination highlights.

Coordinates are approximate (city-centre level) — good enough for
straight-line distance estimation, not for turn-by-turn navigation.
"""

# Each destination: label, state, cost tier (matches model/train_model.py
# tiers), approximate lat/lon, 2-3 famous foods, 2-3 famous things to see.
DESTINATIONS = {
    # ---- metro ----------------------------------------------------------
    "mumbai":      {"label": "Mumbai", "state": "Maharashtra", "tier": "metro", "lat": 19.0760, "lon": 72.8777,
                     "food": ["Vada pav", "Pav bhaji", "Bombay sandwich"],
                     "things": ["Gateway of India", "Marine Drive", "Elephanta Caves"]},
    "delhi":       {"label": "Delhi", "state": "Delhi", "tier": "metro", "lat": 28.6139, "lon": 77.2090,
                     "food": ["Chole bhature", "Paranthe Wali Gali food", "Butter chicken"],
                     "things": ["Red Fort", "India Gate", "Qutub Minar"]},
    "bengaluru":   {"label": "Bengaluru", "state": "Karnataka", "tier": "metro", "lat": 12.9716, "lon": 77.5946,
                     "food": ["Masala dosa", "Bisi bele bath", "Filter coffee"],
                     "things": ["Lalbagh Garden", "Bangalore Palace", "Cubbon Park"]},
    "kolkata":     {"label": "Kolkata", "state": "West Bengal", "tier": "metro", "lat": 22.5726, "lon": 88.3639,
                     "food": ["Rosogolla", "Kathi roll", "Macher jhol"],
                     "things": ["Victoria Memorial", "Howrah Bridge", "Park Street"]},
    "chennai":     {"label": "Chennai", "state": "Tamil Nadu", "tier": "metro", "lat": 13.0827, "lon": 80.2707,
                     "food": ["Idli-sambar", "Chettinad chicken", "Filter coffee"],
                     "things": ["Marina Beach", "Kapaleeshwarar Temple", "Fort St. George"]},
    "hyderabad":   {"label": "Hyderabad", "state": "Telangana", "tier": "metro", "lat": 17.3850, "lon": 78.4867,
                     "food": ["Hyderabadi biryani", "Haleem", "Irani chai"],
                     "things": ["Charminar", "Golconda Fort", "Ramoji Film City"]},

    # ---- tier2 (smaller cities) ------------------------------------------
    "pune":        {"label": "Pune", "state": "Maharashtra", "tier": "tier2", "lat": 18.5204, "lon": 73.8567,
                     "food": ["Misal pav", "Puran poli"], "things": ["Shaniwar Wada", "Aga Khan Palace"]},
    "ahmedabad":   {"label": "Ahmedabad", "state": "Gujarat", "tier": "tier2", "lat": 23.0225, "lon": 72.5714,
                     "food": ["Khaman dhokla", "Gujarati thali"], "things": ["Sabarmati Ashram", "Adalaj Stepwell"]},
    "jaipur":      {"label": "Jaipur", "state": "Rajasthan", "tier": "tier2", "lat": 26.9124, "lon": 75.7873,
                     "food": ["Dal baati churma", "Ghevar"], "things": ["Hawa Mahal", "Amber Fort", "City Palace"]},
    "lucknow":     {"label": "Lucknow", "state": "Uttar Pradesh", "tier": "tier2", "lat": 26.8467, "lon": 80.9462,
                     "food": ["Tunday kababi", "Lucknowi biryani"], "things": ["Bara Imambara", "Rumi Darwaza"]},
    "indore":      {"label": "Indore", "state": "Madhya Pradesh", "tier": "tier2", "lat": 22.7196, "lon": 75.8577,
                     "food": ["Poha-jalebi", "Sarafa Bazaar street food"], "things": ["Rajwada Palace", "Lal Bagh Palace"]},
    "chandigarh":  {"label": "Chandigarh", "state": "Chandigarh", "tier": "tier2", "lat": 30.7333, "lon": 76.7794,
                     "food": ["Chole kulche"], "things": ["Rock Garden", "Sukhna Lake"]},
    "bhopal":      {"label": "Bhopal", "state": "Madhya Pradesh", "tier": "tier2", "lat": 23.2599, "lon": 77.4126,
                     "food": ["Bhopali gosht korma"], "things": ["Upper Lake", "Taj-ul-Masajid"]},
    "nagpur":      {"label": "Nagpur", "state": "Maharashtra", "tier": "tier2", "lat": 21.1458, "lon": 79.0882,
                     "food": ["Saoji mutton", "Nagpur oranges"], "things": ["Deekshabhoomi", "Sitabuldi Fort"]},
    "surat":       {"label": "Surat", "state": "Gujarat", "tier": "tier2", "lat": 21.1702, "lon": 72.8311,
                     "food": ["Locho", "Undhiyu"], "things": ["Dutch Garden", "Surat Castle"]},
    "kochi":       {"label": "Kochi", "state": "Kerala", "tier": "tier2", "lat": 9.9312, "lon": 76.2673,
                     "food": ["Kerala fish curry", "Appam with stew"], "things": ["Chinese Fishing Nets", "Fort Kochi"]},
    "coimbatore":  {"label": "Coimbatore", "state": "Tamil Nadu", "tier": "tier2", "lat": 11.0168, "lon": 76.9558,
                     "food": ["Kongunadu meals"], "things": ["Marudamalai Temple", "VOC Park"]},
    "udaipur":     {"label": "Udaipur", "state": "Rajasthan", "tier": "tier2", "lat": 24.5854, "lon": 73.7125,
                     "food": ["Dal baati", "Rajasthani thali"], "things": ["Lake Pichola", "City Palace"]},

    # ---- heritage ---------------------------------------------------------
    "agra":        {"label": "Agra", "state": "Uttar Pradesh", "tier": "heritage", "lat": 27.1767, "lon": 78.0081,
                     "food": ["Petha", "Mughlai cuisine"], "things": ["Taj Mahal", "Agra Fort"]},
    "varanasi":    {"label": "Varanasi", "state": "Uttar Pradesh", "tier": "heritage", "lat": 25.3176, "lon": 82.9739,
                     "food": ["Kachori sabzi", "Banarasi paan"], "things": ["Ganga Aarti at Dashashwamedh Ghat", "Kashi Vishwanath Temple"]},
    "hampi":       {"label": "Hampi", "state": "Karnataka", "tier": "heritage", "lat": 15.3350, "lon": 76.4600,
                     "food": ["South Indian thali"], "things": ["Virupaksha Temple", "Stone Chariot"]},
    "khajuraho":   {"label": "Khajuraho", "state": "Madhya Pradesh", "tier": "heritage", "lat": 24.8318, "lon": 79.9199,
                     "food": ["Bundelkhandi cuisine"], "things": ["Khajuraho Temples"]},
    "mysuru":      {"label": "Mysuru", "state": "Karnataka", "tier": "heritage", "lat": 12.2958, "lon": 76.6394,
                     "food": ["Mysore pak", "Mysore masala dosa"], "things": ["Mysore Palace", "Chamundi Hills"]},
    "amritsar":    {"label": "Amritsar", "state": "Punjab", "tier": "heritage", "lat": 31.6340, "lon": 74.8723,
                     "food": ["Amritsari kulcha", "Langar at Golden Temple"], "things": ["Golden Temple", "Wagah Border"]},
    "ajmer":       {"label": "Ajmer", "state": "Rajasthan", "tier": "heritage", "lat": 26.4499, "lon": 74.6399,
                     "food": ["Sohan halwa"], "things": ["Ajmer Sharif Dargah", "Ana Sagar Lake"]},
    "gwalior":     {"label": "Gwalior", "state": "Madhya Pradesh", "tier": "heritage", "lat": 26.2183, "lon": 78.1828,
                     "food": ["Gwalior ki bedai"], "things": ["Gwalior Fort", "Jai Vilas Palace"]},
    "mahabalipuram": {"label": "Mahabalipuram", "state": "Tamil Nadu", "tier": "heritage", "lat": 12.6208, "lon": 80.1929,
                     "food": ["Fresh seafood"], "things": ["Shore Temple", "Five Rathas"]},
    "orchha":      {"label": "Orchha", "state": "Madhya Pradesh", "tier": "heritage", "lat": 25.3516, "lon": 78.6407,
                     "food": ["Bundeli cuisine"], "things": ["Orchha Fort", "Chaturbhuj Temple"]},

    # ---- hill ---------------------------------------------------------------
    "manali":      {"label": "Manali", "state": "Himachal Pradesh", "tier": "hill", "lat": 32.2432, "lon": 77.1892,
                     "food": ["Siddu", "Trout fish"], "things": ["Solang Valley", "Hidimba Temple"]},
    "shimla":      {"label": "Shimla", "state": "Himachal Pradesh", "tier": "hill", "lat": 31.1048, "lon": 77.1734,
                     "food": ["Chana madra"], "things": ["The Ridge", "Mall Road"]},
    "munnar":      {"label": "Munnar", "state": "Kerala", "tier": "hill", "lat": 10.0889, "lon": 77.0595,
                     "food": ["Kerala spice-infused dishes"], "things": ["Tea gardens", "Eravikulam National Park"]},
    "darjeeling":  {"label": "Darjeeling", "state": "West Bengal", "tier": "hill", "lat": 27.0360, "lon": 88.2627,
                     "food": ["Darjeeling tea", "Momos"], "things": ["Tiger Hill sunrise", "Darjeeling Toy Train"]},
    "ooty":        {"label": "Ooty", "state": "Tamil Nadu", "tier": "hill", "lat": 11.4064, "lon": 76.6932,
                     "food": ["Homemade chocolates"], "things": ["Botanical Garden", "Ooty Lake"]},
    "nainital":    {"label": "Nainital", "state": "Uttarakhand", "tier": "hill", "lat": 29.3919, "lon": 79.4542,
                     "food": ["Bal mithai"], "things": ["Naini Lake", "Naina Devi Temple"]},
    "mussoorie":   {"label": "Mussoorie", "state": "Uttarakhand", "tier": "hill", "lat": 30.4598, "lon": 78.0664,
                     "food": ["Local Garhwali food"], "things": ["Kempty Falls", "Mall Road"]},
    "gangtok":     {"label": "Gangtok", "state": "Sikkim", "tier": "hill", "lat": 27.3389, "lon": 88.6065,
                     "food": ["Momos", "Thukpa"], "things": ["MG Marg", "Tsomgo Lake"]},
    "coorg":       {"label": "Coorg", "state": "Karnataka", "tier": "hill", "lat": 12.3375, "lon": 75.8069,
                     "food": ["Pandi curry", "Coorg filter coffee"], "things": ["Abbey Falls", "Coffee plantations"]},
    "rishikesh":   {"label": "Rishikesh", "state": "Uttarakhand", "tier": "hill", "lat": 30.0869, "lon": 78.2676,
                     "food": ["Satvik vegetarian food"], "things": ["Laxman Jhula", "Ganga Aarti"]},
    "shillong":    {"label": "Shillong", "state": "Meghalaya", "tier": "hill", "lat": 25.5788, "lon": 91.8933,
                     "food": ["Jadoh", "Local pork dishes"], "things": ["Umiam Lake", "Elephant Falls"]},
    "leh":         {"label": "Leh", "state": "Ladakh", "tier": "hill", "lat": 34.1526, "lon": 77.5771,
                     "food": ["Thukpa", "Butter tea"], "things": ["Pangong Lake", "Leh Palace"]},

    # ---- beach ---------------------------------------------------------------
    "goa":         {"label": "Goa", "state": "Goa", "tier": "beach", "lat": 15.2993, "lon": 74.1240,
                     "food": ["Goan fish curry", "Bebinca"], "things": ["Baga Beach", "Fort Aguada"]},
    "pondicherry": {"label": "Pondicherry", "state": "Puducherry", "tier": "beach", "lat": 11.9416, "lon": 79.8083,
                     "food": ["French-inspired cafe food", "Filter coffee"], "things": ["French Quarter", "Auroville"]},
    "andaman":     {"label": "Andaman (Port Blair)", "state": "Andaman & Nicobar", "tier": "beach", "lat": 11.6234, "lon": 92.7265,
                     "food": ["Fresh seafood"], "things": ["Radhanagar Beach", "Cellular Jail"]},
    "gokarna":     {"label": "Gokarna", "state": "Karnataka", "tier": "beach", "lat": 14.5479, "lon": 74.3188,
                     "food": ["Coastal Karnataka cuisine"], "things": ["Om Beach", "Mahabaleshwar Temple"]},
    "varkala":     {"label": "Varkala", "state": "Kerala", "tier": "beach", "lat": 8.7379, "lon": 76.7163,
                     "food": ["Kerala seafood"], "things": ["Varkala Cliff", "Papanasam Beach"]},
    "alleppey":    {"label": "Alleppey", "state": "Kerala", "tier": "beach", "lat": 9.4981, "lon": 76.3388,
                     "food": ["Karimeen fish fry"], "things": ["Backwater houseboats", "Alappuzha Beach"]},
    "diu":         {"label": "Diu", "state": "Diu", "tier": "beach", "lat": 20.7144, "lon": 70.9874,
                     "food": ["Seafood", "Parsi-influenced dishes"], "things": ["Diu Fort", "Nagoa Beach"]},
    "rameswaram":  {"label": "Rameswaram", "state": "Tamil Nadu", "tier": "beach", "lat": 9.2881, "lon": 79.3129,
                     "food": ["Temple prasadam", "South Indian meals"], "things": ["Ramanathaswamy Temple", "Pamban Bridge"]},
}

# Budget split templates (% of the post-travel remaining budget) by travel style
BUDGET_SPLIT = {
    "relaxed": {"hotel": 0.38, "food": 0.22, "local_transport": 0.16, "activities": 0.16, "buffer": 0.08},
    "active":  {"hotel": 0.28, "food": 0.20, "local_transport": 0.22, "activities": 0.24, "buffer": 0.06},
    "family":  {"hotel": 0.35, "food": 0.24, "local_transport": 0.18, "activities": 0.15, "buffer": 0.08},
}

# Activity pools by tier + style, used to compose day-by-day plans
ACTIVITY_POOL = {
    "beach": {
        "relaxed": ["a slow sunrise walk on the beach", "a beachfront cafe brunch", "a sunset boat cruise", "a spa & wellness session"],
        "active":  ["parasailing at the main beach", "a scooter ride to a hidden cove", "scuba diving taster session", "a night market crawl"],
        "family":  ["a shallow-water beach morning", "a dolphin-spotting boat trip", "a visit to the local fort", "a kid-friendly water park"],
    },
    "hill": {
        "relaxed": ["a cafe-hopping walk through the town", "a viewpoint sunrise stop", "a tea/coffee estate tour", "a quiet lakeside evening"],
        "active":  ["a guided day trek", "paragliding (weather permitting)", "river crossing / zip-line activity", "a summit viewpoint hike"],
        "family":  ["a toy-train or cable-car ride", "a nature park visit", "a local market stroll", "a picnic by the valley viewpoint"],
    },
    "tier2": {
        "relaxed": ["a heritage haveli walking tour", "a rooftop-cafe evening", "a textile/craft market visit", "a slow palace-grounds stroll"],
        "active":  ["a walled-city cycling tour", "a step-well & fort trek", "a street-food tasting trail", "a hot-air-balloon sunrise ride"],
        "family":  ["a palace & museum visit", "a puppet-show / cultural evening", "an elephant/animal sanctuary visit", "a local market shopping stop"],
    },
    "metro": {
        "relaxed": ["a heritage-district walking tour", "a seafront promenade evening", "a museum & art-gallery visit", "a rooftop dinner"],
        "active":  ["a local train + market crawl", "a street-food trail", "a live-music / nightlife stop", "a bay cruise"],
        "family":  ["a science/city museum visit", "a promenade & amusement park stop", "a planetarium visit", "a mall + food-court evening"],
    },
    "heritage": {
        "relaxed": ["a sunrise monument visit (beat the crowds)", "a riverside evening walk", "a local craft workshop visit", "a heritage-hotel high tea"],
        "active":  ["a full monument-complex exploration", "a cycle-rickshaw old-town tour", "a river boat ride at dawn", "a food-trail walking tour"],
        "family":  ["a guided monument tour with a storyteller", "a boat ride on the river", "a local sweets tasting stop", "a cultural evening show"],
    },
}

DAY_THEME_TEMPLATES = [
    "Arrival & First Impressions",
    "Signature Sights",
    "Local Culture & Flavours",
    "Adventure & Nature",
    "Markets & Downtime",
    "Hidden Gems",
    "Departure Day",
]
