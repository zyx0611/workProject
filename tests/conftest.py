# 注册自定义命令行参数
def pytest_addoption(parser):
    print('1231')
    parser.addoption(
        "--url",
        action="store",
        default=None,
        help="传入要测试的 URL"
    )

# 提供 fixture 给测试函数使用
import pytest

@pytest.fixture
def url(request):
    return request.config.getoption("--url")
