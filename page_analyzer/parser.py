from bs4 import BeautifulSoup

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else None

    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else None

    meta_desc = soup.find('meta', attrs={'name': 'description'})
    content = meta_desc.get('content', '').strip() if meta_desc else None

    if content == '':
        content = None

    return h1, title, content