<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-skland-arksign

_✨ 用于每日早八定时签到森空岛明日方舟的Nonebot插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-skland-arksign.svg" alt="license">
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

    plugins = ["nonebot_plugin_example"]

</details>


## 🎉 使用
### 新增账号
    森空岛/skl/skd 舟游戏ID 森空岛cred

> 关于什么是森空岛cred：参见[此处](https://github.com/xxyz30/skyland-auto-sign)

### 删除账号
    森空岛.del/skl.del/skd.del 舟游戏ID

## 🎉 致谢
* [`xxyz30/skyland-auto-sign`](https://github.com/xxyz30/skyland-auto-sign)、[`Yanstory/skland-checkin-ghaction`](https://github.com/Yanstory/skland-checkin-ghaction)、[`Maojuan-lang/SenKongDao`](https://github.com/Maojuan-lang/SenKongDao)：感谢以上大佬项目提供的参考！