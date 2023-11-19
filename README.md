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
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

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

> [!IMPORTANT]
> 如果想在 **Python <= 3.9** 的环境中使用，请选择 `v0.5.8`，这是最后一个支持 **Python <= 3.9** 的 Release
>
> ~严格来说其实是第一个以及最后一个，因为之前的版本有不适用于**非3.10以下**的类型注解语法，为此专门发布的一个可用的支持版本~
>
> 对于其他**非** `v0.5.8` 版本，都有可能不兼容 **Python <= 3.9**

## 🎉 使用

插件命令名为`skland`, 可用别名：`skl`、`skd`、`森空岛`

### 配置

在 bot 项目的`.env`文件中添加下表中的配置

<!-- prettier-ignore-start -->
|             配置项            |  类型  | 必填 |  默认值  | 说明 |
|:----------------------------:|:------:|:--:|:-------:|:------------------------:|
| `skland_arksign_allow_group` | `bool` | 否 | `False` | 允许群组等私信用户以上的对话模型注册模型而不会警告 _请在私聊中使用_ 字样<br><li>**在群聊中使用命令时，命令的权限会受到较大限制**</li> |
|   `skland_timestamp_delay`   | `int`  | 否 |    2    | 针对bot所在机器调整bot生成森空岛签名时进行运算的减数 |  
|  `skland_use_web_timestamp`  | `bool` | 否 | `False` | 无法调到合适的`timestamp_delay`时使用的方案 |
<!-- prettier-ignore-end -->

### 新增账号

```shell
skland add [游戏账号ID] [森空岛token] [-n 可选备注]
```

> [!IMPORTANT]
> 游戏账号ID为游戏主界面博士名下面那串数字（如`114514`）
>
> 在群聊中使用时，一定不要带上token，否则会有盗号风险
>
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
> 例子: 游戏账号ID为114514，访问得到内容 `"content": "1919810"`
>
> 则命令为 `森空岛 add 114514 1919810`

> [!IMPORTANT]
> 注意不要把包裹`content`内容的引号，或是页面返回的整个内容输入到命令中！

#### 私信补充token

在[群聊中添加uid](#新增账号)后，私聊中对bot发送以下命令

```shell
skland bind 森空岛token
```

### 删除账号

```shell
skland del 游戏账号ID/备注
```

> [!WARNING]
> 注意：非[超级用户](https://nonebot.dev/docs/appendices/config#superusers)只可删除自己绑定的账号，超级用户可以删除bot数据库内所有账号

### 列出账号

```shell
skland list
```

> [!WARNING]
> 仅超级用户可用

### 更新账号

```shell
skland update 游戏账号ID/备注 [-u 可选UID] [-t 可选token] [-n 可选备注]
```

> [!WARNING]
> 仅超级用户可用

### 立即手动签到

#### 特定用户

```shell
skland signin 游戏账号ID/备注
```

#### 所有用户

```shell
skland signin !all
```

> [!WARNING]
> 仅超级用户可用
>
> 签到全部用户时，会分发到原本对应的聊天目标

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

3. 为什么我刚获取token并绑定好，一会就用不了了？

- 当您使用浏览器获取token时，**不要去登出账号，否则鹰角网络通行证会失效！**
- 如果要添加多个账号，请删除浏览器缓存。或者使用浏览器自带的隐私浏览模式，拿到Token后，关闭隐私窗口，再登录一次即可
- 注意：电脑在用密码登录后，手机客户端有可能会被挤掉，但一定不要点客户端里的清理会话，否则所有的登录状态**都会被清空！**

4. 报错`{'code': 10001, 'message': '当前用户未经授权'}`？<!-- markdownlint-disable -->

- 参考 [#更新账号](#更新账号) 一栏重新绑定游戏账号ID
- 参考issue：[#29](https://github.com/GuGuMur/nonebot-plugin-skland-arksign/issues/29)

5. 报错`Client error '400 Bad Request' for url xxx`？<!-- markdownlint-disable -->

- 请检查token复制过程中是否有错漏，以及游戏账号ID是否与您输入的token相符

6. 报错`Client error '401 Unauthorized' for url xxx`？<!-- markdownlint-disable -->

- 参考 [#配置](#配置) 一栏修改`skland_timestamp_delay`的数值
  - 参考值：`5`，`10`
- 修改 `skland_use_web_timestamp` 值为 `True`

## 🤗 致谢

- `xxyz30/skyland-auto-sign`([<del>Github</del>](https://github.com/xxyz30/skyland-auto-sign)/[Gitee](https://gitee.com/FancyCabbage/skyland-auto-sign))、[`Yanstory/skland-checkin-ghaction`](https://github.com/Yanstory/skland-checkin-ghaction)、[`Maojuan-lang/SenKongDao`](https://github.com/Maojuan-lang/SenKongDao)、[`enpitsuLin/skland-daily-attendance`](https://github.com/enpitsuLin/skland-daily-attendance)：感谢以上项目提供的参考！
- [`AzideCupric`](https://github.com/AzideCupric)：感谢大佬的技术支持！orz
- [`he0119/nonebot-plugin-datastore`](https://github.com/he0119/nonebot-plugin-datastore)：超好用的数据存储插件！
- [`MountainDash/nonebot-plugin-send-anything-anywhere`](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)：峯驰物流部门的全能转接信使！
- [`noneplugin/nonebot-plugin-session`](https://github.com/noneplugin/nonebot-plugin-session)：全能的<del>账单</del>会话模型管理员！
- [`nonebot/plugin-alconna`](https://github.com/nonebot/plugin-alconna)：<del>比[argparse](https://docs.python.org/3/library/argparse.html)好用十倍甚至九倍的</del>命令行解析器！
