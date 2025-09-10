import requests
import json
import logging

SEFARIA_API_BASE_URL = "https://sefaria.org"

def get_request_json_data(endpoint, ref=None, param=None):
    """
    Helper function to make GET requests to the Sefaria API and parse the JSON response.
    """
    url = f"{SEFARIA_API_BASE_URL}/{endpoint}"

    if ref:
        url += f"{ref}"

    if param:
        url += f"?{param}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

def get_commentary_text(ref):
    """
    Retrieves the title and text of a commentary.
    """
    data = get_request_json_data("api/v3/texts/", ref)

    if data and "versions" in data and len(data['versions']) > 0:
        title = data['title']
        text = data['versions'][0]['text']
        return title, text
    else:
        print(f"Could not retrieve commentary text for {ref}")
        return None, None

def get_parasha_data():
    """
    Retrieves the weekly Parasha data using the Calendars API.
    """
    data = get_request_json_data("api/calendars")

    if data:
        calendar_items = data.get('calendar_items', [])
        for item in calendar_items:
            if item.get('title', {}).get('en') == 'Parashat Hashavua':
                parasha_ref = item.get('ref')
                parasha_name = item.get('displayValue', {}).get('en')
                return parasha_ref, parasha_name
    
    print("Could not retrieve Parasha data.")
    return None, None

def get_first_verse(parasha_ref):
    """
    Extracts the first verse from the Parasha range.
    """
    if parasha_ref:
        return parasha_ref.split("-")[0]
    else:
        return None

def get_hebrew_text(parasha_ref):
    """
    Retrieves the Hebrew text and version title for the given verse.
    """
    data = get_request_json_data("api/v3/texts/", parasha_ref)

    if data and "versions" in data and len(data['versions']) > 0:
        he_pasuk = data['versions'][0]['text']
        return  he_pasuk
    else:
        print(f"Could not retrieve Hebrew text for {parasha_ref}")
        return None

def get_english_text(parasha_ref):
    """
    Retrieves the English text and version title for the given verse.
    """
    data = get_request_json_data("api/v3/texts/", parasha_ref, "version=english")

    if data and "versions" in data and len(data['versions']) > 0:
        en_vtitle = data['versions'][0]['versionTitle']
        en_pasuk = data['versions'][0]['text']
        return en_vtitle, en_pasuk
    else:
        print(f"Could not retrieve English text for {parasha_ref}")
        return None, None

async def get_commentaries(parasha_ref)-> list[str]:
    """
    Retrieves and filters commentaries on the given verse.
    """
    data = get_request_json_data("api/related/", parasha_ref)

    commentaries = []
    if data and "links" in data:
        for linked_text in data["links"]:
            if linked_text.get('type') == 'commentary':
                commentaries.append(linked_text.get('sourceHeRef'))

    return commentaries

async def get_text(reference: str) -> str:
    """
    Retrieves the text for a given reference.
    """
    return str(get_hebrew_text(reference))

