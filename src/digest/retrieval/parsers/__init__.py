"""
Parsers for various types of news sources.
"""

from digest.retrieval.parsers.base import BaseParser, ParserRegistry
from digest.retrieval.parsers.rss import RssParser
from digest.retrieval.parsers.tchan import TchanParser
# Add more parser imports here as they are created 