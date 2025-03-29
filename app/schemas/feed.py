from datetime import datetime
from pydantic import BaseModel
from xml.dom.minidom import Document
from typing import Optional


class AtomItem(BaseModel):
    title: str
    summary: str
    link: str
    id: str
    updated: datetime
    author: Optional[str] = None
    content: Optional[str] = None


class AtomFeed(BaseModel):
    title: str
    subtitle: str
    link: str
    id: str
    updated: datetime
    author: Optional[str] = None
    entries: list[AtomItem]

    def to_xml(self) -> str:
        doc = Document()
        feed = doc.createElement("feed")
        feed.setAttribute("xmlns", "http://www.w3.org/2005/Atom")
        doc.appendChild(feed)

        # Feed metadata
        title_elem = doc.createElement("title")
        title_elem.appendChild(doc.createTextNode(self.title))
        feed.appendChild(title_elem)

        subtitle_elem = doc.createElement("subtitle")
        subtitle_elem.appendChild(doc.createTextNode(self.subtitle))
        feed.appendChild(subtitle_elem)

        link_elem = doc.createElement("link")
        link_elem.setAttribute("href", self.link)
        feed.appendChild(link_elem)

        id_elem = doc.createElement("id")
        id_elem.appendChild(doc.createTextNode(self.id))
        feed.appendChild(id_elem)

        updated_elem = doc.createElement("updated")
        updated_elem.appendChild(doc.createTextNode(self.updated.isoformat()))
        feed.appendChild(updated_elem)

        if self.author:
            author_elem = doc.createElement("author")
            name_elem = doc.createElement("name")
            name_elem.appendChild(doc.createTextNode(self.author))
            author_elem.appendChild(name_elem)
            feed.appendChild(author_elem)

        # Add entries
        for entry in self.entries:
            entry_elem = doc.createElement("entry")
            feed.appendChild(entry_elem)

            title = doc.createElement("title")
            title.appendChild(doc.createTextNode(entry.title))
            entry_elem.appendChild(title)

            summary = doc.createElement("summary")
            summary.appendChild(doc.createTextNode(entry.summary))
            entry_elem.appendChild(summary)

            link = doc.createElement("link")
            link.setAttribute("href", entry.link)
            entry_elem.appendChild(link)

            id_elem = doc.createElement("id")
            id_elem.appendChild(doc.createTextNode(entry.id))
            entry_elem.appendChild(id_elem)

            updated_elem = doc.createElement("updated")
            updated_elem.appendChild(doc.createTextNode(entry.updated.isoformat()))
            entry_elem.appendChild(updated_elem)

            if entry.author:
                author_elem = doc.createElement("author")
                name_elem = doc.createElement("name")
                name_elem.appendChild(doc.createTextNode(entry.author))
                author_elem.appendChild(name_elem)
                entry_elem.appendChild(author_elem)

            if entry.content:
                content_elem = doc.createElement("content")
                content_elem.setAttribute("type", "html")
                content_elem.appendChild(doc.createTextNode(entry.content))
                entry_elem.appendChild(content_elem)

        return doc.toprettyxml(indent="  ", encoding="utf-8")
