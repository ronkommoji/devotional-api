# Our Daily Bread Devotional API

A REST API that scrapes daily devotionals from [Our Daily Bread Ministries](https://www.odbm.org/en/devotionals/) and provides them in JSON format.

## Features

- Get today's devotional
- Get devotional by date (YYYY-MM-DD format)
- Get devotional by slug/URL path
- List recent devotionals with pagination
- On-demand scraping (no database required)

## Tech Stack

- **Python 3.8+**
- **FastAPI** - Modern, fast web framework
- **BeautifulSoup4** - HTML parsing
- **httpx** - Async HTTP client
- **Vercel** - Serverless deployment platform

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd DevotionalAPI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Local Development

Run the API server locally:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

You can also view the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### `GET /`
Health check endpoint that returns API information.

**Response:**
```json
{
  "message": "Our Daily Bread Devotional API",
  "version": "1.0.0",
  "endpoints": {
    "today": "/today",
    "by_date": "/date/{YYYY-MM-DD}",
    "by_slug": "/devotional/{slug}",
    "list": "/list?limit=10&offset=0"
  }
}
```

### `GET /today`
Returns today's devotional with full content.

**Response:**
```json
{
  "title": "Faith and False Accusation",
  "date": "2026-01-18",
  "author": "Tom Felten",
  "scripture": "Nehemiah 6:1-9",
  "featured_verse": "I prayed, \"Now strengthen my hands.\" Nehemiah 6:9",
  "content": [
    "Paragraph 1...",
    "Paragraph 2...",
    "Paragraph 3..."
  ],
  "reflect_pray": {
    "question": "Why are believers in Jesus sometimes falsely accused?",
    "prayer": "Loving God, thank You for helping me when I'm falsely accused."
  },
  "insights": "Nehemiah was serving as cupbearer...",
  "bible_in_year": {
    "old_testament": "Genesis 43-45",
    "new_testament": "Matthew 12:24-50"
  },
  "url": "https://www.odbm.org/en/devotionals/devotional-category/faith-and-false-accusation",
  "image_url": "https://www.odbm.org/.../odb20260118.jpg"
}
```

### `GET /date/{date}`
Returns devotional for a specific date.

**Parameters:**
- `date` (path): Date in YYYY-MM-DD format (e.g., `2026-01-18`)

**Example:**
```
GET /date/2026-01-18
```

### `GET /devotional/{slug}`
Returns devotional by slug/URL path.

**Parameters:**
- `slug` (path): Devotional slug (e.g., `faith-and-false-accusation`)

**Example:**
```
GET /devotional/faith-and-false-accusation
```

### `GET /list`
Returns a paginated list of recent devotionals.

**Query Parameters:**
- `limit` (optional): Number of devotionals to return (1-50, default: 10)
- `offset` (optional): Number of devotionals to skip (default: 0)

**Example:**
```
GET /list?limit=20&offset=0
```

**Response:**
```json
{
  "count": 10,
  "limit": 10,
  "offset": 0,
  "devotionals": [
    {
      "title": "Faith and False Accusation",
      "date": "2026-01-18",
      "author": "Tom Felten",
      "preview": "Driven by powerful winds, the fire raged for days...",
      "url": "https://www.odbm.org/en/devotionals/devotional-category/faith-and-false-accusation",
      "image_url": "https://www.odbm.org/.../odb20260118.jpg"
    },
    ...
  ]
}
```

## Deployment to Vercel

### Prerequisites

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

### Deploy

1. From the project root, run:
```bash
vercel
```

2. Follow the prompts to link your project or create a new one.

3. For production deployment:
```bash
vercel --prod
```

### Configuration

The `vercel.json` file is already configured for Python serverless functions. The API will be automatically deployed as serverless functions.

**Note:** Vercel's Python support has some limitations. If you encounter issues, consider:
- Using **Railway** or **Render** as alternatives (they have better Python support)
- Adding a `runtime.txt` file specifying Python version (e.g., `python-3.11`)
- Using Mangum adapter if needed for better ASGI compatibility

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `404` - Devotional not found
- `500` - Server error (scraping failed, network issues, etc.)

Error responses include a `detail` field with the error message:
```json
{
  "detail": "Devotional not found for date: 2026-01-01"
}
```

## Rate Limiting & Best Practices

- The API scrapes content on-demand from the source website
- Be respectful: The scraper includes delays and proper headers
- Consider implementing caching if you expect high traffic
- Monitor your usage to avoid overloading the source website

## Legal & Ethical Considerations

- This API scrapes publicly available content from Our Daily Bread Ministries
- Ensure compliance with the website's Terms of Service
- Check `robots.txt` before scraping
- Consider reaching out to the website owners for permission, especially for commercial use
- This is for educational/personal use - respect copyright and usage rights

## Project Structure

```
DevotionalAPI/
├── api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and routes
│   ├── scraper.py       # Web scraping logic
│   └── index.py         # Vercel serverless entry point
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel configuration
├── .gitignore
└── README.md
```

## Development

### Running Tests

Test the scraper directly:
```python
python3 -c "import asyncio; from api.scraper import scrape_today; print(asyncio.run(scrape_today()))"
```

### Debugging

If scraping fails, check:
1. Network connectivity
2. Website structure changes (may require scraper updates)
3. Rate limiting from the source website

## License

This project is for educational purposes. Please respect the copyright of Our Daily Bread Ministries content.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on the repository.
