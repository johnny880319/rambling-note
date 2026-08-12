"""A fixed, readable simplex-method simulation for the accompanying note.

The linear program is

    maximize 3 x_1 + 2 x_2 + x_3

    subject to x_1 <= 4, x_2 <= 3, x_3 <= 2,
               x_1 + x_2 + x_3 <= 8, and x >= 0.

Each ``SimplexStep`` stores the tableau exactly as it appears at one teaching
step.  The Plotly code below only draws those states; it does not hide a solver
or a geometry package behind the animation.
"""

from dataclasses import dataclass

import plotly.graph_objects as go


@dataclass(frozen=True)
class SimplexStep:
    title: str
    explanation: str
    operation: str
    columns: tuple[str, ...]
    tableau: tuple[tuple[int, ...], ...]
    rhs: tuple[int, ...]
    basis: tuple[str, ...]
    nonbasis: tuple[str, ...]
    point: tuple[int, int, int]
    entering: str | None = None
    leaving: str | None = None
    pivot_row: int | None = None


# The geometry is intentionally written out.  These are the ten vertices and
# fifteen true edges of the feasible polytope; no convex-hull library is needed.
POLYTOPE_VERTICES = (
    (0, 0, 0),
    (4, 0, 0),
    (0, 3, 0),
    (0, 0, 2),
    (4, 3, 0),
    (4, 0, 2),
    (0, 3, 2),
    (4, 3, 1),
    (4, 2, 2),
    (3, 3, 2),
)

POLYTOPE_EDGES = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 4),
    (1, 5),
    (2, 4),
    (2, 6),
    (3, 5),
    (3, 6),
    (4, 7),
    (5, 8),
    (6, 9),
    (7, 8),
    (7, 9),
    (8, 9),
)

SIMPLEX_PATH = (
    (0, 0, 0),
    (4, 0, 0),
    (4, 3, 0),
    (4, 3, 1),
)


