import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

html_content = """<a target="_blank" aria-labelledby="K8AvaZWoFsLFp84PurvauAk_29" class="Zbfntb" href="https://www.familyhandyman.com/list/floor-trim-moldings-and-styles/#:~:text=%E2%80%9COne%2Dpiece%20baseboard%20is%20what,style%2C%20from%20traditional%20to%20modern." ping="/url?sa=t&amp;source=web&amp;rct=j&amp;url=https://www.familyhandyman.com/list/floor-trim-moldings-and-styles/%23:~:text%3D%25E2%2580%259COne%252Dpiece%2520baseboard%2520is%2520what,style%252C%2520from%2520traditional%2520to%2520modern.&amp;ved=2ahUKEwjV6ZbwzaCRAxXC4skDHbqdFpcQmL8OegQICRAC&amp;opi=89978449"></a>"""

soup = BeautifulSoup(html_content, "html.parser")
links = []

for a in soup.find_all("a", href=True):
    href = a['href']
    # Only keep real external URLs
    if href.startswith("http"):
        links.append(href)
    # Optional: parse Google redirect /url?q= links
    elif href.startswith("/url?q="):
        parsed_url = parse_qs(urlparse(href).query).get("q")
        if parsed_url:
            links.append(parsed_url[0])

print(links)




