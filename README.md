# FoodieSpot AI Reservation Assistant

## Overview

FoodieSpot AI Reservation Assistant is an intelligent, conversational AI solution designed to streamline the restaurant reservation process. Leveraging advanced natural language processing techniques, the system provides a seamless experience for users to discover restaurants, check availability, and make reservations through a natural conversation flow.

## Business Strategy

### Value Proposition

FoodieSpot addresses critical pain points in the restaurant reservation ecosystem:

1. **For Customers**: Eliminates friction in finding and booking restaurants by providing a natural, conversational interface that understands intent and preferences.

2. **For Restaurants**: Increases booking efficiency, reduces no-shows through automated confirmation, and provides valuable data on customer preferences and booking patterns.

3. **For Restaurant Chains**: Centralizes reservation management across multiple locations while maintaining brand consistency in customer interactions.

### Target Market

- **Primary**: Urban professionals (25-45) who frequently dine out and value convenience
- **Secondary**: Restaurant chains looking to modernize their reservation systems
- **Tertiary**: Tourism and hospitality businesses seeking to offer enhanced concierge services

### Monetization Strategy

1. **SaaS Model**: Monthly subscription for restaurants based on size and reservation volume
2. **Tiered Pricing**:
   - Basic: Core reservation functionality
   - Premium: Advanced analytics, CRM integration, customized branding
   - Enterprise: Multi-location management, API access, dedicated support

### Key Performance Indicators

- Conversation completion rate (% of successful reservations)
- Average time to complete reservation
- User satisfaction ratings
- Restaurant partner retention rate
- Monthly active users

### Competitive Advantage

- Natural language understanding surpasses form-based reservation systems
- Contextual awareness remembers user preferences across sessions
- Modular architecture allows easy integration with existing restaurant management systems
- Privacy-first approach with built-in PII protection

## Architecture

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

### Deployment Options

#### Local Development Environment
- Follow the installation steps above
- Use `.env` for local environment variables

#### Streamlit Cloud Deployment
1. Push your code to GitHub (ensure `.env` is in `.gitignore`)
2. Connect your repository in Streamlit Cloud
3. Configure secrets in the Streamlit Cloud dashboard
4. Deploy the application

#### Docker Deployment
1. Build the Docker image:
```
docker build -t foodiespot .
```

2. Run the container:
```
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key_here foodiespot
```

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

The system implements a sophisticated prompt engineering strategy to ensure optimal LLM performance:

### System Prompt Design

1. **Role Definition**: The system prompt clearly establishes the assistant's identity as a restaurant reservation specialist, setting boundaries for its knowledge domain and capabilities.

2. **Base System Message**: Provides comprehensive instructions on how to handle different types of queries, including restaurant search, availability checking, and reservation processing.

3. **Few-Shot Examples**: Includes carefully crafted examples that demonstrate ideal interaction patterns for common scenarios, helping the model understand the expected response format and tone.

4. **Contextual Enrichment**: The system dynamically enhances user messages with:
   - Current date and time information
   - References to previous restaurants mentioned
   - User details already provided (name, contact information)
   - Party size preferences

5. **Guard Rails Implementation**:
   - Clear instructions for handling edge cases (e.g., unavailable restaurants)
   - Guidelines for maintaining a professional, helpful tone
   - Instructions for protecting user privacy (PII redaction)
   - Content moderation rules

### Optimization Techniques

1. **Token Efficiency**: Careful prompt design to maximize information while minimizing token usage
2. **Context Window Management**: Selective inclusion of conversation history
3. **Temperature Tuning**: Lower temperature (0.3) for reservation confirmation, higher (0.7) for recommendations
4. **Hybrid Approach**: Using regex for entity extraction to reduce dependency on the LLM for standard pattern recognition

### Prompt Evolution Process

The system employs a continuous improvement process for prompts:
1. Initial prompt design based on user personas and journey mapping
2. Testing with diverse user scenarios
3. Analyzing failure modes and edge cases
4. Iterative refinement to address identified issues
5. A/B testing of prompt variations to optimize performance

## Example Conversations

### Example 1: Basic Restaurant Search and Reservation

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

### Example 2: Ambiance-Based Recommendation

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

### Example 3: Multi-Step Interaction with Context Retention

**User**: "Hi, I'm Tim. I'll be in Mumbai next week for business."  
**Assistant**: "Welcome, Tim! I'd be happy to help you find restaurants in Mumbai for your business trip next week. What kind of cuisine are you interested in, or do you have any specific preferences for location or ambiance?"

