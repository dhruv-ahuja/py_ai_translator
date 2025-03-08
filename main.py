import asyncio
from pathlib import Path
import time

import logfire

from ai import create_agent, generate_language_prompt
from crawler import crawl_url
from config import settings


if settings.logfire.enable:
    logfire.configure(token=settings.logfire.token.get_secret_value())
    logfire.instrument_openai()

    # sleep to avoid interrupting user input when logfire emits startup log
    print("enabled Logfire telemetry")
    time.sleep(1)


async def sample_conversion():
    url = input("Enter URL to crawl: ").strip()
    name = input("Enter name for output file: ").strip()
    cache = input("Enable cache? (Y/n): ").strip().lower()
    if cache == "" or cache == "y":
        cache = True
    else:
        cache = False

    result = await crawl_url(url, cache)
    content = result.markdown

    if not content:
        print("error crawling page, exiting")
        return

    content = content.fit_markdown if content.fit_markdown else content
    print("content:", content, "\n\n")

    prompt = generate_language_prompt("Spanish", content)
    agent = create_agent(system_prompt=prompt)

    user_prompt = f"""
    Convert the following Markdown content into a bilingual document. Translate each paragraph into Spanish and place the original English paragraph below it. Also, translate headings into Spanish and keep the original English headings below them.
    
    {content}
    """
    translation_result = await agent.run(user_prompt)

    print(translation_result)

    output_folder = Path(settings.general.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file_path = output_folder.joinpath(f"{name}.md")

    with open(output_file_path, "w") as f:
        data = translation_result.data
        # remove markdown codeblock marker
        data = data.replace("```markdown", "").replace("```", "")
        f.write(data)


if __name__ == "__main__":
    asyncio.run(sample_conversion())
