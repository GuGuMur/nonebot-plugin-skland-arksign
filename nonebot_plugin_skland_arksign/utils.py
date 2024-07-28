from .model import SklandSubscribe


def cleantext(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned_lines = [line.strip() for line in lines]
    result = "\n".join(cleaned_lines)
    return result


def show_token(token: str, is_show_token: bool):
    if not token:
        return "未绑定"
    else:
        if is_show_token:
            return "已绑定"
        return token


def report_maker(subscribes: list[SklandSubscribe], is_show_token: bool = False) -> str:
    report = []
    for i, j in enumerate(subscribes):
        report.append(
            cleantext(
                f"""
                序号：{i}
                UID：{j.uid}
                TOKEN：{show_token(j.token, is_show_token)}
                备注：{j.note}
                """
            )
        )
    return "\n\n".join(report)
