"""Small, readable 3D simplex-method simulator used by the note.

The module deliberately supports one teaching-friendly input format:

* exactly three decision variables;
* maximization problems;
* constraints of the form ``A1, A2, A3 <= b`` (``>=`` and ``=`` also work);
* the non-negativity constraints ``x >= 0`` are added automatically.

Constraints that do not hand us a basic feasible solution for free get an
artificial variable, so the simulation walks through the full two-phase method
described in the note: phase one drives the artificials to zero, any artificial
still stuck in the basis is expelled, the original objective is restored, and
phase two optimises.

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

PHASE_ONE = "phase-one"
PHASE_EXPEL = "expel"
PHASE_RESTORE = "restore"
PHASE_TWO = "phase-two"

# Chosen so both phases do real work: phase one needs three pivots to walk in
# from the outside, and phase two needs three more to reach the optimum.
DEFAULT_OBJECTIVE = "4, 2, 5"
DEFAULT_CONSTRAINTS = """1, 0, 0 <= 6
0, 1, 0 <= 3
0, 0, 1 <= 3
1, 2, 2 <= 10
2, 1, 1 >= 5
0, 1, 1 >= 4"""

# Each preset exercises a different branch of the method.  An artificial can
# only stay basic when the rows pin a direction exactly, which also flattens the
# feasible set, so those presets trade the solid body for the expulsion steps.
PRESETS: dict[str, tuple[str, str]] = {
    "兩階段各走三步（立體可行域）": (DEFAULT_OBJECTIVE, DEFAULT_CONSTRAINTS),
    "人工變數卡在基底，需要逐出與刪列": (
        "2, 3, 1",
        "1, 0, 0 <= 3\n0, 1, 0 <= 3\n0, 0, 1 <= 6\n1, 0, 0 = 3\n2, 0, 0 = 6\n0, 2, 2 >= 3",
    ),
    "沒有可行解（phase one 停在負值）": (
        "1, 1, 1",
        "1, 0, 0 <= 2\n0, 1, 0 <= 2\n0, 0, 1 <= 2\n1, 1, 1 <= 1\n1, 1, 1 >= 5",
    ),
    "全是 ≤，不需要 phase one": (
        "3, 2, 1",
        "1, 0, 0 <= 4\n0, 1, 0 <= 3\n0, 0, 1 <= 2\n1, 1, 1 <= 8",
    ),
}


@dataclass(frozen=True)
class Constraint:
    coefficients: tuple[float, float, float]
    sense: str
    rhs: float


@dataclass(frozen=True)
class LinearProgram:
    objective: tuple[float, float, float]
    constraints: tuple[Constraint, ...]

    @property
    def needs_phase_one(self) -> bool:
        return any(constraint.sense != "<=" for constraint in self.constraints)


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
    row_labels: tuple[str, ...]
    point: tuple[float, float, float]
    phase: str
    feasible: bool
    arrow: tuple[float, float, float]
    arrow_kind: str
    violated: tuple[int, ...]
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
    path_feasible: tuple[bool, ...]
    infeasible: bool
    solid: bool


class InfeasibleProgram(ValueError):
    """Phase one finished with a negative optimum: no feasible point exists."""


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

    constraints: list[Constraint] = []
    for line_number, raw_line in enumerate(constraints_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        match = re.split(r"(<=|≤|>=|≥|=)", line, maxsplit=1)
        if len(match) != 3:
            raise ValueError(
                f"限制式第 {line_number} 行必須使用 `A1, A2, A3 <= b`（也支援 >= 與 =）。"
            )

        left, raw_sense, right = match
        sense = {"≤": "<=", "≥": ">="}.get(raw_sense, raw_sense)

        coefficients = _parse_numbers(left)
        rhs_values = _parse_numbers(right)
        if len(coefficients) != 3 or len(rhs_values) != 1:
            raise ValueError(f"限制式第 {line_number} 行需要三個係數與一個常數項。")
        if np.linalg.norm(coefficients) <= TOLERANCE:
            raise ValueError(f"限制式第 {line_number} 行的係數不能全為 0。")

        rhs = rhs_values[0]
        # Normalise to a non-negative right-hand side; negating a row flips the
        # inequality, which is exactly the reduction described in the note.
        if rhs < -TOLERANCE:
            coefficients = tuple(-value for value in coefficients)
            rhs = -rhs
            sense = {"<=": ">=", ">=": "<="}.get(sense, sense)

        constraints.append(
            Constraint(
                coefficients=coefficients,  # type: ignore[arg-type]
                sense=sense,
                rhs=max(0.0, rhs),
            )
        )

    if not constraints:
        raise ValueError("請至少輸入一條限制式。")
    if len(constraints) > MAX_CONSTRAINTS:
        raise ValueError(
            f"為了保持 tableau 可讀，目前最多支援 {MAX_CONSTRAINTS} 條限制式。"
        )

    return LinearProgram(objective=objective, constraints=tuple(constraints))  # type: ignore[arg-type]


def _clean(value: float) -> float:
    return 0.0 if abs(value) <= TOLERANCE else float(value)


def _clean_matrix(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(_clean(value) for value in row) for row in matrix)


def _clean_vector(vector: np.ndarray) -> tuple[float, ...]:
    return tuple(_clean(value) for value in vector)


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


def _math_name(name: str) -> str:
    if "_" not in name:
        return name
    symbol, subscript = name.split("_", maxsplit=1)
    return rf"{symbol}_{{{subscript}}}"


def _is_artificial(name: str) -> bool:
    return name.startswith("a_")


class _Tableau:
    """Mutable tableau kept in canonical form: basic columns form an identity.

    Column 0 holds ``z``; columns ``1 .. len(variables)`` follow ``variables``,
    whose first ``len(basis)`` entries are the basic variables in row order.
    """

    def __init__(
        self,
        matrix: np.ndarray,
        rhs: np.ndarray,
        variables: list[str],
        basis: list[str],
        row_labels: list[str],
    ) -> None:
        self.matrix = matrix
        self.rhs = rhs
        self.variables = variables
        self.basis = basis
        self.row_labels = row_labels

    @property
    def nonbasis(self) -> list[str]:
        return self.variables[len(self.basis) :]

    @property
    def columns(self) -> list[str]:
        return ["z", *self.variables]

    def column_of(self, name: str) -> int:
        return 1 + self.variables.index(name)

    def point(self) -> tuple[float, float, float]:
        values = {name: self.rhs[row + 1] for row, name in enumerate(self.basis)}
        return tuple(  # type: ignore[return-value]
            _clean(values.get(f"x_{index}", 0.0)) for index in range(1, 4)
        )

    def eliminate_into_objective(self, row: int, factor: float) -> None:
        self.matrix[0] -= factor * self.matrix[row]
        self.rhs[0] -= factor * self.rhs[row]

    def pivot(self, pivot_row: int, pivot_column: int) -> None:
        pivot = self.matrix[pivot_row, pivot_column]
        self.matrix[pivot_row] /= pivot
        self.rhs[pivot_row] /= pivot
        for row in range(self.matrix.shape[0]):
            if row == pivot_row:
                continue
            factor = self.matrix[row, pivot_column]
            if abs(factor) <= TOLERANCE:
                continue
            self.matrix[row] -= factor * self.matrix[pivot_row]
            self.rhs[row] -= factor * self.rhs[pivot_row]

    def swap_into_basis(self, pivot_row: int, pivot_column: int) -> None:
        """Move the entering column into the identity block of ``pivot_row``."""
        entering = self.variables[pivot_column - 1]
        basis_column = pivot_row  # identity block starts at variable index 0
        self.matrix[:, [basis_column, pivot_column]] = self.matrix[
            :, [pivot_column, basis_column]
        ]
        self.variables[basis_column - 1], self.variables[pivot_column - 1] = (
            self.variables[pivot_column - 1],
            self.variables[basis_column - 1],
        )
        self.basis[pivot_row - 1] = entering

    def drop_row(self, row: int) -> None:
        basic_name = self.basis[row - 1]
        column = self.column_of(basic_name)
        self.matrix = np.delete(np.delete(self.matrix, row, axis=0), column, axis=1)
        self.rhs = np.delete(self.rhs, row)
        self.variables.pop(column - 1)
        self.basis.pop(row - 1)
        self.row_labels.pop(row)

    def drop_variables(self, names: list[str]) -> None:
        for name in names:
            column = self.column_of(name)
            self.matrix = np.delete(self.matrix, column, axis=1)
            self.variables.pop(column - 1)


def _build_initial_tableau(program: LinearProgram) -> tuple[_Tableau, list[str]]:
    """Add slack/surplus and artificial variables, keeping ``b >= 0``."""
    count = len(program.constraints)
    slacks: list[str] = []
    artificials: list[str] = []
    basis: list[str] = []

    for index, constraint in enumerate(program.constraints, start=1):
        if constraint.sense == "=":
            artificials.append(f"a_{index}")
            basis.append(f"a_{index}")
            continue

        slacks.append(f"s_{index}")
        if constraint.sense == "<=":
            basis.append(f"s_{index}")
        else:
            artificials.append(f"a_{index}")
            basis.append(f"a_{index}")

    decisions = ["x_1", "x_2", "x_3"]
    # Basic columns first so the identity block sits where the note draws it.
    variables = [*basis, *[name for name in slacks if name not in basis], *decisions]
    variables += [name for name in artificials if name not in basis]

    matrix = np.zeros((count + 1, 1 + len(variables)))
    rhs = np.zeros(count + 1)
    matrix[0, 0] = 1.0

    index_of = {name: 1 + position for position, name in enumerate(variables)}
    for row, constraint in enumerate(program.constraints, start=1):
        for offset, coefficient in enumerate(constraint.coefficients):
            matrix[row, index_of[f"x_{offset + 1}"]] = coefficient
        if constraint.sense == "<=":
            matrix[row, index_of[f"s_{row}"]] = 1.0
        elif constraint.sense == ">=":
            matrix[row, index_of[f"s_{row}"]] = -1.0
            matrix[row, index_of[f"a_{row}"]] = 1.0
        else:
            matrix[row, index_of[f"a_{row}"]] = 1.0
        rhs[row] = constraint.rhs

    row_labels = ["R_z", *(f"R_{index}" for index in range(1, count + 1))]
    tableau = _Tableau(matrix, rhs, variables, basis, row_labels)
    return tableau, artificials


def _set_objective_row(tableau: _Tableau, coefficients: dict[str, float]) -> None:
    """Write ``z - c^T v = 0`` into row 0 without restoring canonical form."""
    tableau.matrix[0, :] = 0.0
    tableau.matrix[0, 0] = 1.0
    for name, coefficient in coefficients.items():
        tableau.matrix[0, tableau.column_of(name)] = -coefficient
    tableau.rhs[0] = 0.0


def _make_canonical(tableau: _Tableau) -> None:
    """Zero the objective row on every basic column."""
    for row, name in enumerate(tableau.basis, start=1):
        factor = tableau.matrix[0, tableau.column_of(name)]
        if abs(factor) > TOLERANCE:
            tableau.eliminate_into_objective(row, factor)


def _elimination_operation(
    tableau: _Tableau,
    pivot_row: int,
    pivot_column: int,
) -> str:
    pivot = tableau.matrix[pivot_row, pivot_column]
    labels = tableau.row_labels
    operations: list[str] = []
    if not math.isclose(pivot, 1.0, abs_tol=TOLERANCE):
        operations.append(
            rf"{labels[pivot_row]}\leftarrow "
            rf"\frac{{1}}{{{_latex_number(pivot)}}}{labels[pivot_row]}"
        )

    for row in range(tableau.matrix.shape[0]):
        if row == pivot_row or abs(tableau.matrix[row, pivot_column]) <= TOLERANCE:
            continue
        coefficient = tableau.matrix[row, pivot_column]
        sign = "-" if coefficient > 0 else "+"
        magnitude = abs(coefficient)
        multiplier = "" if math.isclose(magnitude, 1.0) else _latex_number(magnitude)
        operations.append(
            rf"{labels[row]}\leftarrow {labels[row]}{sign}{multiplier}{labels[pivot_row]}"
        )
    return r",\qquad ".join(operations) or r"\text{(不需要列運算)}"


def _is_feasible_point(
    program: LinearProgram,
    point: tuple[float, float, float],
) -> bool:
    vector = np.asarray(point)
    if np.any(vector < -1e-7):
        return False
    for constraint in program.constraints:
        value = np.asarray(constraint.coefficients) @ vector
        if constraint.sense == "<=" and value - constraint.rhs > 1e-7:
            return False
        if constraint.sense == ">=" and constraint.rhs - value > 1e-7:
            return False
        if constraint.sense == "=" and abs(value - constraint.rhs) > 1e-7:
            return False
    return True


def _violated_constraints(tableau: _Tableau) -> tuple[int, ...]:
    """Constraint indices whose artificial variable is still positive."""
    violated: list[int] = []
    for row, name in enumerate(tableau.basis, start=1):
        if _is_artificial(name) and tableau.rhs[row] > 1e-7:
            violated.append(int(name.split("_", maxsplit=1)[1]) - 1)
    return tuple(sorted(violated))


def _arrow_direction(
    program: LinearProgram,
    tableau: _Tableau,
) -> tuple[tuple[float, float, float], str, tuple[int, ...]]:
    """Which way the current phase is pushing the point.

    Phase one minimises the total violation ``V(x) = sum_i max(0, b_i - A_i x)``
    over the rows that still carry a positive artificial, so ``-V`` climbs along
    the sum of those rows' normals.  Once nothing is violated the original
    objective takes over.
    """
    violated = _violated_constraints(tableau)
    if violated:
        direction = np.zeros(3)
        for index in violated:
            direction += np.asarray(program.constraints[index].coefficients)
        if np.linalg.norm(direction) > TOLERANCE:
            return tuple(float(value) for value in direction), "violation", violated  # type: ignore[return-value]
    return tuple(float(value) for value in program.objective), "objective", violated  # type: ignore[return-value]


def _snapshot(
    program: LinearProgram,
    tableau: _Tableau,
    *,
    title: str,
    explanation: str,
    operation: str,
    phase: str,
    entering: str | None = None,
    leaving: str | None = None,
    pivot_row: int | None = None,
) -> SimplexStep:
    point = tableau.point()
    arrow, arrow_kind, violated = _arrow_direction(program, tableau)
    return SimplexStep(
        title=title,
        explanation=explanation,
        operation=operation,
        columns=tuple(tableau.columns),
        tableau=_clean_matrix(tableau.matrix),
        rhs=_clean_vector(tableau.rhs),
        basis=tuple(tableau.basis),
        nonbasis=tuple(tableau.nonbasis),
        row_labels=tuple(tableau.row_labels),
        point=point,
        phase=phase,
        feasible=_is_feasible_point(program, point),
        arrow=arrow,
        arrow_kind=arrow_kind,
        violated=violated,
        entering=entering,
        leaving=leaving,
        pivot_row=pivot_row,
    )


def _run_simplex(
    program: LinearProgram,
    tableau: _Tableau,
    steps: list[SimplexStep],
    phase: str,
) -> None:
    """Pivot until every non-basic reduced cost is non-positive."""
    label = "Phase one" if phase == PHASE_ONE else "Phase two"
    for pivot_number in range(1, MAX_PIVOTS + 1):
        candidates = [
            tableau.column_of(name)
            for name in tableau.nonbasis
            if tableau.matrix[0, tableau.column_of(name)] < -TOLERANCE
        ]
        if not candidates:
            return

        pivot_column = min(candidates, key=lambda column: tableau.matrix[0, column])
        entering = tableau.variables[pivot_column - 1]

        valid_rows = [
            row
            for row in range(1, len(tableau.basis) + 1)
            if tableau.matrix[row, pivot_column] > TOLERANCE
        ]
        if not valid_rows:
            raise ValueError(f"{entering} 可以無限增加，因此目標函數無界。")

        ratios = {
            row: tableau.rhs[row] / tableau.matrix[row, pivot_column]
            for row in valid_rows
        }
        pivot_row = min(valid_rows, key=lambda row: (ratios[row], row))
        leaving = tableau.basis[pivot_row - 1]
        operation = _elimination_operation(tableau, pivot_row, pivot_column)
        ratio_text = ", ".join(_plain_number(ratios[row]) for row in valid_rows)

        tableau.pivot(pivot_row, pivot_column)
        tableau.swap_into_basis(pivot_row, pivot_column)
        point = tableau.point()

        degenerate = math.isclose(ratios[pivot_row], 0.0, abs_tol=TOLERANCE)
        note = "（比值為 0，這是退化 pivot，目標值不會前進）" if degenerate else ""
        steps.append(
            _snapshot(
                program,
                tableau,
                title=f"{label} pivot {pivot_number}：{entering} 進基、{leaving} 離基",
                explanation=(
                    f"minimum ratio test 的候選值為 {ratio_text}，"
                    f"選中 {tableau.row_labels[pivot_row]}{note}。"
                    f"消去後把兩欄交換，讓新的基變數回到 identity 區塊；"
                    f"幾何上的點移到 "
                    f"({', '.join(_plain_number(value) for value in point)})。"
                ),
                operation=operation,
                phase=phase,
                entering=entering,
                leaving=leaving,
                pivot_row=pivot_row,
            )
        )

    raise ValueError(f"超過 {MAX_PIVOTS} 次 pivot；這個例子可能發生 cycling。")


def _expel_artificials(
    program: LinearProgram,
    tableau: _Tableau,
    steps: list[SimplexStep],
) -> None:
    """Drive artificials out of the basis, dropping redundant rows."""
    while True:
        stuck = [
            (row, name)
            for row, name in enumerate(tableau.basis, start=1)
            if _is_artificial(name)
        ]
        if not stuck:
            return

        row, name = stuck[0]
        candidates = [
            tableau.column_of(other)
            for other in tableau.nonbasis
            if not _is_artificial(other)
            and abs(tableau.matrix[row, tableau.column_of(other)]) > TOLERANCE
        ]

        if not candidates:
            label = tableau.row_labels[row]
            tableau.drop_row(row)
            steps.append(
                _snapshot(
                    program,
                    tableau,
                    title=f"刪除多餘的限制式（${_math_name(name)}$ 所在的列）",
                    explanation=(
                        f"{label} 在所有非人工變數的欄位上係數都是 0，"
                        f"代表這條限制式可以完全被其他限制式推得，是多餘的。"
                        f"把 ${_math_name(name)}$ 連同該列一起刪除。"
                    ),
                    operation=rf"\text{{delete }}{label}",
                    phase=PHASE_EXPEL,
                )
            )
            continue

        pivot_column = candidates[0]
        entering = tableau.variables[pivot_column - 1]
        pivot_value = tableau.matrix[row, pivot_column]
        operation = _elimination_operation(tableau, row, pivot_column)

        tableau.pivot(row, pivot_column)
        tableau.swap_into_basis(row, pivot_column)

        sign_note = (
            "（這裡的 pivot 元素是負的，但因為該列常數項為 0，可行性仍然保持）"
            if pivot_value < 0
            else ""
        )
        steps.append(
            _snapshot(
                program,
                tableau,
                title=f"把人工變數 ${_math_name(name)}$ 逐出基底",
                explanation=(
                    f"${_math_name(name)}$ 雖然值是 0，但還留在基底裡。"
                    f"在它所在的列挑一個係數非 0 的非人工變數 ${_math_name(entering)}$ "
                    f"做 pivot 就能把它換出去{sign_note}。"
                ),
                operation=operation,
                phase=PHASE_EXPEL,
                entering=entering,
                leaving=name,
                pivot_row=row,
            )
        )


def _calculate_steps(program: LinearProgram) -> tuple[SimplexStep, ...]:
    tableau, artificials = _build_initial_tableau(program)
    objective = {
        f"x_{index + 1}": value for index, value in enumerate(program.objective)
    }
    steps: list[SimplexStep] = []

    if not artificials:
        _set_objective_row(tableau, objective)
        steps.append(
            _snapshot(
                program,
                tableau,
                title="初始 canonical form",
                explanation=(
                    "所有限制式都是 $\\leq$ 且 $b\\geq0$，slack variables 直接就是"
                    "可行的基底，不需要 phase one。令非基變數為 0 即得起始頂點。"
                ),
                operation=r"x_D=0",
                phase=PHASE_TWO,
            )
        )
        _run_simplex(program, tableau, steps, PHASE_TWO)
        return _mark_final(tuple(steps))

    # --- Phase one -------------------------------------------------------
    _set_objective_row(tableau, {name: -1.0 for name in artificials})
    steps.append(
        _snapshot(
            program,
            tableau,
            title="加入人工變數，寫下 phase one 的目標式",
            explanation=(
                f"$\\geq$ 與 $=$ 的限制式沒辦法直接給出可行的基底，"
                f"所以替它們加上人工變數 "
                f"{', '.join(f'${_math_name(name)}$' for name in artificials)}。"
                f"phase one 先改成最大化 $-\\sum a_i$；"
                f"此時目標列在人工變數的欄位上還不是 0，尚未是 canonical form。"
            ),
            operation=r"z=-\sum_i a_i",
            phase=PHASE_ONE,
        )
    )

    _make_canonical(tableau)
    steps.append(
        _snapshot(
            program,
            tableau,
            title="消去目標列，得到 canonical form",
            explanation=(
                "把每個以人工變數為基變數的列從目標列減掉，"
                "目標列在基變數欄位就全變成 0 了。"
                "此時 RHS 的第一項就是目前的 phase one 目標值 $-\\sum b_i$。"
            ),
            operation=r"R_z\leftarrow R_z-\sum_{i:\,a_i\in x_B}R_i",
            phase=PHASE_ONE,
        )
    )

    _run_simplex(program, tableau, steps, PHASE_ONE)

    if tableau.rhs[0] < -1e-7:
        steps[-1] = replace(
            steps[-1],
            title=steps[-1].title + "（phase one 最佳值 < 0）",
            explanation=(
                steps[-1].explanation
                + " phase one 的最大值小於 0，代表人工變數無法全部歸零，"
                "也就是原問題根本沒有可行解。"
            ),
        )
        raise InfeasibleProgram("原規劃問題沒有可行解（phase one 最佳值小於 0）。")

    steps.append(
        _snapshot(
            program,
            tableau,
            title="Phase one 完成：目標值為 0",
            explanation=(
                "所有人工變數都已經是 0，現在的 basic feasible solution "
                "對原問題來說已經是可行解了。"
            ),
            operation=r"\textstyle\sum_i a_i=0",
            phase=PHASE_ONE,
        )
    )

    # --- Expel artificials, then restore the original objective -----------
    _expel_artificials(program, tableau, steps)
    tableau.drop_variables([name for name in artificials if name in tableau.variables])

    _set_objective_row(tableau, objective)
    steps.append(
        _snapshot(
            program,
            tableau,
            title="刪掉人工變數，換回原本的目標式",
            explanation=(
                "人工變數從現在起永遠是 0，可以整欄刪掉。"
                "把目標列換回 $z=c^Tx$ 之後，它在基變數欄位上通常不是 0，"
                "所以還不是 canonical form。"
            ),
            operation=r"z=c^Tx",
            phase=PHASE_RESTORE,
        )
    )

    _make_canonical(tableau)
    steps.append(
        _snapshot(
            program,
            tableau,
            title="再消去一次，進入 phase two",
            explanation=(
                "用基變數所在的列把目標列清成 0，就回到完美的 canonical form，"
                "而 RHS 的第一項變成目前頂點的目標值 $z_0=c_B^Tb_B$。"
            ),
            operation=r"R_z\leftarrow R_z+\sum_i c_{B,i}R_i",
            phase=PHASE_RESTORE,
        )
    )

    _run_simplex(program, tableau, steps, PHASE_TWO)
    return _mark_final(tuple(steps))


def _mark_final(steps: tuple[SimplexStep, ...]) -> tuple[SimplexStep, ...]:
    final = steps[-1]
    return steps[:-1] + (
        replace(
            final,
            title=final.title + "（最佳解）",
            explanation=(
                final.explanation
                + " 所有非基變數的 reduced cost 都非正，因此目前頂點就是最佳解。"
            ),
        ),
    )


def _plane_data(program: LinearProgram) -> tuple[np.ndarray, np.ndarray]:
    normals = np.vstack(
        [
            *[np.asarray(constraint.coefficients) for constraint in program.constraints],
            np.eye(3),
        ]
    )
    values = np.concatenate(
        ([constraint.rhs for constraint in program.constraints], np.zeros(3))
    )
    return normals, values


def _enumerate_vertices(
    program: LinearProgram,
) -> tuple[tuple[float, float, float], ...]:
    normals, values = _plane_data(program)
    vertices: list[np.ndarray] = []

    for plane_indices in combinations(range(len(normals)), 3):
        selected = normals[list(plane_indices)]
        if np.linalg.matrix_rank(selected, tol=TOLERANCE) < 3:
            continue
        point = np.linalg.solve(selected, values[list(plane_indices)])
        if not _is_feasible_point(program, tuple(point)):  # type: ignore[arg-type]
            continue
        point[np.abs(point) <= TOLERANCE] = 0.0
        if not any(np.linalg.norm(point - known) <= 1e-7 for known in vertices):
            vertices.append(point)

    return tuple(tuple(float(value) for value in vertex) for vertex in vertices)  # type: ignore[return-value]


def _has_volume(vertices: tuple[tuple[float, float, float], ...]) -> bool:
    """A Mesh3d only looks right when the vertices span three dimensions."""
    if len(vertices) < 4:
        return False
    offsets = np.asarray(vertices[1:]) - np.asarray(vertices[0])
    return bool(np.linalg.matrix_rank(offsets, tol=TOLERANCE) >= 3)


def _polytope_edges(
    program: LinearProgram,
    vertices: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[int, int], ...]:
    normals, values = _plane_data(program)
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
    infeasible = False
    try:
        steps = _calculate_steps(program)
    except InfeasibleProgram:
        # Re-run so the caller still gets the tableau history that proves it.
        steps = _collect_infeasible_steps(program)
        infeasible = True

    vertices: tuple[tuple[float, float, float], ...] = ()
    edges: tuple[tuple[int, int], ...] = ()
    solid = False
    if not infeasible:
        # A closed drawing needs a bounded feasible set.  A nonnegative
        # polyhedron is bounded exactly when each coordinate has a finite
        # maximum.
        for coordinate in range(3):
            probe = tuple(1.0 if index == coordinate else 0.0 for index in range(3))
            try:
                _calculate_steps(
                    LinearProgram(objective=probe, constraints=program.constraints)  # type: ignore[arg-type]
                )
            except InfeasibleProgram:
                break
            except ValueError as error:
                raise ValueError("可行域無界，無法畫成封閉的三維多面體。") from error

        vertices = _enumerate_vertices(program)
        edges = _polytope_edges(program, vertices)
        # An equality constraint flattens the region onto a plane; the edges
        # still draw correctly, only the shaded solid has to go.
        solid = _has_volume(vertices)

    path: list[tuple[float, float, float]] = []
    path_feasible: list[bool] = []
    for step in steps:
        if not path or not np.allclose(step.point, path[-1], atol=TOLERANCE):
            path.append(step.point)
            path_feasible.append(step.feasible)

    return SimplexSimulation(
        program=program,
        steps=steps,
        vertices=vertices,
        edges=edges,
        path=tuple(path),
        path_feasible=tuple(path_feasible),
        infeasible=infeasible,
        solid=solid,
    )


def _collect_infeasible_steps(program: LinearProgram) -> tuple[SimplexStep, ...]:
    """Replay phase one, keeping the steps instead of raising."""
    collected: list[SimplexStep] = []
    tableau, artificials = _build_initial_tableau(program)
    _set_objective_row(tableau, {name: -1.0 for name in artificials})
    collected.append(
        _snapshot(
            program,
            tableau,
            title="加入人工變數，寫下 phase one 的目標式",
            explanation=(
                "替沒有現成基底的限制式加上人工變數，phase one 最大化 $-\\sum a_i$。"
            ),
            operation=r"z=-\sum_i a_i",
            phase=PHASE_ONE,
        )
    )
    _make_canonical(tableau)
    collected.append(
        _snapshot(
            program,
            tableau,
            title="消去目標列，得到 canonical form",
            explanation="把人工變數所在的列從目標列減掉。",
            operation=r"R_z\leftarrow R_z-\sum_{i:\,a_i\in x_B}R_i",
            phase=PHASE_ONE,
        )
    )
    _run_simplex(program, tableau, collected, PHASE_ONE)
    collected.append(
        _snapshot(
            program,
            tableau,
            title="Phase one 結束：最佳值 < 0（原問題無解）",
            explanation=(
                f"phase one 的最大值是 "
                f"${_latex_number(tableau.rhs[0])}$，小於 0。"
                "代表無論怎麼選點，人工變數都不可能全部歸零，"
                "也就是原規劃問題**沒有可行解**，不需要進入 phase two。"
            ),
            operation=r"\max\left(-\sum_i a_i\right)<0",
            phase=PHASE_ONE,
        )
    )
    return tuple(collected)


def tableau_latex(simulation: SimplexSimulation, step_index: int) -> str:
    step = simulation.steps[step_index]
    basis_count = len(step.basis)
    nonbasis_count = len(step.nonbasis)
    column_spec = "c|c|" + "c" * basis_count + "|" + "c" * nonbasis_count + "|c"

    headers: list[str] = []
    for name in step.columns:
        label = _math_name(name)
        if name == step.entering:
            label = rf"\color{{orange}}{{\boldsymbol{{{label}}}}}"
        elif _is_artificial(name):
            label = rf"\color{{purple}}{{{label}}}"
        headers.append(label)

    rows = [" & " + " & ".join(headers) + r" & \mathrm{RHS} \\", r"\hline"]
    for row_index, (values, rhs) in enumerate(zip(step.tableau, step.rhs)):
        row_label = step.row_labels[row_index]
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


_PHASE_LABELS = {
    PHASE_ONE: "Phase one",
    PHASE_EXPEL: "逐出人工變數",
    PHASE_RESTORE: "換回原目標式",
    PHASE_TWO: "Phase two",
}


def step_markdown(simulation: SimplexSimulation, step_index: int) -> str:
    step = simulation.steps[step_index]
    basis = ", ".join(f"${_math_name(name)}$" for name in step.basis)
    nonbasis = ", ".join(f"${_math_name(name)}$" for name in step.nonbasis)
    point = np.asarray(step.point)
    objective = np.asarray(simulation.program.objective)
    objective_value = objective @ point
    status = "可行解" if step.feasible else "**尚未可行**"

    if step.arrow_kind == "violation":
        violated = "、".join(f"第 {index + 1} 條" for index in step.violated)
        arrow_line = (
            f"- 綠色箭頭改成**紅色**：目前 {violated} 限制式還被違反，"
            f"箭頭指向它們法向量的和，也就是讓總違反量下降最快的方向"
        )
    else:
        arrow_line = "- 綠色箭頭：原目標函數的梯度 $\\nabla f = c$"

    return f"""
