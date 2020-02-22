# Bandwagonhost

用于home assistant平台的搬瓦工状态监视器,可以监视搬瓦工VPS的流量、内存和硬盘使用情况。  

## 安装

请先在<config>/custom_components/文件夹建立bandwagonhost文件夹

再将本项目中bandwagonhost目录下所有文件复制到上述文件夹下

## 配置

```yaml
sensor:
  - platform: bandwagonhost
    veid: 搬瓦工VPS的veid         # 必须
    api_key: 搬瓦工VPS的API_KEY   # 必须
    monitored_conditions:         # 可选
      - VPS_STATE                 # 可选，VPS运行状态
      - CURRENT_BANDWIDTH_USED    # 可选，流量情况
      - CURRENT_BWG_USED          # 可选，流量数据
      - TOTAL_BANDWIDTH           # 可选，流量总量
      - RAM_USED                  # 可选，已用内存
      - DISK_USED                 # 可选，已用硬盘
      - SWAP_USED                 # 可选，已用SWAP
```

以上信息请从搬瓦工的控制页面获取。

## 效果示例

![image](/Users/nicholas/Downloads/github/bandwagonhost/bandwagonhost.png)

## 注意

为了防止因为api请求过于频繁而被搬瓦工封号，传感器每20分钟更新一次。