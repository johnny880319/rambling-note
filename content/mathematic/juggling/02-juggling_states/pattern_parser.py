"""Normalize input into immutable [beat][hand][copy] (destination, duration) data."""

import re

Throw = tuple[tuple[tuple[int, int], ...], ...]
_WORD = re.compile(r"[0-9a-z]+", re.IGNORECASE)
_TARGET = re.compile(r"([0-9a-z]+)_([0-9]+)", re.IGNORECASE)
_RETIRED_TARGET = re.compile(r"[0-9a-z]+p[0-9]+", re.IGNORECASE)
_PAIR = re.compile(r"\(\s*([0-9]+)\s*,\s*([0-9a-z]+)\s*\)", re.IGNORECASE)


def parse_throws(text: str) -> tuple[Throw, ...]:
    if len(text) > 60000:
        raise ValueError("The input is too long. Shorten the period.")
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
            raise ValueError(f"Cannot parse the throw “{token}”.")
        if not re.fullmatch(r"[0-9]+|[a-z]", value, re.IGNORECASE):
            raise ValueError(
                "Write a throw as a decimal integer or one letter, and separate "
                "beats with whitespace."
            )
        duration = int(value, 10 if value.isascii() and value.isdigit() else 36)
        if target is not None and not 0 <= target < 16:
            raise ValueError("The catching-hand number must be between 1 and 16.")
        if duration > 64:
            raise ValueError("A throw can span at most 64 beats.")
        return target, duration

    def column():
        nonlocal position
        if position >= len(text):
            raise ValueError("Missing hand data after the separator.")
        opener = text[position]
        if opener in "[{":
            closer = "]" if opener == "[" else "}"
            end = text.find(closer, position + 1)
            if end < 0:
                raise ValueError(f"Missing closing bracket {closer}.")
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
                    raise ValueError("Missing throw data before or after a comma.")
                if _RETIRED_TARGET.fullmatch(token):
                    raise ValueError(
                        "Use _ to mark the catching hand; the old p separator is "
                        "no longer supported."
                    )
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
            raise ValueError(
                "Use _ to mark the catching hand; the old p separator is no "
                "longer supported."
            )
        if "_" in token and not _TARGET.fullmatch(token):
            raise ValueError(
                "The catching-hand suffix is incomplete. Use throw_hand."
            )
        if not token:
            raise ValueError(f"Cannot parse a throw at position {position + 1}.")
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
            raise ValueError("Separate beats with a space or newline.")
        beats.append(columns)
        if len(beats) > 128 or len(columns) > 16:
            raise ValueError("The simulator supports at most 16 hands and 128 beats.")
    if not beats:
        raise ValueError("Enter at least one beat.")
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
                raise ValueError(
                    "Every nonzero throw in a multi-hand pattern must specify "
                    "its catching hand."
                )
            columns.append(
                tuple(
                    sorted(
                        (target or 0, duration) for target, duration in hand if duration
                    )
                )
            )
        normalized.append(tuple(columns) + ((),) * (hands - len(columns)))
    if sum(len(hand) for beat in normalized for hand in beat) > 2048:
        raise ValueError("One period can contain at most 2,048 throws.")
    return tuple(normalized)