### {step_index + 1}/{len(simulation.steps)}　{step.title}

`{_PHASE_LABELS[step.phase]}`

{step.explanation}

$$
{step.operation}
$$

- 基變數：{basis}
- 非基變數：{nonbasis}
- 目前的點：$({", ".join(_latex_number(value) for value in point)})$（{status}）
- 原目標值：${_latex_number(objective_value)}$
{arrow_line}

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


_SENSE_LATEX = {"<=": r"\leq", ">=": r"\geq", "=": "="}


def program_markdown(simulation: SimplexSimulation) -> str:
    objective = simulation.program.objective
    constraints = simulation.program.constraints
    constraint_lines = []
    for index, constraint in enumerate(constraints):
        ending = r" \\" if index < len(constraints) - 1 else ""
        constraint_lines.append(
            "        & "
            + _linear_expression(constraint.coefficients)
            + rf"{_SENSE_LATEX[constraint.sense]} "
            + f"{_latex_number(constraint.rhs)}{ending}"
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


_BOX_EDGES = tuple(
    (start, start ^ (1 << axis))
    for axis in range(3)
    for start in range(8)
    if not start & (1 << axis)
)


def _box_corners(lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            [
                upper[axis] if corner & (1 << axis) else lower[axis]
                for axis in range(3)
            ]
            for corner in range(8)
        ]
    )


