import os

config = {
    "goibibo":{
        "app_id":os.environ.get("GOIBIBO_APP_ID", ""),
        "app_key":os.environ.get("GOIBIBO_APP_KEY", ""),
        "urls":{
            "base_url":"http://developer.goibibo.com",
            "flight_search":"/api/search/",
            "min_fare":"/api/stats/minfare/",
            "bus_search":"/api/bus/search/",
            "bus_seat_layout":"/api/bus/seatmap/",
            "hotel_search":"/api/voyager/get_hotels_by_cityid",
            "hotel_details":"/api/voyager/",
            "hotel_search_with_price":"/api/cyclone/",
            "approved_hotel_reviews":"/api/HotelReviews/forWeb",
            "bifurcated_hotel_rating":"/api/Hotels/getRatings",
        }
    }
}