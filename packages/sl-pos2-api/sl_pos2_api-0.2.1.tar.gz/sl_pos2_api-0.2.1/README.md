# SHOPLINE POS2.0 API 工具

## 安装

```bash
pip install sl-pos2-api
```

## 使用

```python
from sl_pos2_api_tool import OrderApi

order_api = OrderApi(
    base_url="https://pos2-api.shoplineapp.com",
    host="pos2-api.shoplineapp.com",
    uid="123456",
    device_info="device_info",
    ticket="ticket",
)

order_api.hello()
```
