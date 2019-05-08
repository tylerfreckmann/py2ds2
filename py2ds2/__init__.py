import json

def py2ds2(py_filename, ds2_filename, inputs=None, outputs=None):

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

def create_from_pickle(pickle_filename, X, model_function,
                       py_score_filename="score.py",
                       ds2_filename="score.sas",
                       inputVar_filename="inputVar.json",
                       outputVar_filename="outputVar.json"):
    '''
    Creates a SAS DS2 scoring package from a Python pickle file

    The pickle file should be a sci-kit learn pipeline that was fit on the pandas DataFrame X.
    A python scoring file (py_score_filename), a SAS DS2 scoring file that wraps the python scoring file (ds2_filename),
    and input and output variable files (inputVar.json, outputVar.json) are all created from the pickle file.

    Parameters
    ---------
    pickle_filename : string
        Specifies the path to the pickle file
    X : :class:`pandas.DataFrame`
        Specifies the pandas DataFrame that the sci-kit learn pipeline was fit on
    model_function : string
        Specifies the model function
        Valid Values: CLASSIFICATION, REGRESSION
    py_score_filename : string
        Specifies the path to the python scoring file that will be created
    ds2_filename : string
        Specifies the path to the SAS DS2 file that will be created
    inputVar_filename : string
        Specifies the path to the inputVar.json file that will be created
    outputVar_filename : string
        Specifies the path to the outputVar.json file that will be created

    '''
    inputs = list(X.dtypes.index)
    input_params = str(inputs).strip("[]").replace("'", "")
    input_df = str([f"'{name}': {name}" for name in inputs]).strip("[]").replace('"', '')
    input_json = []
    for n, t in zip(inputs, list(X.dtypes)):
        v = {}
        v['name'] = n
        v['type'] = 'decimal' if t.kind in 'iufcmM' else 'character'
        v['role'] = 'input'
        input_json.append(v)
    with open(inputVar_filename, 'w') as inputVar_file:
        json.dump(input_json, inputVar_file)
    if model_function == 'CLASSIFICATION':
        output = "EM_EVENTPROBABILITY"
    elif model_function == 'REGRESSION':
        output = "EM_PREDICTION"
    else:
        raise ValueError("model_function must be 'CLASSIFICATION' or 'REGRESSION'")
    output_json = [{'name': output, 'type': 'decimal', 'role': 'output'}]
    with open(outputVar_filename, 'w') as outputVar_file:
        json.dump(output_json, outputVar_file)

    with open(py_score_filename, 'w') as py_file:
        py_file.write("from sklearn.externals import joblib\n")
        py_file.write("import pandas as pd\n")
        py_file.write("\n")
        py_file.write(f"ml_pipe = joblib.load('{pickle_filename}')\n")
        py_file.write("\n")
        py_file.write(f"def score({input_params}):\n")
        py_file.write(f"    'Output: {output}'\n")
        py_file.write(f"    data = pd.DataFrame([{{{input_df}}}])\n")
        if model_function == 'CLASSIFICATION':
            py_file.write("    _, EM_EVENTPROBABILITY = ml_pipe.predict_proba(data)[0]\n")
            py_file.write("    return float(EM_EVENTPROBABILITY)\n")
        else:
            py_file.write("    EM_PREDICTION = ml_pipe.predict(data)[0]\n")
            py_file.write("    return float(EM_PREDICTION)\n")

    py2ds2(py_score_filename, ds2_filename, inputs=inputVar_filename, outputs=outputVar_filename)
