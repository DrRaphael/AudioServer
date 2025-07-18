import socket
import os
from datetime import datetime


class WebServer:
    def __init__(self, host='localhost', port=8080, document_root='www'):
        self.host = host
        self.port = port
        self.document_root = document_root
        self.server_socket = None
        self.running = False

    def start(self):
        """启动Web服务器"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.running = True
            print(f"服务器运行在 http://{self.host}:{self.port}")
            print(f"文档根目录: {os.path.abspath(self.document_root)}")

            while self.running:
                client_socket, client_address = self.server_socket.accept()
                print(f"客户端连接来自: {client_address}")
                self.handle_client(client_socket)

        except Exception as e:
            print(f"启动服务器时出错: {e}")
        finally:
            self.stop()

    def stop(self):
        """停止Web服务器"""
        if self.server_socket:
            self.running = False
            self.server_socket.close()
            self.server_socket = None
            print("服务器已停止")

    def handle_client(self, client_socket):
        """处理客户端请求"""
        try:
            # 接收客户端请求数据
            request_data = client_socket.recv(1024).decode('utf-8')
            if not request_data:
                return

            # 解析HTTP请求
            request_lines = request_data.splitlines()
            request_line = request_lines[0]
            method, path, _ = request_line.split(' ', 2)

            print(f"请求: {method} {path}")

            # 处理请求
            if method == 'GET':
                self.serve_file(client_socket, path)
            else:
                self.send_error(client_socket, 405)

        except Exception as e:
            print(f"处理请求时出错: {e}")
            self.send_error(client_socket, 500)
        finally:
            client_socket.close()

    def serve_file(self, client_socket, path):
        """处理文件请求"""
        # 安全处理路径，防止目录遍历攻击
        if '..' in path:
            self.send_error(client_socket, 403)
            return

        # 处理根路径
        if path == '/':
            file_path = os.path.join(self.document_root, 'index.html')
        else:
            file_path = os.path.join(self.document_root, path[1:])

        # 检查文件是否存在
        if not os.path.exists(file_path):
            self.send_error(client_socket, 404)
            return

        # 检查是否是目录
        if os.path.isdir(file_path):
            if os.path.exists(os.path.join(file_path, 'index.html')):
                file_path = os.path.join(file_path, 'index.html')
            else:
                self.send_error(client_socket, 403)
                return

        # 读取文件内容并发送响应
        try:
            with open(file_path, 'rb') as file:
                content = file.read()

            # 获取文件类型
            content_type = self.get_content_type(file_path)

            # 构建HTTP响应头
            response_headers = [
                'HTTP/1.1 200 OK',
                f'Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}',
                'Server: SimplePythonServer',
                f'Content-Type: {content_type}',
                f'Content-Length: {len(content)}',
                'Connection: close',
                '\r\n'
            ]

            # 发送响应头
            response_header = '\r\n'.join(response_headers).encode('utf-8')
            client_socket.send(response_header)

            # 发送文件内容
            client_socket.send(content)

        except Exception as e:
            print(f"读取文件时出错: {e}")
            self.send_error(client_socket, 500)

    def send_error(self, client_socket, status_code):
        """发送错误响应"""
        # 错误页面内容
        error_pages = {
            400: '<h1>400 Bad Request</h1><p>你的浏览器发送了一个服务器无法理解的请求。</p>',
            403: '<h1>403 Forbidden</h1><p>服务器理解请求客户端的请求，但是拒绝执行此请求。</p>',
            404: '<h1>404 Not Found</h1><p>请求的网页不存在。</p>',
            405: '<h1>405 Method Not Allowed</h1><p>请求方法不被允许。</p>',
            500: '<h1>500 Internal Server Error</h1><p>服务器遇到错误，无法完成请求。</p>'
        }

        # 状态码对应的描述
        status_messages = {
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error'
        }

        # 获取错误信息
        if status_code not in error_pages:
            status_code = 500

        error_content = error_pages[status_code].encode('utf-8')
        status_message = status_messages[status_code]

        # 构建HTTP响应头
        response_headers = [
            f'HTTP/1.1 {status_code} {status_message}',
            f'Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}',
            'Server: SimplePythonServer',
            'Content-Type: text/html; charset=utf-8',
            f'Content-Length: {len(error_content)}',
            'Connection: close',
            '\r\n'
        ]

        # 发送响应头和内容
        response_header = '\r\n'.join(response_headers).encode('utf-8')
        client_socket.send(response_header)
        client_socket.send(error_content)

    def get_content_type(self, file_path):
        """确定文件的MIME类型"""
        # 常见文件类型映射
        content_types = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.txt': 'text/plain',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.json': 'application/json'
        }

        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()

        # 返回对应的MIME类型，默认为application/octet-stream
        return content_types.get(ext, 'application/octet-stream')


if __name__ == '__main__':
    # 创建并启动服务器
    server = WebServer(host='localhost', port=8080, document_root='www')
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("服务器被用户中断")