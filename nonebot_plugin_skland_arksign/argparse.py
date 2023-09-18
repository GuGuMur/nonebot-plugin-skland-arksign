from nonebot.rule import ArgumentParser

# 创建解析器对象
skland_parser = ArgumentParser(prog="skland", description="森空岛命令解析")

# 添加操作子命令
subparsers = skland_parser.add_subparsers(dest="operation", help="操作")

# 子命令 add
add_parser = subparsers.add_parser("add", help="添加新的签到账号")
add_parser.add_argument("uid", type=int, help="游戏UID")
add_parser.add_argument("token", help="游戏TOKEN")
add_parser.add_argument("-n", "--note", help="备注")

# 子命令 list
subparsers.add_parser("list", help="列出所有签到账号")

# 子命令 delete
delete_parser = subparsers.add_parser("delete", help="删除签到账号")
delete_parser.add_argument("identifier", help="游戏UID或备注")

# 子命令 update
update_parser = subparsers.add_parser("update", help="更新签到账号信息")
update_parser.add_argument("identifier", help="游戏UID或备注")
update_parser.add_argument("-u", "--uid", type=int, help="需要修改的UID")
update_parser.add_argument("-t", "--token", help="需要修改的游戏TOKEN")
update_parser.add_argument("-n", "--note", help="需要修改的备注")
