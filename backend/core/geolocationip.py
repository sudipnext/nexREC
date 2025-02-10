import requests
from typing import Dict, Optional

def get_location_from_ip(ip_address: str) -> Optional[Dict]:
    """
    Fetch geolocation data for a given IP address using ip-api.com.
    
    Args:
        ip_address (str): The IP address to lookup
        
    Returns:
        Optional[Dict]: Dictionary containing location data or None if request fails
        
    Example response:
    {
        'status': 'success',
        'country': 'Nepal',
        'countryCode': 'NP',
        'region': 'P3',
        'regionName': 'Bagmati',
        'city': 'Kathmandu',
        'zip': '44600',
        'lat': 27.7167,
        'lon': 85.3167,
        'timezone': 'Asia/Kathmandu',
        'isp': 'WorldLink Communications',
        'org': 'Worldlink Communications',
        'as': 'AS17501 WorldLink Communications Pvt Ltd',
        'query': '27.34.66.126'
    }
    """
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get('status') == 'success':
            return data
        return None
        
    except (requests.RequestException, ValueError) as e:
        # Handle any network or JSON parsing errors
        print(f"Error fetching location data: {e}")
        return None
    


import requests

def get_client_ip(request):
    """Get client's real IP address with fallback to external service for local development"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR'))
    
    # If localhost/127.0.0.1, try to get real IP using external service
    if ip in ['127.0.0.1', 'localhost']:
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            if response.status_code == 200:
                return response.json()['ip']
        except requests.RequestException:
            try:
                response = requests.get('https://api64.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    return response.json()['ip']
            except requests.RequestException:
                pass
    
    return ip



