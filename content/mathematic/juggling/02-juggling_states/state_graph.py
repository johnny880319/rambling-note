"""State graphs for juggling patterns.

A state records what a pattern has already committed to.  For each hand, and
each number of beats still to run, it counts the objects due to land there --
in the notation of the previous note an element of ``M(F)``, the same type as
one entry of a juggling matrix, whose total is the object count ``N``.

Advancing one beat shifts every object one place closer and adds whatever the
hands throw on the new beat.  Balance is what makes this a graph rather than a
free choice: a hand throws exactly as many objects as land in it, so the state
alone decides how many throws leave each hand, and only their destinations are
free.  A ``p``-periodic pattern is then a closed walk of length ``p``.

Everything here is read off a pattern rather than configured.  How many hands,
how high, how many objects at once, how many objects in all: the throws say so,
and a reader who wants a different graph writes a different pattern.  That also
sidesteps the one hard limit -- the space of states grows combinatorially in the
hands and the height, while a pattern's walk grows with its period -- so the
walk always draws, and the surrounding space is drawn when it happens to be
small enough to help.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go

# A state is indexed [hand][beats_from_now - 1] and counts objects due to land.
State = tuple[tuple[int, ...], ...]
# A throw is indexed [hand] and lists the slots that hand's objects fly to,
# each slot a (destination hand, beats of flight) pair.
Throw = tuple[tuple[tuple[int, int], ...], ...]

# The surrounding graph is drawn whole or not at all.  Half of one is worth
# less than none: unlabelled dots with no edges between them say nothing the
# walk has not already said, and they crowd out what it does say.  So the caps
# are where every state and every throw can still carry its name -- `7531` at
# thirty-five states and ninety-five throws is about the last that reads.
MAX_BACKGROUND_STATES = 40
MAX_BACKGROUND_EDGES = 100

# Siteswap writes throws of ten and above as letters, so a column of a juggling
# matrix reads the way a juggler would say it.
_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"

_ACCENT = "#38bdf8"
_MUTED = "#64748b"


# --------------------------------------------------------------------------
# Notation
# --------------------------------------------------------------------------


def digit(value: int) -> str:
    """Render a flight time the way siteswap does.

    >>> digit(3), digit(11), digit(40)
    ('3', 'b', '(40)')
    """
    return _DIGITS[value] if value < len(_DIGITS) else f"({value})"


def state_label(state: State) -> str:
    """A state written as the values it takes on each slot.

    That is what ``M(F)`` is -- a function into the non-negative integers --
    with the hands separated by a slash.

    >>> state_label(((1, 1, 1, 0, 0),))
    '11100'
    >>> state_label(((1, 0), (0, 1)))
    '10/01'
    """
    return "/".join("".join(str(count) for count in hand) for hand in state)


def throw_label(throw: Throw, hands: int) -> str:
    """A throw written the way the notes write an element of ``M(F)``.

    One beat is one column of a juggling matrix, so it carries a multiset per
    hand and the hands are separated by a bar.  A slot is the pair ``(hand,
    flight)`` the notes use; with a single hand ``F`` is canonically
    ``Z_{>0}``, so the hand is dropped rather than written as noise.  Throwing
    nothing is the empty multiset, which says what it means in a way siteswap's
    ``0`` does not.

    >>> throw_label((((0, 5),),), hands=1)
    '{5}'
    >>> throw_label((((0, 3), (0, 4)),), hands=1)
    '{3,4}'
    >>> throw_label(((),), hands=1)
    '{}'
    >>> throw_label((((1, 3),), ()), hands=2)
    '{(2,3)}|{}'
    """
    columns = []
    for slots in throw:
        parts = [
            digit(flight) if hands == 1 else f"({hand + 1},{digit(flight)})"
            for hand, flight in slots
        ]
        columns.append("{" + ",".join(parts) + "}")
    return "|".join(columns)


def notation_examples() -> list[tuple[str, str, str]]:
    """One worked state and throw per shape the notation has to cover.

    Built by calling the labellers rather than by writing the strings out, so
    the table in the note cannot drift away from what the code prints.

    >>> [row[0] for row in notation_examples()]
    ['one hand', 'one hand, multiplex', 'two hands', 'two hands, multiplex']
    """
    rows = [
        ("one hand", ((1, 1, 1, 0, 0),), (((0, 5),),), 1),
        ("one hand, multiplex", ((2, 1, 0, 0),), (((0, 3), (0, 4)),), 1),
        ("two hands", ((1, 0, 0), (0, 1, 0)), (((1, 3),), ()), 2),
        ("two hands, multiplex", ((2, 0), (0, 1)), (((0, 2), (1, 2)), ()), 2),
    ]
    return [
        (name, state_label(state), throw_label(throw, hands))
        for name, state, throw, hands in rows
    ]


# --------------------------------------------------------------------------
# Reading a pattern
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Pattern:
    """A periodic pattern and the walk it makes, read off its own throws.

    ``states[t]`` is the state the pattern throws ``throws[t]`` from, so
    ``advance(states[t], throws[t])`` is beat ``t + 1``.  Reading it this way
    round is what lets a reader step the walk: the state comes first and the
    throw acts on it.
    """

    throws: tuple[Throw, ...]
    states: tuple[State, ...]
    hands: int
    height: int
    capacity: int
    objects: int

    def __len__(self) -> int:
        return len(self.throws)


def read_pattern(text: str) -> Pattern:
    """Read a pattern and work out the shape of the space it lives in.

    A beat is one column of a juggling matrix: a multiset per hand, the hands
    separated by a bar.  A slot is ``(hand, flight)``; with a single hand ``F``
    is canonically ``Z_{>0}`` and the hand may be dropped.  Whitespace is only
    ever cosmetic; the braces and bars carry the structure.

    >>> pattern = read_pattern("{5} {3} {1}")
    >>> pattern.hands, pattern.height, pattern.capacity, pattern.objects
    (1, 5, 1, 3)
    >>> [state_label(state) for state in pattern.states]
    ['11100', '11001', '10110']

    With one hand a run of flight times is the same pattern without the braces,
    one beat per character, which is how a juggler says it.

    >>> read_pattern("531") == read_pattern("{5} {3} {1}")
    True

    A throw that lands where nothing was caught is refused, and so is a hand
    that catches without throwing: that is balance, and it is what makes the
    state decide which throws are available.

    >>> read_pattern("532")
    Traceback (most recent call last):
    ValueError: on beat 0 hand 1 catches 0 objects but throws 1, so the objects do not balance
    """
    hands = _count_hands(text)
    throws = _parse(text, hands)
    height = max(
        (flight for throw in throws for slots in throw for _, flight in slots),
        default=1,
    )
    states = _walk(throws, hands, height)

    for beat, throw in enumerate(throws):
        caught = landing_now(states[beat])
        thrown = tuple(len(slots) for slots in throw)
        if caught != thrown:
            hand = next(
                index
                for index, (left, right) in enumerate(zip(caught, thrown))
                if left != right
            )
            raise ValueError(
                f"on beat {beat} hand {hand + 1} catches {caught[hand]} objects "
                f"but throws {thrown[hand]}, so the objects do not balance"
            )

    return Pattern(
        throws=tuple(throws),
        states=tuple(states),
        hands=hands,
        height=height,
        capacity=max(count for state in states for hand in state for count in hand),
        objects=sum(sum(hand) for hand in states[0]),
    )


def _walk(throws: list[Throw], hands: int, height: int) -> list[State]:
    """The state each beat throws from, read off the pattern."""
    period = len(throws)
    states = []
    for beat in range(period):
        counts = [[0] * height for _ in range(hands)]
        for back in range(1, height + 1):
            for slots in throws[(beat - back) % period]:
                for hand, flight in slots:
                    # A throw made `back` beats ago has `flight - back` still to
                    # run; the object caught on this very beat sits in slot one,
                    # which is where `advance` looks for what must be rethrown.
                    place = flight - back + 1
                    if 1 <= place <= height:
                        counts[hand][place - 1] += 1
        states.append(tuple(tuple(hand) for hand in counts))
    return states


def _count_hands(text: str) -> int:
    """How many hands the text mentions, so the slots can be read at all."""
    mentioned = [int(match) for match in re.findall(r"\(\s*(\d+)\s*,", text)]
    return max(mentioned) if mentioned else 1


def _parse(text: str, hands: int) -> list[Throw]:
    """Beats, each a multiset per hand."""
    beats: list[Throw] = []
    position = 0
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        columns: list[tuple[tuple[int, int], ...]] = []
        while True:
            slots, position = _parse_column(text, position, hands)
            columns.append(slots)
            # Whitespace never carries meaning here: the braces close a hand and
            # the bar joins the hands of one beat, so a reader may lay a pattern
            # out however it reads best.
            after = position
            while after < len(text) and text[after].isspace():
                after += 1
            if after < len(text) and text[after] == "|":
                position = after + 1
                while position < len(text) and text[position].isspace():
                    position += 1
                continue
            break
        if len(columns) > hands:
            raise ValueError(
                f"a beat has {len(columns)} columns but there are {hands} hands"
            )
        beats.append(tuple(columns) + ((),) * (hands - len(columns)))
    if not beats:
        raise ValueError("nothing to read")
    return beats


def _parse_column(
    text: str, position: int, hands: int
) -> tuple[tuple[tuple[int, int], ...], int]:
    """One hand's multiset on one beat, and where reading stopped."""
    if text[position] == "{":
        end = text.find("}", position)
        if end < 0:
            raise ValueError("a multiset is never closed")
        slots = [
            _parse_slot(token, hands)
            for token in _split_slots(text[position + 1 : end])
        ]
        return tuple(sorted(slot for slot in slots if slot)), end + 1

    # The brace-free shorthand: one flight time, one beat.
    character = text[position]
    if character not in _DIGITS:
        raise ValueError(f"cannot read a throw at {text[position:][:8]!r}")
    if hands > 1:
        raise ValueError("with more than one hand every beat needs its braces")
    flight = int(character, 36)
    return (((0, flight),) if flight else ()), position + 1


