"""Web scraping functionality using BeautifulSoup"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional, Tuple
import time
import ipaddress
import socket
import os

from config import TIMEOUTS
from rag.retriever import rag_retriever

class WebScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.max_html_bytes = int(os.environ.get("SOVWREN_SCRAPER_MAX_HTML_BYTES", "2000000"))
        self.max_redirects = int(os.environ.get("SOVWREN_SCRAPER_MAX_REDIRECTS", "3"))
        self.allow_private_hosts = os.environ.get("SOVWREN_SCRAPER_ALLOW_PRIVATE_HOSTS", "").strip() == "1"

    async def _get_session(self):
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=TIMEOUTS["web_scraping"])
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
        return self.session

    def _host_is_private_or_local(self, host: str) -> bool:
        host = (host or "").strip().strip("[]")
        if not host:
            return True

        if host.lower() in {"localhost"}:
            return True

        try:
            ip = ipaddress.ip_address(host)
            return bool(
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            )
        except ValueError:
            # Not an IP literal; resolve and check all addresses.
            try:
                infos = socket.getaddrinfo(host, None)
            except Exception:
                return False

            for info in infos:
                try:
                    addr = info[4][0]
                    ip = ipaddress.ip_address(addr)
                    if (
                        ip.is_private
                        or ip.is_loopback
                        or ip.is_link_local
                        or ip.is_reserved
                        or ip.is_multicast
                    ):
                        return True
                except Exception:
                    continue
            return False

    def _validate_url(self, url: str) -> Optional[str]:
        """
        Basic SSRF guardrails:
        - allowlist schemes: http/https
        - block localhost + private/internal ranges by default
        """
        try:
            parsed = urlparse(url)
        except Exception:
            return "Invalid URL"

        if parsed.scheme not in {"http", "https"}:
            return f"Blocked URL scheme: {parsed.scheme}"

        if not parsed.hostname:
            return "URL missing hostname"

        if not self.allow_private_hosts and self._host_is_private_or_local(parsed.hostname):
            return f"Blocked private/local host: {parsed.hostname}"

        return None

    async def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """Scrape content from a URL"""
        try:
            session = await self._get_session()

            current = url
            for _ in range(max(0, self.max_redirects) + 1):
                reason = self._validate_url(current)
                if reason:
                    print(f"Blocked scrape for {current}: {reason}")
                    return None

                async with session.get(current, allow_redirects=False) as response:
                    # Manual redirect handling so SSRF checks apply to each hop.
                    if response.status in {301, 302, 303, 307, 308}:
                        location = response.headers.get("Location")
                        if not location:
                            print(f"Redirect without Location for {current}")
                            return None
                        current = urljoin(current, location)
                        continue

                    if response.status != 200:
                        print(f"HTTP {response.status} for {current}")
                        return None

                    raw = await response.content.read(self.max_html_bytes + 1)
                    if len(raw) > self.max_html_bytes:
                        print(f"Response too large for {current} (>{self.max_html_bytes} bytes)")
                        return None

                    html = raw.decode(errors="replace")
                    return self._extract_content(html, current)

            print(f"Too many redirects for {url}")
            return None
                
        except asyncio.TimeoutError:
            print(f"Timeout scraping {url}")
            return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _extract_content(self, html: str, url: str) -> Dict[str, str]:
        """Extract clean content from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string.strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        else:
            # Fallback to URL-based title
            title = urlparse(url).netloc
        
        # Extract main content
        content = ""
        
        # Try to find main content areas
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            content = main_content.get_text()
        else:
            # Fallback to body content
            body = soup.find('body')
            if body:
                content = body.get_text()
            else:
                content = soup.get_text()
        
        # Clean up content
        content = self._clean_text(content)
        
        # Extract metadata
        metadata = self._extract_metadata(soup, url)
        
        return {
            'title': title,
            'content': content,
            'url': url,
            'metadata': metadata
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Join lines with proper spacing
        text = '\n'.join(lines)
        
        return text.strip()

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Extract metadata from HTML"""
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                if name in ['description', 'og:description']:
                    metadata['description'] = content
                elif name in ['keywords', 'og:keywords']:
                    metadata['keywords'] = content
                elif name in ['author', 'og:author']:
                    metadata['author'] = content
                elif name == 'og:type':
                    metadata['type'] = content
        
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        return metadata

    async def scrape_and_store(self, url: str) -> Optional[int]:
        """Scrape URL and store in RAG system"""
        print(f"Scraping {url}...")
        
        scraped_data = await self.scrape_url(url)
        if not scraped_data:
            return None
        
        # Check if content is substantial
        if len(scraped_data['content']) < 100:
            print(f"Content too short for {url}")
            return None
        
        # Store in RAG system
        try:
            document_id = await rag_retriever.add_document(
                content=scraped_data['content'],
                title=scraped_data['title'],
                url=scraped_data['url'],
                metadata=scraped_data['metadata']
            )
            
            print(f"Stored {url} as document {document_id}")
            return document_id
            
        except Exception as e:
            print(f"Error storing {url}: {e}")
            return None

    async def scrape_multiple_urls(self, urls: List[str], 
                                  max_concurrent: int = 3) -> List[int]:
        """Scrape multiple URLs concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_and_store(url)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None values
        document_ids = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error scraping {urls[i]}: {result}")
            elif result is not None:
                document_ids.append(result)
        
        return document_ids

    async def search_and_scrape(self, query: str, search_engine: str = "duckduckgo",
                               max_results: int = 5) -> List[int]:
        """Search web and scrape results (basic implementation)"""
        # Note: This is a simplified implementation
        # In production, you might want to use proper search APIs
        
        print(f"Web search not implemented yet. Please provide URLs directly.")
        return []

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Filter out non-HTTP links
            if full_url.startswith(('http://', 'https://')):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates

    async def scrape_with_depth(self, start_url: str, max_depth: int = 1,
                               max_pages: int = 10) -> List[int]:
        """Scrape URL and follow links to specified depth"""
        visited = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        document_ids = []
        
        while to_visit and len(visited) < max_pages:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue

            reason = self._validate_url(url)
            if reason:
                print(f"Blocked scrape for {url}: {reason}")
                continue
            
            visited.add(url)
            
            # Scrape current page
            doc_id = await self.scrape_and_store(url)
            if doc_id:
                document_ids.append(doc_id)
            
            # If not at max depth, extract and queue links
            if depth < max_depth:
                try:
                    session = await self._get_session()
                    async with session.get(url, allow_redirects=True, max_redirects=self.max_redirects) as response:
                        if response.status == 200:
                            raw = await response.content.read(self.max_html_bytes + 1)
                            if len(raw) > self.max_html_bytes:
                                continue
                            html = raw.decode(errors="replace")
                            links = self.extract_links(html, url)
                            
                            # Filter links to same domain to avoid going too wide
                            base_domain = urlparse(url).netloc
                            same_domain_links = [
                                link for link in links
                                if urlparse(link).netloc == base_domain
                            ]
                            
                            # Add links to visit queue
                            for link in same_domain_links[:5]:  # Limit links per page
                                if link not in visited:
                                    to_visit.append((link, depth + 1))
                
                except Exception as e:
                    print(f"Error extracting links from {url}: {e}")
            
            # Small delay to be respectful
            await asyncio.sleep(1)
        
        print(f"Scraped {len(document_ids)} pages from {start_url}")
        return document_ids

    async def cleanup(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global web scraper instance
web_scraper = WebScraper()
