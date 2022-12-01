import pandas as pd
import wfdb
import numpy as np
import os
from glob import glob
import shutil
import wget


dataUrl = 'https://physionet.org/static/published-projects/ecg-arrhythmia/a-large-scale-12-lead-electrocardiogram-' \
          'database-for-arrhythmia-study-1.0.0.zip'

zip_file_name = wget.download(dataUrl)

shutil.unpack_archive(zip_file_name, './', 'zip')

dataPath = zip_file_name[:-4]

files = [y[:-4] for x in os.walk(dataPath) for y in glob(os.path.join(x[0], '*.mat'))]
size = len(files)

all_signals = np.zeros([size*12, 100])
ages = np.zeros(size*12)
genders = np.zeros(size*12)
diagnoses = [""] * size * 12
IDs = np.zeros([size*12])
index = 0

for file in files[:size]:
    try:
        signals, fields = wfdb.rdsamp(file)
        all_signals[index * 12:index * 12 + 12, ] = signals.T[:, ::50]
        ages[index * 12:index * 12 + 12, ] = [int(fields['comments'][0].split(' ')[1])] * 12
        genders[index * 12:index * 12 + 12] = [int(fields['comments'][1].split(' ')[1] == 'Male')] * 12
        diagnoses[index * 12:index * 12 + 12] = [fields['comments'][2].split(' ')[1]] * 12
        IDs[index * 12:index * 12 + 12] = [index] * 12
        index += 1
    except Exception as e:
        print(e)

    if index % 1000 == 0:
        print(index)

dataX = np.concatenate([IDs.reshape(size*12, 1),
                        ages.reshape(size*12, 1), genders.reshape(size*12, 1), all_signals], axis=1)

df = pd.DataFrame(dataX, columns=['ID', 'Age', 'Gender'] + list(range(0, 100)))

data = pd.concat([df, pd.Series(diagnoses).rename('Diagnoses')], axis=1)


df = pd.concat([df.iloc[:12], df[df.ID != 0]])

df.to_csv('all_ecg.csv', index=False)