def _split_slots(inside: str) -> list[str]:
    """Split a multiset on commas that are not inside a ``(hand, flight)``."""
    tokens, current, depth = [], "", 0
    for character in inside:
        depth += (character == "(") - (character == ")")
        if character == "," and depth == 0:
            tokens.append(current)
            current = ""
            continue
        current += character
    tokens.append(current)
    return [token for token in tokens if token.strip()]


def _parse_slot(token: str, hands: int) -> tuple[int, int] | None:
    """``(2,3)``, or just the flight time when there is one hand."""
    token = token.strip()
    if token.startswith("("):
        if not token.endswith(")"):
            raise ValueError(f"cannot read the slot {token!r}")
        head, _, tail = token[1:-1].partition(",")
        hand, flight = int(head) - 1, int(tail.strip(), 36)
    else:
        hand, flight = 0, int(token, 36)
    if not 0 <= hand < hands:
        raise ValueError(f"a throw lands in hand {hand + 1}, but there are {hands}")
    return (hand, flight) if flight else None


# --------------------------------------------------------------------------
# The space of states
# --------------------------------------------------------------------------


def landing_now(state: State) -> tuple[int, ...]:
    """How many objects land in each hand on the next beat.

    Balance turns this into how many that hand must throw.

    >>> landing_now(((1, 1, 1, 0, 0),))
    (1,)
    >>> landing_now(((0, 1), (1, 0)))
    (0, 1)
    """
    return tuple(hand[0] for hand in state)


