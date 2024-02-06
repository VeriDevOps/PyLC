import ast


def get_variable_map(pou_input_ids):
    variable_map = {}
    for entry in pou_input_ids:
        expression = entry['Expression']
        in_variable = entry['InVariable'].strip()
        variable_map[f'V_{in_variable}'] = expression
    return variable_map


def replace_variable_names(code, variable_map):
    class VariableNameReplacer(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in variable_map:
                node.id = variable_map[node.id]
            return node

    tree = ast.parse(code)
    replacer = VariableNameReplacer()
    updated_tree = replacer.visit(tree)
    return ast.unparse(updated_tree)


def replace_function_arguments(code, variable_map):
    class FunctionArgumentReplacer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            for arg in node.args.args:
                if arg.arg in variable_map:
                    arg.arg = variable_map[arg.arg]
            return self.generic_visit(node)

    tree = ast.parse(code)
    replacer = FunctionArgumentReplacer()
    updated_tree = replacer.visit(tree)
    return ast.unparse(updated_tree)


def replace_printed_text(code, variable_map):
    class PrintTextReplacer(ast.NodeTransformer):
        def visit_Str(self, node):
            for key, value in variable_map.items():
                node.s = node.s.replace(key, value)
            return node

    tree = ast.parse(code)
    replacer = PrintTextReplacer()
    updated_tree = replacer.visit(tree)
    return ast.unparse(updated_tree)


def main():
    # Read the content of generated_code_1.py
    with open('generated_code_1.py', 'r') as file:
        code_1 = file.read()

    # Read the content of generated_code_0.py
    with open('generated_code_0.py', 'r') as file:
        code_0 = file.read()

    # Parse the content of generated_code_0.py to obtain the variable map
    pou_dict = {}
    exec(code_0, pou_dict)
    pou_input_ids = pou_dict['POU']['input_ids']
    variable_map = get_variable_map(pou_input_ids)

    # Replace the variable names in generated_code_1.py using the variable map
    updated_code_1 = replace_variable_names(code_1, variable_map)

    # Replace the function arguments in generated_code_1.py using the variable map
    updated_code_2 = replace_function_arguments(updated_code_1, variable_map)

    # Replace the printed text in run_cyclically() using the variable map
    updated_code_3 = replace_printed_text(updated_code_2, variable_map)

    # Write the updated code to generated_code_2.py
    with open('generated_code_2.py', 'w') as file:
        file.write(updated_code_3)


if __name__ == "__main__":
    main()
