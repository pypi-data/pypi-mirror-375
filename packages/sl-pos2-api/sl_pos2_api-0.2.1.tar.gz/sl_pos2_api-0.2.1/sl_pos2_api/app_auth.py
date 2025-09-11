import socket
import hessian2
from nacos import NacosClient

# 1. 从 Nacos 获取服务实例
nacos_client = NacosClient(
    server_addresses="nacos-test-fs.inshopline.com:6801",
    namespace="test"
)
# 替换为实际的服务名、分组、版本（需从接口文档获取）
service_instances = nacos_client.get_service_instances(
    service_name="com.yy.aurogon.user.udb.credit.api.CreditService",
    group_name="DEFAULT_GROUP",
    cluster_name="DEFAULT",
    version="1.0.0"
)
# 选择第一个可用实例（实际需做负载均衡）
instance = service_instances[0]
host = instance.host
port = instance.port  # Dubbo 服务默认端口通常是 20880，可能与注册端口不同

# 2. 构造 CreditGenRequest 对象（Hessian2 序列化）
# 需根据 Java 对象的结构构造字典（字段名、类型需严格匹配）
request_params = {
    "verPro": 0,
    "context": "",
    "uid": "${zpf-uid}",  # 替换为实际值
    "pwdSh1": "0704be6c753ee8648286e5339cd80d850f9d57e8",
    "appId": "${appId_login_hechunqin}",  # 替换为实际值
    "deviceId": "${deviceId_login_hechunqin}",  # 替换为实际值
    "subAppId": "1",
    "ip": 12345678,
    "creditType": 1,
    "pwdType": 1,
    "ext": {}  # 空对象需符合 Java 定义（如 com YY.aurogon...ExtInfo）
}

# 3. 序列化请求（Dubbo 协议头 + Hessian2 数据）
def build_dubbo_request(service_name, method_name, params):
    # Dubbo 协议头（简化示例，实际需按协议规范填充）
    header = b"dubbo\x00\x00\x00\x00\x00\x00\x00"  # 魔数、标志位等
    # 序列化参数（Hessian2）
    hessian_data = hessian2.dumps(params)
    # 拼接请求体（需包含服务名、方法名、参数类型等）
    request_body = f"{service_name}:{method_name}:{hessian_data}".encode()
    return header + request_body

# 连接 Dubbo 服务实例并发送请求
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
request = build_dubbo_request(
    service_name="com.yy.aurogon.user.udb.credit.api.CreditService",
    method_name="creditGen",
    params=request_params
)
sock.send(request)
response = sock.recv(4096)  # 接收响应（需根据实际长度调整）
sock.close()

# 4. 解析响应（Hessian2 反序列化）
result = hessian2.loads(response)
print("调用结果:", result)