"""Browser counterpart of pattern_parser; outputs [beat][hand][copy] pairs."""

JAVASCRIPT = r"""
function parseThrows(text) {
  if (text.length > 60000) throw Error("輸入太長，請縮短週期。");
  const word = /^[0-9a-z]+$/i, targetSlot = /^([0-9a-z]+)_([0-9]+)$/i;
  const retiredTarget = /^[0-9a-z]+p[0-9]+$/i;
  const pair = /^\(\s*([0-9]+)\s*,\s*([0-9a-z]+)\s*\)$/i;
  const beats = [];
  let position = 0;
  const skip = () => { while (position < text.length && /\s/.test(text[position])) position++; };
  function durationValue(value) {
    if (!/^(?:[0-9]+|[a-z])$/i.test(value)) throw Error("拋接時長請使用十進位整數或單一字母；不同拍請以空白或換行分隔。");
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
    else throw Error(`無法讀取投擲「${token}」。`);
    if (target !== null && (!Number.isSafeInteger(target) || target < 0 || target >= 16)) throw Error("接球手編號必須介於 1 與 16。");
    if (!Number.isSafeInteger(duration) || duration > 64) throw Error("拋接時長最多 64 拍。");
    return [target, duration];
  }
  function column() {
    if (position >= text.length) throw Error("分隔符號後缺少手的投擲資料。");
    const opener = text[position];
    if (opener === "[" || opener === "{") {
      const closer = opener === "[" ? "]" : "}";
      const end = text.indexOf(closer, position + 1);
      if (end < 0) throw Error(`缺少右括號 ${closer}。`);
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
        if (!token) throw Error("逗號前後缺少投擲資料。");
        if (retiredTarget.test(token)) throw Error("接球手的分隔符已改為 _；請改寫舊的 p 分隔格式。");
        return slot(token, opener === "{");
      });
    }
    let end = position;
    while (end < text.length && /[0-9a-z_]/i.test(text[end])) end++;
    const token = text.slice(position, end);
    if (retiredTarget.test(token)) throw Error("接球手的分隔符已改為 _；請改寫舊的 p 分隔格式。");
    if (token.includes("_") && !targetSlot.test(token)) throw Error("接球手格式不完整，請使用「時長_手編號」。");
    if (!token) throw Error(`無法讀取位置 ${position + 1} 的投擲資料。`);
    position = end;
    return [slot(token)];
  }
  skip();
  while (position < text.length) {
    const columns = [column()];
    let boundary = position;
    skip();
    while (text[position] === "|") { position++; skip(); columns.push(column()); boundary = position; skip(); }
    if (position < text.length && position === boundary) throw Error("不同拍請以空白或換行分隔。");
    beats.push(columns);
    if (beats.length > 128 || columns.length > 16) throw Error("最多支援 16 隻手、128 拍。");
  }
  if (!beats.length) throw Error("請輸入至少一拍。");
  let hands = Math.max(...beats.map(beat => beat.length));
  for (const beat of beats) for (const hand of beat) for (const [target] of hand) {
    if (target !== null) hands = Math.max(hands, target + 1);
  }
  let copies = 0;
  const normalized = beats.map(beat => {
    const columns = beat.map(hand => {
      if (hands > 1 && hand.some(([target, duration]) => target === null && duration)) throw Error("多手時，非空投擲需要指定接球手。");
      const slots = hand.filter(([, duration]) => duration).map(([target, duration]) => [target ?? 0, duration]);
      copies += slots.length;
      return slots.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    });
    while (columns.length < hands) columns.push([]);
    return columns;
  });
  if (copies > 2048) throw Error("一個週期最多支援 2048 次拋球。");
  return normalized;
}
"""
