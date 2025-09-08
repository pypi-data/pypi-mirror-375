from datamodel_code_generator.format import CustomCodeFormatter

EXTRA_LINES = [
    "from decimal import Decimal",
    "from pydantic import PlainSerializer",
    "from typing import Annotated",
    '',
    "DecimalValue = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used='json')]"
]


class CodeFormatter(CustomCodeFormatter):
    def apply(self, code: str) -> str:
        # Example transformation:
        code = code.replace(": float", ": DecimalValue")
        code = code.replace("[float", "[DecimalValue")
        # fix error in distribution
        code = code.replace("Optional[list[Union[DecimalValue, list[Any]]]]", "Optional[Union[list[list[DecimalValue]], list[DecimalValue]]]")
        return '\n'.join(EXTRA_LINES + ['', code])
