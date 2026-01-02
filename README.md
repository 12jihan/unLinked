# Unlinked

An automated LinkedIn content generation and posting bot powered by Google's Gemini AI. The bot searches for recent tech news, generates professional LinkedIn posts, validates links, and stores content in a PostgreSQL vector database for semantic search and deduplication.

## Features

- **AI-Powered Content Generation**: Uses Google Gemini 2.5 Flash with Google Search grounding to find and summarize recent tech news
- **LinkedIn Integration**: Automated posting to LinkedIn via the UGC Posts API
- **Vector Database Storage**: PostgreSQL with pgvector extension for semantic search and content deduplication
- **Link Validation**: Automatically tests article links before posting to ensure they're accessible
- **Customizable Persona**: Configurable AI persona focused on pragmatic, engineering-focused content

## Architecture

```
src/
├── main.py                    # Application entry point
├── controller/
│   ├── BotController.py       # Main orchestration logic
│   └── MemoryController.py    # Vector database operations
├── gemini/
│   └── gemini_ext.py          # Gemini AI integration
├── linkedin/
│   └── linkedin_ext.py        # LinkedIn API client
└── models/
    ├── DataModels.py          # Core data structures
    ├── GeminiModels.py        # AI response schemas
    └── LinkinModels.py        # LinkedIn API models
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google AI API key (Gemini)
- LinkedIn Developer credentials (Access Token, API Version, User ID)

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd unlinked
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

   Or with pip:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the PostgreSQL vector database**

   ```bash
   docker-compose up -d
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   # Google Gemini
   API_KEY=your_gemini_api_key

   # PostgreSQL
   PG_PORT=5433
   PG_NAME=vectordb
   PG_USER=postgres
   PG_PASS=postgres

   # LinkedIn
   ACCESS_TOKEN=your_linkedin_access_token
   API_VERSION=202401
   USER_ID=urn:li:person:your_person_id
   ```

## Usage

Run the bot:

```bash
cd src
python main.py
```

The bot will:
1. Generate a LinkedIn post about recent tech news using Gemini AI
2. Validate any included article links
3. Store the content in the vector database
4. Optionally post to LinkedIn (currently commented out for safety)

The main loop runs every 15 minutes (900 seconds) by default.

## Configuration

### AI Persona

The Gemini AI is configured with a "Senior Software Engineer" persona that:
- Focuses on pragmatic, grounded technical content
- Avoids marketing fluff and buzzwords
- Prioritizes architectural shifts, security vulnerabilities, and open-source changes
- Outputs structured JSON with text, hashtags, and validated links

### Database Schema

The vector database stores documents with:
- `text`: The generated post content
- `link`: Source article URL
- `hashtags`: Array of relevant hashtags
- `embedding`: 768-dimensional vector (text-embedding-004)
- `created_at` / `modified_at`: Timestamps

### LinkedIn Visibility

Posts default to `PUBLIC` visibility. Modify `LinkinModels.py` to change:

```python
memberNetworkVisibility: str = Field(
    default="CONNECTIONS",  # or "PUBLIC"
    alias="com.linkedin.ugc.MemberNetworkVisibility",
)
```

## API Reference

### MemoryController

```python
memory = MemoryController()

# Add a document
doc = memory.add(DocumentCreate(text="...", link="...", hashtags=["..."]))

# Search similar content
results = memory.search("query string", limit=5)

# Get, update, or delete by ID
doc = memory.get(doc_id)
doc = memory.update(doc_id, "new text")
success = memory.delete(doc_id)
```

### GeminiExt

```python
gemini = GeminiExt()
response = gemini.generate_content("find an article")
# Returns AIResponse(text, link, hashtags) or None
```

## Docker Services

The `docker-compose.yml` provides:

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| database | pgvector/pgvector:pg16 | 5433:5432 | PostgreSQL with vector extension |

Data is persisted in the `pgvector-data` volume.

## Development

### Project Structure

- **BotController**: Orchestrates the content generation pipeline
- **MemoryController**: Handles all database operations with pgvector
- **GeminiExt**: Manages Gemini AI interactions with Google Search grounding
- **LinkedInExt**: Handles LinkedIn API authentication and posting

### Adding New Features

1. Extend data models in `src/models/DataModels.py`
2. Add database operations in `MemoryController`
3. Integrate in `BotController.init()`

### Logging

Gemini responses are logged to `logs/gemini_responses.log` with timestamps.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| google-genai | ≥1.52.0 | Gemini AI client |
| pgvector | ≥0.4.2 | PostgreSQL vector operations |
| psycopg[binary] | ≥3.3.2 | PostgreSQL driver |
| pydantic | ≥2.12.5 | Data validation |
| requests | ≥2.32.5 | HTTP client |
| pynput | ≥1.8.1 | Input handling |
| dotenv | ≥0.9.9 | Environment configuration |

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
