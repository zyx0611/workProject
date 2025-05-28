from bs4 import BeautifulSoup
import requests
import csv

response = requests.get('http://www.cnhivehub.com/sitemap.xml')

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'xml')
    arr = [i.text for i in soup.find_all('loc')]
    with open('../../utils/dayNum.csv', 'r+') as a:
        content = csv.reader(a)
        for con in content:
            num = int(con[0])
        urlArray = arr[num * 10: (num+1) * 10]
        url = "http://data.zz.baidu.com/urls?site=www.cnhivehub.com&token=eehiuOEZPm72Y49K"

        # 拼接为 text/plain 格式：每行一个 URL
        data = "\n".join(urlArray)

        # 发起 POST 请求
        headers = {'Content-Type': 'text/plain'}
        baiduResponse = requests.post(url, headers=headers, data=data.encode('utf-8'))

        # 打印返回结果
        print("Status Code:", baiduResponse.status_code)
        if baiduResponse.status_code == 200:
            a.write(f'\n{num + 1}')
        print("Response:", baiduResponse.text)
