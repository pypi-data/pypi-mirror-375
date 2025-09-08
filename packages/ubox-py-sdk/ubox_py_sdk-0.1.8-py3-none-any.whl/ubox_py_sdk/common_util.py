from typing import Dict, Any

from ubox_py_sdk.logger import get_logger

logger = get_logger(__name__)

def save_base64_image(b64_str, out_path):
    import base64, os
    if ',' in b64_str:
        b64_str = b64_str.split(',', 1)[1]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64_str))


def print_curl_info(method: str, url: str, params: Dict[str, Any],
                     data: Dict[str, Any], headers: Dict[str, str]) -> None:
    """打印curl命令信息，方便调试和复制使用

    Args:
        method: HTTP方法
        url: 请求URL
        params: 查询参数
        data: 请求体数据
        headers: 请求头
    """
    try:
        # 构建查询字符串
        query_string = ""
        if params:
            query_parts = []
            for k, v in params.items():
                if isinstance(v, (list, tuple)):
                    for item in v:
                        query_parts.append(f"{k}={item}")
                else:
                    query_parts.append(f"{k}={v}")
            query_string = "&".join(query_parts)

        # 构建完整的URL
        full_url = url
        if query_string:
            full_url = f"{url}?{query_string}"

        # 构建curl命令
        curl_parts = [f"curl -X {method.upper()}"]

        # 添加请求头
        for k, v in headers.items():
            curl_parts.append(f'-H "{k}: {v}"')

        # 添加请求体
        if data and method.upper() in ['POST', 'PUT', 'PATCH']:
            import json
            data_json = json.dumps(data, ensure_ascii=False, indent=2)
            curl_parts.append(f"-d '{data_json}'")

        # 添加URL
        curl_parts.append(f'"{full_url}"')

        # 组合完整的curl命令
        curl_command = " ".join(curl_parts)

        # 打印curl信息
        logger.info(f"=== CURL命令 ===")
        logger.info(f"URL: {full_url}")
        logger.info(f"方法: {method.upper()}")
        if headers:
            logger.info(f"请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        if data:
            logger.info(f"请求体: {json.dumps(data, ensure_ascii=False, indent=2)}")
        logger.info(f"完整curl命令:")
        logger.info(curl_command)
        logger.info(f"==================")

    except Exception as e:
        logger.warning(f"生成curl信息失败: {e}")
