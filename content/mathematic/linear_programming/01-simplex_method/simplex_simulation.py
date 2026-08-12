"""Small, readable 3D simplex-method simulator used by the note.

The module deliberately supports one teaching-friendly input format:

* exactly three decision variables;
* maximization problems;
* constraints of the form ``a1, a2, a3 <= b`` with ``b >= 0``;
* the non-negativity constraints ``x >= 0`` are added automatically.

Keeping the scope small lets the code show the actual tableau operations rather
than hiding them behind an optimization or computational-geometry library.
"""

import math
import re
from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import combinations

import numpy as np
import plotly.graph_objects as go

TOLERANCE = 1e-9
MAX_CONSTRAINTS = 8
MAX_PIVOTS = 50

DEFAULT_OBJECTIVE = "3, 2, 1"
DEFAULT_CONSTRAINTS = """1, 0, 0 <= 4
0, 1, 0 <= 3
0, 0, 1 <= 2
1, 1, 1 <= 8"""


@dataclass(frozen=True)
class LinearProgram:
    objective: tuple[float, float, float]
    constraints: tuple[tuple[float, float, float, float], ...]


@dataclass(frozen=True)
class SimplexStep:
    title: str
    explanation: str
    operation: str
    columns: tuple[str, ...]
    tableau: tuple[tuple[float, ...], ...]
    rhs: tuple[float, ...]
    basis: tuple[str, ...]
    nonbasis: tuple[str, ...]
    point: tuple[float, float, float]
    entering: str | None = None
    leaving: str | None = None
    pivot_row: int | None = None


@dataclass(frozen=True)
class SimplexSimulation:
    program: LinearProgram
    steps: tuple[SimplexStep, ...]
    vertices: tuple[tuple[float, float, float], ...]
    edges: tuple[tuple[int, int], ...]
    path: tuple[tuple[float, float, float], ...]


def _parse_numbers(text: str) -> tuple[float, ...]:
    pieces = [piece for piece in re.split(r"[\s,]+", text.strip()) if piece]
    try:
        values = tuple(float(piece) for piece in pieces)
    except ValueError as error:
        raise ValueError(f"無法解析數字：{text}") from error

    if not all(math.isfinite(value) for value in values):
        raise ValueError("係數必須是有限的數字。")
    return values


