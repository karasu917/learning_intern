# 配置集中管理，存放API key（或从环境变量/.env读取），模型名称，temperature，Maxxtokens，chunk大小文件路径等参数，方便其他模块统一引用
def get_config():
    print("配置文件读取成功")