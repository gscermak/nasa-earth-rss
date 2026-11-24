#!/usr/bin/env python3

"""
NASA Earth Observatory Image of the Day RSS Generator

Author:
    Greg Cermak

Development:
    Developed collaboratively with OpenAI ChatGPT.

Purpose:
    Provide an independent RSS 2.0 feed for NASA Earth
    Observatory's Image of the Day.

    This application was developed after the official RSS
    feed appeared to stop functioning within start.me
    in September 2026.

Features:
    - Retrieves the six most recent available articles.
    - Extracts article titles, summaries, and publication dates.
    - Includes NASA image thumbnails.
    - Encodes special characters in image URLs.
    - Generates RSS 2.0 with Media RSS extensions.
    - Includes an Atom self-reference for interoperability.
    - Performs internal RSS structural validation.
    - Preserves the existing feed if generation fails.
    - Supports automated execution through GitHub Actions.

Data Source:
    NASA Earth Observatory
    https://science.nasa.gov/earth/earth-observatory/

Published Feed:
    https://gscermak.github.io/nasa-earth-rss/feed.xml

Disclaimer:
    This is an independent project and is not affiliated
    with or endorsed by NASA. Original scientific content
    and imagery are attributed to NASA and the respective
    credited contributors.

Output:
    feed.xml

Requirements:
    Python 3.9 or later
    requests
    beautifulsoup4
"""

import sys
import html
import re

from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Optional, TypedDict
from urllib.parse import urljoin, urlparse, quote
from xml.etree.ElementTree import (
    Element,
    SubElement,
    ElementTree,
    register_namespace,
    indent,
    parse,
)

import requests
from bs4 import BeautifulSoup


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SOURCE_URL = (
    "https://science.nasa.gov/earth/"
    "earth-observatory/image-of-the-day/"
)

ARTICLE_PREFIX = (
    "https://science.nasa.gov/earth/"
    "earth-observatory/"
)

FEED_URL = (
    "https://gscermak.github.io/"
    "nasa-earth-rss/feed.xml"
)

OUTPUT_FILE = Path("feed.xml")

MAX_ARTICLES = 6

REQUEST_TIMEOUT = 30

MEDIA_NS = "http://search.yahoo.com/mrss/"

ATOM_NS = "http://www.w3.org/2005/Atom"

HEADERS = {
    "User-Agent": "Mozilla/5.0 NASA-Earth-RSS/1.0"
}

EXCLUDED = {
    "image-of-the-day",
    "explorer",
    "topics",
    "collections",
    "global-maps",
    "world-of-change",
    "feature-articles",
    "blue-marble-next-generation",
    "about-the-eo",
    "subscribe",
    "search",
    "contact-the-eo",
}

register_namespace("media", MEDIA_NS)
register_namespace("atom", ATOM_NS)


# --------------------------------------------------
# Article Data Structure
# --------------------------------------------------

class Article(TypedDict):
    """Metadata associated with an Earth Observatory article."""

    title: str
    url: str
    summary: str
    image: str
    date: datetime


# --------------------------------------------------
# Download HTML
# --------------------------------------------------

def download(
    session: requests.Session,
    url: str,
) -> BeautifulSoup:
    """Download a web page and return its parsed HTML."""

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser",
    )


# --------------------------------------------------
# Find Candidate Article Links
# --------------------------------------------------

def find_articles(soup: BeautifulSoup) -> list[str]:
    """Identify unique candidate Earth Observatory article URLs."""

    candidates = []
    seen = set()

    for anchor in soup.find_all("a", href=True):

        url = urljoin(
            SOURCE_URL,
            anchor["href"],
        )

        parsed = urlparse(url)

        # Restrict links to the NASA Earth Observatory website.
        if not url.startswith(ARTICLE_PREFIX):
            continue

        relative = parsed.path.removeprefix(
            "/earth/earth-observatory/"
        ).strip("/")

        # Accept only direct article URLs.
        if not relative or "/" in relative:
            continue

        # Exclude navigation and informational pages.
        if relative in EXCLUDED:
            continue

        # Normalize the URL by removing query parameters
        # and fragment identifiers.
        url = (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
            f"{parsed.path.rstrip('/')}/"
        )

        # Ignore duplicate article links.
        if url in seen:
            continue

        seen.add(url)
        candidates.append(url)

    return candidates


# --------------------------------------------------
# Retrieve HTML Metadata
# --------------------------------------------------