def _plane_patch(
    normal: np.ndarray,
    offset: float,
    lower: np.ndarray,
    upper: np.ndarray,
) -> tuple[np.ndarray, list[tuple[int, int, int]]] | None:
    """Clip the plane ``normal . x = offset`` to a box, as a triangle fan."""
    corners = _box_corners(lower, upper)
    signed = corners @ normal - offset

    points: list[np.ndarray] = []
    for start, end in _BOX_EDGES:
        first, second = signed[start], signed[end]
        if abs(first) <= 1e-9:
            points.append(corners[start])
        if abs(second) <= 1e-9:
            points.append(corners[end])
        if first * second < 0:
            ratio = first / (first - second)
            points.append(corners[start] + ratio * (corners[end] - corners[start]))

    unique: list[np.ndarray] = []
    for point in points:
        if not any(np.linalg.norm(point - kept) <= 1e-7 for kept in unique):
            unique.append(point)
    if len(unique) < 3:
        return None

    # Order the polygon by angle inside the plane before fanning it.
    polygon = np.asarray(unique)
    centre = polygon.mean(axis=0)
    axis_u = polygon[0] - centre
    norm_u = np.linalg.norm(axis_u)
    if norm_u <= 1e-9:
        return None
    axis_u /= norm_u
    axis_v = np.cross(normal / np.linalg.norm(normal), axis_u)
    angles = np.arctan2((polygon - centre) @ axis_v, (polygon - centre) @ axis_u)
    polygon = polygon[np.argsort(angles)]

    triangles = [(0, index, index + 1) for index in range(1, len(polygon) - 1)]
    return polygon, triangles