# Column order is always: z, four displayed basic slots, three displayed
# non-basic slots.  Between a row operation and its column swap, the newly
# basic column is still sitting in the old non-basic slot; that is deliberate.
SIMPLEX_STEPS = (
    SimplexStep(
        title="初始 canonical form",
        explanation="令非基變數 x₁=x₂=x₃=0，得到起始頂點。",
        operation=r"x_D=(x_1,x_2,x_3)=0",
        columns=("z", "s_1", "s_2", "s_3", "s_4", "x_1", "x_2", "x_3"),
        tableau=(
            (1, 0, 0, 0, 0, -3, -2, -1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 0, 0, 1),
            (0, 0, 0, 0, 1, 1, 1, 1),
        ),
        rhs=(0, 4, 3, 2, 8),
        basis=("s_1", "s_2", "s_3", "s_4"),
        nonbasis=("x_1", "x_2", "x_3"),
        point=(0, 0, 0),
    ),
    SimplexStep(
        title="Pivot 1：高斯消去",
        explanation="x₁ 的 reduced cost 最大；ratio test 選到 s₁ 離基。列運算使 x₁ 欄成為單位向量，點沿著邊移到 (4,0,0)。",
        operation=r"R_z\leftarrow R_z+3R_1,\qquad R_4\leftarrow R_4-R_1",
        columns=("z", "s_1", "s_2", "s_3", "s_4", "x_1", "x_2", "x_3"),
        tableau=(
            (1, 3, 0, 0, 0, 0, -2, -1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 0, 0, 1),
            (0, -1, 0, 0, 1, 0, 1, 1),
        ),
        rhs=(12, 4, 3, 2, 4),
        basis=("x_1", "s_2", "s_3", "s_4"),
        nonbasis=("s_1", "x_2", "x_3"),
        point=(4, 0, 0),
        entering="x_1",
        leaving="s_1",
        pivot_row=1,
    ),
    SimplexStep(
        title="Pivot 1：交換 x₁、s₁ 兩欄",
        explanation="欄交換不改變方程或幾何位置；它只把新基變數重新排回 canonical form 的左半部。",
        operation=r"C_{x_1}\leftrightarrow C_{s_1}",
        columns=("z", "x_1", "s_2", "s_3", "s_4", "s_1", "x_2", "x_3"),
        tableau=(
            (1, 0, 0, 0, 0, 3, -2, -1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 0, 0, 1),
            (0, 0, 0, 0, 1, -1, 1, 1),
        ),
        rhs=(12, 4, 3, 2, 4),
        basis=("x_1", "s_2", "s_3", "s_4"),
        nonbasis=("s_1", "x_2", "x_3"),
        point=(4, 0, 0),
    ),
    SimplexStep(
        title="Pivot 2：高斯消去",
        explanation="x₂ 進基、s₂ 離基。ratio test 比較 3 與 4，因此沿第二條邊走到 (4,3,0)。",
        operation=r"R_z\leftarrow R_z+2R_2,\qquad R_4\leftarrow R_4-R_2",
        columns=("z", "x_1", "s_2", "s_3", "s_4", "s_1", "x_2", "x_3"),
        tableau=(
            (1, 0, 2, 0, 0, 3, 0, -1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 0, 0, 1),
            (0, 0, -1, 0, 1, -1, 0, 1),
        ),
        rhs=(18, 4, 3, 2, 1),
        basis=("x_1", "x_2", "s_3", "s_4"),
        nonbasis=("s_1", "s_2", "x_3"),
        point=(4, 3, 0),
        entering="x_2",
        leaving="s_2",
        pivot_row=2,
    ),
    SimplexStep(
        title="Pivot 2：交換 x₂、s₂ 兩欄",
        explanation="重新排列欄後，前四個變數又構成 identity matrix。",
        operation=r"C_{x_2}\leftrightarrow C_{s_2}",
        columns=("z", "x_1", "x_2", "s_3", "s_4", "s_1", "s_2", "x_3"),
        tableau=(
            (1, 0, 0, 0, 0, 3, 2, -1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 0, 0, 1),
            (0, 0, 0, 0, 1, -1, -1, 1),
        ),
        rhs=(18, 4, 3, 2, 1),
        basis=("x_1", "x_2", "s_3", "s_4"),
        nonbasis=("s_1", "s_2", "x_3"),
        point=(4, 3, 0),
    ),
    SimplexStep(
        title="Pivot 3：高斯消去",
        explanation="x₃ 進基。s₃ 給出的 ratio 是 2，s₄ 給出的是 1，所以 s₄ 離基，點抵達 (4,3,1)。",
        operation=r"R_z\leftarrow R_z+R_4,\qquad R_3\leftarrow R_3-R_4",
        columns=("z", "x_1", "x_2", "s_3", "s_4", "s_1", "s_2", "x_3"),
        tableau=(
            (1, 0, 0, 0, 1, 2, 1, 0),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, -1, 1, 1, 0),
            (0, 0, 0, 0, 1, -1, -1, 1),
        ),
        rhs=(19, 4, 3, 1, 1),
        basis=("x_1", "x_2", "s_3", "x_3"),
        nonbasis=("s_1", "s_2", "s_4"),
        point=(4, 3, 1),
        entering="x_3",
        leaving="s_4",
        pivot_row=4,
    ),
    SimplexStep(
        title="Pivot 3：交換 x₃、s₄ 兩欄（最佳解）",
        explanation="所有非基變數的 reduced costs 都非正，因此目前頂點就是最佳解。",
        operation=r"C_{x_3}\leftrightarrow C_{s_4}",
        columns=("z", "x_1", "x_2", "s_3", "x_3", "s_1", "s_2", "s_4"),
        tableau=(
            (1, 0, 0, 0, 0, 2, 1, 1),
            (0, 1, 0, 0, 0, 1, 0, 0),
            (0, 0, 1, 0, 0, 0, 1, 0),
            (0, 0, 0, 1, 0, 1, 1, -1),
            (0, 0, 0, 0, 1, -1, -1, 1),
        ),
        rhs=(19, 4, 3, 1, 1),
        basis=("x_1", "x_2", "s_3", "x_3"),
        nonbasis=("s_1", "s_2", "s_4"),
        point=(4, 3, 1),
    ),
)


def _math_name(name: str) -> str:
    """Turn ``x_1`` into a small LaTeX fragment."""
    if "_" not in name:
        return name
    symbol, subscript = name.split("_", maxsplit=1)
    return rf"{symbol}_{{{subscript}}}"


def tableau_latex(step_index: int) -> str:
    """Render the current exact tableau as KaTeX-compatible LaTeX."""
    step = SIMPLEX_STEPS[step_index]
    row_names = ("R_z", "R_1", "R_2", "R_3", "R_4")
    column_spec = r"c|c|cccc|ccc|c"

    headers = []
    for name in step.columns:
        label = _math_name(name)
        if name == step.entering:
            label = rf"\color{{orange}}{{\boldsymbol{{{label}}}}}"
        headers.append(label)

    rows = [
        " & " + " & ".join(headers) + r" & \mathrm{RHS} \\",
        r"\hline",
    ]

    for row_index, (values, rhs) in enumerate(zip(step.tableau, step.rhs)):
        row_label = row_names[row_index]
        if row_index == step.pivot_row:
            row_label = rf"\color{{orange}}{{\boldsymbol{{{row_label}}}}}"

        cells = [str(value) for value in values]
        if step.entering is not None and row_index == step.pivot_row:
            pivot_column = step.columns.index(step.entering)
            cells[pivot_column] = rf"\boxed{{{cells[pivot_column]}}}"

        rows.append(row_label + " & " + " & ".join(cells) + f" & {rhs} " + r"\\")
        if row_index == 0:
            rows.append(r"\hline")

    return (
        "$$\n"
        rf"\begin{{array}}{{{column_spec}}}"
        + "\n"
        + "\n".join(rows)
        + "\n"
        + r"\end{array}"
        + "\n$$"
    )


