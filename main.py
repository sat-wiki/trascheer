import csv
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import re
import requests
from tqdm import tqdm

re1 = re.compile(r'<td style="text-align:left" id="c24">(.*?)</td>', re.DOTALL)
re2 = re.compile(r'href="\.\./img/sat/([a-zA-Z\-_0-9]*)\.([a-zA-Z]*)"', re.DOTALL)

headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/120.0.2210.150 Version/16.0 Mobile/15E148 Safari/604.1"}

descriptions = []

contentPro = ''

with open('data.csv', newline = '', encoding = 'utf-8') as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in tqdm(spamreader):
        response = requests.get(row['Link_full'], headers = headers)
        cyberdescription = re1.search(response.text).group(2).replace("      ", "").replace("<p>", "").replace("</p>", "").replace("<ul>", "").replace("</ul>", "").replace("  <li>", "- ").replace("</li>", "")
        description = cyberdescription.replace("<b>", "*").replrep("</b>", "*").replace("<i>", "_").replace("</i>", "_")
        contentPro += f'== {row["Value"]}\n\n\u0023table([*原文*], [*中文翻译*], [{description}], [Translationcky])\n'
        images = (re.findall(re2, response.text))
        for image in images:
            image_url = f'https://www.nanosats.eu/img/sat/{image[0]}.{image[1]}'
            open(f'images/{image[0]}.{image[1]}', 'wb').write(requests.get(image_url, headers = headers).content)
            contentPro += f'#figure(image("images/{image[0]}.{image[1]}"), caption: [{image[0]}.{image[1]}])\n'

input_sequence = '<SENT_SPLIT>'.join(descriptions)
pipeline_ins = pipeline(task = Tasks.translation, model = "damo/nlp_csanmt_translation_en2zh")
outputs = pipeline_ins(input = input_sequence)

for translation in tqdm(outputs['translation'].split('<SENT_SPLIT>')):
    contentPro.replace('Translationcky', translation, 1)
print(contentPro, file = open('contentPro.typ', 'a'))

wikiDescription = contentPro.replace("*", "'''").replrep("_", "''")
print(wikiDescription, file = open('content.wikitext', 'w'))
