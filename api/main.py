"""
FastAPI application for Our Daily Bread Ministries devotional API.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio

from .scraper import (
    scrape_today,
    scrape_by_date,
    scrape_by_slug,
    scrape_devotional_list
)

app = FastAPI(
    title="Our Daily Bread Devotional API",
    description="API for accessing Our Daily Bread Ministries daily devotionals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Our Daily Bread Devotional API",
        "version": "1.0.0",
        "endpoints": {
            "today": "/today",
            "by_date": "/date/{YYYY-MM-DD}",
            "by_slug": "/devotional/{slug}",
            "list": "/list?limit=10&offset=0"
        }
    }


@app.get("/today")
async def get_today():
    """
    Get today's devotional.
    
    Returns:
        Full devotional data for today
    """
    try:
        devotional = await scrape_today()
        return devotional
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's devotional: {str(e)}")


@app.get("/date/{date}")
async def get_by_date(date: str):
    """
    Get devotional for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        Full devotional data for the specified date
    """
    try:
        devotional = await scrape_by_date(date)
        return devotional
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching devotional: {str(e)}")


@app.get("/devotional/{slug}")
async def get_by_slug(slug: str):
    """
    Get devotional by slug/URL path.
    
    Args:
        slug: Devotional slug (e.g., "faith-and-false-accusation")
        
    Returns:
        Full devotional data for the specified slug
    """
    try:
        devotional = await scrape_by_slug(slug)
        return devotional
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching devotional: {str(e)}")


@app.get("/list")
async def get_list(
    limit: int = Query(default=10, ge=1, le=50, description="Number of devotionals to return"),
    offset: int = Query(default=0, ge=0, description="Number of devotionals to skip")
):
    """
    Get list of recent devotionals.
    
    Args:
        limit: Number of devotionals to return (1-50)
        offset: Number of devotionals to skip
        
    Returns:
        List of devotional previews
    """
    try:
        devotionals = await scrape_devotional_list(limit=limit, offset=offset)
        return {
            "count": len(devotionals),
            "limit": limit,
            "offset": offset,
            "devotionals": devotionals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching devotional list: {str(e)}")


# For Vercel serverless function
def handler(request):
    """Vercel serverless function handler."""
    return app


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
