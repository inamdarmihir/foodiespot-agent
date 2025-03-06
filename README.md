# FoodieSpot AI Reservation Assistant

## Overview

FoodieSpot AI Reservation Assistant is an intelligent, conversational AI solution designed to streamline the restaurant reservation process. Leveraging advanced natural language processing techniques, the system provides a seamless experience for users to discover restaurants, check availability, and make reservations through a natural conversation flow.

## Architecture

![FoodieSpot Architecture](https://i.imgur.com/diagram-placeholder.png)

The system follows a modular architecture with the following components:

### High-Level Architecture
```
┌─────────────────┐      ┌───────────────────┐      ┌────────────────┐
│                 │      │                   │      │                │
│  Streamlit UI   │─────▶│  Backend Service  │─────▶│  OpenAI API    │
│                 │      │                   │      │                │
└─────────────────┘      └───────────────────┘      └────────────────┘
                                  │                          │
                                  ▼                          ▼
                         ┌─────────────────┐      ┌────────────────┐
                         │                 │      │                │
                         │  Restaurant DB  │      │  Conversation  │
                         │  (JSON)         │      │  History       │
                         │                 │      │                │
                         └─────────────────┘      └────────────────┘
```

### Components
1. **Streamlit UI**: Provides the web interface for user interaction
2. **Backend Service**: Processes user requests, manages session state, and orchestrates the system
3. **Restaurant Database**: Stores restaurant information in JSON format
4. **Context Management**: Maintains conversation history and user context
5. **LLM Integration**: Interfaces with OpenAI API for natural language understanding and generation
6. **Security Layer**: Handles input validation, PII detection, and content moderation

## Features

- **Intelligent Restaurant Search**: Find restaurants by cuisine, location, rating, price range, and ambiance
- **Smart Availability Checking**: Check if a restaurant has available tables for a specific date, time, and party size
- **Seamless Reservation Processing**: Make reservations with all necessary details in a conversational flow
- **User Context Awareness**: Remembers user information and preferences throughout the conversation
- **Natural Language Understanding**: Process various ways users might phrase their requests
- **Privacy Protection**: PII detection and redaction for user data security
- **Automated Date/Time Understanding**: Automatically translates references like "this weekend" to actual dates
- **Content Moderation**: Guards against inappropriate language and inputs

## Technical Stack

- **Frontend**: Streamlit web application
- **Backend**: Python with OpenAI API integration
- **Language Model**: GPT-4 Turbo (configurable)
- **Data Store**: JSON-based restaurant database
- **NLP Processing**: Custom regex-based entity extraction, context enrichment
- **Security**: Input/output validation, PII detection, profanity filtering

## Data Flow

1. User submits a query through the Streamlit interface
2. Backend processes the query and extracts entities (names, dates, preferences)
3. System enriches the query with contextual information (date/time, previous preferences)
4. The enriched query is sent to the LLM with a carefully crafted system prompt
5. LLM generates a response based on available restaurant data and user context
6. Response is validated for appropriate content and PII redaction
7. Formatted response is displayed to the user in the Streamlit interface

## Setup Instructions

### Prerequisites

- Python 3.8+
- An OpenAI API key

### Installation

1. Clone the repository
```
git clone https://github.com/yourusername/foodiespot.git
cd foodiespot
```

2. Install the required dependencies
```
pip install -r requirements.txt
```

3. Configure your API key
   - Create a `.env` file in the root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

4. Run the application
```
python -m streamlit run app/main.py
```

5. Access the application in your web browser at `http://localhost:8501`

## Security and Credentials Management

This project includes a `.gitignore` file to prevent sensitive credentials from being pushed to source control. For security best practices:

1. **Never commit your `.env` file** - It's already in the `.gitignore`
2. **Use environment variables** for all sensitive information
3. **For production deployment**, use the platform's secrets management:
   - For Streamlit Cloud: Use the Secrets Management feature
   - For other platforms: Use their equivalent environment variable systems

## Code Structure

```
foodiespot/
├── app/
│   ├── agent/
│   │   ├── agent.py           # LLM integration and conversation management
│   │   └── prompt.py          # System prompts and templates
│   ├── data/
│   │   ├── restaurants.json   # Restaurant data store
│   │   └── data_utils.py      # Data loading and manipulation utilities
│   ├── utils/
│   │   ├── validation.py      # Input/output validation
│   │   ├── security.py        # PII detection and content moderation
│   │   └── helpers.py         # General utility functions
│   └── main.py                # Main Streamlit application entry point
├── tests/                     # Unit and integration tests
├── .env                       # Environment variables (not in version control)
├── .gitignore                 # Git ignore patterns
└── requirements.txt           # Python dependencies
```

## Prompt Engineering Approach

The system uses a sophisticated prompt engineering strategy:

1. **Base System Message**: Establishes the assistant's identity and capabilities
2. **Dynamic Context Enrichment**: Enhances user messages with date/time information and user details
3. **Few-Shot Examples**: Provides the model with examples of expected behavior
4. **Chain-of-Thought**: Guides the model to break down complex queries into steps
5. **Guard Rails**: Explicit instructions for handling edge cases and maintaining conversational flow

## Example Conversations

### Example 1: Making a Reservation

**User**: "Hi, I'm looking for Japanese restaurants in Bandra"  
**Assistant**: "I found one excellent Japanese restaurant in Bandra: Sakura Fusion (ID: sf010). They offer authentic Japanese cuisine with a modern twist. It has a 4.7/5 rating, a ₹₹₹₹ price range, and features a sushi bar and private dining. Would you like more details or check availability for a reservation?"

**User**: "I'd like to make a reservation at Coastal Tides for this Saturday at 7 PM for 2 people. My name is Alex and my number is 555-123-4567."  
**Assistant**: "I've booked your reservation at Coastal Tides for Saturday, December 9th at 7:00 PM. Your reservation code is RES-23946. To summarize:
- Restaurant: Coastal Tides
- Date: Saturday, December 9th
- Time: 7:00 PM
- Party Size: 2 people
- Name: Alex
- Contact: 555-XXX-4567
Is there anything else you'd like help with, such as directions or information about their menu?"

### Example 2: Restaurant Recommendations

**User**: "Can you recommend a romantic dinner place with a good view?"  
**Assistant**: "Based on your preference for a romantic dinner with a good view, I recommend these options:

1. Seafood Cove (ID: sc005)
   - Cuisine: Seafood
   - Location: Juhu Beach
   - Rating: 4.8/5
   - Ambiance: Beachfront casual elegance with panoramic ocean views
   - Features: Outdoor seating, ocean view, romantic lighting

2. Coastal Tides (ID: ct007)
   - Cuisine: French-Mediterranean fusion
   - Location: Marine Drive
   - Rating: 4.9/5
   - Ambiance: Sophisticated waterfront dining with sunset views
   - Features: Candlelight dining, private balcony tables, piano music

Would you like more information or would you like to check availability for either of these restaurants?"

## Development Guidelines

### Adding New Restaurants

To add new restaurants to the system:

1. Update the `app/data/restaurants.json` file with the new restaurant information
2. Follow the existing schema structure
3. Ensure all required fields are populated

### Extending the System

The modular architecture allows for easy extensions:

1. **New Features**: Add new modules to the `app/utils/` directory
2. **Enhanced Prompts**: Modify system prompts in `app/agent/prompt.py`
3. **UI Improvements**: Update the Streamlit interface in `app/main.py`

## Performance Considerations

The system includes several optimizations:

1. **Caching**: Restaurant data is cached to minimize loading times
2. **Conversation Management**: Only relevant history is sent to the LLM to reduce token usage
3. **Efficient Entity Extraction**: Regex-based extraction reduces dependency on LLM for simple tasks

## Limitations and Future Improvements

Current limitations and planned improvements:

1. **Database**: Currently using JSON; future versions will support SQL/NoSQL databases
2. **Availability**: Static availability checking; future versions will integrate with real-time systems
3. **Payment Processing**: Reservations only; future versions will support deposits/pre-payments
4. **Multi-language Support**: Currently English only; expansion planned for additional languages
5. **Voice Interface**: Text-only currently; voice integration planned

## Contributing

Contributions to FoodieSpot are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 