import ast
import os
import shutil
import importlib
from pathlib import Path
import re
from hestia_earth.schema import NodeType

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.join(_CURRENT_DIR, '..')

EXTRA_LINES = sorted(
    importlib.import_module('formatters.float').EXTRA_LINES +
    importlib.import_module('formatters.dates').EXTRA_LINES,
    reverse=True
)

INPUT_DIR = Path(os.path.join(_ROOT_DIR, 'hestia_earth', 'schema', 'pydantic'))
OUTPUT_FILE = Path(os.path.join(INPUT_DIR, '__init__.py'))

seen_classes = set()
seen_imports = set()
unique_defs = []


# handle incompatibility with new pydantic version
class RootModelTransformer(ast.NodeTransformer):
    def visit_ClassDef(self, node):
        """
        Called for every class definition.
        """
        has_root_field = False
        body_to_keep = []

        for body_node in node.body:
            if isinstance(body_node, ast.AnnAssign) and isinstance(body_node.target, ast.Name):
                if body_node.target.id == '__root__':
                    has_root_field = True
                    # Rename the field to 'root'
                    body_node.target.id = 'root'
                    body_to_keep.append(body_node)

            # Identify and remove the 'Config' class definition
            elif isinstance(body_node, ast.ClassDef) and body_node.name == 'Config':
                continue # Skip this node to remove it
            else:
                body_to_keep.append(body_node)

        # If the class has a __root__ field, update its base class and body
        if has_root_field:
            for i, base in enumerate(node.bases):
                if isinstance(base, ast.Name) and base.id == 'BaseModel':
                    node.bases[i] = ast.Name(id='RootModel', ctx=ast.Load())
            node.body = body_to_keep

        # Ensure we visit all child nodes
        return self.generic_visit(node)


def root_transform(source_code: str):
    tree = ast.parse(source_code)

    transformer = RootModelTransformer()
    new_tree = transformer.visit(tree)

    # 3. Add the 'RootModel' import
    for node in new_tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == 'pydantic':
            has_root_model_import = any(alias.name == 'RootModel' for alias in node.names)
            if not has_root_model_import:
                node.names.append(ast.alias(name='RootModel'))
            break

    return ast.unparse(new_tree)


# handle generating errors using `const=True`
class ConstTransformer(ast.NodeTransformer):
    def visit_AnnAssign(self, node):
        """Called for every annotated assignment (e.g., `my_field: str = ...`)."""

        # Check if the right-hand side is a call to `Field`
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'Field':
            field_args = node.value.keywords

            is_const = False
            const_value = None

            # Find the 'const=True' argument and the 'examples' argument
            for arg in field_args:
                if arg.arg == 'const' and isinstance(arg.value, ast.Constant) and arg.value.value is True:
                    is_const = True
                if arg.arg == 'examples' and isinstance(arg.value, ast.List) and len(arg.value.elts) == 1:
                    # Extract the value from the examples list
                    const_value = arg.value.elts[0]

            if is_const and const_value is not None:
                # If const is found and a value is available, transform the node

                # 1. Update the type hint to `Literal`
                # The node.annotation is the original type (e.g., `DecimalValue`)
                node.annotation = ast.Subscript(
                    value=ast.Name(id='Literal', ctx=ast.Load()),
                    slice=ast.Constant(value=const_value.value)
                )

                # 2. Change the assignment to just the constant value
                # This removes the `Field` function call
                node.value = const_value

                # 3. Mark the AST for an import to be added
                self._needs_literal_import = True

        return self.generic_visit(node)


def const_transform(source_code: str):
    tree = ast.parse(source_code)

    transformer = ConstTransformer()
    transformer._needs_literal_import = False
    new_tree = transformer.visit(tree)

    # 3. Add the 'Literal' import if needed
    if transformer._needs_literal_import:
        import_found = False
        for node in new_tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == 'typing':
                node.names.append(ast.alias(name='Literal', asname=None))
                import_found = True
                break

        if not import_found:
            # Add a new typing import if one doesn't exist
            literal_import = ast.ImportFrom(
                module='typing',
                names=[ast.alias(name='Literal', asname=None)],
                level=0
            )
            new_tree.body.insert(0, literal_import)

    return ast.unparse(new_tree)


for file in INPUT_DIR.glob("*.py"):
    text = file.read_text()
    text = root_transform(text)
    text = const_transform(text)
    tree = ast.parse(text, filename=str(file))
    for node in tree.body:
        # Handle imports
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            # Skip relative imports (like `from . import Foo`)
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                continue
            imp = ast.unparse(node)
            if imp not in seen_imports:
                seen_imports.add(imp)
                unique_defs.append(imp)
        # Handle classes
        elif isinstance(node, ast.ClassDef):
            if node.name not in seen_classes:
                seen_classes.add(node.name)
                unique_defs.append(ast.unparse(node))
        # Handle top-level functions (sometimes generated)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name not in seen_classes:
                seen_classes.add(node.name)
                unique_defs.append(ast.unparse(node))


def _clean_dir(folder: str):
    os.makedirs(folder, exist_ok=True)
    shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)


def _read_header():
    with open(os.path.join(_CURRENT_DIR, 'templates', 'header.py'), 'r') as f:
        return f.read()


def main():
    _clean_dir(INPUT_DIR)

    generated_code = "\n\n".join(unique_defs).replace('from __future__ import annotations', '')

    code = "\n".join(
        ['from __future__ import annotations'] +
        [_read_header()] +
        EXTRA_LINES +
        [generated_code]
    )
    code = code.replace(
        "field_id: Optional[str] = Field(None, alias='@id', description='Unique id assigned by HESTIA', examples=['@hestia-unique-id-1'])",
        ""
    )
    code = code.replace(
        "constr(regex",
        "constr(pattern"
    )
    pattern = r"(\w+:\s+\w+)\s+=\s+Field\((.*?),\s+const=True\)"
    replacement = r"\1: Literal[\2]"
    code = re.sub(pattern, replacement, code)

    node_types = [e.value for e in NodeType]
    # set `Node` as parent class for NodeType
    code = re.sub(
        r"class\s+(" + "|".join(node_types) + r")\(BaseModel\):",
        r"class \1(Node):",
        code
    )
    # allow nested Node to be used as Ref
    code = re.sub(
        r":\sOptional\[(" + "|".join(node_types) + r")\]\s=",  # : Optional[Site]
        r": Optional[Union[\1, NodeRef]] =",
        code
    )
    code = re.sub(
        r":\sOptional\[list\[(" + "|".join(node_types) + r")\]\]\s=",  # : Optional[list[Site]]
        r": Optional[list[Union[\1, NodeRef]]] =",
        code
    )
    code = re.sub(
        r":\slist\[(" + "|".join(node_types) + r")\]\s=",  # : list[Site]
        r": list[Union[\1, NodeRef]] =",
        code
    )
    code = re.sub(
        r":\s(" + "|".join(node_types) + r")\s=",  # : Site
        r": Union[\1, NodeRef] =",
        code
    )

    code = re.sub(r",\sge=[\d\.]+", '', code)

    # Write out combined file
    with open(OUTPUT_FILE, "w") as f:
        f.write(code)

    print(f"✅ Combined models written to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
