<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-skland-arksign

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
_✨ 用于每日早八定时签到森空岛明日方舟的Nonebot插件 ✨_
<!-- prettier-ignore-end -->

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

```shell
nb plugin install nonebot-plugin-skland-arksign
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```shell
pip install nonebot-plugin-skland-arksign
```

</details>
<details>
<summary>pdm</summary>

```shell
pdm add nonebot-plugin-skland-arksign
```

</details>
<details>
<summary>poetry</summary>

```shell
poetry add nonebot-plugin-skland-arksign
```

</details>
<details>
<summary>conda</summary>

```shell
conda install nonebot-plugin-skland-arksign
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

```toml
plugins = ["nonebot_plugin_skland_arksign"]
```

</details>

## 🎉 使用

插件命令名为`skland`, 可用别名：`skl`、`skd`、`森空岛`

### 配置

#### 群聊中使用

在bot文件夹下的`.env.dev`文件中追加

```dotnet
skland_arksign_allow_group=True
```

这将允许群组等私信用户以上的对话模型注册模型而不会警告 _请在私聊中使用_ 字样

> [!IMPORTANT]
> 在群聊中使用命令时，命令的权限会受到较大限制
> 基本只有[超级用户](https://nonebot.dev/docs/appendices/config#superusers)可以使用

### 新增账号

```shell
skland add 舟游戏ID [森空岛token] [-n 可选备注]
```

> [!IMPORTANT]
> 在群聊中使用时，一定不要带上token，否则会有盗号风险
> 缺少的token会在私聊中补充：[使用 bind 命令](#私信补充token)

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

> [!NOTE]
> 例子: `"content": "1145141919810"`
>
> 则命令为 `森空岛 你的游戏UID 1145141919810`

#### 私信补充token

在[群聊中添加uid](#新增账号)后，私聊中对bot发送以下命令

```shell
skland bind 森空岛token
```

### 删除账号

```shell
skland del 舟游戏ID/备注
```

> {!WARNING}
> 注意：非[超级用户](https://nonebot.dev/docs/appendices/config#superusers)只可删除自己绑定的账号，超级用户可以删除bot数据库内所有账号

### 列出账号

```shell
skland list
```

> [!WARNING]
> 仅超级用户可用

### 更新账号

```shell
skland update 舟游戏ID/备注 [-u 可选UID] [-t 可选token] [-n 可选备注]
```

> [!WARNING]
> 仅超级用户可用

### 立即手动签到

```shell
skland signin 舟游戏ID/备注
```

> [!WARNING]
> 仅超级用户可用

## ♿️ FAQ

1. 为什么这么多仅超级用户可用的命令？
   因为当前的数据库模型没有记录添加者的信息，只记录了需要发送到的用户信息，所以暂时只能通过超级用户来操作
   未来可能会加入权限系统，以及增加数据库模型字段

2. 使用例子？

   ```shell
   skland add 114514 1919810 -n hhhaaa
   skland add 114514 1919810
   skland add 114514
   skland del 114514
   skland del hhhaaa
   skland list
   skland update 114514 -u 1919810 -n hhhaaaaa
   skland update hhhaaaaa -t 0189191
   skland signin 1919810
   ```

## 🤗 致谢

- `xxyz30/skyland-auto-sign`([<del>Github</del>](https://github.com/xxyz30/skyland-auto-sign)/[Gitee](https://gitee.com/FancyCabbage/skyland-auto-sign))、[`Yanstory/skland-checkin-ghaction`](https://github.com/Yanstory/skland-checkin-ghaction)、[`Maojuan-lang/SenKongDao`](https://github.com/Maojuan-lang/SenKongDao)：感谢以上项目提供的参考！
- [`AzideCupric`](https://github.com/AzideCupric)：感谢大佬的技术支持！orz
- [`he0119/nonebot-plugin-datastore`](https://github.com/he0119/nonebot-plugin-datastore)：超好用的数据存储插件！
- [`MountainDash/nonebot-plugin-send-anything-anywhere`](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)：峯驰物流部门的全能转接信使！
- [`noneplugin/nonebot-plugin-session`](https://github.com/noneplugin/nonebot-plugin-session)：全能的<del>账单</del>会话模型管理员！
- [`nonebot/plugin-alconna`](https://github.com/nonebot/plugin-alconna)：超好用命令行解析器！
