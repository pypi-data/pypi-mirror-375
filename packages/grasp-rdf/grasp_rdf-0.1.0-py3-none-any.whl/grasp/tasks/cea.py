from dataclasses import dataclass
from typing import Any, Iterator

from pydantic import BaseModel
from universal_ml_utils.table import generate_table

from grasp.functions import TaskFunctions, find_manager
from grasp.manager import KgManager, format_kgs
from grasp.sparql.utils import parse_into_binding
from grasp.utils import FunctionCallException, format_list, format_notes


@dataclass
class Annotation:
    identifier: str
    entity: str
    label: str | None = None

    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "entity": self.entity,
            "label": self.label,
        }

    def format(self, with_label: bool = False) -> str:
        s = self.entity
        if self.label and with_label:
            s += f": {self.label}"
        return s


def clean(s: str) -> str:
    return " ".join(s.strip().split())


class Annotations:
    def __init__(
        self,
        header: list[str],
        data: list[list[str]],
        annotate_rows: list[int] | None = None,
        annotate_columns: list[int] | None = None,
    ) -> None:
        assert len(header) > 0, "Header must not be empty"
        assert all(len(row) == len(header) for row in data), (
            "All rows must have the same length as the header"
        )
        self.width = len(header)
        self.height = len(data)
        self.header = [clean(h) for h in header]
        self.data = [[clean(cell) for cell in row] for row in data]

        self.rows = set(annotate_rows) if annotate_rows is not None else None
        self.cols = set(annotate_columns) if annotate_columns is not None else None

        # map from cell (row, column) to annoation
        self.annotations: dict[tuple[int, int], Annotation] = {}

    def iter(self) -> Iterator[list[Annotation | None]]:
        for r in range(self.height):
            yield [self.get(r, c) for c in range(self.width)]

    def annotate(
        self,
        row: int,
        column: int,
        annotation: Annotation | None,
    ) -> Annotation | None:
        if row < 0 or row >= self.height:
            raise ValueError(f"Row {row} out of bounds")

        if self.rows is not None and row not in self.rows:
            raise ValueError(f"Row {row} must not be annotated")

        if column < 0 or column >= self.width:
            raise ValueError(f"Column {column} out of bounds")

        if self.cols is not None and column not in self.cols:
            raise ValueError(f"Column {column} must not be annotated")

        current = self.annotations.pop((row, column), None)
        if annotation is not None:
            self.annotations[(row, column)] = annotation
        return current

    def get(self, row: int, column: int) -> Annotation | None:
        return self.annotations.get((row, column), None)

    def to_dict(self, with_labels: bool = False) -> dict:
        return {
            "formatted": self.format(with_labels),
            "annotations": [
                {
                    "row": row,
                    "column": column,
                    **annot.to_dict(),
                }
                for (row, column), annot in self.annotations.items()
            ],
        }

    def format(self, with_labels: bool = False) -> str:
        data = [
            [str(i)]
            + [
                col + (f" ({annot.format(with_labels)})" if annot is not None else "")
                for col, annot in zip(row, annots)
            ]
            for i, (row, annots) in enumerate(zip(self.data, self.iter()))
        ]
        max_data_width = max(len(cell) for row in data for cell in row)

        header = ["Row"] + [f"Column {i}: {name}" for i, name in enumerate(self.header)]
        max_header_width = max(len(h) for h in header)

        table = generate_table(
            data=data,
            headers=[header],
            max_column_width=max(max_data_width, max_header_width),
        )
        return table


def rules() -> list[str]:
    return [
        "If you cannot find a suitable entity for a cell, leave it unannotated.",
        "If there are multiple suitable entities for a cell, choose the one that "
        "fits best in the context of the table, or the one that is more popular/general.",
        "If you find common patterns within or across rows and columns, executing a corresponding SPARQL query "
        "to retrieve multiple entities at once might be easier than searching for each cell individually.",
        "All of your annotations should be full or prefixed IRIs.",
        "Every once in a while and before stopping, look at your current annotations and "
        "verify that they make sense.",
        "If the same entity occurs multiple times in the table, annotate all occurrences.",
    ]


def system_information() -> str:
    return """\
You are an entity annotation assistant. \
Your job is to annotate cells from a given table with entities \
from the available knowledge graphs.

You should follow a step-by-step approach to annotate the cells:
1. Determine what the table might be about and what the different columns \
might represent. Think about how the cells might be represented with entities \
in the knowledge graphs.
2. Annotate the cells, starting with the ones that are easiest to annotate. \
Use the provided functions to search and query the knowledge graphs for the \
corresponding entities. You may need to refine or rethink your annotations \
based on new insights along the way and alter them if needed, possibly \
multiple times.
3. Use the stop function to finalize your annotations and stop the \
annotation process."""


def functions(managers: list[KgManager]) -> TaskFunctions:
    kgs = [manager.kg for manager in managers]
    fns = [
        {
            "name": "annotate",
            "description": """\
Annotate a cell in the table with an entity from the specified knowledge graph.
This function overwrites any previous annotation of the cell.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "kg": {
                        "type": "string",
                        "enum": kgs,
                        "description": "The knowledge graph to use for the annotation",
                    },
                    "row": {
                        "type": "integer",
                        "description": "The row index of the cell to annotate (0-based, ignoring header)",
                    },
                    "column": {
                        "type": "integer",
                        "description": "The column index of the cell to annotate (0-based, ignoring header)",
                    },
                    "entity": {
                        "type": "string",
                        "description": "The IRI of the entity to annotate the cell with",
                    },
                },
                "required": ["kg", "row", "column", "entity"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "name": "clear",
            "description": """\
Clear the annotation of a cell in the table.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "row": {
                        "type": "integer",
                        "description": "The row index of the cell to clear (0-based, ignoring header)",
                    },
                    "column": {
                        "type": "integer",
                        "description": "The column index of the cell to clear (0-based, ignoring header)",
                    },
                },
                "required": ["row", "column"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "name": "show",
            "description": """\
Show the current annotations in the table.""",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "name": "stop",
            "description": """\
Finalize your annotations and stop the annotation process.""",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "strict": True,
        },
    ]
    return fns, call_function