async def get_daily_learnings(
    diaspora: bool = True,
    custom: str = None,
    year: int = None,
    month: int = None,
    day: int = None,
    timezone: str = None
) -> str:
    """
    Get the daily or weekly learning schedule for a given date from Sefaria's calendar API.
    
    Args:
        diaspora (bool, optional): When True, returns weekly Torah reading for diaspora. 
                                 When False, returns Torah reading for Israel. Defaults to True.
        custom (str, optional): If available, the weekly Haftarah will be returned for the selected custom.
        year (int, optional): Year for the date. Must be used with month and day, or API falls back to current date.
        month (int, optional): Month for the date. Must be used with year and day, or API falls back to current date.
        day (int, optional): Day for the date. Must be used with year and month, or API falls back to current date.
        timezone (str, optional): Timezone name in accordance with IANA Standards. 
                                Defaults to client's timezone if not specified.
    
    Returns:
        str: Formatted daily/weekly learning schedule
    """
    url = "https://www.sefaria.org/api/calendars"
    
    # Build query parameters
    params = {}
    
    # Add diaspora parameter
    params["diaspora"] = "1" if diaspora else "0"
    
    # Add custom parameter if provided
    if custom:
        params["custom"] = custom
    
    # Add date parameters if all three are provided
    if year is not None and month is not None and day is not None:
        params["year"] = year
        params["month"] = month
        params["day"] = day
    
    # Add timezone parameter if provided
    if timezone:
        params["timezone"] = timezone
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        logging.debug(f"Sefaria's Calendar API response: {response.text}")
        
        # Parse JSON response
        data = response.json()
        
        # Format the results
        result_lines = []
        
        # Add header with date and timezone
        date = data.get("date", "Unknown date")
        tz = data.get("timezone", "Unknown timezone")
        result_lines.append(f"Learning Schedule for {date} ({tz})")
        result_lines.append("=" * 50)
        
        # Process calendar items
        calendar_items = data.get("calendar_items", [])
        
        for item in calendar_items:
            title_en = item.get("title", {}).get("en", "Unknown")
            title_he = item.get("title", {}).get("he", "")
            
            display_en = item.get("displayValue", {}).get("en", "")
            display_he = item.get("displayValue", {}).get("he", "")
            
            ref = item.get("ref", "")
            he_ref = item.get("heRef", "")
            
            category = item.get("category", "")
            order = item.get("order", 0)
            
            # Format each learning item
            result_lines.append(f"\n{order}. {title_en} ({title_he})")
            result_lines.append(f"   Text: {display_en} ({display_he})")
            result_lines.append(f"   Reference: {ref}")
            if he_ref:
                result_lines.append(f"   Hebrew Reference: {he_ref}")
            if category:
                result_lines.append(f"   Category: {category}")
            
            # Add description if available
            description = item.get("description", {})
            if description:
                desc_en = description.get("en", "")
                if desc_en:
                    # Limit description length for readability
                    if len(desc_en) > 200:
                        desc_en = desc_en[:200] + "..."
                    result_lines.append(f"   Description: {desc_en}")
            
            # Add extra details if available (like aliyot for Torah reading)
            extra_details = item.get("extraDetails", {})
            if extra_details:
                aliyot = extra_details.get("aliyot", [])
                if aliyot:
                    result_lines.append(f"   Aliyot: {', '.join(aliyot[:3])}..." if len(aliyot) > 3 else f"   Aliyot: {', '.join(aliyot)}")
        
        if not calendar_items:
            result_lines.append("No learning items found for this date.")
        
        return "\n".join(result_lines)
    
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse JSON response: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Error during calendar API request: {str(e)}"

async def search_texts(query: str, slop: int =2, filters=None, size=10):
    """
    Search for texts in the Sefaria library.
    
    Args:
        query (str): The search query
        slop (int, optional): The maximum distance between each query word in the resulting document. 0 means an exact match must be found. defaults to 2
        filters (list, optional): Filters to apply to the text path in English (Examples: "Shulkhan Arukh", "maimonides", "talmud").
        size (int, optional): Number of results to return. defaults to 10.
        
    Returns:
        str: Formatted search results
    """
    # Use the www subdomain as specified in the documentation
    url = "https://www.sefaria.org/api/search-wrapper"
    
    # Build the request payload
    payload = {
        "query": query,
        "type": "text",
        "field":  "naive_lemmatizer",
        "size": size,
  "source_proj": True,
        "sort_fields": [
    "pagesheetrank"
  ],
  "sort_method": "score",
        "slop": slop,
     
    }
    if filters:
        payload["filters"] = filters

    
    # Make the POST request
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        logging.debug(f"Sefaria's Search API response: {response.text}")
        
        # Parse JSON response
        data = response.json()
        
        print(data)
        
        # Format the results
        results = []
        
        # Check if we have hits in the response
        if "hits" in data and "hits" in data["hits"]:
            # Get the actual total hits count
            total_hits = data["hits"].get("total", 0)
            # Handle different response formats
            if isinstance(total_hits, dict) and "value" in total_hits:
                total_hits = total_hits["value"]
         
            # Process each hit
            for hit in data["hits"]["hits"]:
                source = hit["_source"]
                ref = source["ref"]
                heRef = source["heRef"]
                
                # Get the content snippet
                text_snippet = ""
                
                # Get highlighted text if available (this contains the search term highlighted)
                if "highlight" in hit:
                    for field_name, highlights in hit["highlight"].items():
                        if highlights and len(highlights) > 0:
                            # Join multiple highlights with ellipses
                            text_snippet = " [...] ".join(highlights)
                            break
                
                # If no highlight, use content from the source
                if not text_snippet:
                    # Try different fields that might contain content
                    for field_name in ["naive_lemmatizer", "exact"]:
                        if field_name in source and source[field_name]:
                            content = source[field_name]
                            if isinstance(content, str):
                                # Limit to a reasonable snippet length
                                text_snippet = content[:300] + ("..." if len(content) > 300 else "")
                                break
             
                # Add the formatted result
                results.append(f"Reference: {ref}\n Hebrew Reference: {heRef}\n Highlight: {text_snippet}\n")
        
        # Return a message if no results were found
        if len(results) <= 1:
            return f"No results found for '{query}'."
        logging.debug(f"formated results: {results}")
        return "\n".join(results)
    
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse JSON response: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Error during search API request: {str(e)}"
