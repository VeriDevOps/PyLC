import sys
import time
import inspect

# Import the given Python code as a module
sys.path.append('.')
import generated_code_0

# Extract the block definitions (Dynamic range of Blocks)
blocks = [obj for name, obj in vars(generated_code_0).items() if name.startswith('B')]

# Extract the POU definition
POU = generated_code_0.POU

# Count the occurrences of each typeName
type_count = {}
for block in blocks:
    type_name = block['typeName']
    if type_name in type_count:
        type_count[type_name] += 1
    else:
        type_count[type_name] = 1

# Extract the input variable types from the POU dictionary
input_var_types = POU['input_vars']

# Match 'Expression' from input_ids with the corresponding type in input_vars
expression_to_type = {}
for input_id, input_type in zip(POU['input_ids'], input_var_types):
    expression_to_type[input_id['Expression']] = input_type.split(':')[1]  # Extract only the type name

# Generate the new Python code
generated_code_str = f"""
import time
import sys

def {POU['pou_name']}({', '.join([f"V_{input_id['InVariable'].strip()}:{expression_to_type[input_id['Expression']]}" if input_id['Expression'] in expression_to_type else f"V_{input_id['InVariable'].strip()}" for input_id in POU['input_ids']])}):
"""
# Generate the subfunctions
for block in blocks:
    type_name = block['typeName']
    subfunc_name = type_name
    if type_count[type_name] > 1:
        # Append a suffix to subfunction name if there are multiple instances of the same type
        subfunc_name += f"_{type_count[type_name]}"
        type_count[type_name] -= 1

    block_local_id = block['block_localId']
    result_var = str(int(block_local_id))  # Compute the result variable name

    generated_code_str += f"""
    def {subfunc_name}(V_{', V_'.join([var.replace(' ', '_') for var in block['inputVariables']])}):
        """
    if type_name == 'TON':
        generated_code_str += f"""
        import time
        state = {{'Q': False, 'ET': 0, 'is_active': False, 'last_update_time': time.time()}}

        def update():
            current_time = time.time()
            elapsed_time = current_time - state['last_update_time']

            if V_{block['inputVariables'][0]}:
                if not state['is_active']:
                    state['is_active'] = True
                    state['ET'] = 0
                    state['last_update_time'] = current_time

                state['ET'] += elapsed_time
                if state['ET'] >= V_20000000003:  # Use the input 'Preset Time' as the time limit
                    state['Q'] = True
            else:
                state['Q'] = False
                state['ET'] = 0
                state['is_active'] = False

        # Update the TON function just once
        update()
        V_{block_local_id} = state['Q']
        return V_{block_local_id}
        """

    elif type_name == 'TOF':
        generated_code_str += f"""
        import time
        state = {{'Q': False, 'ET': 0, 'last_update_time': time.time()}}

        def update():
            current_time = time.time()
            elapsed_time = current_time - state['last_update_time']

            if V_{block['inputVariables'][0]}:
                state['ET'] = 0
            elif not state['Q']:
                state['ET'] += elapsed_time
                if state['ET'] >= V_{block['inputVariables'][1]}:  # Use the input 'Time' as the time limit
                    state['Q'] = True

            state['last_update_time'] = current_time

        # Update the TOF function just once
        update()
        V_{block_local_id} = state['Q']
        return V_{block_local_id}
        """
    elif type_name == 'TP':
        generated_code_str += f"""
        import time
        state = {{'Q': False, 'is_active': False}}

        def update():
            if V_{block['inputVariables'][0]}:
                if not state['is_active']:
                    state['is_active'] = True
                    state['Q'] = True
            else:
                state['is_active'] = False
                state['Q'] = False

        update()
        V_{block_local_id} = state['Q']
        return V_{block_local_id}
        """

    elif type_name == 'RS':
        generated_code_str += f"""
        state = {{'Q': False}}

        def update():
            if V_{block['inputVariables'][1]}:  # If Reset input is True
                state['Q'] = False
            elif V_{block['inputVariables'][0]}:  # If Set input is True
                state['Q'] = True

        update()
        V_{block_local_id} = state['Q']
        return V_{block_local_id}
        """

    else:
        if type_name == 'XOR':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' ^ '.join(input_variables)}\n"
        elif type_name == 'AND':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' and '.join(input_variables)}\n"
        elif type_name == 'OR':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' or '.join(input_variables)}\n"
        elif type_name == 'NOT':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' not '.join(input_variables)}\n"
        elif type_name == 'R_TRIG':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {''.join(input_variables)}\n"
        elif type_name == 'ADD':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' + '.join(input_variables)}\n"
        elif type_name == 'LT':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' < '.join(input_variables)}\n"
        elif type_name == 'GE':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' >= '.join(input_variables)}\n"
        elif type_name == 'LE':
            input_variables = [f"V_{var.replace(' ', '_')}" for var in block['inputVariables']]
            generated_code_str += f"V_{result_var} = {' <= '.join(input_variables)}\n"

        generated_code_str += f"        return V_{result_var}\n\n"
    generated_code_str += f"""
    V_{block_local_id} = {subfunc_name}(V_{', V_'.join([var.replace(' ', '_') for var in block['inputVariables']])})
    """

