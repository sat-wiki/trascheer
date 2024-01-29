import csv
import filetype
import re
import requests
from tqdm import tqdm
from transformers import pipeline, AutoModelWithLMHead, AutoTokenizer
import warnings

warnings.filterwarnings('ignore')

re1 = re.compile(r'<td style="text-align:left" id="c24">(.*?)</td>', re.DOTALL)
re2 = re.compile(r'href="\.\./img/sat/([a-zA-Z\-_0-9]*)\.([a-zA-Z]*)"', re.DOTALL)
re3 = re.compile(r'<a [^>]*href="([^"]*)"[^>]*>([^<]*)</a>')
re3n = '#link("\1")[\2]'

headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/120.0.2210.150 Version/16.0 Mobile/15E148 Safari/604.1"}

descriptions = []

contentPro = ''

print('loading model...')

model = AutoModelWithLMHead.from_pretrained('Helsinki-NLP/opus-mt-en-zh')
tokenizer = AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-zh')
translation = pipeline('translation_xx_to_yy', model = model, tokenizer = tokenizer)

print('loaded model!')

test = 0

with open('data.csv', newline = '', encoding = 'utf-8') as csvfile:
    spamreader = csv.DictReader(csvfile)
    for row in tqdm(spamreader):
        try:
            response = requests.get(row['Link_full'], headers = headers)
            cyberdescription = re3.sub(re3n, re1.search(response.text).group(1).replace("<p>", "").replace("</p>", "").replace("<ul>", "").replace("</ul>", "").replace("  <li>", "- ").replace("</li>", "").replace("  ", ""))
            description = cyberdescription.replace("<b>", "*").replace("</b>", "*").replace("<i>", "_").replace("</i>", "_")
            contentPro += f'== {row["Value"]} \n === 原文 === \n {description} \n === 中文翻译 \n {translation(description)[0]["translation_text"]} \n'
        except Exception as e:
            print(f'Fetch {row["Mission name"]} error with {e}!', file = open('stare.txt', 'a'))
        images = (re.findall(re2, response.text))
        for image in images:
            image_url = f'https://www.nanosats.eu/img/sat/{image[0]}.{image[1]}'
            imageContent = requests.get(image_url, headers = headers).content
            try:
                imageKind = filetype.guess(imageContent)
                if imageKind and imageKind.extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico']:
                    imageKind = imageKind.extension
                    open(f'images/{image[0].replace("*", "").replace("_", "")}.{imageKind}', 'wb').write(imageContent)
                    contentPro += f'#figure(image("images/{image[0].replace("*", "").replace("_", "")}.{imageKind}"), caption: [{image[0].replace("*", "").replace("_", "")}.{imageKind}])\n'
                else:
                    print(f'Unable to insert {image[0]}.{image[1]}!', file = open('stare.txt', 'a'))
            except Exception as e:
                print(f'Unable to insert {image[0]}.{image[1]} with error {e}!', file = open('stare.txt', 'a'))
        test += 1
        if test > 25:
            break

print(descriptions, file = open('contentPro.list', 'w'))
print(contentPro, file = open('contentPro.typ', 'a'))
wikiDescription = contentPro.replace("*", "'''").replace("_", "''")
print(wikiDescription, file = open('content.wikitext', 'w'))
