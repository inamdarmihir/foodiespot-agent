import json
import os
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from .tools import RestaurantTools, AVAILABLE_TOOLS
import re
import time

class FoodieSpotAgent:
    def __init__(self, openai_api_key: str, openai_model: str, track_performance: bool = False):
        """Initialize the FoodieSpot agent."""
        self.api_key = openai_api_key
        self.model = openai_model
        self.tools = RestaurantTools()
        self.conversation_history = []
        self.track_performance = track_performance
        if track_performance:
            self.metrics = {
                "total_queries": 0,
                "successful_searches": 0,
                "reservations_made": 0,
                "failed_queries": 0,
                "response_times": []
            }
        
    # Add PII detection method
    def _detect_pii(self, text: str) -> Tuple[bool, str]:
        """
        Detect personally identifiable information (PII) in user inputs.
        Returns (contains_pii, processed_text)
        """
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}\b',
            "credit_card": r'\b(?:\d{4}[\s-]?){4}|\b(?:\d{4}[\s-]?){3}\d{4}\b',
            "ssn": r'\b\d{3}[\s-]?\d{2}[\s-]?\d{4}\b',
            "address": r'\b\d+\s+[A-Za-z0-9\s,]+(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|parkway|pkwy|circle|cir|boulevard|blvd)\b'
        }
        
        pii_detected = False
        processed_text = text
        
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                pii_detected = True
                # Redact PII for processing
                processed_text = re.sub(pattern, f"[REDACTED {pii_type.upper()}]", processed_text, flags=re.IGNORECASE)
                
        return pii_detected, processed_text
        
    # Add input validation method
    def _validate_input(self, user_message: str) -> Tuple[bool, str]:
        """
        Validate user input for inappropriate content and PII.
        Returns (is_valid, message)
        """
        # Check for empty or extremely short inputs
        if not user_message or len(user_message.strip()) < 2:
            return False, "Please provide a valid request."
            
        # Check for PII
        contains_pii, processed_text = self._detect_pii(user_message)
        
        # Check length (prevent extremely long inputs)
        if len(user_message) > 1000:
            return False, "Your message is too long. Please keep your request concise."
            
        # Basic profanity filter - check for exact word matches with word boundaries
        profanity_words = ["fuck", "shit", "ass", "bitch", "dick", "pussy", "cunt"]
        contains_profanity = any(re.search(r'\b' + word + r'\b', user_message.lower()) for word in profanity_words)
        
        if contains_profanity:
            return False, "Please refrain from using inappropriate language."
            
        if contains_pii:
            # If PII is detected, return the processed (redacted) text
            return True, processed_text
            
        return True, user_message
        
    # Add output validation method
    def _validate_output(self, response: str) -> Tuple[bool, str]:
        """
        Validate the output to ensure it doesn't contain inappropriate content.
        Returns (is_valid, processed_response)
        """
        # Check for empty or too short responses
        if not response or len(response.strip()) < 10:
            return False, "I apologize, but I couldn't generate a proper response. Please try again."
            
        # Basic profanity filter - check for exact word matches with word boundaries
        profanity_words = ["fuck", "shit", "ass", "bitch", "dick", "pussy", "cunt"]
        contains_profanity = any(re.search(r'\b' + word + r'\b', response.lower()) for word in profanity_words)
        
        if contains_profanity:
            return False, "I apologize, but I cannot provide the generated response due to inappropriate content. Please ask a different question."
            
        return True, response
        
    def _format_restaurant_results(self, restaurants: List[Dict[str, Any]]) -> str:
        """
        Format the restaurant search results into a nice string.
        """
        if not restaurants:
            return "No restaurants found matching your criteria."
            
        result = f"Found {len(restaurants)} restaurants:\n\n"
        
        for i, restaurant in enumerate(restaurants, 1):
            try:
                name = restaurant.get("name", "Unknown Restaurant")
                cuisine = restaurant.get("cuisine", "Various")
                location = restaurant.get("location", "Unknown Location")
                rating = restaurant.get("rating", "Not rated")
                price_range = restaurant.get("price_range", "₹")
                ambiance_list = restaurant.get("ambiance", [])
                ambiance = ", ".join(ambiance_list) if ambiance_list else "Not specified"
                
                result += f"**{i}. {name}** (ID: {restaurant.get('id', 'unknown')})\n"
                result += f"   - Cuisine: {cuisine}\n"
                result += f"   - Location: {location}\n"
                result += f"   - Rating: {rating}/5\n"
                result += f"   - Price: {price_range}\n"
                result += f"   - Ambiance: {ambiance}\n"
                
                # Add address if available
                if restaurant.get("address"):
                    result += f"   - Address: {restaurant['address']}\n"
                    
                # Add features if available
                if restaurant.get("features") and len(restaurant["features"]) > 0:
                    features = ", ".join(restaurant["features"])
                    result += f"   - Features: {features}\n"
                
                # Only add a blank line if this isn't the last restaurant
                if i < len(restaurants):
                    result += "\n"
            except Exception as e:
                # In case of any formatting error, add a simpler entry
                result += f"**{i}. {restaurant.get('name', 'Restaurant')}** (Error formatting details: {str(e)})\n\n"
                
        # Add instructions on how to use the results
        result += "\nTo get more details, ask about a specific restaurant by name or ID."
        result += "\nTo make a reservation, let me know which restaurant you're interested in."
        
        return result
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        """
        try:
            # Check if this message contains enriched context
            system_context = None
            if "[System Context Information:" in user_message:
                # Split the message and extract the context
                parts = user_message.split("[System Context Information:", 1)
                user_content = parts[0].strip()
                system_context = parts[1].strip().rstrip("]")
                # Use the original message without the system context
                user_message = user_content
            
            # Validate input
            is_valid_input, processed_message = self._validate_input(user_message)
            
            if not is_valid_input:
                return processed_message  # Return error message
                
            # Start performance tracking if enabled
            if self.track_performance:
                start_time = time.time()
                self.metrics["total_queries"] += 1
                
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": processed_message
            })
            
            # Build the system message with enhanced context if available
            base_system_message = """You are FoodieSpot's AI reservation assistant. Your goal is to help users find restaurants and make reservations.
                You have access to tools for searching restaurants, checking availability, and making reservations.
                Be friendly and helpful, and guide users through the process step by step.
                Always provide relevant details about restaurants when discussing them.
                If you need to make a reservation, make sure to get all necessary information first.
                
                When searching for restaurants:
                1. Try to understand the user's specific requirements, including variations in how they might phrase their request.
                2. If no exact matches are found, suggest broadening the search criteria.
                3. Always offer alternatives if available.
                4. Use a min_rating of 4.0 for fine dining searches.
                5. If you're not confident in the results, acknowledge this to the user.
                6. Handle vague queries by asking clarifying questions rather than making assumptions.
                
                Security and privacy guidelines:
                1. Never collect or prompt for personally identifiable information (PII) beyond what's needed for a reservation.
                2. When asking for personal information, explain clearly why it's needed.
                3. Any detected PII will be automatically redacted in the system.
                4. Do not engage with inappropriate requests or content.
                
                If a user asks for anything outside the scope of restaurant reservations, politely redirect them.
                """
                
            # Add any system context information if available
            if system_context:
                base_system_message += f"\n\nImportant context information: {system_context}\n"
                base_system_message += """
                Use this context information intelligently:
                - If you know the user's name, address them by name.
                - If you have date and time information, use it to streamline the reservation process.
                - If you already have the user's contact information, don't ask for it again.
                - If you know the party size, use it when checking availability.
                
                When checking availability or making a reservation:
                - For date references like "this weekend", "tomorrow", use the exact date from the context.
                - Use the current time to suggest appropriate reservation times.
                """
                
            # System message
            system_message = {
                "role": "system",
                "content": base_system_message
            }
            
            # Available tools
            available_functions = {
                "search_restaurants": self.tools.search_restaurants,
                "check_availability": self.tools.check_availability,
                "make_reservation": self.tools.make_reservation,
                "get_restaurant_details": self.tools.get_restaurant_details
            }
            
            # Define tools for OpenAI
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_restaurants",
                        "description": "Search for restaurants based on criteria like cuisine, location, rating, etc.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "cuisine": {"type": "string", "description": "Type of cuisine (e.g., Italian, Japanese)"},
                                "location": {"type": "string", "description": "Location or neighborhood"},
                                "min_rating": {"type": "number", "description": "Minimum rating (0-5)"},
                                "price_range": {"type": "string", "description": "Price range (₹, ₹₹, ₹₹₹, or ₹₹₹₹)"},
                                "ambiance": {"type": "array", "items": {"type": "string"}, "description": "Desired ambiance (e.g., Romantic, Family-friendly)"}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "check_availability",
                        "description": "Check if a restaurant has availability for a given date, time, and party size",
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
            ]
            
            # Create OpenAI client
            client = OpenAI(api_key=self.api_key)
            
            # Call the OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=[system_message] + self.conversation_history,
                tools=tools,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            
            # Process the response
            self.conversation_history.append(response_message)
            
            # Check if function call is needed
            if response_message.tool_calls:
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Get the function
                    function_to_call = available_functions.get(function_name)
                    if function_to_call:
                        # Call the function
                        function_response = function_to_call(**function_args)
                        
                        # Special formatting for restaurant search results
                        if function_name == "search_restaurants":
                            if self.track_performance and function_response:
                                self.metrics["successful_searches"] += 1
                            function_response = self._format_restaurant_results(function_response)
                        elif function_name == "make_reservation" and function_response.get("success", False):
                            if self.track_performance:
                                self.metrics["reservations_made"] += 1
                    else:
                        function_response = {"error": f"Function {function_name} not found"}
                    
                    # Add the function response to the conversation
                    self.conversation_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(function_response) if not isinstance(function_response, str) else function_response
                    })
                
                # Get the final response
                second_response = client.chat.completions.create(
                    model=self.model,
                    messages=[system_message] + self.conversation_history
                )
                
                final_response = second_response.choices[0].message.content
            else:
                final_response = response_message.content
                
            # Validate output
            is_valid_output, processed_output = self._validate_output(final_response)
            
            if not is_valid_output:
                return processed_output  # Return error message
                
            # Add the final response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": processed_output
            })
            
            # Track performance if enabled
            if self.track_performance:
                end_time = time.time()
                self.metrics["response_times"].append(end_time - start_time)
                
            return processed_output
            
        except Exception as e:
            if self.track_performance:
                self.metrics["failed_queries"] += 1
                
            error_message = f"I apologize, but I encountered an error processing your request. Please try again or rephrase your question. Technical details: {str(e)}"
            
            # For debugging only - in production, you'd want to log this instead
            print(f"Error in process_message: {str(e)}")
            
            return error_message

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
