# coding:utf-8
import base64
import io
import os
import logging
import tempfile
import contextlib
import httpx
import webbrowser
import sys
from typing import Any, Dict, Union
from PIL import Image
from volcengine.visual.VisualService import VisualService
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlsplit, urlunsplit, quote

# 重要修复：完全禁用所有日志输出到stderr，防止缓冲区溢出
# MCP协议使用stdio进行通信，任何stderr输出都可能导致问题
class NullHandler(logging.Handler):
    """空日志处理器，丢弃所有日志"""
    def emit(self, record):
        pass

# 配置根日志器使用空处理器
logging.basicConfig(
    level=logging.CRITICAL,  # 设置为最高级别，减少日志调用
    handlers=[NullHandler()]
)

# 完全禁用所有第三方库的日志
for logger_name in ['volcengine', 'httpx', 'urllib3', 'PIL', 'requests']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).handlers = [NullHandler()]
    logging.getLogger(logger_name).propagate = False

# 如果需要调试，可以将日志写入文件而不是stderr
DEBUG_MODE = os.getenv('MCP_DEBUG') == '1'
if DEBUG_MODE:
    debug_log_file = os.path.expanduser('~/mcp_image_cutout_debug.log')
    file_handler = logging.FileHandler(debug_log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.handlers = [file_handler]
else:
    logger = logging.getLogger(__name__)
    logger.handlers = [NullHandler()]

# 初始化FastMCP服务器
mcp = FastMCP("抠图工具")


class VolcImageCutter:
    """图像抠图处理器"""

    def __init__(self):
        self.visual_service = VisualService()
        # 允许通过环境变量覆盖上传地址
        self.upload_url = os.getenv(
            "MCP_UPLOAD_URL",
            "https://www.mcpcn.cc/api/fileUploadAndDownload/uploadMcpFile",
        )
        self._setup_credentials()

    def _normalize_url(self, url: str) -> str:
        """将可能包含空格、中文或其他非 ASCII 字符的 URL 进行标准化编码。"""
        try:
            parts = urlsplit(url)
            encoded_path = quote(parts.path, safe="/-_.~")
            encoded_query = quote(parts.query, safe="=&-_.~")
            encoded_fragment = quote(parts.fragment, safe="-_.~")
            normalized = urlunsplit((parts.scheme, parts.netloc, encoded_path, encoded_query, encoded_fragment))
            return normalized
        except Exception:
            return url

    @contextlib.contextmanager
    def _maybe_disable_proxies(self):
        """根据环境变量 MCP_DISABLE_PROXIES=1 临时禁用代理配置。"""
        if os.getenv("MCP_DISABLE_PROXIES") == "1":
            keys = [
                "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                "http_proxy", "https_proxy", "all_proxy",
                "NO_PROXY", "no_proxy",
            ]
            backup = {k: os.environ.get(k) for k in keys}
            try:
                for k in keys:
                    if k in os.environ:
                        os.environ.pop(k)
                yield
            finally:
                for k, v in backup.items():
                    if v is not None:
                        os.environ[k] = v
        else:
            yield

    def _setup_credentials(self):
        """设置API凭证"""
        ak = os.getenv('VOLC_ACCESS_KEY')
        sk = os.getenv('VOLC_SECRET_KEY')
        self.visual_service.set_ak(ak)
        self.visual_service.set_sk(sk)

        if DEBUG_MODE:
            if not ak or not sk:
                logger.warning("未检测到 VOLC_ACCESS_KEY 或 VOLC_SECRET_KEY")
            else:
                logger.info(f"已配置火山AK/SK: ak={ak[:6]}*** sk_len={len(sk)}")

    def saliency_segmentation(self, image_urls: list[str]) -> list[str]:
        """显著性分割抠图，直接返回base64列表"""
        try:
            # 规范化URL
            normalized_urls = []
            for u in image_urls:
                nu = self._normalize_url(u)
                if DEBUG_MODE and nu != u:
                    logger.info(f"URL 已标准化: '{u}' -> '{nu}'")
                normalized_urls.append(nu)

            form = {
                "req_key": "saliency_seg",
                "image_urls": normalized_urls,
            }

            # 调用API时禁用SDK内部的日志输出
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            try:
                # 重定向stdout和stderr到空设备，防止SDK输出大量数据
                with open(os.devnull, 'w') as devnull:
                    sys.stdout = devnull
                    sys.stderr = devnull

                    with self._maybe_disable_proxies():
                        resp = self.visual_service.cv_process(form)
            finally:
                # 恢复原始输出
                sys.stdout = original_stdout
                sys.stderr = original_stderr

            # 处理响应
            if resp:
                if 'data' in resp:
                    data = resp['data']

                    # 检查多种可能的base64数据字段名
                    possible_fields = ['binary_data_base64', 'base64_images', 'images', 'result_images', 'image_base64']
                    for field in possible_fields:
                        if field in data:
                            result = data[field]
                            if isinstance(result, list) and result:
                                if DEBUG_MODE:
                                    logger.info(f"找到base64数据在 data.{field}, 数量: {len(result)}")
                                return result
                            elif isinstance(result, str) and result:
                                if DEBUG_MODE:
                                    logger.info(f"找到单个base64数据在 data.{field}")
                                return [result]

                # 检查顶层结构
                possible_top_fields = ['binary_data_base64', 'base64_images', 'images', 'result_images']
                for field in possible_top_fields:
                    if field in resp:
                        result = resp[field]
                        if isinstance(result, list) and result:
                            if DEBUG_MODE:
                                logger.info(f"找到base64数据在顶层 {field}, 数量: {len(result)}")
                            return result
                        elif isinstance(result, str) and result:
                            if DEBUG_MODE:
                                logger.info(f"找到单个base64数据在顶层 {field}")
                            return [result]

                if DEBUG_MODE:
                    # 只在调试模式下记录响应结构，避免大量数据输出
                    logger.error(f"未找到base64数据，响应键: {list(resp.keys())}")
            else:
                if DEBUG_MODE:
                    logger.error("API返回空响应")

            return []

        except Exception as e:
            if DEBUG_MODE:
                logger.error(f"显著性分割处理异常: {str(e)}", exc_info=True)
            return []

    async def upload_image_to_server(self, image_data: bytes, filename: str) -> dict[str, Any]:
        """上传图片到服务器"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name

            try:
                # 上传文件
                async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                    with open(temp_file_path, 'rb') as f:
                        files = {'file': (filename, f, 'image/png')}
                        response = await client.post(self.upload_url, files=files)

                    if response.status_code == 200:
                        result = response.json()
                        if result.get('code') == 0:
                            if DEBUG_MODE:
                                logger.info(f"图片上传成功: {result['data']['url']}")
                            return {"success": True, "url": result['data']['url']}
                        else:
                            if DEBUG_MODE:
                                logger.error(f"上传失败: code={result.get('code')} msg={result.get('msg')}")
                            return {
                                "success": False,
                                "error": result.get('msg', '未知错误'),
                                "code": result.get('code'),
                            }
                    else:
                        if DEBUG_MODE:
                            logger.error(f"上传请求失败: HTTP {response.status_code}")
                        return {"success": False, "error": f"HTTP {response.status_code}"}

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            if DEBUG_MODE:
                logger.error(f"上传图片异常: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


# 创建全局处理器实例
cutter = VolcImageCutter()


@mcp.tool()
async def image_cutout(image_urls: list[str], open_in_browser: bool = False) -> Dict[str, Any]:
    """
    对图像进行显著性分割抠图，自动上传到服务器并返回结果

    Args:
        image_urls: 图像URL列表，支持多张图像同时处理
        open_in_browser: 是否自动在默认浏览器中打开生成的图像，默认值：False

    Returns:
        返回包含处理结果的字典
    """
    # 获取base64列表
    base64_images = cutter.saliency_segmentation(image_urls)

    if not base64_images:
        raise Exception("抠图失败：未获取到有效的抠图结果")

    response_text = f"显著性分割抠图处理完成！共生成 {len(base64_images)} 张抠图结果：\n\n"
    uploaded_urls = []
    failure_count = 0

    for i, base64_data in enumerate(base64_images):
        try:
            # 解码base64数据
            image_data = base64.b64decode(base64_data)

            # 验证图片
            image = Image.open(io.BytesIO(image_data))

            # 上传到服务器
            filename = f"saliency_cutout_{i + 1}.png"
            upload_result = await cutter.upload_image_to_server(image_data, filename)

            if upload_result.get('success'):
                uploaded_urls.append(upload_result['url'])
                response_text += f"第 {i + 1} 张: ✅ {upload_result['url']}\n"
            else:
                failure_count += 1
                err = upload_result.get('error', '未知错误')
                response_text += f"第 {i + 1} 张: ❌ 上传失败 - {err}\n"

        except Exception as e:
            failure_count += 1
            response_text += f"第 {i + 1} 张: ❌ 处理失败 - {str(e)}\n"

    # 打开浏览器（如果需要）
    if open_in_browser and uploaded_urls:
        import time
        for i, url in enumerate(uploaded_urls):
            try:
                webbrowser.open_new_tab(url)
                if i < len(uploaded_urls) - 1:
                    time.sleep(0.5)
            except:
                pass  # 静默处理浏览器打开失败

    # 返回结果
    if uploaded_urls:
        return {
            "iserror": False,
            "data": uploaded_urls[0] if len(uploaded_urls) == 1 else uploaded_urls,
            "message": response_text
        }
    else:
        raise Exception(f"抠图失败：所有图片处理失败 ({failure_count}个)")


def main():
    """命令行入口点"""
    import argparse

    # 创建参数解析器
    parser = argparse.ArgumentParser(description='MCP 抠图服务器')
    parser.add_argument('transport', nargs='?', default='stdio',
                        choices=['stdio', 'sse'],
                        help='Transport type (stdio or sse)')

    # 解析命令行参数
    args = parser.parse_args()

    # 启动服务器（不输出任何日志到stderr）
    if args.transport == 'sse':
        mcp.run(transport='sse', sse_host='127.0.0.1', sse_port=8080)
    else:
        mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
