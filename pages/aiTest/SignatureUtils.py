import hashlib
from typing import Dict, Any
class SignatureUtils:
    @staticmethod
    def get_sorted_params(params: Dict[str, Any]) -> str:
        """
        对参数字典进行排序并拼接成key=value形式的字符串

        """
        sorted_params = sorted((k, v) for k, v in params.items() if k != 'sign')
        return '&'.join(f"{k}={v}" for k, v in sorted_params)
    @staticmethod
    def generate_signature(params_str: str, salt: str) -> str:
        """
        生成签名值

        """
        params_with_salt = f"{params_str}{salt}"
        return hashlib.md5(params_with_salt.encode()).hexdigest()
    @staticmethod
    def get_salted_signature(params: Dict[str, Any], salt: str) -> str:
        """
        根据参数和盐值生成带盐的签名

        """
        params_str = SignatureUtils.get_sorted_params(params)
        return SignatureUtils.generate_signature(params_str, salt)
