import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def markdown_to_html(text):
    """
    Transforms markdown text of encyclopedia entry to html format.
    """
    # transformation of '#', '##', '###' regular expressions into h1, h2, h3 heading tags respectively
    text = re.sub(r'\s*#{3} ?(.+)', r'<h3>\1</h3>', text)
    text = re.sub(r'\s*#{2} ?(.+)', r'<h2>\1</h2>', text)
    text = re.sub(r'\s*#{1} ?(.+)', r'<h1>\1</h1>', text)
   
    # transformation of '**sampletext**' or '__sampletext__' into <b>sampleboldtext</b> (bold text)
    if '**' or '__' in text:
        text = re.sub(r'(\*\*|__)([^*_]+)\1', r'<b>\2</b>', text)

    # transformation of '* sampletext' or '- sampletext' into <li>sampletext</li> with all listitems surrounded by <ul></ul> tags
    if '*' or '-' in text:    
        text = re.sub(r'\s[*-] (.+)', r'<li>\1</li>', text)
        text = re.sub(r'(?s)(<li.*li>)', r'<ul>\1</ul>', text)

    # transformation of '[sampletext](link reference)' RE into link tag with href attribute
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)

    # adding paragraph tags (<p>...<p>) for text portions separated by '\r\n' at all places other than within or surounding headings and unordered lists
    text = re.sub(r'[\r][\n](.+)', r'<p>\1</p>', text)
    text = re.sub(r'(?s)(<p>.*)(<h\d>.*?</h\d>)(</p>)', r'\1\3\2', text)
    text = re.sub(r'(?s)<p>(<ul>.*?</ul>)', r'\1', text)
    text = re.sub(r'(?s)(<ul>.*?</ul>)</p>', r'\1', text)
    text = re.sub(r'(?s)(<ul>.*)(<p>|</p>)(.*</ul>)', r'\1\3', text)
  
    return text





