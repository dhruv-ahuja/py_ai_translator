import asyncio
import logfire
import os

from ai import create_agent, generate_language_prompt
from crawler import crawl_url


logfire.configure(token=os.environ["LOGFIRE_TOKEN"])
logfire.instrument_openai()


async def sample_conversion():
    url, name = "https://www.sparknotes.com/lit/montecristo/full-text/chapter-1/", "montecristo_1"
    # url, name = "https://firecrawl.dev", "fc"

    result = await crawl_url(url)
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

    with open(f"{name}.md", "w") as f:
        data = translation_result.data
        data = data.replace("```markdown", "").replace("```", "")
        f.write(data)


if __name__ == "__main__":
    asyncio.run(sample_conversion())