def get_meta(
    soup: BeautifulSoup,
    property_name: str,
) -> str:
    """Extract the content of an HTML metadata property."""

    tag = soup.find(
        "meta",
        attrs={"property": property_name},
    )

    if tag is None:
        return ""

    return tag.get("content", "").strip()


# --------------------------------------------------
# Encode Image URLs
# --------------------------------------------------

def encode_image_url(url: str) -> str:
    """Encode special characters while preserving valid URL syntax."""

    return quote(
        url,
        safe=":/%?&=+#@!$'()*;,[]",
    )


# --------------------------------------------------
# Retrieve Article Metadata
# --------------------------------------------------

def get_article(
    session: requests.Session,
    url: str,
) -> Optional[Article]:
    """Retrieve and validate metadata for an individual article."""

    soup = download(session, url)

    title = get_meta(soup, "og:title")

    summary = get_meta(soup, "og:description")

    image = get_meta(soup, "og:image")

    published = get_meta(
        soup,
        "article:published_time",
    )

    # Reject articles with incomplete metadata.
    if not all((title, summary, image, published)):

        print(
            f"Warning: Incomplete metadata: {url}",
            file=sys.stderr,
        )

        return None

    # Resolve and encode the image URL.
    image = encode_image_url(
        urljoin(url, image)
    )

    # Convert the publication date to a datetime object.
    try:

        date = datetime.fromisoformat(
            published.replace("Z", "+00:00")
        )

    except ValueError:

        print(
            f"Warning: Invalid publication date: {url}",
            file=sys.stderr,
        )

        return None

    # Assume UTC when timezone information is unavailable.
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Normalize publication dates to UTC.
    date = date.astimezone(timezone.utc)

    # Remove the NASA Science suffix from article titles.
    title = re.sub(
        r"\s*-\s*NASA Science$",
        "",
        title,
    ).strip()

    if not title:
        return None

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "image": image,
        "date": date,
    }


# --------------------------------------------------
# Validate RSS
# --------------------------------------------------

def validate_rss(filename: Path) -> None:
    """Perform basic structural validation of the generated RSS feed."""

    tree = parse(filename)

    root = tree.getroot()

    if root.tag != "rss":
        raise RuntimeError("Invalid RSS root element")

    if root.get("version") != "2.0":
        raise RuntimeError("Invalid RSS version")

    channel = root.find("channel")

    if channel is None:
        raise RuntimeError("Missing RSS channel")

    # Verify required channel elements.
    for field in ("title", "link", "description"):

        if not channel.findtext(field):
            raise RuntimeError(
                f"Missing channel element: {field}"
            )

    # Verify the Atom self-reference recommended by W3C.
    atom_link = channel.find(
        f"{{{ATOM_NS}}}link[@rel='self']"
    )

    if atom_link is None:
        raise RuntimeError("Missing Atom self-reference")

    if atom_link.get("href") != FEED_URL:
        raise RuntimeError("Invalid Atom self-reference URL")

    if atom_link.get("type") != "application/rss+xml":
        raise RuntimeError("Invalid Atom self-reference type")

    # Verify the number of RSS items.
    items = channel.findall("item")

    if len(items) != MAX_ARTICLES:

        raise RuntimeError(
            f"Expected {MAX_ARTICLES} RSS items, "
            f"found {len(items)}"
        )

    seen = set()

    for item in items:

        # Verify the expected article elements.
        for field in (
            "title",
            "link",
            "guid",
            "pubDate",
            "description",
        ):

            if not item.findtext(field):

                raise RuntimeError(
                    f"Missing item element: {field}"
                )

        # Verify unique article identifiers.
        guid = item.findtext("guid")

        if guid in seen:
            raise RuntimeError(
                f"Duplicate article GUID: {guid}"
            )

        seen.add(guid)

        # Verify the Media RSS thumbnail.
        thumbnail = item.find(
            f"{{{MEDIA_NS}}}thumbnail"
        )

        if thumbnail is None or not thumbnail.get("url"):

            raise RuntimeError(
                f"Missing thumbnail: {guid}"
            )


# --------------------------------------------------
# Generate RSS
# --------------------------------------------------