def prepare_annotation(manager: KgManager, entity: str) -> Annotation:
    binding = parse_into_binding(entity, manager.iri_literal_parser, manager.prefixes)
    if binding is None or binding.typ != "uri":
        raise ValueError(f"Entity {entity} is not a valid IRI")

    identifier = binding.identifier()

    label = None

    map = manager.entity_mapping
    norm = map.normalize(identifier)
    if norm is not None and norm[0] in map:
        id = map[norm[0]]
        label = manager.entity_index.get_name(id)

    return Annotation(identifier, entity, label)


def annotate(
    managers: list[KgManager],
    kg: str,
    row: int,
    column: int,
    entity: str,
    state: Annotations,
) -> str:
    manager, _ = find_manager(managers, kg)

    try:
        annotation = prepare_annotation(manager, entity)
        current = state.annotate(row, column, annotation)
    except ValueError as e:
        raise FunctionCallException(str(e)) from e

    if current is None:
        return f"Annotated cell ({row}, {column}) with entity {entity}"
    else:
        return f"Updated annotation of cell ({row}, {column}) from {current.entity} to {entity}"


def clear(row: int, column: int, state: Annotations) -> str:
    try:
        current = state.annotate(row, column, None)
    except ValueError as e:
        raise FunctionCallException(str(e)) from e

    if current is None:
        raise FunctionCallException(f"Cell ({row}, {column}) is not annotated")

    return f"Cleared annotation {current.entity} from cell ({row}, {column})"


class CEAInput(BaseModel):
    header: list[str]
    data: list[list[str]]
    annotate_rows: list[int] | None = None
    annotate_columns: list[int] | None = None


def input_instructions(annotations: Annotations) -> str:
    instructions = """\
Annotate the following table. If there already are annotations \
for some cells, they are shown in parentheses after the cell value.

"""

    if annotations.rows is not None and len(annotations.rows) != annotations.height:
        rows_to_annotate = ", ".join(str(r) for r in sorted(annotations.rows))
        sfx = "s" if len(annotations.rows) != 1 else ""
        instructions += f"Only annotate row{sfx} {rows_to_annotate}.\n\n"
    else:
        instructions += "Annotate all rows.\n\n"

    if annotations.cols is not None and len(annotations.cols) != annotations.width:
        cols_to_annotate = ", ".join(str(c) for c in sorted(annotations.cols))
        sfx = "s" if len(annotations.cols) != 1 else ""
        instructions += f"Only annotate column{sfx} {cols_to_annotate}.\n\n"
    else:
        instructions += "Annotate all columns.\n\n"

    instructions += annotations.format()
    return instructions


def input_and_state(input: Any) -> tuple[str, Annotations]:
    try:
        cea_input = CEAInput(**input)
    except Exception as e:
        raise ValueError(
            "CEA task input must be a dict with 'header' and 'data' fields"
        ) from e

    annots = Annotations(
        cea_input.header,
        cea_input.data,
        cea_input.annotate_rows,
        cea_input.annotate_columns,
    )
    instructions = input_instructions(annots)
    return instructions, annots


def call_function(
    managers: list[KgManager],
    fn_name: str,
    fn_args: dict,
    known: set[str],
    state: Annotations | None = None,
    **kwargs: Any,
) -> str:
    assert isinstance(state, Annotations), (
        "Annotations must be provided as state for CEA task"
    )

    if fn_name == "annotate":
        return annotate(
            managers,
            fn_args["kg"],
            fn_args["row"],
            fn_args["column"],
            fn_args["entity"],
            state,
        )

    elif fn_name == "clear":
        return clear(fn_args["row"], fn_args["column"], state)

    elif fn_name == "show":
        return state.format()

    elif fn_name == "stop":
        return "Stopping"

    else:
        raise ValueError(f"Unknown function {fn_name}")


def output(state: Annotations) -> dict:
    return state.to_dict(with_labels=True)


def feedback_system_message(
    managers: list[KgManager],
    kg_notes: dict[str, list[str]],
    notes: list[str],
) -> str:
    return f"""\
You are a table annotation assistant providing feedback on the \
output of a table annotation system for a given input table.

The system has access to the following knowledge graphs:
{format_kgs(managers, kg_notes)}

The system was provided the following notes across all knowledge graphs:
{format_notes(notes)}

The system was provided the following rules to follow:
{format_list(rules())}

Provide your feedback with the give_feedback function."""


def feedback_instructions(inputs: list[str], output: dict) -> str:
    assert inputs, "At least one input is required for feedback"

    if len(inputs) > 1:
        prompt = (
            "Previous inputs:\n" + "\n\n".join(i.strip() for i in inputs[:-1]) + "\n\n"
        )

    else:
        prompt = ""

    prompt += f"Input:\n{inputs[-1].strip()}"
    prompt += f"\n\nAnnotations:\n{output['formatted']}"
    return prompt
