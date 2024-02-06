import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse('ABB_Joystick_Forward_Request.xml')
root = tree.getroot()

# Define the namespaces
ns = {'plcopen': 'http://www.plcopen.org/xml/tc6_0200', 'xhtml': 'http://www.w3.org/1999/xhtml'}

# Create the Python code file
with open('generated_code_0.py', mode='w') as file:
    file.write("import xml.etree.ElementTree as ET\n\n")

    # iterate through the function blocks and extract the required information
    for pou in root.findall('.//{http://www.plcopen.org/xml/tc6_0200}pou'):
        pou_name = pou.attrib['name']
        pou_type = pou.attrib['pouType']

        # extract the POU input variables and their types
        input_vars = []
        for var in pou.findall(
                './/{http://www.plcopen.org/xml/tc6_0200}inputVars/{http://www.plcopen.org/xml/tc6_0200}variable'):
            input_name = var.attrib['name']
            input_type = var.find('.//{http://www.plcopen.org/xml/tc6_0200}type').find('*').tag
            input_name = input_name.split('}')[1] if '}' in input_name else input_name
            input_type = input_type.split('}')[1] if '}' in input_type else input_type
            input_vars.append(f"{input_name}:{input_type}")

        #extract the POU input variables and their ID
        input_ids = []
        for var in pou.findall(".//{http://www.plcopen.org/xml/tc6_0200}inVariable"):
            expression = var.find("{http://www.plcopen.org/xml/tc6_0200}expression").text
            local_id = var.get('localId')
            input_ids.append({'Expression': expression, 'InVariable': f' {local_id}'})

        # extract the POU output variables and their types
        output_vars = []
        for var in pou.findall(
                './/{http://www.plcopen.org/xml/tc6_0200}outputVars/{http://www.plcopen.org/xml/tc6_0200}variable'):
            output_name = var.attrib['name']
            output_type = var.find('.//{http://www.plcopen.org/xml/tc6_0200}type').find('*').tag
            output_name = output_name.split('}')[1] if '}' in output_name else output_name
            output_type = output_type.split('}')[1] if '}' in output_type else output_type
            output_vars.append(f"{output_name}:{output_type}")

        #extract the POU output variables and their ID
        output_ids = []
        for var in pou.findall(".//{http://www.plcopen.org/xml/tc6_0200}outVariable"):
            expression = var.find("{http://www.plcopen.org/xml/tc6_0200}expression").text
            local_id = var.get('localId')
            output_ids.append({'Expression': expression, 'OutVariable': f' {local_id}'})

        # extract the POU local variables and their types
        local_vars = []
        for var in pou.findall(
                './/{http://www.plcopen.org/xml/tc6_0200}localVars/{http://www.plcopen.org/xml/tc6_0200}variable'):
            local_name = var.attrib['name']

            local_type_elem = var.find('.//{http://www.plcopen.org/xml/tc6_0200}type')
            local_type = local_type_elem.find('.//{http://www.plcopen.org/xml/tc6_0200}derived')

            if local_type is not None:
                local_type_name = local_type.attrib.get('name', "")
                local_type_name = local_type_name.split('}')[1] if '}' in local_type_name else local_type_name
            else:
                local_type_name = "UnknownType"  # Set a default type if 'derived' is not found

            local_name = local_name.split('}')[1] if '}' in local_name else local_name
            local_vars.append(f"{local_name}:{local_type_name}")

        # Loop through each block
        for index, block in enumerate(root.findall('.//plcopen:block', ns)):
            # Get the block localId
            B_local_id = block.attrib['localId']
            B_dict_name = f"B{index + 1}"  # Generate dictionary name like B1, B2, B3, etc.

            # Get the typeName
            B_type_name = block.attrib['typeName']

            # Get the position
            B_position = block.find('plcopen:position', ns).attrib

            # Get the inputVariables
            B_input_vars = []
            for input_var in block.findall('.//plcopen:inputVariables/plcopen:variable', ns):
                input_local_id = input_var.find('.//plcopen:connection', ns).attrib['refLocalId']
                B_input_vars.append(input_local_id)

            # Get the variable formalParameter
            B_var_formal_param = []
            for var in block.findall('.//plcopen:variable', ns):
                B_var_formal_param.append(var.attrib['formalParameter'])

            # Get the connectionPointIn and connection refLocalId
            B_conn_point_in = []
            B_conn_ref_local_id = []
            for conn_point in block.findall('.//plcopen:connectionPointIn', ns):
                B_conn_point_in.append(conn_point.tag.split('}')[-1])
                B_conn_ref_local_id.append(conn_point.find('plcopen:connection', ns).attrib['refLocalId'])

            # Write the extracted information about EACH BLOCK into the Python code file
            file.write(f"{B_dict_name} = {{\n")
            file.write(f"\t'pou_name': '{pou_name}',\n")
            file.write(f"\t'block_localId': '{B_local_id}',\n")
            file.write(f"\t'typeName': '{B_type_name}',\n")
            file.write(f"\t'position': {B_position},\n")
            file.write(f"\t'inputVariables': {B_input_vars},\n")
            file.write(f"\t'variableFormalParameter': {B_var_formal_param},\n")
            file.write(f"\t'connectionPointIn': {B_conn_point_in},\n")
            file.write(f"\t'connectionRefLocalId': {B_conn_ref_local_id}\n")
            file.write("}\n\n")

        # write the extracted information about the POU into the Python code file
        file.write(f"POU = {{\n")
        file.write(f"\t'pou_name': '{pou_name}',\n")
        file.write(f"\t'pou_type': '{pou_type}',\n")
        file.write(f"\t'input_vars': {input_vars},\n")
        file.write(f"\t'input_ids': {input_ids},\n")
        file.write(f"\t'output_vars': {output_vars},\n")
        file.write(f"\t'output_ids': {output_ids},\n")
        file.write(f"\t'local_vars': {local_vars}\n")
        file.write("}\n\n")






