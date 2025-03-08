from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import os


def generate_language_prompt(language: str = "Spanish", content: str = ""):
    PROMPT = f"""
Please take the following Markdown content and create a bilingual document. Translate each paragraph into {language}, then place the original English paragraph below it. Repeat this process for all paragraphs. Ensure that headings are translated as well.
Input Markdown Content:
{content}
Output Requirements:
Translate each paragraph into {language}.
Place the original English paragraph below its {language} translation.
Repeat steps 1 and 2 for all paragraphs.
Translate headings into {language} and maintain the original English headings below them.

- Ensure each pair of paragraphs is separated by a blank line for readability.
- Maintain consistency in formatting across both languages, especially for lists, code blocks, and quotes.

Example Output Format:
<{language} translation of the first paragraph.>

<Original English first paragraph.>

<{language} translation of the second paragraph.>

<Original English second paragraph.>

...

---------------------------------------------

Please proceed with the conversion.
"""
    return PROMPT


def create_agent(
    model_name: str = "google/gemini-2.0-flash-lite-001",
    instrument: bool = True,
    system_prompt: str = generate_language_prompt(),
) -> Agent:
    model = OpenAIModel(
        model_name=model_name,
        provider=OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]),
    )
    agent = Agent(model, instrument=instrument, system_prompt=system_prompt)

    return agent
