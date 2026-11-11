#!/usr/bin/env python3

"""
NASA Earth Observatory Image of the Day RSS Generator

Creates an RSS 2.0 feed containing the latest image
plus the previous five images.

Includes:
    - Article title
    - Article URL
    - NASA summary
    - NASA thumbnail (URL encoded)
    - Publication date

Output:
    feed.xml
"""

import sys
import html
import re

from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, quote
from xml.etree.ElementTree import (
    Element,
    SubElement,
    ElementTree,
    register_namespace,
    indent,
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

OUTPUT_FILE = Path("feed.xml")

MAX_ARTICLES = 6

MEDIA_NS = "http://search.yahoo.com/mrss/"

register_namespace("media", MEDIA_NS)

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


# --------------------------------------------------
# Download HTML
# --------------------------------------------------

def download(url):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


# --------------------------------------------------
# Find candidate article links
# --------------------------------------------------

def find_articles(soup):

    candidates = []
    seen = set()

    for anchor in soup.find_all("a", href=True):

        url = urljoin(SOURCE_URL, anchor["href"])
        parsed = urlparse(url)

        if not url.startswith(ARTICLE_PREFIX):
            continue

        relative = parsed.path.removeprefix(
            "/earth/earth-observatory/"
        ).strip("/")

        # Only direct article URLs.
        if not relative or "/" in relative:
            continue

        if relative in EXCLUDED:
            continue

        # Ignore duplicate links.
        url = url.split("#")[0].rstrip("/") + "/"

        if url in seen:
            continue

        seen.add(url)
        candidates.append(url)

    return candidates


# --------------------------------------------------
# Retrieve article metadata
# --------------------------------------------------

def get_meta(soup, property_name):

    tag = soup.find(
        "meta",
        attrs={"property": property_name},
    )

    return (
        tag.get("content", "").strip()
        if tag else ""
    )


def get_article(url):

    soup = download(url)

    title = get_meta(soup, "og:title")
    summary = get_meta(soup, "og:description")

    # Encode special characters in NASA image URLs.
    # Example: curly apostrophe becomes %E2%80%99.
    image = quote(
        get_meta(soup, "og:image"),
        safe=":/"
    )

    published = get_meta(
        soup, "article:published_time"
    )

    if not all((title, summary, image, published)):
        return None

    try:
        date = datetime.fromisoformat(
            published.replace("Z", "+00:00")
        )
    except ValueError:
        return None

    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Remove NASA Science suffix.
    title = re.sub(
        r"\s*-\s*NASA Science$",
        "",
        title,
    )

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "image": image,
        "date": date,
    }


# --------------------------------------------------
# Generate RSS
# --------------------------------------------------

def generate_rss(articles):

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = (
        "NASA Earth Observatory - Image of the Day"
    )

    SubElement(channel, "link").text = SOURCE_URL

    SubElement(channel, "description").text = (
        "The six most recent NASA Earth Observatory "
        "Images of the Day."
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

        # HTML description containing thumbnail
        # and NASA's original summary.
        description = (
            f'<img src="{html.escape(article["image"], quote=True)}" '
            f'alt="{html.escape(article["title"], quote=True)}">'
            f'<p>{html.escape(article["summary"])}</p>'
        )

        SubElement(item, "description").text = (
            description
        )

        # Media RSS thumbnail.
        SubElement(
            item,
            f"{{{MEDIA_NS}}}thumbnail",
            url=article["image"],
        )

    indent(rss, space="  ")

    tree = ElementTree(rss)

    # Write to a temporary file first.
    # Only replace the existing feed after success.
    temporary = OUTPUT_FILE.with_suffix(".tmp")

    tree.write(
        temporary,
        encoding="utf-8",
        xml_declaration=True,
    )

    temporary.replace(OUTPUT_FILE)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\nNASA Earth Observatory RSS Generator")
    print("=" * 50)

    try:

        soup = download(SOURCE_URL)

        candidates = find_articles(soup)

        print(
            f"Candidate article links: "
            f"{len(candidates)}"
        )

        articles = []

        for url in candidates:

            try:
                article = get_article(url)

                if article:
                    articles.append(article)

            except requests.RequestException as error:
                print(
                    f"Warning: Could not retrieve {url}: "
                    f"{error}",
                    file=sys.stderr,
                )

        # Sort newest to oldest.
        articles.sort(
            key=lambda item: item["date"],
            reverse=True,
        )

        # Keep the latest six.
        articles = articles[:MAX_ARTICLES]

        if len(articles) != MAX_ARTICLES:
            raise RuntimeError(
                f"Expected {MAX_ARTICLES} articles, "
                f"found {len(articles)}"
            )

        generate_rss(articles)

        print(f"\nGenerated: {OUTPUT_FILE}")
        print(f"Articles: {len(articles)}\n")

        for number, article in enumerate(
            articles, start=1
        ):

            print(
                f"{number}. "
                f"{article['title']}"
            )

            print(
                f"   Date: "
                f"{article['date'].date()}"
            )

            print(
                f"   URL: "
                f"{article['url']}"
            )

            print(
                f"   Image: "
                f"{article['image']}"
            )

            print()

    except Exception as error:

        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