def _tight_planes(program: LinearProgram, point: tuple[float, float, float]) -> set[int]:
    """Indices into ``_plane_data`` whose plane passes through ``point``."""
    normals, values = _plane_data(program)
    vector = np.asarray(point)
    return {
        index
        for index, (normal, value) in enumerate(zip(normals, values))
        if abs(normal @ vector - value) <= 1e-7
    }


def _add_plane_traces(
    figure: go.Figure,
    simulation: SimplexSimulation,
    step: SimplexStep,
    lower: np.ndarray,
    upper: np.ndarray,
) -> None:
    """Draw every constraint plane, highlighting the ones meeting at the point."""
    normals, values = _plane_data(simulation.program)
    tight = _tight_planes(simulation.program, step.point)
    labels = [
        f"限制式 {index + 1}" for index in range(len(simulation.program.constraints))
    ] + ["x₁=0", "x₂=0", "x₃=0"]

    groups: dict[bool, list[tuple[np.ndarray, list[tuple[int, int, int]], str]]] = {
        True: [],
        False: [],
    }
    for index, (normal, value) in enumerate(zip(normals, values)):
        patch = _plane_patch(np.asarray(normal, dtype=float), float(value), lower, upper)
        if patch is None:
            continue
        groups[index in tight].append((*patch, labels[index]))

    for highlighted, color, opacity, name in (
        (False, "#94a3b8", 0.05, "限制式平面"),
        (True, "#facc15", 0.22, "通過目前點的平面"),
    ):
        patches = groups[highlighted]
        if not patches:
            continue

        vertices: list[np.ndarray] = []
        faces: list[tuple[int, int, int]] = []
        hover: list[str] = []
        for polygon, triangles, label in patches:
            base = len(vertices)
            vertices.extend(polygon)
            hover.extend([label] * len(polygon))
            faces.extend(
                (base + a, base + b, base + c) for a, b, c in triangles
            )

        stacked = np.asarray(vertices)
        figure.add_trace(
            go.Mesh3d(
                x=stacked[:, 0],
                y=stacked[:, 1],
                z=stacked[:, 2],
                i=[face[0] for face in faces],
                j=[face[1] for face in faces],
                k=[face[2] for face in faces],
                color=color,
                opacity=opacity,
                flatshading=True,
                text=hover,
                hovertemplate="%{text}<extra></extra>",
                name=name,
                showlegend=True,
            )
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


def _add_path_traces(figure: go.Figure, simulation: SimplexSimulation) -> None:
    """Draw the walk, splitting infeasible (phase one) from feasible legs."""
    points = simulation.path
    if len(points) < 2:
        return

    for infeasible_leg, color, name, dash in (
        (True, "#ef4444", "phase one（可行域外）", "dot"),
        (False, "#94a3b8", "完整路徑", "dot"),
    ):
        coordinates: tuple[list[float | None], ...] = ([], [], [])
        for index in range(len(points) - 1):
            leg_is_infeasible = not (
                simulation.path_feasible[index] and simulation.path_feasible[index + 1]
            )
            if leg_is_infeasible != infeasible_leg:
                continue
            for axis, destination in enumerate(coordinates):
                destination.extend(
                    (points[index][axis], points[index + 1][axis], None)
                )
        if not coordinates[0]:
            continue
        figure.add_trace(
            go.Scatter3d(
                x=coordinates[0],
                y=coordinates[1],
                z=coordinates[2],
                mode="lines",
                line={"color": color, "width": 4, "dash": dash},
                hoverinfo="skip",
                name=name,
            )
        )


def make_figure(simulation: SimplexSimulation, step_index: int) -> go.Figure:
    step = simulation.steps[step_index]
    figure = go.Figure()

    gradient = np.asarray(step.arrow, dtype=float)
    gradient /= np.linalg.norm(gradient)
    reference_points = np.asarray(simulation.vertices or simulation.path)
    plot_scale = max(float(np.max(np.abs(reference_points))), 1.0)
    arrow_length = plot_scale * 0.25

    # Every step's arrow has to fit, otherwise the scene would resize as the
    # direction changes between phases.
    walk = np.asarray(simulation.path)
    tips = [
        np.asarray(other.point)
        + arrow_length * np.asarray(other.arrow) / np.linalg.norm(other.arrow)
        for other in simulation.steps
    ]
    display_points = np.vstack((reference_points, walk, np.asarray(tips)))
    display_minima = np.min(display_points, axis=0)
    display_maxima = np.max(display_points, axis=0)
    display_padding = np.maximum(0.06 * (display_maxima - display_minima), 0.05)
    maxima = np.maximum(display_maxima, 1.0)
    scene_lower = np.minimum(-0.05 * maxima, display_minima - display_padding)
    scene_upper = np.maximum(1.15 * maxima, display_maxima + display_padding)

    # Planes first, so every later trace draws on top of them.
    _add_plane_traces(figure, simulation, step, scene_lower, scene_upper)

    if simulation.vertices:
        vertices = simulation.vertices
        if simulation.solid:
            vertices_x, vertices_y, vertices_z = zip(*vertices)
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

    _add_path_traces(figure, simulation)

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
    marker_color = "#ea580c" if step.feasible else "#dc2626"
    figure.add_trace(
        go.Scatter3d(
            x=[point_x],
            y=[point_y],
            z=[point_z],
            mode="markers+text",
            marker={
                "size": 10,
                "color": marker_color,
                "symbol": "circle" if step.feasible else "x",
            },
            text=[f"z={_plain_number(objective_value)}"],
            textposition="top center",
            hovertemplate=(
                ("目前的點" if step.feasible else "目前的點（尚未可行）")
                + " (%{x}, %{y}, %{z})<extra></extra>"
            ),
            name="目前的點" if step.feasible else "目前的點（尚未可行）",
        )
    )

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

    if step.arrow_kind == "violation":
        arrow_color = "#e11d48"
        violated_labels = "、".join(f"限制式 {index + 1}" for index in step.violated)
        arrow_name = "往可行域的方向"
        arrow_hover = f"減少違反量最快的方向（{violated_labels} 的法向量之和）"
    else:
        arrow_color = "#22c55e"
        arrow_name = "目標函數梯度"
        arrow_hover = "∇f=(" + ", ".join(
            _plain_number(value) for value in simulation.program.objective
        ) + ")"

    figure.add_trace(
        go.Scatter3d(
            x=[point_x, shaft_end[0]],
            y=[point_y, shaft_end[1]],
            z=[point_z, shaft_end[2]],
            mode="lines",
            line={"color": arrow_color, "width": 7},
            hovertemplate=f"{arrow_hover}<extra></extra>",
            name=arrow_name,
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
            color=arrow_color,
            flatshading=True,
            hoverinfo="skip",
            showlegend=False,
            name="箭頭",
        )
    )

    figure.update_layout(
        height=590,
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#64748b"},
        legend={"orientation": "h", "y": -0.05, "x": 0},
        uirevision="simplex-user-input",
        scene={
            "xaxis": {"title": "x₁", "range": [scene_lower[0], scene_upper[0]]},
            "yaxis": {"title": "x₂", "range": [scene_lower[1], scene_upper[1]]},
            "zaxis": {"title": "x₃", "range": [scene_lower[2], scene_upper[2]]},
            "aspectmode": "data",
            "camera": {"eye": {"x": 1.55, "y": 1.55, "z": 1.15}},
        },
    )
    return figure


DEFAULT_SIMULATION = build_simulation(
    parse_linear_program(DEFAULT_OBJECTIVE, DEFAULT_CONSTRAINTS)
)
