import csv
import re
import requests
import sys
from tqdm import tqdm
from transformers import pipeline, AutoModelWithLMHead, AutoTokenizer
import warnings

warnings.filterwarnings('ignore')

re1 = re.compile(r'<th><b>Units or mass</b></th>--newline-- *<td>--newline-- *<p>(.*)</p>--newline-- *</td>', re.DOTALL)
re2 = re.compile(r'<th><b>Mass in kg</b></th>--newline-- *<td>--newline-- *<p>(.*)</p>--newline-- *</td>', re.DOTALL)
re3 = re.compile(r'<th><b>Oneliner</b></th>--newline-- *<td>--newline-- *<p>(.*)</p>--newline-- *</td>', re.DOTALL)
re4 = re.compile(r'<td style="text-align:left" id="c24">(.*?)</td>', re.DOTALL)
reNotFound = re1.findall('Hello!')

headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/120.0.2210.150 Version/16.0 Mobile/15E148 Safari/604.1"}

print('loading model...')

model = AutoModelWithLMHead.from_pretrained('Helsinki-NLP/opus-mt-en-zh')
tokenizer = AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-zh')
translation = pipeline('translation_xx_to_yy', model = model, tokenizer = tokenizer)

print('model loaded!')

with open('data.csv', newline = '', encoding = 'utf-8') as csvfile:
    spamreader = csv.DictReader(csvfile)
    test = 0
    for row in tqdm(spamreader):
        try:
            response = requests.get(row['Link_full'], headers = headers)
            piano = response.text.replace('\n', '--newline--')
            unit = re1.findall(response.text)
            if unit != reNotFound:
                unit = unit[0]
            else:
                unit = ''
            mass = re2.findall(response.text)
            if mass != reNotFound:
                mass = mass[0]
            else:
                mass = ''
            oneliner = re3.findall(response.text)
            if oneliner != reNotFound:
                oneliner = oneliner[0]
                try:
                    onelinerCN = translation(oneliner.replace('--newline--', '\n'))[0]["translation_text"]
                except Exception as e:
                    onelinerCN = '英文过长，大模型表示拒绝工作 qwq'
            else:
                oneliner, onelinerCN = '', ''
            description = re4.findall(response.text)
            if description != reNotFound:
                description = description[0]
                if type(description) != type('abc'):
                    description = description[0]
                try:
                    descriptionCN = translation(description.replace('--newline--', '\n'))[0]["translation_text"]
                except Exception as e:
                    descriptionCN = '英文过长，大模型表示拒绝工作 qwq'
            else:
                description, descriptionCN = '', ''
            theLine = f'{row["Mission name"]} 6cky6 {unit} 6cky6 {mass} 6cky6 {oneliner} 6cky6 {onelinerCN} 6cky6 {description} 6cky6 {descriptionCN}'.replace('--newline--', ' 8cky8 ').replace('\n', ' 8cky8 ')
            print(theLine, file = open('output.csv', 'a'))
        except Exception as e:
            print(f'Fetch {row["Mission name"]} error with {e}!', file = open('stare.txt', 'a'))
        test += 1
        if test >= 10:
            sys.exit()