**User**: "I enjoy seafood and would prefer something not too formal, as I'll be dining alone."  
**Assistant**: "I understand, Tim. For a solo business traveler who enjoys seafood in a more casual setting, I recommend:

1. The Coastal Kitchen (ID: ck003)
   - Cuisine: Seafood
   - Location: Colaba
   - Rating: 4.6/5
   - Price: ₹₹₹
   - Ambiance: Relaxed maritime theme with bar seating perfect for solo diners
   - Features: Chef's counter, daily catch specials, business traveler menu

Would you like to know more about this option or would you prefer additional recommendations?"

**User**: "That sounds perfect. Can I book for Tuesday at 6:30 PM?"  
**Assistant**: "I've reserved a spot for you at The Coastal Kitchen for Tuesday, December 12th at 6:30 PM. Your reservation code is RES-45231. To confirm:
- Restaurant: The Coastal Kitchen
- Date: Tuesday, December 12th
- Time: 6:30 PM
- Party Size: 1 person
- Name: Tim
Would you like me to send the confirmation details to your email or phone?"

### Example 4: Handling Special Requests

**User**: "I need a restaurant that can accommodate a wheelchair and has vegetarian options."  
**Assistant**: "I can definitely help you find restaurants that are wheelchair accessible and offer vegetarian options. Here are two excellent choices:

1. Green Leaf Bistro (ID: glb012)
   - Cuisine: International with extensive vegetarian menu
   - Location: Powai
   - Accessibility: Full wheelchair access, accessible restrooms
   - Vegetarian Options: Dedicated vegetarian menu with 20+ dishes
   - Rating: 4.5/5
   - Features: Wide doorways, elevator access, spacious table arrangement

2. Fusion Garden (ID: fg008)
   - Cuisine: Pan-Asian fusion with vegetarian specialties
   - Location: Andheri West
   - Accessibility: Ramp entrance, accessible seating, accessible restrooms
   - Vegetarian Options: 75% of menu is vegetarian or can be made vegetarian
   - Rating: 4.7/5
   - Features: Ground floor location, dedicated parking for disabled guests

Would you like more details about either of these restaurants?"

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

## Assumptions, Limitations, and Future Enhancements

### Key Assumptions

1. **User Behavior**: Users prefer conversational interfaces over traditional form-based reservation systems
2. **Technical Environment**: Users have reliable internet access and devices capable of running web applications
3. **Restaurant Data**: Restaurant information remains relatively static and can be managed through JSON files
4. **Language**: Primary users speak English fluently
5. **Availability Management**: Restaurants manage their own availability and the system serves as an interface

### Current Limitations

1. **Database**: JSON-based storage limits scalability for very large restaurant datasets
2. **Real-time Availability**: No direct integration with restaurant POS/reservation systems
3. **Language Support**: Currently English only
4. **Payment Processing**: No integrated payment system for deposits or pre-payments
5. **Offline Access**: Requires constant internet connection
6. **Authentication**: Basic authentication system with limited user account features

### Future Enhancements

#### Short-term (3-6 months)
1. **Database Migration**: Move from JSON to SQL/NoSQL for improved scalability
2. **Enhanced Analytics**: Restaurant-facing dashboard with booking trends and customer preferences
3. **User Accounts**: Persistent user profiles with reservation history and preferences
4. **Multi-language Support**: Expand to include major global languages
5. **Notification System**: SMS/email confirmations and reminders

#### Mid-term (6-12 months)
1. **Real-time Integration**: Connect with restaurant POS systems for live availability
2. **Payment Processing**: Add secure payment handling for deposits and pre-payments
3. **Voice Interface**: Add speech recognition for voice-based interactions
4. **Mobile Application**: Dedicated mobile apps for iOS and Android
5. **Expanded Recommendations**: AI-driven personalized restaurant recommendations

#### Long-term (12+ months)
1. **Restaurant Management System**: Complete restaurant-side booking and table management
2. **Loyalty Program**: Integrated rewards system for frequent diners
3. **Marketplace Features**: Special offers, chef's tables, and exclusive events
4. **AR Menu Previews**: Augmented reality food previews
5. **Predictive Booking**: AI-driven suggestions based on user behavior patterns

## Contributing

Contributions to FoodieSpot are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
