from .model import SklandSubscribe


def cleantext(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned_lines = [line.strip() for line in lines]
    result = "\n".join(cleaned_lines)
    return result


def compare_user_info(dict1, dict2: dict[any, any]):
    # excludes = ["bot_id", "level", "id2", "id3"]
    # includes = [i for i in dict2.keys() if i not in excludes]
    includes = ["bot_type", "platform", "id1"]
    filter1 = {k: dict1.get(k) for k in includes}
    filter2 = {k: dict2.get(k) for k in includes}
    return filter1 == filter2


def show_token(token: str, is_group: bool) -> str:
    if not token:
        return "未绑定"
    else:
        if is_group:
            return "已绑定"
        return token


def report_maker(subscribes: list[SklandSubscribe], is_group: bool) -> str:
    report = []
    for n, i in enumerate(subscribes):
        report.append(cleantext(f"""
                {n}：
                UID：{i.uid}
                TOKEN：{show_token(i.token,is_group)}
                备注：{i.note}
                """))
    return "\n\n".join(report)
