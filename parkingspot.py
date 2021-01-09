class ParkingSpot:
    def __init__(self, address, latitude, longitude, parking_places, parking_places_dis):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.parking_places = parking_places
        self.parking_places_dis = parking_places_dis

    def __eq__(self, other):
        return other.address == self.address
