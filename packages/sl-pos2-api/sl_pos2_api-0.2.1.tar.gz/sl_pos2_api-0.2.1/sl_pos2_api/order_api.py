import requests
import json

class OrderAPI:
    def __init__(self, base_url, host, uid, device_info, ticket):
        """
        初始化OrderAPI

        Args:
            base_url: API基础URL
            host: Host头信息
            uid: 用户ID
            device_info: 设备信息
            ticket: 认证票据信息
        """
        self.base_url = base_url
        self.host = host
        self.uid = uid
        self.device_info = device_info
        self.ticket = ticket


    def hello(self):
        print("hello")
        return "hello"

    def checkout(
        self,
        request_send_time,
        otp,
        order_data
    ):
        """
        发起订单结算请求

        Args:
            request_send_time: 请求发送时间
            otp: 一次性密码
            order_data: 订单数据
        """

        # 构建完整请求URL
        url = f"{self.base_url}/sl/apps/pos/app/order/checkout"

        # 请求头
        headers = {
            "Host": self.host,
            "content-type": "application/json",
            "requestsendtime": request_send_time,
            "uid": self.uid,
            "accept": "*/*",
            "ticket": json.dumps(self.ticket) if isinstance(self.ticket, dict) else self.ticket,
            "otp": otp,
            "accept-language": "zh-Hans-CN;q=1.0",
            "deviceinfo": json.dumps(self.device_info) if isinstance(self.device_info, dict) else self.device_info,
            "user-agent": "SL2Pos/2.32.0 (com.shopline.enterprise.pos2; build:3094; iOS 15.7.9) Alamofire/5.10.2",
            "lang": "zh-hans-cn"
        }

        # 发送POST请求
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(order_data),
            verify=True
        )

        return response

# 示例使用
if __name__ == "__main__":
    # ticket信息
    ticket = {
        "posStaffId": "3787",
        "merchantId": "4600508114",
        "innerToken": "1d958bb1a1e4490dbb26149b718dc4fe",
        "offlineStoreId": "6369562508760987402",
        "storeId": "1709983459019",
        "posId": "16"
    }

    # 设备信息
    device_info = {
        "appVersion": "2.32.0",
        "osVersion": "15.7.9",
        "model": "iPad Air 2",
        "brand": "Apple",
        "deviceId": "AF41CF27-325B-40D6-94CB-6D036C960B85",
        "newDeviceId": "28f938f19f04b8002caa528fc04ba96456ebf8f2",
        "os": "ios"
    }

    # 创建API实例，URL参数化
    order_api = OrderAPI(
        base_url="https://uizidonghuaceshi.myshoplinestg.com",
        host="uizidonghuaceshi.myshoplinestg.com",
        uid="4600508114",
        device_info=device_info,
        ticket=ticket
    )

    # 配置参数
    request_send_time = "1756732868.7806911"
    otp = "05010000015602c49db5686000139605a5cfdde0a32600fff8b7594b202054ee07df66f92139c8c53ae104e68e6efe3a892f2cfda223177b582728fd1df6103e7d632371a6f519573957c49f4cb894bf246a5c424fc8f7832df8bca2c3b059fe3c46a1d2b6a38c25940fcbf92c9a0000c08b3e009a00029000cb340001e06933925e91d446d7608e4cf94bf7209d637699cf7dae75ba92a693e3f2e8097970ad018ec36bb022e81e1757a24fd89222838b7f2dbe87d348f91c1f2975eec3d65612a3c7a7d597d1ac05bf1bee45b8c49d7242a28f3aa58b600379644f9fb5edef5401f7e3e6be8905229836e166c2e42a4e223c51512d90d044a4ba32ad18e5bedbe35abfdea89a695c"

    # 订单数据
    order_data = {
        "roundingType": 0,
        "openDutyFree": False,
        "productInfos": [
            {
                "spuId": "16063695978613582153162405",
                "productPriceType": "customize",
                "source": 1,
                "title": "单库存商品001",
                "serviceCharge": False,
                "quantity": 1,
                "skuId": "18063695978625661748802405",
                "price": "0.00"
            }
        ]
    }

    # 发起请求
    response = order_api.checkout(
        request_send_time=request_send_time,
        otp=otp,
        order_data=order_data
    )

    # 输出结果
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
