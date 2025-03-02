"""
Content processors for cleaning and enriching retrieved content.
"""

from digest.retrieval.processors.base import BaseProcessor, ProcessorRegistry
from digest.retrieval.processors.pipeline import ProcessingPipeline
from digest.retrieval.processors.cleaners import ReaderModeProcessor
from digest.retrieval.processors.enrichers import LanguageDetectorProcessor, KeywordExtractorProcessor, ReadabilityScoreProcessor 