def advance(state: State, throw: Throw) -> State:
    """Shift one beat and add the objects thrown on the new beat.

    >>> advance(((1, 1, 1, 0, 0),), (((0, 5),),))
    ((1, 1, 0, 0, 1),)
    """
    counts = [[*hand[1:], 0] for hand in state]
    for slots in throw:
        for hand, flight in slots:
            counts[hand][flight - 1] += 1
    return tuple(tuple(hand) for hand in counts)


def throws_from(state: State, capacity: int) -> list[Throw]:
    """Every throw the state allows, in the order a reader would list them.

    The number of objects leaving each hand is fixed by the state; the choice
    is only where they go.

    >>> [throw_label(t, 1) for t in throws_from(((1, 1, 1, 0, 0),), 1)]
    ['{3}', '{4}', '{5}']
    >>> [throw_label(t, 1) for t in throws_from(((0, 1, 1, 1, 0),), 1)]
    ['{}']
    """
    hands, height = len(state), len(state[0])
    room = [[*hand[1:], 0] for hand in state]
    slots = [(hand, flight) for hand in range(hands) for flight in range(1, height + 1)]

    # Objects leaving one hand on one beat are interchangeable, so the choice is
    # a multiset of destinations rather than a sequence.
    per_hand = [
        list(itertools.combinations_with_replacement(slots, count))
        for count in landing_now(state)
    ]

    legal: list[Throw] = []
    for combination in itertools.product(*per_hand):
        added: dict[tuple[int, int], int] = {}
        for slots_for_hand in combination:
            for slot in slots_for_hand:
                added[slot] = added.get(slot, 0) + 1
        if all(
            room[hand][flight - 1] + extra <= capacity
            for (hand, flight), extra in added.items()
        ):
            legal.append(tuple(combination))
    return legal


