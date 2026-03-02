"""Automates updating README.md with the latest blog posts from Medium and Data Flakes RSS feeds.

===================================================
Filename: update_readme.py
Created Date: 09-09-2024
Author: Elliott Fairhall
Email: elliott@elliottfairhall.dev
Version: 1.2

Purpose:
--------
This script automates the process of updating the README.md file in a GitHub repository
with the latest blog posts from Medium and Data Flakes personal website RSS feeds.
It checks for new posts, ensures the connections to the feeds are valid, and updates
the README.md only if new posts are found. The script is designed to run within a
GitHub Action workflow.

Revision History:
-----------------
09-09-2024: Redesign of solution to meet new standards. (Elliott Fairhall)
05-11-2024: Implemented more error handling and ensured that tests are completed before continuing. (Elliott Fairhall)
25-01-2026: Refactored for Ruff standards, added type hints and Google-style docstrings. (Antigravity AI)
02-03-2026: Switched Data Flakes feed from rss-featured.xml to rss.xml for full post coverage. (Elliott Fairhall)
===================================================
"""

import logging
from pathlib import Path

import feedparser
import requests

# Constants for the RSS feed URLs and the maximum number of posts to display
MEDIUM_RSS_FEED_URL = "https://medium.com/feed/@ElliottFairhall"
DATA_FLAKES_RSS_FEED_URL = "https://www.data-flakes.dev/rss.xml"
MAX_POSTS = 5
TIMEOUT = 10  # Timeout for connection testing (in seconds)
HTTP_OK = 200

# Set up logging for debugging and error handling
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_connection(url: str) -> bool:
    """Tests if a URL is reachable by making a HEAD request.

    Args:
        url: The URL to test.

    Returns:
        True if the URL is reachable (status code 200), False otherwise.
    """
    try:
        response = requests.head(url, timeout=TIMEOUT)
        if response.status_code == HTTP_OK:
            logging.info("Successfully connected to %s", url)
            return True
        logging.error(
            "Failed to connect to %s. Status code: %d", url, response.status_code
        )
        return False
    except requests.exceptions.RequestException as e:
        logging.error("Error connecting to %s: %s", url, str(e))
        return False


def fetch_posts_from_feed(feed_url: str) -> list[str]:
    """Fetches and parses posts from an RSS feed URL.

    Args:
        feed_url: The URL of the RSS feed to fetch posts from.

    Returns:
        A list of formatted strings containing post titles and URLs in markdown format.
    """
    try:
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            logging.error("Error parsing feed %s: %s", feed_url, feed.bozo_exception)
            return []

        posts: list[str] = [
            f"- [{entry.title}]({entry.link})" for entry in feed.entries[:MAX_POSTS]
        ]
        logging.info("Successfully fetched %d posts from %s", len(posts), feed_url)
        return posts

    except Exception as e:
        logging.error("Failed to fetch posts from %s: %s", feed_url, str(e))
        return []


def update_readme(medium_posts: list[str], data_flakes_posts: list[str]) -> None:
    """Updates the README.md file with the fetched blog posts.

    Args:
        medium_posts: List of formatted Medium blog post strings.
        data_flakes_posts: List of formatted Data Flakes blog post strings.
    """
    try:
        readme = Path("README.md")
        content = readme.read_text(encoding="utf-8")

        # Markers in README.md to indicate where to insert the blog posts
        start_marker = "<!-- BLOG-POST-LIST:START -->"
        end_marker = "<!-- BLOG-POST-LIST:END -->"
        start_index = content.find(start_marker) + len(start_marker)
        end_index = content.find(end_marker)

        if start_index == -1 or end_index == -1:
            logging.error("Blog post markers not found in README.md.")
            return

        # Build the new content to insert
        new_content = content[:start_index] + "\n"

        if medium_posts:
            new_content += "### Latest Medium Posts\n"
            new_content += "\n".join(medium_posts) + "\n\n"

        if data_flakes_posts:
            new_content += "### Latest Data Flakes Posts\n"
            new_content += "\n".join(data_flakes_posts) + "\n"

        new_content += content[end_index:]

        # Only write if content has changed to avoid unnecessary commits
        if content != new_content:
            readme.write_text(new_content, encoding="utf-8")
            logging.info("README.md successfully updated with the latest blog posts.")
        else:
            logging.info("No changes to README.md detected. Skipping write.")

    except Exception as e:
        logging.error("Failed to update README.md: %s", str(e))


def main() -> None:
    """Main execution block to fetch posts and update the README."""
    m_posts: list[str] = []
    df_posts: list[str] = []

    # Fetch Medium posts if the connection is successful
    if test_connection(MEDIUM_RSS_FEED_URL):
        m_posts = fetch_posts_from_feed(MEDIUM_RSS_FEED_URL)
    else:
        logging.warning("Skipping Medium feed due to connection issues.")

    # Fetch Data Flakes posts if the connection is successful
    if test_connection(DATA_FLAKES_RSS_FEED_URL):
        df_posts = fetch_posts_from_feed(DATA_FLAKES_RSS_FEED_URL)
    else:
        logging.warning("Skipping Data Flakes feed due to connection issues.")

    # Update README.md if there are new posts
    if m_posts or df_posts:
        logging.info("Updating README with new posts.")
        update_readme(m_posts, df_posts)
    else:
        logging.info("No new posts available. Skipping README update.")


if __name__ == "__main__":
    main()
