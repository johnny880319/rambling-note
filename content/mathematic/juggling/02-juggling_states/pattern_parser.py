"""Normalize input into immutable [beat][hand][copy] (destination, duration) data."""

import re

Throw = tuple[tuple[tuple[int, int], ...], ...]
_WORD = re.compile(r"[0-9a-z]+", re.IGNORECASE)
_TARGET = re.compile(r"([0-9a-z]+)_([0-9]+)", re.IGNORECASE)
_RETIRED_TARGET = re.compile(r"[0-9a-z]+p[0-9]+", re.IGNORECASE)
_PAIR = re.compile(r"\(\s*([0-9]+)\s*,\s*([0-9a-z]+)\s*\)", re.IGNORECASE)


def parse_throws(text: str) -> tuple[Throw, ...]:
    if len(text) > 60000:
        raise ValueError("輸入太長，請縮短週期。")
    position = 0
    beats = []

    def skip():
        nonlocal position
        while position < len(text) and text[position].isspace():
            position += 1

    def slot(token, legacy=False):
        match = _PAIR.fullmatch(token) if legacy else None
        if match:
            target, value = int(match[1]) - 1, match[2]
        elif match := _TARGET.fullmatch(token):
            target, value = int(match[2]) - 1, match[1]
        elif _WORD.fullmatch(token):
            target, value = (0 if legacy else None), token
        else:
            raise ValueError(f"無法讀取投擲「{token}」。")
        if not re.fullmatch(r"[0-9]+|[a-z]", value, re.IGNORECASE):
            raise ValueError("拋接時長請使用十進位整數或單一字母；不同拍請以空白或換行分隔。")
        duration = int(value, 10 if value.isascii() and value.isdigit() else 36)
        if target is not None and not 0 <= target < 16:
            raise ValueError("接球手編號必須介於 1 與 16。")
        if duration > 64:
            raise ValueError("拋接時長最多 64 拍。")
        return target, duration

    def column():
        nonlocal position
        if position >= len(text):
            raise ValueError("分隔符號後缺少手的投擲資料。")
        opener = text[position]
        if opener in "[{":
            closer = "]" if opener == "[" else "}"
            end = text.find(closer, position + 1)
            if end < 0:
                raise ValueError(f"缺少右括號 {closer}。")
            inside = text[position + 1 : end].strip()
            position = end + 1
            if not inside:
                return []
            tokens, start, depth = [], 0, 0
            for offset, char in enumerate(inside):
                depth += (char == "(") - (char == ")")
                if char == "," and depth == 0:
                    tokens.append(inside[start:offset].strip())
                    start = offset + 1
            tokens.append(inside[start:].strip())
            result = []
            for token in tokens:
                if not token:
                    raise ValueError("逗號前後缺少投擲資料。")
                if _RETIRED_TARGET.fullmatch(token):
                    raise ValueError("接球手的分隔符已改為 _；請改寫舊的 p 分隔格式。")
                result.append(slot(token, legacy=opener == "{"))
            return result
        end = position
        while (
            end < len(text)
            and text[end].isascii()
            and (text[end].isalnum() or text[end] == "_")
        ):
            end += 1
        token = text[position:end]
        if _RETIRED_TARGET.fullmatch(token):
            raise ValueError("接球手的分隔符已改為 _；請改寫舊的 p 分隔格式。")
        if "_" in token and not _TARGET.fullmatch(token):
            raise ValueError("接球手格式不完整，請使用「時長_手編號」。")
        if not token:
            raise ValueError(f"無法讀取位置 {position + 1} 的投擲資料。")
        position = end
        return [slot(token)]

    skip()
    while position < len(text):
        columns = [column()]
        boundary = position
        skip()
        while position < len(text) and text[position] == "|":
            position += 1
            skip()
            columns.append(column())
            boundary = position
            skip()
        if position < len(text) and position == boundary:
            raise ValueError("不同拍請以空白或換行分隔。")
        beats.append(columns)
        if len(beats) > 128 or len(columns) > 16:
            raise ValueError("最多支援 16 隻手、128 拍。")
    if not beats:
        raise ValueError("請輸入至少一拍。")
    hands = max(
        max(len(beat) for beat in beats),
        max(
            (
                target + 1
                for beat in beats
                for hand in beat
                for target, _ in hand
                if target is not None
            ),
            default=1,
        ),
    )
    normalized = []
    for beat in beats:
        columns = []
        for hand in beat:
            if hands > 1 and any(
                target is None and duration for target, duration in hand
            ):
                raise ValueError("多手時，非空投擲需要指定接球手。")
            columns.append(
                tuple(
                    sorted(
                        (target or 0, duration) for target, duration in hand if duration
                    )
                )
            )
        normalized.append(tuple(columns) + ((),) * (hands - len(columns)))
    if sum(len(hand) for beat in normalized for hand in beat) > 2048:
        raise ValueError("一個週期最多支援 2048 次拋球。")
    return tuple(normalized)