def ground_state(objects: int, hands: int, height: int, capacity: int) -> State:
    """The state that packs every object into the earliest slots it can reach.

    Ground means least excited, and excitation weights an object by how long it
    still has to fly, so the earliest beats are filled to the brim first.  With
    one hand and no multiplex this is the familiar string of ones.

    >>> state_label(ground_state(3, 1, 5, 1))
    '11100'
    >>> state_label(ground_state(4, 1, 3, 2))
    '220'
    """
    counts = [[0] * height for _ in range(hands)]
    left = objects
    for beat in range(height):
        for hand in range(hands):
            take = min(capacity, left)
            counts[hand][beat] = take
            left -= take
    return tuple(tuple(hand) for hand in counts)


def count_states(objects: int, hands: int, height: int, capacity: int) -> int:
    """How many states there are, without building any of them.

    Enumerating four hands at height four takes half a minute; deciding whether
    the graph is worth drawing should not cost that.

    >>> count_states(3, 1, 5, 1)
    10
    >>> count_states(7, 4, 3, 1)
    792
    """
    # One slot at a time, counting the ways to have placed j objects so far.
    ways = [1] + [0] * objects
    for _ in range(hands * height):
        ways = [
            sum(ways[j - take] for take in range(min(capacity, j) + 1))
            for j in range(objects + 1)
        ]
    return ways[objects]


def enumerate_states(
    objects: int, hands: int, height: int, capacity: int
) -> list[State]:
    """Every state with ``objects`` objects landing no later than ``height``.

    >>> len(enumerate_states(3, 1, 5, 1))
    10
    >>> len(enumerate_states(2, 1, 3, 2))
    6
    """

    def spread(total: int, parts: int) -> list[list[int]]:
        if parts == 0:
            return [[]] if total == 0 else []
        return [
            [first, *rest]
            for first in range(min(total, capacity) + 1)
            for rest in spread(total - first, parts - 1)
        ]

    return [
        tuple(
            tuple(counts[hand * height : (hand + 1) * height]) for hand in range(hands)
        )
        for counts in spread(objects, hands * height)
    ]


@dataclass(frozen=True)
class StateGraph:
    """Every state a pattern of this shape could reach, and the throws between.

    Edges are kept as pairs of states rather than as throws: several throws can
    join the same two states -- with four hands, every way of dealing the same
    throws out to the hands does -- and the drawing wants one curve either way.
    A pair joined by exactly one throw carries its label; one joined by several
    has no single label to carry, and holds ``None``.
    """

    states: tuple[State, ...]
    pairs: dict[tuple[int, int], str | None]
    index: dict[State, int]
    ground: int


def surrounding(pattern: Pattern) -> StateGraph | None:
    """The space around a pattern, when the whole of it can be drawn.

    The walk always draws; the space it sits in grows combinatorially in the
    hands and the height, so past a point there is nothing to show that would
    not hide the walk.
    """
    size = count_states(
        pattern.objects, pattern.hands, pattern.height, pattern.capacity
    )
    if size > MAX_BACKGROUND_STATES:
        return None

    states = enumerate_states(
        pattern.objects, pattern.hands, pattern.height, pattern.capacity
    )
    index = {state: position for position, state in enumerate(states)}
    pairs: dict[tuple[int, int], str | None] = {}
    for source, state in enumerate(states):
        for throw in throws_from(state, pattern.capacity):
            target = index.get(advance(state, throw))
            if target is None:
                continue
            key = (source, target)
            label = throw_label(throw, pattern.hands)
            pairs[key] = label if key not in pairs else None

    if len(pairs) > MAX_BACKGROUND_EDGES:
        return None

    ground = index[
        ground_state(
            pattern.objects, pattern.hands, pattern.height, pattern.capacity
        )
    ]
    return StateGraph(tuple(states), pairs, index, ground)


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------


