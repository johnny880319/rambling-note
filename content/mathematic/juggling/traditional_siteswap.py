"""Translate solo asynchronous and synchronous siteswaps into canonical throws.

Conventions follow https://jugglinglab.org/html/ssnotation.html: asynchronous
throws start with the right hand; synchronous pairs are (left, right), with an
empty beat after each pair. A trailing star appends a hand-swapped repeat.
"""

import re


def parse_siteswap(text: str) -> tuple:
    if len(text) > 60000:
        raise ValueError("The input is too long. Shorten the period.")
    source = re.sub(r"\s", "", text)
    if not source:
        raise ValueError("Enter at least one beat.")
    synchronous = source.startswith("(")
    mirrored = source.endswith("*")
    if mirrored:
        if not synchronous:
            raise ValueError("The * suffix requires a synchronous siteswap.")
        source = source[:-1]
    position = 0

    def take(char):
        nonlocal position
        if position >= len(source) or source[position] != char:
            raise ValueError(f"Expected {char} at position {position + 1}.")
        position += 1

    def throw():
        nonlocal position
        if position >= len(source):
            raise ValueError("Missing throw value.")
        char = source[position]
        if char == "{":
            end = source.find("}", position + 1)
            token = source[position + 1 : end] if end >= 0 else ""
            if not re.fullmatch(r"[0-9]+", token):
                raise ValueError("Use a decimal integer inside braces, such as {36}.")
            duration = int(token)
            position = end + 1
        elif char in "0123456789abcdefghijklmnopqrstuvwxyz":
            duration = int(char, 36)
            position += 1
        else:
            raise ValueError(
                f"Cannot parse traditional siteswap at position {position + 1}. "
                "Use lowercase siteswap symbols; disable Traditional Siteswap "
                "for juggling matrices."
            )
        if duration > 64:
            raise ValueError("A throw can span at most 64 beats.")
        crossed = synchronous and position < len(source) and source[position] == "x"
        if crossed:
            position += 1
        if synchronous and duration % 2:
            raise ValueError("Synchronous throws must be even.")
        if crossed and duration == 0:
            raise ValueError("0x is not a throw; use 0 for an empty hand.")
        return duration, crossed

    def hand():
        if position < len(source) and source[position] == "[":
            take("[")
            values = []
            while position < len(source) and source[position] != "]":
                values.append(throw())
                if len(values) > 2048:
                    raise ValueError("One period can contain at most 2,048 throws.")
            take("]")
            if not values:
                raise ValueError("A traditional multiplex cannot be empty; use 0.")
            return values
        return [throw()]

    events = []
    while position < len(source):
        if synchronous:
            take("(")
            left = hand()
            take(",")
            right = hand()
            take(")")
            events.append((left, right))
        else:
            events.append(hand())
        if len(events) * (2 if synchronous else 1) > 128:
            raise ValueError("The simulator supports at most 16 hands and 128 beats.")

    def slots(values, source_hand):
        return tuple(
            sorted(
                (1 - source_hand if crossed else source_hand, duration)
                for duration, crossed in values
                if duration
            )
        )

    beats = []
    if synchronous:
        for left, right in events:
            beats.extend(((slots(left, 0), slots(right, 1)), ((), ())))
        if mirrored:
            beats += [
                tuple(
                    tuple(sorted((1 - target, duration) for target, duration in hand))
                    for hand in reversed(beat)
                )
                for beat in beats
            ]
    else:
        if len(events) % 2:
            events *= 2
        for t, values in enumerate(events):
            source_hand = (t + 1) % 2
            columns = [(), ()]
            columns[source_hand] = tuple(
                sorted(
                    ((source_hand + duration) % 2, duration)
                    for duration, _ in values
                    if duration
                )
            )
            beats.append(tuple(columns))
    if len(beats) > 128:
        raise ValueError("The simulator supports at most 16 hands and 128 beats.")
    if sum(len(hand) for beat in beats for hand in beat) > 2048:
        raise ValueError("One period can contain at most 2,048 throws.")
    return tuple(beats)


JAVASCRIPT = r"""
function parseTraditionalSiteswap(text) {
  if (text.length > 60000) throw Error("The input is too long. Shorten the period.");
  let source = text.replace(/\s/g, "");
  if (!source) throw Error("Enter at least one beat.");
  const synchronous = source.startsWith("("), mirrored = source.endsWith("*");
  if (mirrored) {
    if (!synchronous) throw Error("The * suffix requires a synchronous siteswap.");
    source = source.slice(0, -1);
  }
  let position = 0;
  function take(char) {
    if (source[position] !== char) throw Error(`Expected ${char} at position ${position + 1}.`);
    position++;
  }
  function slot() {
    if (position >= source.length) throw Error("Missing throw value.");
    const char = source[position];
    let duration;
    if (char === "{") {
      const end = source.indexOf("}", position + 1), token = end < 0 ? "" : source.slice(position + 1, end);
      if (!/^[0-9]+$/.test(token)) throw Error("Use a decimal integer inside braces, such as {36}.");
      duration = Number(token); position = end + 1;
    } else if (/^[0-9a-z]$/.test(char)) { duration = parseInt(char, 36); position++; }
    else throw Error(`Cannot parse traditional siteswap at position ${position + 1}. Use lowercase siteswap symbols; disable Traditional Siteswap for juggling matrices.`);
    if (!Number.isSafeInteger(duration) || duration > 64) throw Error("A throw can span at most 64 beats.");
    const crossed = synchronous && source[position] === "x";
    if (crossed) position++;
    if (synchronous && duration % 2) throw Error("Synchronous throws must be even.");
    if (crossed && duration === 0) throw Error("0x is not a throw; use 0 for an empty hand.");
    return [duration, crossed];
  }
  function hand() {
    if (source[position] !== "[") return [slot()];
    take("[");
    const values = [];
    while (position < source.length && source[position] !== "]") {
      values.push(slot());
      if (values.length > 2048) throw Error("One period can contain at most 2,048 throws.");
    }
    take("]");
    if (!values.length) throw Error("A traditional multiplex cannot be empty; use 0.");
    return values;
  }
  const events = [];
  while (position < source.length) {
    if (synchronous) { take("("); const left = hand(); take(","); const right = hand(); take(")"); events.push([left, right]); }
    else events.push(hand());
    if (events.length * (synchronous ? 2 : 1) > 128) throw Error("The simulator supports at most 16 hands and 128 beats.");
  }
  const sorted = slots => slots.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  let beats;
  if (synchronous) {
    beats = events.flatMap(event => [event.map((values, h) => sorted(values.filter(([duration]) => duration).map(([duration, crossed]) => [crossed ? 1 - h : h, duration]))), [[], []]]);
    if (mirrored) beats = [...beats, ...beats.map(beat => [...beat].reverse().map(hand => sorted(hand.map(([target, duration]) => [1 - target, duration]))))];
  } else {
    const period = events.length * (events.length % 2 ? 2 : 1);
    beats = Array.from({length: period}, (_, t) => {
      const sourceHand = (t + 1) % 2, columns = [[], []];
      columns[sourceHand] = sorted(events[t % events.length].filter(([duration]) => duration).map(([duration]) => [(sourceHand + duration) % 2, duration]));
      return columns;
    });
  }
  if (beats.length > 128) throw Error("The simulator supports at most 16 hands and 128 beats.");
  if (beats.reduce((total, beat) => total + beat.reduce((sum, hand) => sum + hand.length, 0), 0) > 2048) throw Error("One period can contain at most 2,048 throws.");
  return beats;
}
"""
