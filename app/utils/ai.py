from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config.app_settings import settings


def get_language_prompt(language: str = "Spanish"):
    PROMPT = f"""
Please take the following Markdown content and create a bilingual document. Translate each paragraph into {language}, then place the original English paragraph below it. Repeat this process for all paragraphs. Ensure that headings are translated as well.
Output Requirements:
Translate each paragraph into {language}.
Place the original English paragraph below its {language} translation.
Repeat steps 1 and 2 for all paragraphs.
Translate headings into {language} and maintain the original English headings below them.

- Ensure each pair of paragraphs is separated by a blank line for readability.
- Maintain consistency in formatting across both languages, especially for lists, code blocks, and quotes.
- Remove any website navigation content like headers, footers, sidebar, etc.
- Ensure that you retain code blocks.
    - Ensure that you keep links relevant to the content such as image links, links to another articles and so on.
    - Ensure that you extract source links to images and keep them in the content as they were originally.
    - IMPORTANT: Do not remove or alter any image links or references. Ensure all images are properly displayed in both translations.
    - For image links, ensure you preserve them.
    - For image links inside markdown content, retain the original markdown syntax, e.g., ![Alt text](<link>).
    - For external links, ensure they are preserved exactly as in the original content.
    
    Example Output Format:
    <{language} translation of the first paragraph.>

    <Original English first paragraph.>

    <{language} translation of the second paragraph.>

    <Original English second paragraph.>

    ...

    ---------------------------------------------

    Please proceed with the conversions as the data is given to you.
    """
    return PROMPT


def get_agent_prompt(content: str, language: str = "Spanish") -> str:
    PROMPT = f"""
    Convert the following Markdown content into a bilingual document. Translate each paragraph into {language} and place the original English paragraph below it. Also, translate headings into {language} and keep the original English headings below them.

    IMPORTANT: 
    - Preserve all image links and external links exactly as they appear in the original content, including image sources inside link tags.
    - Do not remove or alter any markdown syntax for images, links, or code blocks.
    - Ensure images are displayed correctly in both translations by retaining their source links.

    {content}
    """
    return PROMPT


def create_agent(
    model_name: str = "google/gemini-2.0-flash-lite-001",
    instrument: bool = True,
    system_prompt: str = get_language_prompt(),
) -> Agent:
    model = OpenAIModel(
        model_name=model_name,
        provider=OpenAIProvider(
            base_url=settings.open_router.base_url, api_key=settings.open_router.api_key.get_secret_value()
        ),
    )
    agent = Agent(model, instrument=instrument, system_prompt=system_prompt)

    return agent
