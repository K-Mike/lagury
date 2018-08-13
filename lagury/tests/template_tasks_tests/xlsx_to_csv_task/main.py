import sys
import json
import pprint
import glob
import os
import pandas as pd


if __name__ == '__main__':
    data = json.loads(sys.argv[1])

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)

    assert 'input_dirs' in data
    assert 'output_dir' in data
    assert 'parameters' in data

    # read xlsx file and save as csv

    excel_files = glob.glob(os.path.join(data['input_dirs'][0], '*.xlsx'))

    for path in excel_files:
        print(path)
        df = pd.read_excel(path)

        output_path = os.path.join(data['output_dir'], os.path.basename(path).rsplit('.', 1)[0] + '.csv')
        df.to_csv(output_path, index=False)