for out_id in POU['output_ids']:
    out_var = out_id['OutVariable'].strip()
    generated_code_str += f"\n    " \
                          f"V_{out_var} = V_{out_var[:-1]}{int(out_var[-1]) - 1}"
    # print statement
    generated_code_str += f"\n    " \
                          f"print('Value of V_{out_var}:', V_{out_var})\n"

output_variables = []
for out_id in POU['output_ids']:
    out_var = out_id['OutVariable'].strip()
    output_variables.append(f"{out_var}:{{V_{out_var}}}")

# Rename BOOL as bool and TIME as int and INT as int
generated_code_str = generated_code_str.replace('BOOL', 'bool').replace('TIME', 'int').replace('INT', 'int').replace(
    'STRING', 'str').replace('CHAR', 'str').replace('WCHAR', 'str').replace('WSTRING', 'str')

# Write the generated code to a file
with open('generated_code_1.py', 'w') as file:
    file.write(generated_code_str)

    # return the output
    file.write(f"\n    return f\"{' '.join(output_variables)}\"\n")

    # Generate the run_cyclically function
    file.write('''
# External loop module
def run_cyclically():
    # Add str_to_bool and str_to_int functions inside run_cyclically
    def str_to_bool(s):
        return s.lower() in ('true', 't', '1')

    def str_to_int(s):
        try:
            return int(s)
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            return None

    for i in range(5):
        print(f"Iteration {i + 1}")
''')
    # Extract input variable names and types from the POU definition
    input_variable_names = [f"V_{input_id['InVariable'].strip()}" for input_id in POU['input_ids']]
    input_variable_types = [expression_to_type.get(input_id['Expression'], 'TIME') for input_id in POU['input_ids']]

    # Replace BOOL, TIME, and INT with bool, int, and int respectively in input_variable_types
    input_variable_types = [t.replace('BOOL', 'bool').replace('TIME', 'int').replace('INT', 'int') for t in input_variable_types]

    # Add input argument prompts using str_to_bool or str_to_int
    for var_name, var_type in zip(input_variable_names, input_variable_types):
        if var_type == 'bool':
            file.write(f"        {var_name} = str_to_bool(input(f\"Enter value for {var_name} ({var_type}): \"))\n")
        elif var_type == 'int':
            if var_name == 'V_T#200ms':
                file.write(f"        {var_name} = 200\n")  # Set a constant value for the time constant
            else:
                file.write(f"        {var_name} = str_to_int(input(f\"Enter value for {var_name} ({var_type}): \"))\n")
        else:
            file.write(f"        {var_name} = {var_type}(input(f\"Enter value for {var_name} ({var_type}): \"))\n")

    # Call the function specified in POU['pou_name'] with the input arguments
    function_name = POU['pou_name']
    file.write(f"        result = {function_name}(")
    file.write(", ".join(input_variable_names))
    file.write(")\n")

    # Print the result and add delay
    file.write("        print('Result:', result)\n")
    file.write("        time.sleep(3)\n")

    file.write("# Run the cyclic execution\n")
    file.write("run_cyclically()\n")


print("Generated code has been written to 'generated_code_1.py'.")






