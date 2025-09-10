import re
from typing import List, Optional

from whatthepatch_pydantic import parse_patch as wtp_parse_patch
from whatthepatch_pydantic.model import Diff as WTPDiff

from Patche.config import settings
from Patche.model import Change, Diff, Hunk, Patch
from Patche.utils.header import CHANGE_LINE, HEADER_OLD, HUNK_START, parse_header

git_diffcmd_header = re.compile("^diff --git a/(.+) b/(.+)$")
unified_diff_header = re.compile("^---\s{1}")
spliter_line = re.compile("^---$")


def changes_to_hunks(changes: list[Change]) -> list[Hunk]:
    """
    Convert a list of changes to a list of hunks

    Args:
        changes (list[Change]): A list of changes

    Returns:
        list[Hunk]: A list of hunks
    """

    # 首先统计 Hunk 数
    hunk_indexes = []
    for change in changes:
        if change.hunk not in hunk_indexes:
            hunk_indexes.append(change.hunk)

    # 将changes按照hunk分组，注意同一个 hunk 中的 change 要进行分类，前三行要放入前置上下文，中间的要放入中间上下文，后三行要放入后置上下文
    hunk_list: list[Hunk] = []
    for hunk_index in hunk_indexes:
        hunk_changes = [change for change in changes if change.hunk == hunk_index]

        # 这里遍历的顺序已经是正确的顺序
        hunk_context = []
        hunk_middle = []
        hunk_post = []
        # 首先正向遍历，获取前置上下文
        for change in hunk_changes:
            if change.old is not None and change.new is not None:
                hunk_context.append(change)
            else:
                break

        # 然后反向遍历，获取后置上下文
        for change in reversed(hunk_changes):
            if change.old is not None and change.new is not None:
                hunk_post.append(change)
            else:
                break

        assert len(hunk_context) <= settings.max_diff_lines
        assert len(hunk_post) <= settings.max_diff_lines

        # 最后获取中间代码
        for change in hunk_changes:
            if change not in hunk_context and change not in hunk_post:
                hunk_middle.append(change)

        # 注意把后置上下文反转回来
        hunk_post = list(reversed(hunk_post))

        hunk_list.append(
            Hunk(
                index=hunk_index,
                context=hunk_context,
                middle=hunk_middle,
                post=hunk_post,
                all_=hunk_changes,
            )
        )

    return hunk_list


def wtp_diff_to_diff(wtp_diff: WTPDiff) -> Diff:
    """
    Convert a whatthepatch Diff object to a patche Diff object

    Args:
        wtp_diff (WTPDiff): A whatthepatch Diff object

    Returns:
        Diff: A patche Diff object
    """

    return Diff(
        header=wtp_diff.header,
        changes=wtp_diff.changes,
        text=wtp_diff.text,
        hunks=changes_to_hunks(wtp_diff.changes),
    )


def parse_unified_diff(text: str) -> Optional[List[Diff]]:
    """解析 unified diff 格式的补丁"""
    lines = iter(text.splitlines())
    diffs: List[Diff] = []

    while True:
        try:
            header = parse_header(lines)
            if not header:
                break

            changes: List[Change] = []
            hunk_index = 0

            for line in lines:
                # 检查是否是新的 diff 块开始
                if HEADER_OLD.match(line):
                    lines = iter([line] + list(lines))
                    break

                # 解析 hunk 头
                hunk_match = HUNK_START.match(line)
                if hunk_match:
                    old_start = int(hunk_match.group(1))
                    old_count = int(hunk_match.group(2) or "1")
                    new_start = int(hunk_match.group(3))
                    new_count = int(hunk_match.group(4) or "1")

                    old_current = old_start
                    new_current = new_start
                    hunk_index += 1
                    continue

                # 解析变更行
                change_match = CHANGE_LINE.match(line)
                if change_match:
                    change_type = change_match.group(1)
                    content = change_match.group(2)

                    if change_type == " ":
                        # 上下文行 / 中间行
                        changes.append(
                            Change(
                                old=old_current,
                                new=new_current,
                                line=content,
                                hunk=hunk_index,
                            )
                        )
                        old_current += 1
                        new_current += 1
                    elif change_type == "-":
                        # 删除行
                        changes.append(
                            Change(
                                old=old_current, new=None, line=content, hunk=hunk_index
                            )
                        )
                        old_current += 1
                    elif change_type == "+":
                        # 新增行
                        changes.append(
                            Change(
                                old=None, new=new_current, line=content, hunk=hunk_index
                            )
                        )
                        new_current += 1

            if header and changes:
                diffs.append(
                    Diff(
                        header=header,
                        changes=changes,
                        text=text,
                        hunks=changes_to_hunks(changes),
                    )
                )

        except StopIteration:
            break

    return diffs if diffs else None


def parse_patch(text: str) -> Patch:
    """
    Parse a patch file
    Diiference between this and whatthepatch.parse_patch is that this function also
    returns the sha, author, date and message of the commit
    """

    lines = text.splitlines()

    idx = 0
    for i, line in enumerate(lines):
        # 这里考虑 git log 格式和 git format-patch 格式
        if (
            git_diffcmd_header.match(line)
            or spliter_line.match(line)
            or unified_diff_header.match(line)
        ):
            idx = i
            break

    else:
        # raise ValueError(
        #     "No diff --git line found, check if the input is a valid patch"
        # )
        idx = len(lines) + 1

    git_message_lines: list[str] = []
    if idx == 0:
        return Patch(
            sha=None,
            author=None,
            date=None,
            subject=None,
            message=None,
            # diff=[wtp_diff_to_diff(diff) for diff in wtp_parse_patch(text)],
            diff=parse_unified_diff(text),
        )
    else:
        git_message_lines = lines[:idx]

    message = "\n".join(git_message_lines)

    sha_line = git_message_lines.pop(0)
    if sha_line.startswith("From ") or sha_line.startswith("commit "):
        sha = sha_line.split(" ")[1]
    else:
        sha = None

    author_line = git_message_lines.pop(0)
    if author_line.startswith("Author: ") or author_line.startswith("From:"):
        author = " ".join(author_line.split(" ")[1:])
    else:
        author = None

    date_line = git_message_lines.pop(0)
    if date_line.startswith("Date: "):
        date_str = date_line.split("Date: ")[1]
        # 解析 Thu, 7 Mar 2024 15:41:57 +0800 或 Tue Feb 2 16:07:37 2021 +0100
        # if "," in date_str:
        #     date_fromat = "%a, %d %b %Y %H:%M:%S %z"
        # else:
        #     date_fromat = "%a %b %d %H:%M:%S %Y %z"

        # date = datetime.datetime.strptime(date_str.strip(), date_fromat)
        date = date_str.strip()
    else:
        date = None

    # 如果接下来的一行以 Subject 开头，则直接解析出 subject
    if git_message_lines[0].startswith("Subject: "):
        subject = git_message_lines.pop(0).split("Subject: ")[1]
    else:
        # 否则找到剩余的行里第一个非换行/非空行作为 subject
        subject = None
        for line in git_message_lines:
            if line.strip() != "":
                subject = line
                break

    return Patch(
        sha=sha.strip() if sha else None,
        author=author.strip() if author else None,
        date=date,
        subject=subject.strip() if subject else None,
        message=message,
        diff=[wtp_diff_to_diff(diff) for diff in wtp_parse_patch(text)],
    )
