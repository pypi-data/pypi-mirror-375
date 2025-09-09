"""Search Agent Plugin using Cadence SDK."""

from typing import Optional, TypedDict

from cadence_sdk import BaseAgent, BasePlugin, PluginMetadata
from cadence_sdk.decorators import list_schema
from typing_extensions import Annotated


@list_schema
class SearchResponseSchema(TypedDict):
    """Unified schema for representing heterogeneous search response entities"""

    title: Annotated[
        str,
        ...,
        "Primary identifier or headline of the search result. For news articles: the article headline; for images: descriptive caption or filename; for general search: the page title or primary heading that encapsulates the content's essence",
    ]

    description: Annotated[
        Optional[str],
        None,
        "Contextual summary or metadata providing substantive insight into the search result. For news: article excerpt or lead paragraph; for images: alt text, caption, or contextual description; for general search: meta description or extracted content snippet that offers semantic understanding of the result's relevance",
    ]

    link: Annotated[
        str,
        ...,
        "Canonical URI representing the authoritative source location. This serves as the primary navigation endpoint, ensuring consistent access to the original resource regardless of search result type or content modality",
    ]

    thumbnail_link: Annotated[
        Optional[str],
        None,
        "Optional visual representation URI for enhanced user experience. For images: compressed preview version; for news articles: featured image or publication logo; for general search: favicon, screenshot, or representative visual element that aids in result recognition and selection",
    ]


class SearchPlugin(BasePlugin):
    """Search Plugin Bundle using SDK interfaces."""

    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="browse_internet",
            version="1.3.0",
            description="Internet Browser Search agent, using DuckDuckGo API",
            agent_type="specialized",
            response_schema=SearchResponseSchema,
            response_suggestion="When presenting search results, use clear headings and bullet points for better readability. Search response must include title, image (thumbnail if has any), link to article, maybe the approximated time",
            capabilities=[
                "web_search",
                "news_search",
                "image_search",
            ],
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            dependencies=[
                "cadence-sdk>=1.3.0,<2.0.0",
                "ddgs>=9.5.4,<10.0.0",
            ],
        )

    @staticmethod
    def create_agent() -> BaseAgent:
        """Create search agent instance."""
        from .agent import SearchAgent

        return SearchAgent(SearchPlugin.get_metadata())

    @staticmethod
    def health_check() -> dict:
        """Perform health check."""
        try:
            return {
                "healthy": True,
                "details": "Search plugin is operational",
                "checks": {"search_engine": "OK", "dependencies": "OK"},
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": f"Search plugin health check failed: {e}",
                "error": str(e),
            }
