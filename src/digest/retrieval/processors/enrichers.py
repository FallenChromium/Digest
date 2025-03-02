import yake
import textstat
import langdetect
from typing import Any, Dict, List, Optional

from digest.retrieval.models import ContentPiece
from digest.retrieval.processors.base import BaseProcessor, ProcessorRegistry


@ProcessorRegistry.register
class LanguageDetectorProcessor(BaseProcessor):
    """Processor that detects the language of content."""
    
    processor_id = "language_detector"
    name = "Language Detector"
    description = "Detects the language of content using langdetect library."
    
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        """Configuration schema for language detector."""
        return {
            "type": "object",
            "properties": {}
        }
    
    async def process(self, content: ContentPiece) -> ContentPiece:
        """Detect language of content."""
        processed_content = ContentPiece(**content.model_dump())
        
        if not processed_content.content:
            return processed_content
            
        try:
            language = langdetect.detect(processed_content.content)
            processed_content.metadata["language"] = language
        except:
            # Default to English if detection fails
            processed_content.metadata["language"] = "en"
            
        return processed_content


@ProcessorRegistry.register
class KeywordExtractorProcessor(BaseProcessor):
    """Processor that extracts keywords using YAKE."""
    
    processor_id = "keyword_extractor"
    name = "Keyword Extractor"
    description = "Extracts keywords from content using YAKE algorithm."
    
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        """Configuration schema for keyword extractor."""
        return {
            "type": "object",
            "properties": {
                "max_keywords": {
                    "type": "integer",
                    "description": "Maximum number of keywords to extract",
                    "default": 10
                }
            }
        }
    
    async def process(self, content: ContentPiece) -> ContentPiece:
        """Extract keywords from content."""
        processed_content = ContentPiece(**content.model_dump())
        
        if not processed_content.content:
            return processed_content
            
        language = processed_content.metadata.get("language", "en")
        max_keywords = self.config.get("max_keywords", 10)
        
        # Initialize YAKE keyword extractor
        kw_extractor = yake.KeywordExtractor(
            lan=language,
            n=3,  # ngram size
            dedupLim=0.9,  # deduplication threshold
            top=max_keywords,
            features=None
        )
        
        # Extract keywords
        keywords = kw_extractor.extract_keywords(processed_content.content)
        # YAKE returns (keyword, score) tuples - we just want keywords
        keywords = [kw[0] for kw in keywords]
        
        processed_content.metadata["keywords"] = keywords
        
        return processed_content


@ProcessorRegistry.register
class ReadabilityScoreProcessor(BaseProcessor):
    """Processor that calculates readability scores using textstat."""
    
    processor_id = "readability_score"
    name = "Readability Score"
    description = "Calculates readability metrics using textstat library."
    
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        """Configuration schema for readability score."""
        return {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "description": "Readability metrics to calculate",
                    "items": {
                        "type": "string",
                        "enum": [
                            "flesch_reading_ease",
                            "flesch_kincaid_grade",
                            "gunning_fog",
                            "smog_index",
                            "coleman_liau_index",
                            "automated_readability_index",
                            "dale_chall_readability_score"
                        ]
                    },
                    "default": ["flesch_reading_ease", "flesch_kincaid_grade"]
                }
            }
        }
    
    async def process(self, content: ContentPiece) -> ContentPiece:
        """Calculate readability metrics for content."""
        processed_content = ContentPiece(**content.model_dump())
        
        if not processed_content.content:
            return processed_content
            
        language = processed_content.metadata.get("language", "en")
        metrics = self.config.get("metrics", ["flesch_reading_ease", "flesch_kincaid_grade"])
        
        # Initialize readability scores
        processed_content.metadata["readability"] = {}
        
        # Set language for textstat
        textstat.set_lang(language)
        
        # Calculate requested metrics
        metric_functions = {
            "flesch_reading_ease": textstat.flesch_reading_ease,
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade,
            "gunning_fog": textstat.gunning_fog,
            "smog_index": textstat.smog_index,
            "coleman_liau_index": textstat.coleman_liau_index,
            "automated_readability_index": textstat.automated_readability_index,
            "dale_chall_readability_score": textstat.dale_chall_readability_score
        }
        
        for metric in metrics:
            if metric in metric_functions:
                score = metric_functions[metric](processed_content.content)
                processed_content.metadata["readability"][metric] = round(score, 2)
        
        return processed_content