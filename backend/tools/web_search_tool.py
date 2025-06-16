"""
Web search tool for internet search and information gathering.
Provides safe and efficient web search capabilities with multiple search engines.
"""
import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, urljoin, urlparse
import xml.etree.ElementTree as ET

import aiohttp
from bs4 import BeautifulSoup
import feedparser

from .base_tool import BaseTool, ToolError, ToolConfig
from utils.logger import logger


class WebSearchConfig(ToolConfig):
    """Configuration specific to web search operations."""
    max_results: int = 10
    max_content_length: int = 50000  # 50KB per page
    timeout: int = 30
    user_agent: str = "Local AI Agent Web Search Tool 1.0"
    allowed_domains: Optional[List[str]] = None
    blocked_domains: List[str] = [
        "malware.com", "phishing.com", "spam.com"  # Example blocked domains
    ]
    search_engines: Dict[str, str] = {
        "duckduckgo": "https://api.duckduckgo.com/",
        "google_custom": "https://www.googleapis.com/customsearch/v1",
        "bing": "https://api.bing.microsoft.com/v7.0/search"
    }
    default_search_engine: str = "duckduckgo"
    enable_content_extraction: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour


class WebSearchTool(BaseTool):
    """
    Comprehensive web search tool with safety controls.
    
    Provides secure web search capabilities including search engine queries,
    content extraction, RSS feed parsing, and URL validation.
    """
    
    def __init__(self, config: Optional[WebSearchConfig] = None):
        self.web_config = config or WebSearchConfig()
        super().__init__(self.web_config)
        
        # HTTP session for connection pooling
        self.session = None
        
        # Search cache
        self.search_cache: Dict[str, Dict] = {}
        
        logger.info("WebSearchTool initialized")
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return """Comprehensive web search and information gathering tool. Can search the internet,
        extract content from web pages, parse RSS feeds, and validate URLs. Includes safety controls
        and content filtering."""
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "search", "extract_content", "validate_url", "parse_rss",
                        "get_page_info", "search_news", "search_images", "bulk_search"
                    ],
                    "description": "Web search operation to perform"
                },
                "query": {
                    "type": "string",
                    "description": "Search query or URL"
                },
                "search_engine": {
                    "type": "string",
                    "enum": ["duckduckgo", "google_custom", "bing"],
                    "default": "duckduckgo",
                    "description": "Search engine to use"
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "Maximum number of results to return"
                },
                "region": {
                    "type": "string",
                    "description": "Region/country code for localized search"
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "description": "Language for search results"
                },
                "time_range": {
                    "type": "string",
                    "enum": ["day", "week", "month", "year", "all"],
                    "default": "all",
                    "description": "Time range for search results"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["web", "news", "images", "videos"],
                    "default": "web",
                    "description": "Type of content to search for"
                },
                "extract_content": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to extract content from result URLs"
                },
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs for bulk operations"
                }
            },
            "required": ["operation"]
        }
    
    async def _execute(self, **kwargs) -> Any:
        """Execute web search operation."""
        operation = kwargs.get("operation")
        
        # Initialize session if needed
        if self.session is None:
            await self._init_session()
        
        # Dispatch to specific operation method
        operation_methods = {
            "search": self._search_web,
            "extract_content": self._extract_content,
            "validate_url": self._validate_url,
            "parse_rss": self._parse_rss_feed,
            "get_page_info": self._get_page_info,
            "search_news": self._search_news,
            "search_images": self._search_images,
            "bulk_search": self._bulk_search
        }
        
        if operation not in operation_methods:
            raise ToolError(f"Unsupported operation: {operation}", self.name)
        
        try:
            return await operation_methods[operation](**kwargs)
        finally:
            # Keep session open for reuse
            pass
    
    def _security_check(self, kwargs: Dict[str, Any]) -> None:
        """Enhanced security checks for web operations."""
        super()._security_check(kwargs)
        
        operation = kwargs.get("operation")
        query = kwargs.get("query", "")
        urls = kwargs.get("urls", [])
        
        # Check for suspicious patterns in queries
        suspicious_patterns = [
            r'javascript:', r'data:', r'vbscript:', r'file://',
            r'<script', r'</script>', r'onclick=', r'onerror='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ToolError(
                    f"Suspicious pattern detected in query: {pattern}",
                    self.name
                )
        
        # Validate URLs if provided
        all_urls = [query] if query.startswith(('http://', 'https://')) else []
        all_urls.extend(urls)
        
        for url in all_urls:
            if url.startswith(('http://', 'https://')):
                self._validate_url_security(url)
    
    def _validate_url_security(self, url: str) -> None:
        """Validate URL for security concerns."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check blocked domains
        for blocked in self.web_config.blocked_domains:
            if blocked in domain:
                raise ToolError(
                    f"Domain is blocked: {domain}",
                    self.name
                )
        
        # Check allowed domains if specified
        if self.web_config.allowed_domains:
            allowed = False
            for allowed_domain in self.web_config.allowed_domains:
                if allowed_domain in domain:
                    allowed = True
                    break
            
            if not allowed:
                raise ToolError(
                    f"Domain not in allowed list: {domain}",
                    self.name
                )
        
        # Check for suspicious URL patterns
        if any(suspicious in url.lower() for suspicious in [
            'localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.0.0.',
            'file://', 'javascript:', 'data:'
        ]):
            raise ToolError(
                f"Suspicious URL pattern detected: {url}",
                self.name
            )
    
    async def _init_session(self):
        """Initialize HTTP session with security settings."""
        timeout = aiohttp.ClientTimeout(total=self.web_config.timeout)
        headers = {
            'User-Agent': self.web_config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                enable_cleanup_closed=True
            )
        )
    
    async def _search_web(
        self,
        query: str,
        search_engine: str = None,
        max_results: int = None,
        extract_content: bool = False,
        time_range: str = "all",
        language: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Perform web search using specified search engine."""
        search_engine = search_engine or self.web_config.default_search_engine
        max_results = max_results or self.web_config.max_results
        
        # Check cache first
        cache_key = f"{search_engine}:{query}:{max_results}:{time_range}:{language}"
        if self.web_config.enable_caching and cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if datetime.now() - cached_result["timestamp"] < timedelta(seconds=self.web_config.cache_ttl):
                logger.debug(f"Returning cached search result for: {query}")
                return cached_result["data"]
        
        logger.info(f"Searching web: {query} using {search_engine}")
        
        try:
            if search_engine == "duckduckgo":
                results = await self._search_duckduckgo(query, max_results, time_range)
            elif search_engine == "google_custom":
                results = await self._search_google_custom(query, max_results, language)
            elif search_engine == "bing":
                results = await self._search_bing(query, max_results, language)
            else:
                raise ToolError(f"Unsupported search engine: {search_engine}", self.name)
            
            # Extract content if requested
            if extract_content and results.get("results"):
                for result in results["results"]:
                    if "url" in result:
                        try:
                            content = await self._extract_content(query=result["url"])
                            result["extracted_content"] = content.get("content", "")[:1000]  # Limit content
                        except Exception as e:
                            logger.warning(f"Failed to extract content from {result['url']}: {e}")
                            result["extracted_content"] = "Content extraction failed"
            
            # Cache the result
            if self.web_config.enable_caching:
                self.search_cache[cache_key] = {
                    "data": results,
                    "timestamp": datetime.now()
                }
            
            return results
            
        except Exception as e:
            raise ToolError(f"Search failed: {str(e)}", self.name)
    
    async def _search_duckduckgo(self, query: str, max_results: int, time_range: str) -> Dict[str, Any]:
        """Search using DuckDuckGo API."""
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise ToolError(f"DuckDuckGo API error: {response.status}", self.name)
                
                data = await response.json()
                
                results = []
                
                # Process abstract
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", "Abstract"),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("Abstract", ""),
                        "source": data.get("AbstractSource", "DuckDuckGo")
                    })
                
                # Process related topics
                for topic in data.get("RelatedTopics", [])[:max_results-1]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                            "source": "DuckDuckGo"
                        })
                
                return {
                    "query": query,
                    "search_engine": "duckduckgo",
                    "total_results": len(results),
                    "results": results[:max_results],
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            raise ToolError(f"DuckDuckGo search failed: {str(e)}", self.name)
    
    async def _search_google_custom(self, query: str, max_results: int, language: str) -> Dict[str, Any]:
        """Search using Google Custom Search API (requires API key)."""
        # Note: This would require Google Custom Search API key
        # For now, we'll return a placeholder response
        return {
            "query": query,
            "search_engine": "google_custom",
            "total_results": 0,
            "results": [],
            "error": "Google Custom Search API key required",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _search_bing(self, query: str, max_results: int, language: str) -> Dict[str, Any]:
        """Search using Bing Search API (requires API key)."""
        # Note: This would require Bing Search API key
        # For now, we'll return a placeholder response
        return {
            "query": query,
            "search_engine": "bing",
            "total_results": 0,
            "results": [],
            "error": "Bing Search API key required",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _extract_content(self, query: str, **kwargs) -> Dict[str, Any]:
        """Extract content from a web page."""
        url = query
        
        logger.info(f"Extracting content from: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise ToolError(f"HTTP error {response.status} for URL: {url}", self.name)
                
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    raise ToolError(f"Unsupported content type: {content_type}", self.name)
                
                # Check content length
                content_length = int(response.headers.get('content-length', 0))
                if content_length > self.web_config.max_content_length:
                    raise ToolError(f"Content too large: {content_length} bytes", self.name)
                
                html_content = await response.text()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract basic information
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "No title"
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ''
                
                # Extract main content
                main_content = ""
                
                # Try to find main content areas
                for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
                    content_element = soup.select_one(selector)
                    if content_element:
                        main_content = content_element.get_text(separator=' ', strip=True)
                        break
                
                # Fallback to body if no main content found
                if not main_content:
                    body = soup.find('body')
                    if body:
                        main_content = body.get_text(separator=' ', strip=True)
                
                # Clean up content
                main_content = re.sub(r'\s+', ' ', main_content)[:5000]  # Limit to 5000 chars
                
                # Extract links
                links = []
                for link in soup.find_all('a', href=True)[:20]:  # Limit to 20 links
                    href = link.get('href')
                    if href and href.startswith(('http://', 'https://')):
                        links.append({
                            "text": link.get_text().strip(),
                            "url": href
                        })
                
                return {
                    "url": url,
                    "title": title_text,
                    "description": description,
                    "content": main_content,
                    "content_length": len(main_content),
                    "links": links,
                    "extraction_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            raise ToolError(f"Content extraction failed: {str(e)}", self.name)
    
    async def _validate_url(self, query: str, **kwargs) -> Dict[str, Any]:
        """Validate URL accessibility and basic information."""
        url = query
        
        logger.info(f"Validating URL: {url}")
        
        try:
            async with self.session.head(url) as response:
                return {
                    "url": url,
                    "accessible": True,
                    "status_code": response.status,
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": response.headers.get('content-length', ''),
                    "last_modified": response.headers.get('last-modified', ''),
                    "server": response.headers.get('server', ''),
                    "validation_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "url": url,
                "accessible": False,
                "error": str(e),
                "validation_timestamp": datetime.now().isoformat()
            }
    
    async def _parse_rss_feed(self, query: str, **kwargs) -> Dict[str, Any]:
        """Parse RSS/Atom feed from URL."""
        url = query
        
        logger.info(f"Parsing RSS feed: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise ToolError(f"HTTP error {response.status} for RSS feed: {url}", self.name)
                
                feed_content = await response.text()
                
                # Parse with feedparser
                feed = feedparser.parse(feed_content)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing warning: {feed.bozo_exception}")
                
                # Extract feed information
                feed_info = {
                    "title": feed.feed.get('title', ''),
                    "description": feed.feed.get('description', ''),
                    "link": feed.feed.get('link', ''),
                    "language": feed.feed.get('language', ''),
                    "last_updated": feed.feed.get('updated', ''),
                    "total_entries": len(feed.entries)
                }
                
                # Extract entries
                entries = []
                for entry in feed.entries[:20]:  # Limit to 20 entries
                    entries.append({
                        "title": entry.get('title', ''),
                        "link": entry.get('link', ''),
                        "description": entry.get('description', ''),
                        "published": entry.get('published', ''),
                        "author": entry.get('author', ''),
                        "tags": [tag.term for tag in entry.get('tags', [])]
                    })
                
                return {
                    "url": url,
                    "feed_info": feed_info,
                    "entries": entries,
                    "parsing_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            raise ToolError(f"RSS feed parsing failed: {str(e)}", self.name)
    
    async def _get_page_info(self, query: str, **kwargs) -> Dict[str, Any]:
        """Get comprehensive page information."""
        url = query
        
        logger.info(f"Getting page info: {url}")
        
        try:
            # Combine validation and content extraction
            validation = await self._validate_url(url)
            if validation["accessible"]:
                content_info = await self._extract_content(url)
                
                return {
                    "url": url,
                    "validation": validation,
                    "content": content_info,
                    "comprehensive": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "url": url,
                    "validation": validation,
                    "content": None,
                    "comprehensive": False,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            raise ToolError(f"Page info gathering failed: {str(e)}", self.name)
    
    async def _search_news(
        self,
        query: str,
        max_results: int = None,
        time_range: str = "week",
        **kwargs
    ) -> Dict[str, Any]:
        """Search for news articles."""
        # For now, delegate to general search with news focus
        return await self._search_web(
            query=f"{query} news",
            max_results=max_results or 10,
            time_range=time_range,
            **kwargs
        )
    
    async def _search_images(
        self,
        query: str,
        max_results: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search for images (placeholder implementation)."""
        return {
            "query": query,
            "search_type": "images",
            "results": [],
            "message": "Image search not implemented yet",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _bulk_search(
        self,
        urls: List[str],
        operation: str = "validate_url",
        **kwargs
    ) -> Dict[str, Any]:
        """Perform bulk operations on multiple URLs."""
        logger.info(f"Performing bulk {operation} on {len(urls)} URLs")
        
        results = []
        
        for url in urls[:10]:  # Limit to 10 URLs for safety
            try:
                if operation == "validate_url":
                    result = await self._validate_url(url)
                elif operation == "extract_content":
                    result = await self._extract_content(url)
                elif operation == "get_page_info":
                    result = await self._get_page_info(url)
                else:
                    result = {"url": url, "error": f"Unsupported bulk operation: {operation}"}
                
                results.append(result)
                
                # Small delay between requests to be respectful
                await asyncio.sleep(0.5)
                
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e),
                    "operation": operation
                })
        
        return {
            "operation": operation,
            "total_urls": len(urls),
            "processed_urls": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()
        
        logger.info("WebSearchTool cleanup completed")