def _excitation(state: State) -> int:
    """How far the objects sit from the earliest slots they could occupy."""
    return sum(
        beats * count for hand in state for beats, count in enumerate(hand, start=1)
    )


def layout(states: list[State] | tuple[State, ...], floor: int) -> np.ndarray:
    """Place each state, the least excited on top and excitation running down.

    Excitation is the natural coordinate: one throw moves a pattern between
    neighbouring levels, so the edges mostly run between adjacent rows and the
    picture reads as a ladder rather than a tangle.  The levels stack
    vertically because an article column is narrow and long.
    """
    levels: dict[int, list[int]] = {}
    for position, state in enumerate(states):
        levels.setdefault(_excitation(state) - floor, []).append(position)

    points = np.zeros((len(states), 2))
    for level, members in levels.items():
        members.sort(key=lambda position: state_label(states[position]))
        for column, position in enumerate(members):
            points[position] = (column - (len(members) - 1) / 2, -1.5 * level)
    return points


def _curve(start: np.ndarray, end: np.ndarray, bulge: float = 0.13) -> np.ndarray:
    """A quadratic arc, so the two edges of a mutual pair stay apart."""
    delta = end - start
    control = (start + end) / 2 + bulge * np.array([-delta[1], delta[0]])
    steps = np.linspace(0, 1, 12)[:, None]
    return (1 - steps) ** 2 * start + 2 * (1 - steps) * steps * control + steps**2 * end


def _loop(centre: np.ndarray, radius: float = 0.3) -> np.ndarray:
    """A throw that returns to its own state has nowhere to go but around."""
    angles = np.linspace(0, 2 * np.pi, 16)
    return centre + radius * np.column_stack((1 - np.cos(angles), np.sin(angles)))


def _beside(path: np.ndarray, share: float = 0.3, clear: float = 0.22) -> np.ndarray:
    """A point beside the curve rather than on it, so a label stays readable.

    The offset runs along the curve's own normal, away from the chord, so the
    two labels of a mutual pair -- whose curves bulge opposite ways -- end up on
    opposite sides of the edge.  Taking the same share of each curve puts them
    near opposite ends as well, which is where the room is.
    """
    index = round(share * (len(path) - 1))
    tangent = path[min(index + 1, len(path) - 1)] - path[max(index - 1, 0)]
    normal = np.array([-tangent[1], tangent[0]])
    length = float(np.hypot(*normal))
    if not length:
        return path[index]
    normal /= length
    if float(np.dot(path[index] - (path[0] + path[-1]) / 2, normal)) < 0:
        normal = -normal
    return path[index] + clear * normal


def _edges(
    drawn: list[tuple[int, int, str | None]], points: np.ndarray, lit: bool
) -> list[go.Scatter]:
    """Every edge of one kind in three traces, not three traces per edge.

    A notebook running under Pyodide feels the difference: a graph of any size
    would otherwise arrive as hundreds of separate traces.
    """
    colour = _ACCENT if lit else _MUTED
    opacity = 1.0 if lit else 0.32
    lines_x: list[float | None] = []
    lines_y: list[float | None] = []
    tips, angles, marks, texts = [], [], [], []

    for source, target, label in drawn:
        path = (
            _loop(points[source])
            if source == target
            else _curve(points[source], points[target])
        )
        # Full float repr would trail eighteen digits into the payload, and a
        # figure is thousands of points long.
        lines_x.extend([*np.round(path[:, 0], 3), None])
        lines_y.extend([*np.round(path[:, 1], 3), None])
        # The head sits short of the target so it does not cover the marker.
        heading = path[-3] - path[-5]
        tips.append(path[-3])
        angles.append(float(np.degrees(np.arctan2(heading[0], heading[1]))))
        if label is not None:
            marks.append(_beside(path))
            texts.append(label)

    if not tips:
        return []
    traces = [
        go.Scatter(
            x=lines_x,
            y=lines_y,
            mode="lines",
            line={"width": 2.4 if lit else 1.1, "color": colour},
            opacity=opacity,
            hoverinfo="skip",
            showlegend=False,
        ),
        go.Scatter(
            x=[point[0] for point in tips],
            y=[point[1] for point in tips],
            mode="markers",
            marker={
                "symbol": "arrow",
                "size": 9 if lit else 7,
                "angle": angles,
                "color": colour,
            },
            opacity=opacity,
            hoverinfo="skip",
            showlegend=False,
        ),
    ]
    if marks:
        traces.append(
            go.Scatter(
                x=[point[0] for point in marks],
                y=[point[1] for point in marks],
                mode="text",
                text=texts,
                textfont={"size": 11, "color": colour},
                opacity=1.0 if lit else 0.6,
                hoverinfo="skip",
                showlegend=False,
            )
        )
    return traces