def parse_linear_program(
    objective_text: str,
    constraints_text: str,
) -> LinearProgram:
    """Parse the two text fields shown in the Marimo notebook."""
    objective = _parse_numbers(objective_text)
    if len(objective) != 3:
        raise ValueError("目標係數必須剛好有三個數字。")
    if np.linalg.norm(objective) <= TOLERANCE:
        raise ValueError("目標向量不能是零向量。")

    constraints: list[tuple[float, float, float, float]] = []
    for line_number, raw_line in enumerate(constraints_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        parts = re.split(r"<=|≤", line)
        if len(parts) != 2:
            raise ValueError(f"限制式第 {line_number} 行必須使用 `a1, a2, a3 <= b`。")

        coefficients = _parse_numbers(parts[0])
        rhs_values = _parse_numbers(parts[1])
        if len(coefficients) != 3 or len(rhs_values) != 1:
            raise ValueError(f"限制式第 {line_number} 行需要三個係數與一個常數項。")

        rhs = rhs_values[0]
        if rhs < -TOLERANCE:
            raise ValueError(
                f"限制式第 {line_number} 行的 b 必須非負，才能由 slack variables 得到初始 basis。"
            )
        constraints.append((*coefficients, max(0.0, rhs)))

    if not constraints:
        raise ValueError("請至少輸入一條限制式。")
    if len(constraints) > MAX_CONSTRAINTS:
        raise ValueError(
            f"為了保持 tableau 可讀，目前最多支援 {MAX_CONSTRAINTS} 條限制式。"
        )

    return LinearProgram(
        objective=objective,  # type: ignore[arg-type]
        constraints=tuple(constraints),
    )


def _clean(value: float) -> float:
    return 0.0 if abs(value) <= TOLERANCE else float(value)


def _clean_matrix(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(_clean(value) for value in row) for row in matrix)


def _clean_vector(vector: np.ndarray) -> tuple[float, ...]:
    return tuple(_clean(value) for value in vector)


def _point_from_basis(
    basis: list[str],
    rhs: np.ndarray,
) -> tuple[float, float, float]:
    values = {name: rhs[row + 1] for row, name in enumerate(basis)}
    return tuple(_clean(values.get(f"x_{index}", 0.0)) for index in range(1, 4))  # type: ignore[return-value]


def _plain_number(value: float) -> str:
    value = _clean(value)
    if math.isclose(value, round(value), abs_tol=TOLERANCE):
        return str(round(value))
    return f"{value:.4g}"


def _latex_number(value: float) -> str:
    value = _clean(value)
    if math.isclose(value, round(value), abs_tol=TOLERANCE):
        return str(round(value))

    fraction = Fraction(value).limit_denominator(100)
    if math.isclose(float(fraction), value, abs_tol=1e-8):
        sign = "-" if fraction.numerator < 0 else ""
        return rf"{sign}\frac{{{abs(fraction.numerator)}}}{{{fraction.denominator}}}"
    return f"{value:.4g}"


def _row_name(row: int) -> str:
    return "R_z" if row == 0 else f"R_{row}"


def _elimination_operation(
    tableau: np.ndarray,
    pivot_row: int,
    pivot_column: int,
) -> str:
    pivot = tableau[pivot_row, pivot_column]
    operations: list[str] = []
    if not math.isclose(pivot, 1.0, abs_tol=TOLERANCE):
        operations.append(
            rf"{_row_name(pivot_row)}\leftarrow "
            rf"\frac{{1}}{{{_latex_number(pivot)}}}{_row_name(pivot_row)}"
        )

    for row in range(tableau.shape[0]):
        if row == pivot_row or abs(tableau[row, pivot_column]) <= TOLERANCE:
            continue
        coefficient = tableau[row, pivot_column]
        sign = "-" if coefficient > 0 else "+"
        magnitude = abs(coefficient)
        multiplier = "" if math.isclose(magnitude, 1.0) else _latex_number(magnitude)
        operations.append(
            rf"{_row_name(row)}\leftarrow {_row_name(row)}"
            rf"{sign}{multiplier}{_row_name(pivot_row)}"
        )
    return r",\qquad ".join(operations)


def _calculate_steps(program: LinearProgram) -> tuple[SimplexStep, ...]:
    constraints = np.asarray(program.constraints, dtype=float)
    objective = np.asarray(program.objective, dtype=float)
    matrix = constraints[:, :3]
    rhs = np.concatenate(([0.0], constraints[:, 3]))
    constraint_count = len(constraints)

    tableau = np.zeros((constraint_count + 1, constraint_count + 4))
    tableau[0, 0] = 1.0
    tableau[0, 1 + constraint_count :] = -objective
    tableau[1:, 1 : 1 + constraint_count] = np.eye(constraint_count)
    tableau[1:, 1 + constraint_count :] = matrix

    basis = [f"s_{index}" for index in range(1, constraint_count + 1)]
    nonbasis = ["x_1", "x_2", "x_3"]
    columns = ["z", *basis, *nonbasis]
    steps = [
        SimplexStep(
            title="初始 canonical form",
            explanation="令所有非基變數為 0；slack variables 直接給出起始頂點。",
            operation=r"x_D=0",
            columns=tuple(columns),
            tableau=_clean_matrix(tableau),
            rhs=_clean_vector(rhs),
            basis=tuple(basis),
            nonbasis=tuple(nonbasis),
            point=_point_from_basis(basis, rhs),
        )
    ]

    for pivot_number in range(1, MAX_PIVOTS + 1):
        nonbasic_positions = range(1 + constraint_count, tableau.shape[1])
        candidates = [
            column for column in nonbasic_positions if tableau[0, column] < -TOLERANCE
        ]
        if not candidates:
            final_step = steps[-1]
            steps[-1] = replace(
                final_step,
                title=final_step.title + "（最佳解）",
                explanation=(
                    final_step.explanation
                    + " 所有非基變數的 reduced costs 都非正，因此目前頂點是最佳解。"
                ),
            )
            return tuple(steps)

        # Choose the most negative objective-row coefficient.  Ties follow the
        # displayed column order, keeping the route deterministic.
        pivot_column = min(candidates, key=lambda column: tableau[0, column])
        entering = columns[pivot_column]
        valid_rows = [
            row
            for row in range(1, constraint_count + 1)
            if tableau[row, pivot_column] > TOLERANCE
        ]
        if not valid_rows:
            raise ValueError(f"{entering} 可以無限增加，因此目標函數無界。")

        ratios = {row: rhs[row] / tableau[row, pivot_column] for row in valid_rows}
        pivot_row = min(valid_rows, key=lambda row: (ratios[row], row))
        leaving = basis[pivot_row - 1]
        operation = _elimination_operation(tableau, pivot_row, pivot_column)

        pivot = tableau[pivot_row, pivot_column]
        tableau[pivot_row] /= pivot
        rhs[pivot_row] /= pivot
        for row in range(constraint_count + 1):
            if row == pivot_row:
                continue
            factor = tableau[row, pivot_column]
            tableau[row] -= factor * tableau[pivot_row]
            rhs[row] -= factor * rhs[pivot_row]

        basis[pivot_row - 1] = entering
        entering_index = nonbasis.index(entering)
        nonbasis[entering_index] = leaving
        point = _point_from_basis(basis, rhs)
        ratio_text = ", ".join(_plain_number(ratios[row]) for row in valid_rows)

        steps.append(
            SimplexStep(
                title=f"Pivot {pivot_number}：高斯消去",
                explanation=(
                    f"{entering} 進基、{leaving} 離基；ratio test 的候選值為 "
                    f"{ratio_text}。列運算後，幾何上的點移到 "
                    f"({', '.join(_plain_number(value) for value in point)})。"
                ),
                operation=operation,
                columns=tuple(columns),
                tableau=_clean_matrix(tableau),
                rhs=_clean_vector(rhs),
                basis=tuple(basis),
                nonbasis=tuple(nonbasis),
                point=point,
                entering=entering,
                leaving=leaving,
                pivot_row=pivot_row,
            )
        )

        leaving_column = pivot_row
        tableau[:, [leaving_column, pivot_column]] = tableau[
            :, [pivot_column, leaving_column]
        ]
        columns[leaving_column], columns[pivot_column] = (
            columns[pivot_column],
            columns[leaving_column],
        )

        steps.append(
            SimplexStep(
                title=f"Pivot {pivot_number}：交換 {entering}、{leaving} 兩欄",
                explanation="交換欄不改變方程與幾何位置，只把新基變數排回 identity matrix 的區塊。",
                operation=rf"C_{{{entering}}}\leftrightarrow C_{{{leaving}}}",
                columns=tuple(columns),
                tableau=_clean_matrix(tableau),
                rhs=_clean_vector(rhs),
                basis=tuple(basis),
                nonbasis=tuple(nonbasis),
                point=point,
            )
        )

    raise ValueError(f"超過 {MAX_PIVOTS} 次 pivot；這個例子可能發生 cycling。")


def _enumerate_vertices(
    program: LinearProgram,
) -> tuple[tuple[float, float, float], ...]:
    constraints = np.asarray(program.constraints, dtype=float)
    matrix = constraints[:, :3]
    bounds = constraints[:, 3]

    # Include x_i = 0 as three possible boundary planes.
    plane_normals = [*matrix, *np.eye(3)]
    plane_values = [*bounds, 0.0, 0.0, 0.0]
    vertices: list[np.ndarray] = []

    for plane_indices in combinations(range(len(plane_normals)), 3):
        normals = np.asarray([plane_normals[index] for index in plane_indices])
        if np.linalg.matrix_rank(normals, tol=TOLERANCE) < 3:
            continue
        values = np.asarray([plane_values[index] for index in plane_indices])
        point = np.linalg.solve(normals, values)
        if np.any(point < -TOLERANCE) or np.any(matrix @ point - bounds > TOLERANCE):
            continue
        point[np.abs(point) <= TOLERANCE] = 0.0
        if not any(np.linalg.norm(point - known) <= 1e-7 for known in vertices):
            vertices.append(point)

    if (
        len(vertices) < 4
        or np.linalg.matrix_rank(np.asarray(vertices[1:]) - vertices[0], tol=TOLERANCE)
        < 3
    ):
        raise ValueError("可行域不是有體積的三維多面體，目前無法用 3D Mesh 顯示。")

    return tuple(tuple(float(value) for value in vertex) for vertex in vertices)  # type: ignore[return-value]


def _polytope_edges(
    program: LinearProgram,
    vertices: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[int, int], ...]:
    constraints = np.asarray(program.constraints, dtype=float)
    normals = np.vstack((constraints[:, :3], np.eye(3)))
    values = np.concatenate((constraints[:, 3], np.zeros(3)))
    points = np.asarray(vertices)

    active_sets = [
        {
            plane
            for plane, (normal, value) in enumerate(zip(normals, values))
            if abs(normal @ point - value) <= 1e-7
        }
        for point in points
    ]
    edges: list[tuple[int, int]] = []

    for start, end in combinations(range(len(vertices)), 2):
        shared = active_sets[start] & active_sets[end]
        if len(shared) < 2 or np.linalg.matrix_rank(normals[list(shared)]) < 2:
            continue

        # Do not draw a long segment across another collinear vertex.
        segment = points[end] - points[start]
        segment_length_squared = segment @ segment
        has_middle_vertex = False
        for middle in range(len(vertices)):
            if middle in (start, end):
                continue
            relative = points[middle] - points[start]
            parameter = (relative @ segment) / segment_length_squared
            if (
                1e-7 < parameter < 1 - 1e-7
                and np.linalg.norm(relative - parameter * segment) <= 1e-7
            ):
                has_middle_vertex = True
                break
        if not has_middle_vertex:
            edges.append((start, end))
    return tuple(edges)


def build_simulation(program: LinearProgram) -> SimplexSimulation:
    """Solve the LP and prepare matching algebraic and geometric states."""
    steps = _calculate_steps(program)

    # A 3D mesh needs a bounded feasible set.  A nonnegative polyhedron is
    # bounded exactly when each coordinate has a finite maximum.
    for coordinate in range(3):
        objective = tuple(1.0 if index == coordinate else 0.0 for index in range(3))
        try:
            _calculate_steps(
                LinearProgram(
                    objective=objective,  # type: ignore[arg-type]
                    constraints=program.constraints,
                )
            )
        except ValueError as error:
            raise ValueError("可行域無界，無法畫成封閉的三維多面體。") from error

    vertices = _enumerate_vertices(program)
    edges = _polytope_edges(program, vertices)
    path: list[tuple[float, float, float]] = []
    for step in steps:
        if not path or not np.allclose(step.point, path[-1], atol=TOLERANCE):
            path.append(step.point)

    return SimplexSimulation(
        program=program,
        steps=steps,
        vertices=vertices,
        edges=edges,
        path=tuple(path),
    )


def _math_name(name: str) -> str:
    if "_" not in name:
        return name
    symbol, subscript = name.split("_", maxsplit=1)
    return rf"{symbol}_{{{subscript}}}"


def tableau_latex(simulation: SimplexSimulation, step_index: int) -> str:
    step = simulation.steps[step_index]
    constraint_count = len(simulation.program.constraints)
    row_names = ("R_z", *(f"R_{index}" for index in range(1, constraint_count + 1)))
    column_spec = "c|c|" + "c" * constraint_count + "|ccc|c"

    headers: list[str] = []
    for name in step.columns:
        label = _math_name(name)
        if name == step.entering:
            label = rf"\color{{orange}}{{\boldsymbol{{{label}}}}}"
        headers.append(label)

    rows = [" & " + " & ".join(headers) + r" & \mathrm{RHS} \\", r"\hline"]
    for row_index, (values, rhs) in enumerate(zip(step.tableau, step.rhs)):
        row_label = row_names[row_index]
        if row_index == step.pivot_row:
            row_label = rf"\color{{orange}}{{\boldsymbol{{{row_label}}}}}"

        cells = [_latex_number(value) for value in values]
        if step.entering is not None and row_index == step.pivot_row:
            pivot_column = step.columns.index(step.entering)
            cells[pivot_column] = rf"\boxed{{{cells[pivot_column]}}}"

        rows.append(
            row_label + " & " + " & ".join(cells) + f" & {_latex_number(rhs)} " + r"\\"
        )
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


def step_markdown(simulation: SimplexSimulation, step_index: int) -> str:
    step = simulation.steps[step_index]
    basis = ", ".join(f"${_math_name(name)}$" for name in step.basis)
    nonbasis = ", ".join(f"${_math_name(name)}$" for name in step.nonbasis)
    point = np.asarray(step.point)
    objective = np.asarray(simulation.program.objective)
    objective_value = objective @ point

    return f"""
### {step_index + 1}/{len(simulation.steps)}　{step.title}

{step.explanation}

$$
{step.operation}
$$

- 基變數：{basis}
- 非基變數：{nonbasis}
- 目前頂點：$({", ".join(_latex_number(value) for value in point)})$
- 目標值：${_latex_number(objective_value)}$

{tableau_latex(simulation, step_index)}
"""


def _linear_expression(coefficients: tuple[float, ...]) -> str:
    """Format a short linear expression without noisy 0 or 1 coefficients."""
    pieces: list[str] = []
    for index, coefficient in enumerate(coefficients, start=1):
        coefficient = _clean(coefficient)
        if coefficient == 0:
            continue

        magnitude = abs(coefficient)
        factor = "" if math.isclose(magnitude, 1.0) else _latex_number(magnitude)
        term = rf"{factor}x_{{{index}}}"
        if not pieces:
            pieces.append(("-" if coefficient < 0 else "") + term)
        else:
            pieces.append((" - " if coefficient < 0 else " + ") + term)
    return "".join(pieces) or "0"


def program_markdown(simulation: SimplexSimulation) -> str:
    objective = simulation.program.objective
    constraint_lines = []
    for index, constraint in enumerate(simulation.program.constraints):
        coefficients = constraint[:3]
        ending = r" \\" if index < len(simulation.program.constraints) - 1 else ""
        constraint_lines.append(
            "        & "
            + _linear_expression(coefficients)
            + rf"\leq {_latex_number(constraint[3])}{ending}"
        )

    return (
        "$$\n"
        "\\begin{aligned}\n"
        "\\text{maximize}\\quad & "
        + _linear_expression(objective)
        + r" \\"
        + "\n\\text{subject to}\\quad\n"
        + "\n".join(constraint_lines)
        + r" \\"
        + "\n        & x_1,x_2,x_3\\geq0.\n"
        "\\end{aligned}\n"
        "$$"
    )


def _arrow_head(
    tip: np.ndarray,
    direction: np.ndarray,
    length: float,
    width: float,
) -> tuple[np.ndarray, tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Build a small square pyramid pointing along a 3D direction."""
    reference = np.array([0.0, 0.0, 1.0])
    if abs(direction @ reference) > 0.9:
        reference = np.array([0.0, 1.0, 0.0])

    side_1 = np.cross(direction, reference)
    side_1 /= np.linalg.norm(side_1)
    side_2 = np.cross(direction, side_1)
    base = tip - length * direction
    corners = (
        base + width * side_1 + width * side_2,
        base - width * side_1 + width * side_2,
        base - width * side_1 - width * side_2,
        base + width * side_1 - width * side_2,
    )
    vertices = np.vstack((tip, corners))

    # Four triangular sides plus two triangles closing the square base.
    return (
        vertices,
        (0, 0, 0, 0, 1, 1),
        (1, 2, 3, 4, 2, 3),
        (2, 3, 4, 1, 3, 4),
    )


def make_figure(simulation: SimplexSimulation, step_index: int) -> go.Figure:
    step = simulation.steps[step_index]
    vertices = simulation.vertices
    vertices_x, vertices_y, vertices_z = zip(*vertices)
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
        )
    )

    edge_coordinates: tuple[list[float | None], ...] = ([], [], [])
    for start, end in simulation.edges:
        for axis, destination in enumerate(edge_coordinates):
            destination.extend((vertices[start][axis], vertices[end][axis], None))
    figure.add_trace(
        go.Scatter3d(
            x=edge_coordinates[0],
            y=edge_coordinates[1],
            z=edge_coordinates[2],
            mode="lines",
            line={"color": "#0ea5e9", "width": 4},
            hoverinfo="skip",
            name="多面體的邊",
        )
    )

    path_x, path_y, path_z = zip(*simulation.path)
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

    reached_index = next(
        index
        for index, point in enumerate(simulation.path)
        if np.allclose(point, step.point, atol=TOLERANCE)
    )
    reached_path = simulation.path[: reached_index + 1]
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
    objective_value = np.asarray(simulation.program.objective) @ np.asarray(step.point)
    figure.add_trace(
        go.Scatter3d(
            x=[point_x],
            y=[point_y],
            z=[point_z],
            mode="markers+text",
            marker={"size": 10, "color": "#ea580c"},
            text=[f"z={_plain_number(objective_value)}"],
            textposition="top center",
            hovertemplate="目前頂點 (%{x}, %{y}, %{z})<extra></extra>",
            name="目前頂點",
        )
    )

    gradient = np.asarray(simulation.program.objective, dtype=float)
    gradient /= np.linalg.norm(gradient)
    plot_scale = max(max(vertices_x), max(vertices_y), max(vertices_z), 1.0)
    arrow_length = plot_scale * 0.25
    arrow_tip = np.asarray(step.point) + arrow_length * gradient
    head_length = arrow_length * 0.24
    head_width = arrow_length * 0.075
    arrow_vertices, arrow_i, arrow_j, arrow_k = _arrow_head(
        arrow_tip,
        gradient,
        head_length,
        head_width,
    )
    shaft_end = arrow_tip - head_length * gradient

    figure.add_trace(
        go.Scatter3d(
            x=[point_x, shaft_end[0]],
            y=[point_y, shaft_end[1]],
            z=[point_z, shaft_end[2]],
            mode="lines",
            line={"color": "#22c55e", "width": 7},
            hovertemplate=(
                "∇f=("
                + ", ".join(
                    _plain_number(value) for value in simulation.program.objective
                )
                + ")<extra></extra>"
            ),
            name="目標函數梯度",
        )
    )
    figure.add_trace(
        go.Mesh3d(
            x=arrow_vertices[:, 0],
            y=arrow_vertices[:, 1],
            z=arrow_vertices[:, 2],
            i=arrow_i,
            j=arrow_j,
            k=arrow_k,
            color="#22c55e",
            flatshading=True,
            hoverinfo="skip",
            showlegend=False,
            name="梯度箭頭",
        )
    )

    maxima = np.maximum(np.max(np.asarray(vertices), axis=0), 1.0)
    all_arrow_tips = np.asarray(simulation.path) + arrow_length * gradient
    display_points = np.vstack((np.asarray(vertices), all_arrow_tips))
    display_minima = np.min(display_points, axis=0)
    display_maxima = np.max(display_points, axis=0)
    display_padding = np.maximum(0.06 * (display_maxima - display_minima), 0.05)
    figure.update_layout(
        height=590,
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#64748b"},
        legend={"orientation": "h", "y": -0.05, "x": 0},
        uirevision="simplex-user-input",
        scene={
            "xaxis": {
                "title": "x₁",
                "range": [
                    min(-0.05 * maxima[0], display_minima[0] - display_padding[0]),
                    max(1.15 * maxima[0], display_maxima[0] + display_padding[0]),
                ],
            },
            "yaxis": {
                "title": "x₂",
                "range": [
                    min(-0.05 * maxima[1], display_minima[1] - display_padding[1]),
                    max(1.15 * maxima[1], display_maxima[1] + display_padding[1]),
                ],
            },
            "zaxis": {
                "title": "x₃",
                "range": [
                    min(-0.05 * maxima[2], display_minima[2] - display_padding[2]),
                    max(1.15 * maxima[2], display_maxima[2] + display_padding[2]),
                ],
            },
            "aspectmode": "data",
            "camera": {"eye": {"x": 1.55, "y": 1.55, "z": 1.15}},
        },
    )
    return figure


DEFAULT_SIMULATION = build_simulation(
    parse_linear_program(DEFAULT_OBJECTIVE, DEFAULT_CONSTRAINTS)
)
