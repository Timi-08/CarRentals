"""
Sample data for FAST CARS: 10 brands and 30 vehicles.

Prices are example daily rental rates in naira. Change them in the admin
to match what FAST CARS really charges.
"""

BRANDS = [
    'Toyota', 'Honda', 'Lexus', 'Mercedes-Benz', 'Hyundai',
    'Kia', 'Nissan', 'Ford', 'Peugeot', 'Volkswagen',
]

# (brand, name, price per day, seats, fuel type, available, featured, description)
VEHICLES = [
    # Toyota
    ('Toyota', 'Corolla', '35000.00', 5, 'petrol', True, False,
     'Reliable, economical compact sedan that is easy to drive around the city.'),
    ('Toyota', 'Camry', '45000.00', 5, 'petrol', True, True,
     'Comfortable mid-size sedan with plenty of room for passengers and luggage.'),
    ('Toyota', 'Highlander', '80000.00', 7, 'petrol', True, True,
     'Spacious seven-seater SUV for families and group trips.'),
    ('Toyota', 'Hilux', '85000.00', 5, 'diesel', True, True,
     'Tough pickup truck suited to rough roads and heavy loads.'),
    ('Toyota', 'Hiace Bus', '90000.00', 14, 'diesel', True, False,
     'Fourteen-seater bus for events, staff transport and long-distance group travel.'),
    ('Toyota', 'Prius', '50000.00', 5, 'hybrid', True, False,
     'Hybrid hatchback that uses very little fuel, ideal for daily driving.'),

    # Honda
    ('Honda', 'Civic', '38000.00', 5, 'petrol', True, False,
     'Sporty and efficient sedan with a comfortable ride.'),
    ('Honda', 'Accord', '48000.00', 5, 'petrol', False, False,
     'Smooth, roomy executive sedan for business trips.'),
    ('Honda', 'CR-V', '65000.00', 5, 'petrol', True, False,
     'Practical compact SUV with generous boot space.'),

    # Lexus
    ('Lexus', 'ES 350', '85000.00', 5, 'petrol', True, False,
     'Quiet, luxurious sedan for airport pickups and special occasions.'),
    ('Lexus', 'RX 350', '120000.00', 5, 'petrol', True, True,
     'Premium SUV with a plush interior and a smooth ride.'),
    ('Lexus', 'RX 450h', '135000.00', 5, 'hybrid', True, False,
     'Luxury hybrid SUV that combines comfort with lower fuel use.'),

    # Mercedes-Benz
    ('Mercedes-Benz', 'C300', '110000.00', 5, 'petrol', True, True,
     'Elegant executive sedan for weddings, business and VIP transport.'),
    ('Mercedes-Benz', 'GLE 350', '200000.00', 5, 'petrol', False, False,
     'Top-of-the-range luxury SUV for guests who want the very best.'),
    ('Mercedes-Benz', 'Sprinter Bus', '140000.00', 15, 'diesel', True, False,
     'Fifteen-seater bus for corporate shuttles and large groups.'),

    # Hyundai
    ('Hyundai', 'Elantra', '32000.00', 5, 'petrol', True, False,
     'Stylish, affordable sedan that is good value for everyday trips.'),
    ('Hyundai', 'Tucson', '60000.00', 5, 'petrol', True, False,
     'Modern compact SUV with a comfortable cabin.'),
    ('Hyundai', 'Ioniq 5', '95000.00', 5, 'electric', True, True,
     'Fully electric crossover with no fuel costs and quiet, smooth driving.'),

    # Kia
    ('Kia', 'Rio', '28000.00', 5, 'petrol', True, False,
     'Small, budget-friendly car that is easy to park and cheap to run.'),
    ('Kia', 'Sportage', '58000.00', 5, 'petrol', True, False,
     'Comfortable compact SUV for city and highway driving.'),
    ('Kia', 'Sorento', '75000.00', 7, 'petrol', True, False,
     'Seven-seater SUV with room for the whole family.'),

    # Nissan
    ('Nissan', 'Sentra', '30000.00', 5, 'petrol', False, False,
     'Simple, dependable sedan that is economical on fuel.'),
    ('Nissan', 'Pathfinder', '80000.00', 7, 'petrol', True, False,
     'Large seven-seater SUV with plenty of space for passengers and bags.'),

    # Ford
    ('Ford', 'Ranger', '85000.00', 5, 'diesel', True, False,
     'Strong double-cab pickup for work and off-road trips.'),
    ('Ford', 'Explorer', '90000.00', 7, 'petrol', True, False,
     'Full-size seven-seater SUV with a powerful engine.'),

    # Peugeot
    ('Peugeot', '301', '25000.00', 5, 'petrol', True, False,
     'Affordable, spacious sedan, our most budget-friendly choice.'),
    ('Peugeot', '508', '55000.00', 5, 'petrol', True, False,
     'Stylish executive saloon with a refined interior.'),

    # Volkswagen
    ('Volkswagen', 'Golf', '33000.00', 5, 'petrol', True, False,
     'Compact hatchback that is nimble in traffic.'),
    ('Volkswagen', 'Passat', '45000.00', 5, 'petrol', True, False,
     'Spacious, comfortable sedan for longer journeys.'),
    ('Volkswagen', 'Tiguan', '62000.00', 5, 'petrol', True, False,
     'Practical compact SUV with a solid, well-built feel.'),
]

VEHICLE_IMAGES = {
    ('Ford', 'Explorer'): 'vehicles/FordExplorer.png',
    ('Ford', 'Ranger'): 'vehicles/FordRanger.avif',
    ('Honda', 'Accord'): 'vehicles/HondaAccord.png',
}
