# %%
import numpy as np
import plotly.express as px
import json
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

# %%
# Set the folder path of the frames
folder = Path('../write-json-dance')

# %%
# Load data from frames
json_files = [e for e in folder.iterdir() if e.name.endswith('.json')]
print('Found {} json files'.format(len(json_files)))

dfs = []
for p in tqdm(json_files, 'Read Files'):
    dct = json.load(open(p, 'rb'))

    people = dct['people']

    for i, peo in enumerate(people):
        peo['person_id'] = i

    df = pd.DataFrame(people)

    df['file'] = p.name
    dfs.append(df)

data = pd.concat(dfs)
data = data[['person_id', 'pose_keypoints_2d', 'file']]
data['n'] = data['pose_keypoints_2d'].map(len)
data


# %%
'''
Parse frames

The first person in the first frame is tracked,
and the output table contains the positions of the joint in the frames.
'''

latest = None


def _feature(lst):
    '''
    Compute feature value

    The feature is computed as the L1 distance between the points in the current and latest frame.
    So, the user makes sure that the first people found in the first frame is the target person.
    '''

    if latest is None:
        return 0

    lst = [a-b for a, b in zip(lst, latest)]

    x = lst[0::3]
    y = lst[1::3]

    # Only test for the valid points in the latest frame
    z = latest[0+2::3]

    x = [e for e, a in zip(x, z) if a != 0]
    y = [e for e, a in zip(y, z) if a != 0]

    return np.sum([np.abs(e) for e in x]) + np.sum([np.abs(e) for e in y])


dfs = []
for j, file_path in tqdm(enumerate(json_files), 'Parse Frame'):
    file = file_path.name

    select = data.query('file == "{}"'.format(file)).copy()
    select['feature'] = select['pose_keypoints_2d'].map(_feature)
    select = select.sort_values(by='feature', ascending=True)

    for i in range(len(select)):
        d = select.iloc[i]['pose_keypoints_2d']
        person_id = select.iloc[i]['person_id']
        d = np.array(d).reshape(int(len(d)/3), 3)
        df = pd.DataFrame(d, columns=['x', 'y', 'z'])
        df['person_id'] = str(person_id)
        df['order'] = range(len(df))
        df['frame'] = j
        dfs.append(df)
        # We only need the first one
        break

    latest = select.iloc[i]['pose_keypoints_2d']

table = pd.concat(dfs)
table

# %%
# Save the table
df = table
df.to_csv('data.csv')
df


# %%
# Show the points
if __name__ == '__main__':
    fig = px.scatter(df, x='x', y='y', color='frame', opacity=0.5)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.show()

# %%
