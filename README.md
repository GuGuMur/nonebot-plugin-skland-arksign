<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-skland-arksign

_✨ 用于每日早八定时签到森空岛明日方舟的Nonebot插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/GuGuMur/nonebot-plugin-skland-arksign.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-skland-arksign">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-skland-arksign.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-skland-arksign

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-skland-arksign

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-skland-arksign

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-skland-arksign

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-skland-arksign

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_skland_arksign"]

</details>

## 🎉 使用

### 新增账号

    森空岛/skl/skd 舟游戏ID 森空岛token

#### 获取Token

1. 登录[森空岛](https://www.skland.com/)

2. 访问这个[网址](https://web-api.skland.com/account/info/hg)

   返回如下信息

   ```json
   {
     "code": 0,
     "data": {
       "content": "<Token>"
     },
     "msg": "接口会返回您的鹰角网络通行证账号的登录凭证，此凭证可以用于鹰角网络账号系统校验您登录的有效性。泄露登录凭证属于极度危险操作，为了您的账号安全，请勿将此凭证以任何形式告知他人！"
   }
   ```

3. 将`<Token>`填入命令中

> 例子: "content": "1145141919810"
> 则命令为`森空岛 你的游戏UID 1145141919810`

### 删除账号

    森空岛.del/skl.del/skd.del 舟游戏ID

> 注意：非[超级用户](https://nonebot.dev/docs/appendices/config#superusers)只可删除自己绑定的账号，超级用户可以删除bot数据库内所有账号

## 🤗 致谢

- [`xxyz30/skyland-auto-sign`](https://github.com/xxyz30/skyland-auto-sign)、[`Yanstory/skland-checkin-ghaction`](https://github.com/Yanstory/skland-checkin-ghaction)、[`Maojuan-lang/SenKongDao`](https://github.com/Maojuan-lang/SenKongDao)：感谢以上项目提供的参考！
- [`AzideCupric`](https://github.com/AzideCupric)：感谢大佬的技术支持！orz
- [`he0119/nonebot-plugin-datastore`](https://github.com/he0119/nonebot-plugin-datastore)：超好用的数据存储插件！
- [`MountainDash/nonebot-plugin-send-anything-anywhere`](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)：峯驰物流部门的全能转接信使！
- [`noneplugin/nonebot-plugin-session`](https://github.com/noneplugin/nonebot-plugin-session)：全能的<del>账单</del>会话模型管理员！
