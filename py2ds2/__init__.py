import json

def create_package(py_filename, ds2_filename, inputs=None, outputs=None):

    if inputs != None:
        with open(inputs, 'r') as input_file:
            inputs = json.load(input_file)
    else:
        inputs = []

    if outputs != None:
        with open(outputs, 'r') as output_file:
            outputs = json.load(output_file)
    else:
        outputs = []

    def transformVars(var):
        if var['type'] == "decimal":
            var['type'] = "double"
            var['set_type'] = "Double"
        if var['type'] == "character":
            var['type'] = "varchar"
            var['set_type'] = "String"
        if 'role' in var:
            if var['role'] == "input":
                var['role'] = ""
            if var['role'] == "output":
                var['role'] = "in_out"
        else:
            var['role'] = ""
        return var

    inputs = list(map(transformVars, inputs))
    outputs = list(map(transformVars, outputs))
    variables = inputs + outputs

    with open(py_filename, 'r') as py_file:
        with open(ds2_filename, 'w') as ds2_file:
            ds2_file.write("ds2_options sas;\n")
            ds2_file.write("package pyscore / overwrite=yes;\n")
            ds2_file.write("    dcl package pymas py;\n")
            ds2_file.write("    dcl double pystop;\n")
            ds2_file.write("    dcl package logger logr('App.tk.MAS');\n")
            ds2_file.write("\n")
            ds2_file.write("    method score(\n")

            if variables:
                firstvar = variables.pop(0)
                ds2_file.write(f"        {firstvar['role']} {firstvar['type']} \"{firstvar['name']}\"\n")

                for var in variables:
                    ds2_file.write(f"        , {var['role']} {var['type']} \"{var['name']}\"\n")

            ds2_file.write("    );\n")
            ds2_file.write("        dcl nvarchar(10485760) pypgm;\n")
            ds2_file.write("        dcl double rc;\n")
            ds2_file.write("        if null(py) and pystop ^= 1 then do;\n")
            ds2_file.write("            py = _new_ pymas();\n")

            for line in py_file:
                line = line.strip("\n")
                line = line.replace("'", "''")
                ds2_file.write(f"            rc = py.appendSrcLine('{line}');\n")

            ds2_file.write("            pypgm = py.getSource();\n")
            ds2_file.write("            revision = py.publish(pypgm, 'pyscore');\n")
            ds2_file.write("            if revision < 1 then do;\n")
            ds2_file.write("                pystop = 1;\n")
            ds2_file.write("                logr.log( 'e', 'publish revision=$s', revision );\n")
            ds2_file.write("                return;\n")
            ds2_file.write("            end;\n")
            ds2_file.write("            rc = py.useMethod('score');\n")
            ds2_file.write("            if rc then do;\n")
            ds2_file.write("                pystop = 1;\n")
            ds2_file.write("                logr.log( 'e', 'useMethod rc=$s', rc );\n")
            ds2_file.write("                return;\n")
            ds2_file.write("            end;\n")
            ds2_file.write("        end;\n")
            ds2_file.write("        if pystop ^= 1 then do;\n")

            for var in inputs:
                ds2_file.write(f"            rc = py.set{var['set_type']}('{var['name']}', {var['name']});\n")
                ds2_file.write(f"            if rc then do;\n")
                ds2_file.write(f"                logr.log('e', 'set {var['name']} rc=$s', rc);\n")
                ds2_file.write(f"                return;\n")
                ds2_file.write(f"            end;\n")

            ds2_file.write("            rc = py.execute();\n")
            ds2_file.write("            logr.log('d', 'execute rc=$s', rc);\n")

            for var in outputs:
                ds2_file.write(f"            {var['name']} = py.get{var['set_type']}('{var['name']}');\n")

            ds2_file.write("        end;\n")
            ds2_file.write("    end;\n")
            ds2_file.write("endpackage;\n")
