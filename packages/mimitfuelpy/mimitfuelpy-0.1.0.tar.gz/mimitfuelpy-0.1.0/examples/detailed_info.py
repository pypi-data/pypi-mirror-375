#!/usr/bin/env python3
"""
Get detailed station information with error handling
"""

from mimitfuelpy import Client
from mimitfuelpy.models.search.criteria.search_by_brand_criteria import SearchByBrandCriteria
from mimitfuelpy.utils.exceptions import MimitApiError


def get_station_details(client, station_id, station_name):
    """Get comprehensive station details"""
    try:
        details = client.registry.service_area(station_id)
        
        info = {
            'name': details.name,
            'address': details.address,
            'brand': details.brand,
            'phone': getattr(details, 'phoneNumber', None),
            'fuels': [],
            'services': []
        }
        
        if details.fuels:
            info['fuels'] = [{'name': f.name, 'price': f.price} for f in details.fuels]
        
        if details.services:
            info['services'] = [s.name for s in details.services]
        
        # Opening hours
        if hasattr(details, 'orariapertura') and details.orariapertura:
            info['has_hours'] = True
        else:
            info['has_hours'] = False
        
        return info
        
    except Exception as e:
        print(f"Error getting details for {station_name}: {e}")
        return None


def robust_search(client, province, max_retries=2):
    """Search with retry logic"""
    for attempt in range(max_retries):
        try:
            criteria = SearchByBrandCriteria(province=province)
            results = client.search.byBrand(criteria)
            
            if results.success:
                return results.results
            else:
                print(f"Search returned no results (attempt {attempt + 1})")
                
        except MimitApiError as e:
            print(f"API error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)  # Wait before retry
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    return []


def main():
    try:
        client = Client()
        
        # Robust search
        stations = robust_search(client, "MI")
        
        if stations:
            print(f"Found {len(stations)} stations")
            
            # Get details for first 2 stations
            print("\nDetailed information:")
            for station in stations[:2]:
                details = get_station_details(client, station.id, station.name)
                
                if details:
                    print(f"\n📍 {details['name']} ({details['brand']})")
                    print(f"   Address: {details['address']}")
                    
                    if details['phone']:
                        print(f"   Phone: {details['phone']}")
                    
                    print(f"   Fuels: {len(details['fuels'])}")
                    for fuel in details['fuels'][:3]:  # Show first 3
                        print(f"   • {fuel['name']}: €{fuel['price']}")
                    
                    if details['services']:
                        print(f"   Services: {', '.join(details['services'][:3])}")
                    
                    print(f"   Hours available: {'Yes' if details['has_hours'] else 'No'}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()