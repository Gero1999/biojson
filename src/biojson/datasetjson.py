def read_datasetjson(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    columns = [col['name'] for col in data['columns']]
    rows = data['rows']
    labels = [col['label'] for col in data['columns']]
    datatypes = {col['name']: col.get('dataType', 'string') for col in data['columns']}

    df = pd.DataFrame(rows, columns=columns)

    # Convert columns to appropriate types
    for col, dtype in datatypes.items():
        if dtype == 'date' or dtype == 'datetime':
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif dtype == 'integer':
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        elif dtype == 'float' or dtype == 'double' or dtype == 'number':
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif dtype == 'boolean':
            df[col] = df[col].map(lambda x: True if x is True or x == 'Y' or x == 'TRUE' else (False if x is False or x == 'N' or x == 'FALSE' else pd.NA))
        else:
            df[col] = df[col].astype('string')

    df.attrs['labels'] = dict(zip(columns, labels))
    return df

# Create a function to convert a dataset in R to datasetJSON format
# Write a function to write a pandas DataFrame to a datasetJSON file
# for metadata, if the arg is not specified use a default (i.e, date of json creation put actual)
import json
import pandas as pd
def write_datasetjson(df, file_path, name = None, label = None, datasetJSONVersion = "1.1.0", dbLastModifiedDateTime = None, studyOID = None, metaDataVersionOID = None, metaDataRef = None, itemGroupOID = None):

    if datasetJSONVersion != "1.1.0":
        raise ValueError("Only datasetJSON version 1.1.0 is supported.")

    data = {}
    from datetime import datetime
    data['datasetJSONCreationDateTime'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    data['datasetJSONVersion'] = datasetJSONVersion
    data['fileOID'] = "generated.by.biojson"
    data['dbLastModifiedDateTime'] = dbLastModifiedDateTime if dbLastModifiedDateTime else datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    data['originator'] = "biojson"
    data['sourceSystem'] = {
        "name": "biojson",
        "version": "1.0.0"
    }
    data['studyOID'] = studyOID if studyOID else "unknown.study"
    data['metaDataVersionOID'] = metaDataVersionOID if metaDataVersionOID else "unknown.mdv"
    data['metaDataRef'] = metaDataRef if metaDataRef else "http://unknown.metadata.ref"
    data['itemGroupOID'] = itemGroupOID if itemGroupOID else "IG.UNKNOWN"
    data['records'] = len(df)
    data['name'] = name if name else "UNKNOWN"
    data['label'] = label if label else "Unknown Label"


    columns = []
    df_to_write = df.copy()
    for col in df.columns:
        # Determine dataType for JSON schema
        dtype = df[col].dtype
        if pd.api.types.is_datetime64_any_dtype(dtype):
            dataType = 'date'
            df_to_write[col] = df_to_write[col].dt.strftime("%Y-%m-%d")
        elif pd.api.types.is_integer_dtype(dtype):
            dataType = 'integer'
            # Ensure integers remain as int, not string
            df_to_write[col] = df_to_write[col].astype('Int64')
        elif pd.api.types.is_float_dtype(dtype):
            dataType = 'float'
        elif pd.api.types.is_bool_dtype(dtype):
            dataType = 'boolean'
        else:
            dataType = 'string'
            df_to_write[col] = df_to_write[col].astype('string')
        col_meta = {
            "itemOID": f"IT.{data['itemGroupOID']}.{col}",
            "name": col,
            "label": df.attrs.get('labels', {}).get(col, col),
            "dataType": dataType
        }
        columns.append(col_meta)
    data['columns'] = columns

    data['rows'] = df_to_write.where(pd.notnull(df_to_write), None).values.tolist()

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