def step_markdown(step_index: int) -> str:
    """Text shown beside the polytope for one teaching step."""
    step = SIMPLEX_STEPS[step_index]
    basis = ", ".join(f"${_math_name(name)}$" for name in step.basis)
    nonbasis = ", ".join(f"${_math_name(name)}$" for name in step.nonbasis)
    x_1, x_2, x_3 = step.point
    objective = 3 * x_1 + 2 * x_2 + x_3

    return f"""
### {step_index + 1}/{len(SIMPLEX_STEPS)}　{step.title}

{step.explanation}

$$
{step.operation}
$$

- 基變數：{basis}
- 非基變數：{nonbasis}
- 目前頂點：$({x_1},{x_2},{x_3})$
- 目標值：$3({x_1})+2({x_2})+({x_3})={objective}$

{tableau_latex(step_index)}
"""


def make_figure(step_index: int) -> go.Figure:
    """Draw the fixed feasible polytope and the path reached so far."""
    step = SIMPLEX_STEPS[step_index]
    vertices_x, vertices_y, vertices_z = zip(*POLYTOPE_VERTICES)

    figure = go.Figure()
    figure.add_trace(
        go.Mesh3d(
            x=vertices_x,
            y=vertices_y,
            z=vertices_z,
            alphahull=0,
            color="#38bdf8",
            opacity=0.16,
            flatshading=True,
            hoverinfo="skip",
            name="可行域",
            showlegend=True,
        )
    )

    edge_x: list[int | None] = []
    edge_y: list[int | None] = []
    edge_z: list[int | None] = []
    for start, end in POLYTOPE_EDGES:
        for coordinate, destination in zip(
            POLYTOPE_VERTICES[start], (edge_x, edge_y, edge_z)
        ):
            destination.append(coordinate)
        for coordinate, destination in zip(
            POLYTOPE_VERTICES[end], (edge_x, edge_y, edge_z)
        ):
            destination.append(coordinate)
        edge_x.append(None)
        edge_y.append(None)
        edge_z.append(None)

    figure.add_trace(
        go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode="lines",
            line={"color": "#0ea5e9", "width": 4},
            hoverinfo="skip",
            name="多面體的邊",
        )
    )

    # The dotted line previews the full route; the orange line is the part
    # actually reached by the current tableau state.
    path_x, path_y, path_z = zip(*SIMPLEX_PATH)
    figure.add_trace(
        go.Scatter3d(
            x=path_x,
            y=path_y,
            z=path_z,
            mode="lines+markers",
            line={"color": "#94a3b8", "width": 3, "dash": "dot"},
            marker={"size": 4, "color": "#94a3b8"},
            hoverinfo="skip",
            name="完整路徑",
        )
    )

    reached_index = SIMPLEX_PATH.index(step.point)
    reached_path = SIMPLEX_PATH[: reached_index + 1]
    reached_x, reached_y, reached_z = zip(*reached_path)
    figure.add_trace(
        go.Scatter3d(
            x=reached_x,
            y=reached_y,
            z=reached_z,
            mode="lines+markers",
            line={"color": "#f97316", "width": 8},
            marker={"size": 6, "color": "#f97316"},
            hovertemplate="(%{x}, %{y}, %{z})<extra></extra>",
            name="已走路徑",
        )
    )

    point_x, point_y, point_z = step.point
    figure.add_trace(
        go.Scatter3d(
            x=[point_x],
            y=[point_y],
            z=[point_z],
            mode="markers+text",
            marker={"size": 10, "color": "#ea580c"},
            text=[f"z={3 * point_x + 2 * point_y + point_z}"],
            textposition="top center",
            hovertemplate="目前頂點 (%{x}, %{y}, %{z})<extra></extra>",
            name="目前頂點",
        )
    )

    # The objective gradient is always (3, 2, 1).  Starting the cone at the
    # current point makes the algebraic improvement direction visible.
    figure.add_trace(
        go.Cone(
            x=[point_x],
            y=[point_y],
            z=[point_z],
            u=[3],
            v=[2],
            w=[1],
            anchor="tail",
            sizemode="absolute",
            sizeref=0.8,
            colorscale=[[0, "#22c55e"], [1, "#22c55e"]],
            showscale=False,
            hovertemplate="∇f=(3,2,1)<extra></extra>",
            name="目標函數梯度",
        )
    )

    figure.update_layout(
        height=590,
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#64748b"},
        legend={"orientation": "h", "y": -0.05, "x": 0},
        uirevision="fixed-simplex-example",
        scene={
            "xaxis": {"title": "x₁", "range": [-0.25, 4.8]},
            "yaxis": {"title": "x₂", "range": [-0.25, 3.8]},
            "zaxis": {"title": "x₃", "range": [-0.15, 2.8]},
            "aspectmode": "manual",
            "aspectratio": {"x": 1.35, "y": 1.0, "z": 0.8},
            "camera": {"eye": {"x": 1.55, "y": 1.55, "z": 1.15}},
        },
    )
    return figure
