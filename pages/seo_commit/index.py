from bs4 import BeautifulSoup
import requests
import csv

response = requests.get('http://www.cnhivehub.com/sitemap.xml')

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'xml')
    arr = [i.text for i in soup.find_all('loc')]

    # csv_path = '../../utils/dayNum.csv'
    csv_path = 'utils/dayNum.csv'
    with open(csv_path, 'r+') as a:
        reader = csv.reader(a)
        rows = list(reader)
        if rows:
            num = int(rows[0][0])
        else:
            num = 0  # fallback

        urlArray = arr[num * 10: (num * 10 + 1)]
        url = "http://data.zz.baidu.com/urls?site=www.cnhivehub.com&token=eehiuOEZPm72Y49K"

        data = "\n".join(urlArray)
        print('本次 URL:', data)

        headers = {'Content-Type': 'text/plain'}
        baiduResponse = requests.post(url, headers=headers, data=data.encode('utf-8'))
        print("Status Code:", baiduResponse.status_code)
        print("Response:", baiduResponse.text)

        # 如果成功，覆盖写入新的 dayNum
        if baiduResponse.status_code == 200:
            a.seek(0)           # 回到文件头
            a.truncate()        # 清空文件
            writer = csv.writer(a)
            writer.writerow([num + 1])