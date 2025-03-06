from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
import random

class RestaurantTools:
    def __init__(self, data_path: str = None):
        if data_path is None:
            # Default to the data directory relative to the app directory
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "restaurants.json")
        self.data_path = data_path
        self._load_data()
        
    def _load_data(self):
        """Load restaurant data from JSON file."""
        try:
            with open(self.data_path, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"Error loading restaurant data: {str(e)}")
            # Initialize with empty data if file cannot be loaded
            self.data = {"restaurants": []}

    def search_restaurants(self, 
                         cuisine: Optional[str] = None,
                         location: Optional[str] = None,
                         min_rating: float = 0.0,
                         price_range: Optional[str] = None,
                         ambiance: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for restaurants based on given criteria.
        """
        results = []
        
        # Handle edge case of empty restaurant data
        if not self.data or "restaurants" not in self.data or not self.data["restaurants"]:
            return []
            
        for restaurant in self.data["restaurants"]:
            matches = True
            
            # Make cuisine matching case-insensitive and partial
            if cuisine and cuisine.strip():  # Check if cuisine is not empty after stripping
                if not restaurant.get("cuisine") or cuisine.lower() not in restaurant["cuisine"].lower():
                    matches = False
                    
            # Make location matching case-insensitive and partial
            if location and location.strip():  # Check if location is not empty after stripping
                if not restaurant.get("location") or (
                    location.lower() not in restaurant["location"].lower() and 
                    restaurant["location"].lower() not in location.lower()
                ):
                    matches = False
                    
            # Handle rating with a default if missing
            restaurant_rating = restaurant.get("rating", 0.0)
            if restaurant_rating < min_rating:
                matches = False
                
            # Handle price range matching
            if price_range and price_range.strip():  # Check if price_range is not empty after stripping
                if not restaurant.get("price_range") or price_range != restaurant["price_range"]:
                    matches = False
                    
            # Handle ambiance matching with protection against missing values
            if ambiance and any(a.strip() for a in ambiance):  # Check if any ambiance value is not empty after stripping
                if not restaurant.get("ambiance") or not any(
                    a.lower() in [x.lower() for x in restaurant["ambiance"]] 
                    for a in ambiance if a.strip()
                ):
                    matches = False
            
            if matches:
                results.append(restaurant)
        
        return results

    def check_availability(self,
                          restaurant_id: str,
                          party_size: int,
                          date: str,
                          time: str) -> Dict[str, Any]:
        """
        Check if a restaurant has availability for the given party size and time.
        For demo purposes, this uses a simple algorithm and doesn't maintain real state.
        """
        # Input validation
        if not restaurant_id:
            return {"available": False, "reason": "Restaurant ID is required"}
            
        try:
            party_size = int(party_size)
            if party_size <= 0:
                return {"available": False, "reason": "Party size must be a positive number"}
        except (ValueError, TypeError):
            return {"available": False, "reason": "Invalid party size format. Please provide a number."}
        
        if not date or not time:
            return {"available": False, "reason": "Both date and time are required"}
        
        # Find restaurant
        restaurant = None
        for r in self.data.get("restaurants", []):
            if r.get("id") == restaurant_id:
                restaurant = r
                break
        
        if not restaurant:
            return {"available": False, "reason": f"Restaurant with ID {restaurant_id} not found"}

        # Parse date and time
        try:
            dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            # Check if date is in the past
            if dt < datetime.now():
                return {"available": False, "reason": "Cannot make reservations for past dates"}
                
            day = dt.strftime("%A").lower()
            
            # Check if the day exists in hours
            if not restaurant.get("hours") or day not in restaurant.get("hours", {}):
                return {"available": False, "reason": f"No hours information available for {day}"}
            
            # Check if restaurant is open
            hours = restaurant["hours"][day]
            try:
                open_time, close_time = hours.split("-")
            except ValueError:
                return {"available": False, "reason": f"Invalid hours format for {day}"}
                
            current_time = dt.strftime("%H:%M")
            
            if current_time < open_time or current_time > close_time:
                return {
                    "available": False,
                    "reason": f"Restaurant is closed at this time. Hours on {day}: {hours}"
                }

            # Check if we can accommodate the party size
            if not restaurant.get("seating") or not restaurant["seating"].get("table_types"):
                return {"available": False, "reason": "No seating information available"}
                
            seating = restaurant["seating"]["table_types"]
            
            try:
                total_seats = sum(int(k.split("_")[0]) * v for k, v in seating.items() 
                                if k != "private_room" and k.split("_")[0].isdigit())
            except (ValueError, IndexError, KeyError):
                return {"available": False, "reason": "Invalid seating configuration"}
            
            if party_size > total_seats:
                return {
                    "available": False,
                    "reason": f"Cannot accommodate party of {party_size}. Maximum capacity is {total_seats}."
                }
                
            # For demo purposes, randomly determine if there's availability
            # In a real system, this would check actual bookings
            availability_chance = 0.7  # 70% chance of availability
            available = party_size <= 8 or random.random() < availability_chance
            
            if not available:
                return {
                    "available": False,
                    "reason": "All tables are booked at this time"
                }
            
            return {
                "available": True,
                "restaurant_name": restaurant["name"],
                "party_size": party_size,
                "date": date,
                "time": time,
                "confirmation_code": f"TEMP-{random.randint(1000, 9999)}"
            }
            
        except ValueError as e:
            return {"available": False, "reason": f"Invalid date or time format. Please use YYYY-MM-DD and HH:MM formats. Error: {str(e)}"}
        except Exception as e:
            return {"available": False, "reason": f"An error occurred: {str(e)}"}

    def make_reservation(self,
                       restaurant_id: str,
                       customer_name: str,
                       email: str,
                       phone: str,
                       party_size: int,
                       date: str,
                       time: str,
                       special_requests: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a reservation at the specified restaurant.
        For demo purposes, this doesn't actually persist the reservation.
        """
        # Input validation
        if not restaurant_id or not customer_name or not email or not phone:
            missing_fields = []
            if not restaurant_id: missing_fields.append("restaurant_id")
            if not customer_name: missing_fields.append("customer_name")
            if not email: missing_fields.append("email")
            if not phone: missing_fields.append("phone")
            return {"success": False, "reason": f"Missing required fields: {', '.join(missing_fields)}"}
            
        # Email validation (basic)
        if '@' not in email or '.' not in email:
            return {"success": False, "reason": "Invalid email format"}
            
        # Phone validation (basic)
        if not any(c.isdigit() for c in phone) or len(phone) < 8:
            return {"success": False, "reason": "Invalid phone number"}
            
        try:
            party_size = int(party_size)
            if party_size <= 0:
                return {"success": False, "reason": "Party size must be a positive number"}
        except (ValueError, TypeError):
            return {"success": False, "reason": "Invalid party size format. Please provide a number."}
            
        if not date or not time:
            return {"success": False, "reason": "Both date and time are required"}
            
        # First, check availability
        availability_result = self.check_availability(
            restaurant_id=restaurant_id,
            party_size=party_size,
            date=date,
            time=time
        )
        
        if not availability_result.get("available", False):
            return {
                "success": False, 
                "reason": f"Restaurant is not available: {availability_result.get('reason', 'Unknown reason')}"
            }
        
        # Find restaurant name
        restaurant_name = "Restaurant"
        for r in self.data.get("restaurants", []):
            if r.get("id") == restaurant_id:
                restaurant_name = r.get("name", "Restaurant")
                break
        
        # In a real system, this would save to a database
        confirmation_code = f"RES-{random.randint(10000, 99999)}"
        
        return {
            "success": True,
            "confirmation_code": confirmation_code,
            "restaurant_name": restaurant_name,
            "customer_name": customer_name,
            "party_size": party_size,
            "date": date,
            "time": time,
            "special_requests": special_requests if special_requests else "None",
            "message": f"Reservation confirmed for {customer_name} at {restaurant_name} on {date} at {time} for {party_size} people."
        }

    def get_restaurant_details(self, restaurant_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific restaurant.
        """
        if not restaurant_id:
            return {"success": False, "reason": "Restaurant ID is required"}
            
        for restaurant in self.data.get("restaurants", []):
            if restaurant.get("id") == restaurant_id:
                # Format hours for better readability
                formatted_hours = {}
                if "hours" in restaurant:
                    for day, hours in restaurant["hours"].items():
                        formatted_hours[day.capitalize()] = hours
                
                # Format seating for better readability
                formatted_seating = {}
                if restaurant.get("seating") and restaurant["seating"].get("table_types"):
                    for table_type, count in restaurant["seating"]["table_types"].items():
                        if table_type == "private_room":
                            formatted_seating["Private Rooms"] = count
                        else:
                            try:
                                seats = table_type.split("_")[0]
                                formatted_seating[f"{seats}-Person Tables"] = count
                            except (IndexError, ValueError):
                                formatted_seating[table_type] = count
                
                details = {
                    "success": True,
                    "id": restaurant.get("id", ""),
                    "name": restaurant.get("name", "Unknown Restaurant"),
                    "cuisine": restaurant.get("cuisine", "Various"),
                    "location": restaurant.get("location", "Unknown Location"),
                    "address": restaurant.get("address", "Address not available"),
                    "rating": restaurant.get("rating", "Not rated"),
                    "price_range": restaurant.get("price_range", "₹"),
                    "hours": formatted_hours,
                    "ambiance": restaurant.get("ambiance", []),
                    "features": restaurant.get("features", []),
                    "seating": formatted_seating,
                    "total_capacity": restaurant.get("seating", {}).get("total_capacity", 0) if restaurant.get("seating") else 0
                }
                return details
        
        return {"success": False, "reason": f"Restaurant with ID {restaurant_id} not found"}

# Define the available tools for the LLM
AVAILABLE_TOOLS = {
    "search_restaurants": {
        "name": "search_restaurants",
        "description": "Search for restaurants based on criteria like cuisine, location, rating, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "cuisine": {"type": "string", "description": "Type of cuisine (e.g., Italian, Japanese)"},
                "location": {"type": "string", "description": "Area or district name"},
                "min_rating": {"type": "number", "description": "Minimum rating (0-5)"},
                "price_range": {"type": "string", "description": "Price range (₹, ₹₹, ₹₹₹, or ₹₹₹₹)"},
                "ambiance": {"type": "array", "items": {"type": "string"}, "description": "Desired ambiance types"}
            }
        }
    },
    "check_availability": {
        "name": "check_availability",
        "description": "Check if a restaurant has availability for a given party size and time",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string", "description": "ID of the restaurant"},
                "party_size": {"type": "integer", "description": "Number of people"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time in HH:MM format"}
            },
            "required": ["restaurant_id", "party_size", "date", "time"]
        }
    },
    "make_reservation": {
        "name": "make_reservation",
        "description": "Make a reservation at a restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string", "description": "ID of the restaurant"},
                "customer_name": {"type": "string", "description": "Name for the reservation"},
                "email": {"type": "string", "description": "Email for the reservation"},
                "phone": {"type": "string", "description": "Phone number for the reservation"},
                "party_size": {"type": "integer", "description": "Number of people"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time in HH:MM format"},
                "special_requests": {"type": "string", "description": "Special requests for the reservation"}
            },
            "required": ["restaurant_id", "customer_name", "email", "phone", "party_size", "date", "time"]
        }
    },
    "get_restaurant_details": {
        "name": "get_restaurant_details",
        "description": "Get detailed information about a specific restaurant",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "string", "description": "ID of the restaurant"}
            },
            "required": ["restaurant_id"]
        }
    }
} 