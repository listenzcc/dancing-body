# %%
import numpy as np
import plotly.express as px
import json
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

# %%
folder = Path('../write-json-dance')
json_files = [e for e in folder.iterdir() if e.name.endswith('.json')]
print('Found {} json files'.format(len(json_files)))

# %%
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
file = data.iloc[0]['file']
file = json_files[500].name
print(file)

select = data.query('file == "{}"'.format(file))

dfs = []
for i in range(len(select)):
    d = select.iloc[i]['pose_keypoints_2d']
    person_id = select.iloc[i]['person_id']
    d = np.array(d).reshape(int(len(d)/3), 3)
    df = pd.DataFrame(d, columns=['x', 'y', 'z'])
    df['person_id'] = str(person_id)
    df['order'] = range(len(df))
    dfs.append(df)

df = pd.concat(dfs)
df

# %%
_df = df.copy()

# _df['size'] = 1
# _df['x'] *= 0.01
# _df['y'] *= 0.01

# fig = px.scatter_3d(_df, x='x', y='y', z='z',
#                     symbol='person_id', color='order', size='size', size_max=10)
# fig.update_layout(scene=dict(aspectmode="data"))


fig = px.scatter(_df.query('z > 0'), x='x', y='y',
                 symbol='person_id', color='order')
fig.update_layout(yaxis=dict(autorange="reversed"))
fig.update_layout(scene=dict(aspectmode="data"))

fig.show()
# %%
data

# %%
