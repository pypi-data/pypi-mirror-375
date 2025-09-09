#!/usr/bin/env python3
"""
Basic usage example - getting started with mimitfuelpy
"""

from mimitfuelpy import Client
from mimitfuelpy.models.search.criteria.search_by_brand_criteria import SearchByBrandCriteria
from mimitfuelpy.models.enums.fuel_type import FuelType


def main():
    try:
        client = Client()
        
        # Get brands
        brands = client.registry.brands()
        print(f"Found {len(brands)} fuel brands")
        
        # Get regions
        regions = client.registry.regions()
        lombardy = next((r for r in regions if "LOMBARD" in r.name.upper()), None)
        print(f"Found region: {lombardy.name}")
        
        # Search stations in Milan
        criteria = SearchByBrandCriteria(province="MI")
        results = client.search.byBrand(criteria)
        
        if results.success:
            print(f"Found {len(results.results)} stations in Milan")
            
            # Show first 3 stations with prices
            for i, station in enumerate(results.results[:3], 1):
                print(f"{i}. {station.name} ({station.brand})")
                if station.fuels:
                    for fuel in station.fuels[:2]:  # Show first 2 fuels
                        print(f"   {fuel.name}: €{fuel.price}")
                print()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()