from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


def generate_language_prompt_old(language: str = "Spanish", content: str = ""):
    # - Remove any extraneous content such as social media links, email addresses, webpage links, navigation menus, account login sections, headers, footers, or any other elements that do not contribute to the main text.
    PROMPT = f"""
    You are an intelligent translation assistant tasked with translating markdown content from a website into {language}. Your task is to:
    - Translate and output the markdown content while preserving all relevant markdown formatting such as headings, lists, code blocks, and quotes—only if they are part of the main body of the text.
    - For every paragraph in the text, produce a pair of paragraphs:
         1. The first paragraph should be the translated text in {language}.
         2. The second paragraph should be the original English text.
    - Ensure each pair of paragraphs is separated by a blank line for readability.
    - Maintain consistency in formatting across both languages, especially for lists, code blocks, and quotes.
    - If the source content includes non-standard elements or ambiguous formatting (e.g., excessive or unnecessary headings), reformat them into a clear, consistent structure that maintains readability.
    - Handle unclear or ambiguous content by providing a faithful translation and leaving a placeholder or a note if necessary.
    - Do not add any extra text outside of the markdown response; simply output the translated markdown content.
    """
    return PROMPT


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
    model_name = "google/gemini-flash-1.5-8b"
    # model_name = "deepseek/deepseek-r1"
    # model_name = "nousresearch/hermes-3-llama-3.1-70b"
    model = OpenAIModel(model_name=model_name)
    agent = Agent(model, instrument=instrument, system_prompt=system_prompt)

    return agent
