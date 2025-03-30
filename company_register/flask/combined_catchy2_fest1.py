import requests
from datetime import datetime
import icalendar
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from duckduckgo_search import DDGS

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def get_upcoming_festivals(count=5):
    today = datetime.today().date()
    ics_url = "https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"
    
    try:
        response = requests.get(ics_url)
        response.raise_for_status()
        calendar = icalendar.Calendar.from_ical(response.text)
        
        events = []
        for event in calendar.walk('vevent'):
            event_name = str(event.get('summary'))
            event_date = event.get('dtstart').dt
            if isinstance(event_date, datetime):  
                event_date = event_date.date()  
            if event_date >= today:
                events.append((event_date, event_name))
        
        events.sort()
        return events[:count] if events else None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching festival data: {e}")
        return None

def search_market_trends(domain_topic, max_results=5):
    ddgs = DDGS()
    query = f"{domain_topic} market trends 2024 OR industry growth OR latest news OR innovations"
    search_results = list(ddgs.text(query, max_results=max_results))
    extracted_results = [
        {"title": res.get("title", "No Title"), "content": res.get("body", "No Content")}
        for res in search_results
    ]
    return extracted_results if extracted_results else [{"title": "No results found", "content": "Try a different query"}]

# Get the next 10 festivals
upcoming_festivals = get_upcoming_festivals()
if upcoming_festivals:
    festival_names = [festival[1] for festival in upcoming_festivals]
else:
    festival_names = []

# Get market trends
trends = search_market_trends("events and celebrations", max_results=5)
trend_titles = [trend["title"] for trend in trends]

# Use Gemini AI to determine the most popular festival or trend
prompt = f"""
Based on the following upcoming festivals and trending topics, choose the most popular one.

Festivals: {', '.join(festival_names)}
Trends: {', '.join(trend_titles)}

Provide only the most relevant one.
"""
response = model.generate_content(prompt)
selected_topic = response.text.strip()

# Define product details
promoted_product = 'TV remotes'
company_name = 'Onida TV remotes'
company_description = 'Sells TV remotes'

# Generate advertisement content
ad_prompt = f"""
Generate a catchy advertisement for an Instagram post for my
product/service: {promoted_product}, which belongs to my company: {company_name}.

**Description:** {company_description}w
**Make it related to:** {selected_topic}.

Format your response exactly as follows:
1. Instagram Caption: [Your caption here]
2. Hashtags: [Your hashtags here]
3. Text on Image: [Your text here]
4. Description of Image: [Your description here]
"""

ad_response = model.generate_content(ad_prompt)
generated_text = ad_response.text

# Initialize dictionary for storing parsed data
data = {
    "caption": "",
    "hashtags": "",
    "text_on_image": "",
    "description_of_image": ""
}

# Improved parsing logic
current_section = None
sections = {
    "instagram caption:": "caption",
    "hashtags:": "hashtags",
    "text on image:": "text_on_image",
    "description of image:": "description_of_image"
}

# Process the text line by line
for line in generated_text.split('\n'):
    line = line.strip().lower()
    if not line:
        continue
        
    # Remove numbers and dots from the start of lines (e.g., "1. ", "2. ")
    line = line.lstrip('0123456789. ')
    
    # Check if this line is a section header
    for header, key in sections.items():
        if line.startswith(header):
            current_section = key
            # Remove the header from the line
            line = line[len(header):].strip()
            break
    
    # If we have a current section and there's content, add it to the data
    if current_section and line and not any(line.startswith(h) for h in sections.keys()):
        if data[current_section]:
            data[current_section] += " " + line
        else:
            data[current_section] = line

# Clean up the data
for key in data:
    data[key] = data[key].strip()

# Save as JSON
json_filename = "instagram_ad.json"
with open(json_filename, "w") as json_file:
    json.dump(data, json_file, indent=4)

# Print the data for verification
print(f"✅ JSON file saved: {json_filename}")
print("\nGenerated Content:")
print(generated_text)
print("\nParsed JSON Data:")
print(json.dumps(data, indent=4))
