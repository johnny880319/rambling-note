"""Browser counterpart of pattern_parser; outputs [beat][hand][copy] pairs."""

JAVASCRIPT = r"""
function parseThrows(text) {
  if (text.length > 60000) throw Error("The input is too long. Shorten the period.");
  const word = /^[0-9a-z]+$/i, targetSlot = /^([0-9a-z]+)_([0-9]+)$/i;
  const retiredTarget = /^[0-9a-z]+p[0-9]+$/i;
  const pair = /^\(\s*([0-9]+)\s*,\s*([0-9a-z]+)\s*\)$/i;
  const beats = [];
  let position = 0;
  const skip = () => { while (position < text.length && /\s/.test(text[position])) position++; };
  function durationValue(value) {
    if (!/^(?:[0-9]+|[a-z])$/i.test(value)) throw Error("Write a throw as a decimal integer or one letter, and separate beats with whitespace.");
    return parseInt(value, /^[0-9]+$/.test(value) ? 10 : 36);
  }
  function slot(token, legacy = false) {
    let target, duration, match = legacy ? pair.exec(token) : null;
    if (match) { target = Number(match[1]) - 1; duration = durationValue(match[2]); }
    else if ((match = targetSlot.exec(token))) {
      target = Number(match[2]) - 1;
      duration = durationValue(match[1]);
    }
    else if (word.test(token)) { target = legacy ? 0 : null; duration = durationValue(token); }
    else throw Error(`Cannot parse the throw “${token}”.`);
    if (target !== null && (!Number.isSafeInteger(target) || target < 0 || target >= 16)) throw Error("The catching-hand number must be between 1 and 16.");
    if (!Number.isSafeInteger(duration) || duration > 64) throw Error("A throw can span at most 64 beats.");
    return [target, duration];
  }
  function column() {
    if (position >= text.length) throw Error("Missing hand data after the separator.");
    const opener = text[position];
    if (opener === "[" || opener === "{") {
      const closer = opener === "[" ? "]" : "}";
      const end = text.indexOf(closer, position + 1);
      if (end < 0) throw Error(`Missing closing bracket ${closer}.`);
      const inside = text.slice(position + 1, end).trim();
      position = end + 1;
      if (!inside) return [];
      const tokens = [];
      let start = 0, depth = 0;
      for (let offset = 0; offset < inside.length; offset++) {
        const char = inside[offset];
        depth += Number(char === "(") - Number(char === ")");
        if (char === "," && depth === 0) { tokens.push(inside.slice(start, offset).trim()); start = offset + 1; }
      }
      tokens.push(inside.slice(start).trim());
      return tokens.map(token => {
        if (!token) throw Error("Missing throw data before or after a comma.");
        if (retiredTarget.test(token)) throw Error("Use _ to mark the catching hand; the old p separator is no longer supported.");
        return slot(token, opener === "{");
      });
    }
    let end = position;
    while (end < text.length && /[0-9a-z_]/i.test(text[end])) end++;
    const token = text.slice(position, end);
    if (retiredTarget.test(token)) throw Error("Use _ to mark the catching hand; the old p separator is no longer supported.");
    if (token.includes("_") && !targetSlot.test(token)) throw Error("The catching-hand suffix is incomplete. Use throw_hand.");
    if (!token) throw Error(`Cannot parse a throw at position ${position + 1}.`);
    position = end;
    return [slot(token)];
  }
  skip();
  while (position < text.length) {
    const columns = [column()];
    let boundary = position;
    skip();
    while (text[position] === "|") { position++; skip(); columns.push(column()); boundary = position; skip(); }
    if (position < text.length && position === boundary) throw Error("Separate beats with a space or newline.");
    beats.push(columns);
    if (beats.length > 128 || columns.length > 16) throw Error("The simulator supports at most 16 hands and 128 beats.");
  }
  if (!beats.length) throw Error("Enter at least one beat.");
  let hands = Math.max(...beats.map(beat => beat.length));
  for (const beat of beats) for (const hand of beat) for (const [target] of hand) {
    if (target !== null) hands = Math.max(hands, target + 1);
  }
  let copies = 0;
  const normalized = beats.map(beat => {
    const columns = beat.map(hand => {
      if (hands > 1 && hand.some(([target, duration]) => target === null && duration)) throw Error("Every nonzero throw in a multi-hand pattern must specify its catching hand.");
      const slots = hand.filter(([, duration]) => duration).map(([target, duration]) => [target ?? 0, duration]);
      copies += slots.length;
      return slots.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    });
    while (columns.length < hands) columns.push([]);
    return columns;
  });
  if (copies > 2048) throw Error("One period can contain at most 2,048 throws.");
  return normalized;
}
"""
