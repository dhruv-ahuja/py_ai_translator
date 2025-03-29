from pydantic import BaseModel
from xml.dom.minidom import Document


class RSSItem(BaseModel):
    title: str
    description: str
    link: str
    guid: str


class RSSFeed(BaseModel):
    title: str
    description: str
    link: str
    items: list[RSSItem]

    def to_xml(self) -> str:
        doc = Document()
        rss = doc.createElement("rss")
        rss.setAttribute("version", "2.0")
        doc.appendChild(rss)

        channel = doc.createElement("channel")
        rss.appendChild(channel)

        # Channel elements
        title_elem = doc.createElement("title")
        title_elem.appendChild(doc.createTextNode(self.title))
        channel.appendChild(title_elem)

        link_elem = doc.createElement("link")
        link_elem.appendChild(doc.createTextNode(self.link))
        channel.appendChild(link_elem)

        description_elem = doc.createElement("description")
        description_elem.appendChild(doc.createTextNode(self.description))
        channel.appendChild(description_elem)

        # Add items
        for item in self.items:
            item_elem = doc.createElement("item")
            channel.appendChild(item_elem)

            title = doc.createElement("title")
            title.appendChild(doc.createTextNode(item.title))
            item_elem.appendChild(title)

            description = doc.createElement("description")
            description.appendChild(doc.createTextNode(item.description))
            item_elem.appendChild(description)

            link = doc.createElement("link")
            link.appendChild(doc.createTextNode(item.link))
            item_elem.appendChild(link)

            guid = doc.createElement("guid")
            guid.appendChild(doc.createTextNode(item.guid))
            item_elem.appendChild(guid)

        return doc.toprettyxml(indent="  ", encoding="utf-8")
