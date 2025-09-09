#!/usr/bin/env python3
"""
Search and price comparison example
"""

from mimitfuelpy import Client
from mimitfuelpy.models.search.criteria.search_by_brand_criteria import SearchByBrandCriteria
from mimitfuelpy.models.enums.fuel_type import FuelType
from mimitfuelpy.models.enums.service_type import ServiceType


def find_cheapest_petrol(client, province):
    """Find cheapest petrol stations in a province"""
    criteria = SearchByBrandCriteria(
        province=province,
        fuelType=FuelType.PETROL.value,
        priceOrder="asc"
    )
    
    results = client.search.byBrand(criteria)
    if results.success and results.results:
        station = results.results[0]  # Cheapest
        if station.fuels:
            petrol = next((f for f in station.fuels if "benzina" in f.name.lower()), None)
            if petrol:
                return {
                    'station': station.name,
                    'brand': station.brand,
                    'price': petrol.price
                }
    return None


def compare_service_types(client, province):
    """Compare self-service vs full-service prices"""
    service_types = [
        (ServiceType.SELF.value, "Self-service"),
        (ServiceType.SERVED.value, "Full-service")
    ]
    
    comparison = {}
    
    for service_type, name in service_types:
        criteria = SearchByBrandCriteria(
            province=province,
            fuelType=FuelType.PETROL.value,
            serviceType=service_type
        )
        
        results = client.search.byBrand(criteria)
        if results.success:
            prices = []
            for station in results.results:
                if station.fuels:
                    for fuel in station.fuels:
                        if "benzina" in fuel.name.lower():
                            prices.append(fuel.price)
            
            if prices:
                comparison[name] = {
                    'stations': len(results.results),
                    'avg_price': sum(prices) / len(prices),
                    'min_price': min(prices)
                }
    
    return comparison


def main():
    try:
        client = Client()
        provinces = ["MI", "RM", "TO"]
        
        print("🏆 Cheapest petrol by city:")
        for province in provinces:
            cheapest = find_cheapest_petrol(client, province)
            if cheapest:
                print(f"{province}: {cheapest['station']} (€{cheapest['price']:.3f})")
        
        print("\n⛽ Service type comparison (Milan):")
        comparison = compare_service_types(client, "MI")
        for service_type, data in comparison.items():
            print(f"{service_type}: {data['stations']} stations, avg €{data['avg_price']:.3f}")
        
        # Price difference
        if 'Self-service' in comparison and 'Full-service' in comparison:
            diff = comparison['Full-service']['avg_price'] - comparison['Self-service']['avg_price']
            print(f"Full-service premium: €{diff:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()