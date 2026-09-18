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
<a href="https://pypi.python.org/pypi/nonebot-plugin-skland-arksign">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-skland-arksign">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 💿 安装

根据数美 device ID 获取的方法的不同，可选择以下版本（区别下述）：

```bash
nb plugin install nonebot-plugin-skland-arksign
nb plugin install nonebot-plugin-skland-arksign[sm_local]
nb plugin install nonebot-plugin-skland-arksign[sm_htmlrender]
```

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
| `skland_sm_method_identifier`| `int` | **是** | `0` | 数美Device ID / dId 的获取方式 |
| `skland_sm_api_endpoint`| `str` | 否 | ... | 选用 [retrieval-server api](https://github.com/GuGuMur/skland-did-retrieval-server) 时的 URL路径，可自行部署 |
| `htmlrender-...`| ... | ... | ... | 选用 [htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender) 时该插件的相关配置 |
<!-- prettier-ignore-end -->

#### 关于数美Device ID / dId 的配置

2024.09 起，yjwl在获取 `cred` 的部分接入了 [阿里云 Web 应用防火墙](https://www.alibabacloud.com/help/zh/waf/)，导致全网项目拉闸

~~在监狱待着顺便蹲网上大佬们的成果后~~本插件提供以下几种应对措施：

##### retrieval-server api（编号`0`）

采用 Koajs + Nodejs VM 的 API 方案，不需要额外安装依赖。

库：[GuGuMur/skland-did-retrieval-server](https://github.com/GuGuMur/skland-did-retrieval-server)

安装：`nb plugin install nonebot-plugin-skland-arksign`

配置：`skland_sm_method_identifier = 0`

##### Python 实现原生模拟 （编号`1`）

由<del>市面上几乎所有森空岛签到项目的蓝本</del>大佬 [FancyCabbage(Gitee)](https://gitee.com/FancyCabbage/skyland-auto-sign)对数美 SDK 逆向后使用Python 实现。

**额外安装库**：`cryptography`

**代码协议**：[MIT](https://gitee.com/FancyCabbage/skyland-auto-sign/blob/master/LICENSE)

安装：`nb plugin install nonebot-plugin-skland-arksign[sm_local]`

配置：`skland_sm_method_identifier = 1`

##### HTMLRender / Playwright 模拟 （编号`2`）

灵感来自 [ztmzzz/skyland_auto_sign_qinglong](https://github.com/ztmzzz/skyland_auto_sign_qinglong) ，通过模拟浏览器环境获取dId

**额外安装插件**：[`nonebot-plugin-htmlrender`](https://github.com/kexue-z/nonebot-plugin-htmlrender)

安装：`nb plugin install nonebot-plugin-skland-arksign[sm_htmlrender]`

配置：`skland_sm_method_identifier = 2`

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

- `xxyz30/skyland-auto-sign`([<del>Github</del>](https://github.com/xxyz30/skyland-auto-sign)/[Gitee](https://gitee.com/FancyCabbage/skyland-auto-sign))、[`Yanstory/skland-checkin-ghaction`](https://github.com/Yanstory/skland-checkin-ghaction)、[`Maojuan-lang/SenKongDao`](https://github.com/Maojuan-lang/SenKongDao)、[`enpitsuLin/skland-daily-attendance`](https://github.com/enpitsuLin/skland-daily-attendance)、[ztmzzz/skyland_auto_sign_qinglong](https://github.com/ztmzzz/skyland_auto_sign_qinglong)：感谢以上项目提供的参考！<del>几乎是市面上所有的森空岛签到项目</del>
- [`AzideCupric`](https://github.com/AzideCupric)：感谢大佬的技术支持！orz
- [`he0119/nonebot-plugin-datastore`](https://github.com/he0119/nonebot-plugin-datastore)：超好用的数据存储插件！
- [`MountainDash/nonebot-plugin-send-anything-anywhere`](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)：峯驰物流部门的全能转接信使！
- [`noneplugin/nonebot-plugin-session`](https://github.com/noneplugin/nonebot-plugin-session)：全能的<del>账单</del>会话模型管理员！
- [`nonebot/plugin-alconna`](https://github.com/nonebot/plugin-alconna)：<del>比[argparse](https://docs.python.org/3/library/argparse.html)好用十倍甚至九倍的</del>命令行解析器！
