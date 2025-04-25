# 放在测试文件里或 conftest.py 中
import csv


# def pytest_generate_tests(metafunc):
#     if 'url' in metafunc.fixturenames:
#         with open('../utils/yesterdayURL.csv', 'r') as f:
#             reader = csv.reader(f)
#             urls = [row[0] for row in reader if row]
#         metafunc.parametrize("url", urls)
