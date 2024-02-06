import ast

def remove_redundant_args(node):
    if isinstance(node, ast.FunctionDef):
        seen_args = set()
        updated_args = []
        for arg in node.args.args:
            if arg.arg not in seen_args:
                seen_args.add(arg.arg)
                updated_args.append(arg)
        node.args.args = updated_args

def get_function_definition(node, function_name):
    if isinstance(node, ast.FunctionDef) and node.name == function_name:
        return node
    for child in ast.iter_child_nodes(node):
        result = get_function_definition(child, function_name)
        if result:
            return result
    return None

def remove_redundant_input_args(file_path, output_file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)

    # Remove redundant input arguments in function definitions
    for node in ast.walk(tree):
        remove_redundant_args(node)

        if isinstance(node, ast.FunctionDef) and node.name == 'run_cyclically':
            # Remove redundant variables in the function
            seen_vars = set()
            updated_body = []
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id not in seen_vars:
                            seen_vars.add(target.id)
                            updated_body.append(stmt)
                            break
                else:
                    updated_body.append(stmt)
            node.body = updated_body

            # Remove redundant input arguments in function calls
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Call) and hasattr(stmt, 'func') and hasattr(stmt.func, 'id'):
                    function_name = stmt.func.id
                    function_def = get_function_definition(tree, function_name)
                    if function_def:
                        args_count = len(function_def.args.args)
                        args = stmt.args[:args_count]
                        stmt.args = args

            # Remove redundant lines in the for loop
            if isinstance(node, ast.FunctionDef) and node.name == 'run_cyclically':
                loop_body = []
                seen_lines = set()
                for stmt in node.body[0].body:
                    line_code = ast.unparse(stmt)
                    if line_code not in seen_lines:
                        seen_lines.add(line_code)
                        loop_body.append(stmt)
                node.body[0].body = loop_body

    updated_code = ast.unparse(tree)

    with open(output_file_path, 'w') as output_file:
        output_file.write(updated_code)
def remove_redundant_loop_variables(node):
    if isinstance(node, ast.For):
        seen_vars = set()
        updated_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id not in seen_vars:
                        seen_vars.add(target.id)
                        updated_body.append(stmt)
                        break
            else:
                updated_body.append(stmt)
        node.body = updated_body

if __name__ == "__main__":
    input_file = 'generated_code_2.py'
    output_file = 'generated_code_3.py'
    remove_redundant_input_args(input_file, output_file)

print("Generated code has been written to 'generated_code_3.py'.")
tree = ast.parse(open(output_file).read())
for node in ast.walk(tree):
    remove_redundant_loop_variables(node)

updated_code = ast.unparse(tree)

with open(output_file, 'w') as output_file:
    output_file.write(updated_code)