def generate_rss(articles: list[Article]) -> None:
    """Generate, validate, and publish the RSS XML file."""

    rss = Element("rss", version="2.0")

    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = (
        "NASA Earth Observatory - Image of the Day"
    )

    SubElement(channel, "link").text = SOURCE_URL

    # Identify the canonical RSS feed URL.
    # Recommended by the W3C Feed Validation Service.
    SubElement(
        channel,
        f"{{{ATOM_NS}}}link",
        href=FEED_URL,
        rel="self",
        type="application/rss+xml",
    )

    SubElement(channel, "description").text = (
        f"The {MAX_ARTICLES} most recent NASA Earth "
        "Observatory Images of the Day."
    )

    SubElement(channel, "language").text = "en-us"

    SubElement(channel, "lastBuildDate").text = (
        format_datetime(datetime.now(timezone.utc))
    )

    for article in articles:

        item = SubElement(channel, "item")

        SubElement(item, "title").text = (
            article["title"]
        )

        SubElement(item, "link").text = (
            article["url"]
        )

        SubElement(
            item,
            "guid",
            isPermaLink="true",
        ).text = article["url"]

        SubElement(item, "pubDate").text = (
            format_datetime(article["date"])
        )

        # Create an HTML description containing the NASA
        # thumbnail and original article summary.
        description = (
            f'<img src="{html.escape(article["image"], quote=True)}" '
            f'alt="{html.escape(article["title"], quote=True)}">'
            f'<p>{html.escape(article["summary"])}</p>'
        )

        SubElement(item, "description").text = (
            description
        )

        # Include a Media RSS thumbnail for compatible readers.
        SubElement(
            item,
            f"{{{MEDIA_NS}}}thumbnail",
            url=article["image"],
        )

    # Format the XML for readability.
    indent(rss, space="  ")

    tree = ElementTree(rss)

    temporary = OUTPUT_FILE.with_suffix(".tmp")

    try:

        # Write to a temporary file.
        tree.write(
            temporary,
            encoding="utf-8",
            xml_declaration=True,
        )

        # Validate the temporary RSS file before publication.
        validate_rss(temporary)

        # Replace the existing feed only after successful
        # generation and validation.
        temporary.replace(OUTPUT_FILE)

    finally:

        # Remove any temporary file remaining after failure.
        temporary.unlink(missing_ok=True)


# --------------------------------------------------
# Display Results
# --------------------------------------------------

def display_results(articles: list[Article]) -> None:
    """Display a summary of the generated RSS feed."""

    print("\nRSS Generation Summary")
    print("=" * 50)

    print(f"Generated: {OUTPUT_FILE}")
    print(f"Articles:  {len(articles)}")
    print("Validation: PASSED")

    print(
        "Updated:   "
        f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S UTC}"
    )

    print(f"Feed URL:  {FEED_URL}")

    print()

    for number, article in enumerate(
        articles,
        start=1,
    ):

        print(f"{number}. {article['title']}")

        print(f"   Date:  {article['date'].date()}")

        print(f"   URL:   {article['url']}")

        print(f"   Image: {article['image']}")

        print()


# --------------------------------------------------
# Main
# --------------------------------------------------

def main() -> int:
    """Execute the complete RSS generation workflow."""

    print("\nNASA Earth Observatory RSS Generator")
    print("=" * 50)

    print(f"Source: {SOURCE_URL}")
    print(f"Requested articles: {MAX_ARTICLES}")

    try:

        # Reuse HTTP connections throughout the workflow.
        with requests.Session() as session:

            session.headers.update(HEADERS)

            # Download the Image of the Day landing page.
            soup = download(session, SOURCE_URL)

            # Identify candidate article URLs.
            candidates = find_articles(soup)

            print(
                f"Candidate article links: "
                f"{len(candidates)}"
            )

            articles = []

            # Retrieve metadata for each candidate article.
            for url in candidates:

                try:

                    article = get_article(session, url)

                    if article is not None:
                        articles.append(article)

                except requests.RequestException as error:

                    print(
                        f"Warning: Could not retrieve {url}: "
                        f"{error}",
                        file=sys.stderr,
                    )

        print(f"Valid candidate articles: {len(articles)}")

        # Sort articles from newest to oldest.
        articles.sort(
            key=lambda article: article["date"],
            reverse=True,
        )

        # Retain the most recent articles.
        articles = articles[:MAX_ARTICLES]

        # Prevent publication of an incomplete feed.
        if len(articles) != MAX_ARTICLES:

            raise RuntimeError(
                f"Expected {MAX_ARTICLES} articles, "
                f"found {len(articles)}"
            )

        # Generate and validate the RSS feed.
        generate_rss(articles)

        # Display the results.
        display_results(articles)

        return 0

    except Exception as error:

        print(
            f"\nERROR: {error}",
            file=sys.stderr,
        )

        print(
            "RSS generation failed.",
            file=sys.stderr,
        )

        print(
            "The existing feed has not been replaced "
            "if generation or validation failed.",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())