def make_figure(
    pattern: Pattern,
    traced: int | None = None,
    background: StateGraph | None = None,
) -> go.Figure:
    """Draw the cycle a pattern walks, with its surroundings when there are any.

    ``traced`` stops the walk after that many throws, so a reader can take the
    cycle a beat at a time; ``None`` lights the whole of it.  The state the walk
    has reached is ringed, which is the only thing that distinguishes it once
    the cycle closes and every state on it is lit.
    """
    if background is not None:
        states = list(background.states)
        floor = _excitation(background.states[background.ground])
        position = background.index
    else:
        states = list(dict.fromkeys(pattern.states))
        floor = _excitation(
            ground_state(
                pattern.objects, pattern.hands, pattern.height, pattern.capacity
            )
        )
        position = {state: index for index, state in enumerate(states)}
    points = layout(states, floor)

    steps = [position[state] for state in pattern.states]
    count = len(steps) if traced is None else max(0, min(traced, len(steps)))
    visited = {steps[step % len(steps)] for step in range(count + 1)}
    current = steps[count % len(steps)]

    lit: list[tuple[int, int, str | None]] = []
    for step in range(count):
        # Stepping a pattern, the throw just made is the one worth naming; the
        # rest of the cycle is drawn and the caption carries the detail.
        named = traced is None or step == count - 1
        lit.append(
            (
                steps[step],
                steps[(step + 1) % len(steps)],
                throw_label(pattern.throws[step], pattern.hands) if named else None,
            )
        )

    figure = go.Figure()
    if background is not None:
        walked = {(source, target) for source, target, _ in lit}
        figure.add_traces(
            _edges(
                [
                    (source, target, label)
                    for (source, target), label in background.pairs.items()
                    if (source, target) not in walked
                ],
                points,
                lit=False,
            )
        )
    figure.add_traces(_edges(lit, points, lit=True))

    labels = [state_label(state) for state in states]
    figure.add_trace(
        go.Scatter(
            x=points[:, 0],
            y=points[:, 1],
            mode="markers+text",
            text=labels,
            textposition="middle right",
            textfont={
                "size": [13 if index in visited else 11 for index in range(len(states))],
                "color": [
                    _ACCENT if index in visited else "rgba(100,116,139,0.45)"
                    for index in range(len(states))
                ],
            },
            marker={
                "size": 14,
                "color": [
                    _ACCENT if index in visited else "rgba(100,116,139,0.22)"
                    for index in range(len(states))
                ],
                "line": {"width": 1.4, "color": _MUTED},
            },
            customdata=[state_label(state) for state in states],
            hovertemplate="%{customdata}<extra></extra>",
            showlegend=False,
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[points[current][0]],
            y=[points[current][1]],
            mode="markers",
            marker={
                "size": 24,
                "color": "rgba(0,0,0,0)",
                "line": {"width": 2.2, "color": _ACCENT},
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    rows = round(abs(points[:, 1].min() - points[:, 1].max()) / 1.5) + 1
    figure.update_layout(
        height=int(np.clip(140 + 62 * rows, 300, 900)),
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": _MUTED},
        uirevision=f"state-graph-{pattern.hands}-{pattern.height}-{pattern.objects}",
        xaxis={"visible": False},
        # Equal scaling keeps the arrowheads pointing where the edges go.
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
    )
    return figure
