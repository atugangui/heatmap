# -*- coding: utf-8 -*-
"""seaborn-heatmap-all-regions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10_QgZ199zEk4W5fl2npS-z-6vkMIAtlG
"""

#@title
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
import seaborn as sb
import numpy as np
from urllib.request import urlopen
import json
import re

#@title
all_trio = [
    'SW180509-01A_aavretro',
    'SW180509-02A_enva',
    'SW180509-05A_enva',
    'SW180510-01A_enva',
    #'SW180606-01A_aav8',
    #'SW180606-01A_aavretro',
    #'SW180606-01A_enva',
    'SW180606-05A_aav8',
    'SW180606-05A_aavretro',
    'SW180606-05A_enva',
    'SW181217-01A_aav8',
    'SW181217-01A_aavretro',
    'SW181217-01A_enva',
    'SW181217-02A_enva',
    'SW181219-01A_enva',
    'SW181219-02A_enva',
    'SW181219-03A_enva',
    'SW181219-04A_enva'
]

all_rabies = [
    'SW180509-02A_enva',
    'SW180509-05A_enva',
    'SW180510-01A_enva',
    #'SW180606-01A_enva',
    'SW180606-05A_enva',
    'SW181217-01A_enva',
    'SW181217-02A_enva',
    'SW181219-02A_enva',
    'SW181219-03A_enva',
    'SW181219-04A_enva',
    'SW181219-01A_enva'
]

all_aav2retro = [
    'SW180509-01A_aavretro',
    #'SW180606-01A_aavretro',
    'SW180606-05A_aavretro',
    'SW181217-01A_aavretro'
]

all_aav8 = [
    #'SW180606-01A_aav8',
    'SW180606-05A_aav8',
    'SW181217-01A_aav8'
]

#@title
codeurl = urlopen('https://raw.githubusercontent.com/tugangui/heatmap/main/code.json')
code = json.loads(codeurl.read())
regionsurl = urlopen('https://raw.githubusercontent.com/tugangui/heatmap/main/regions.json')
regions = json.loads(regionsurl.read())
mappingsurl = urlopen('https://raw.githubusercontent.com/tugangui/heatmap/main/mappings.json')
mappings = json.loads(mappingsurl.read())
mappings = mappings['cembaMappings']['mappings'][0]
blobs = {}
structuresToBrainAreasDf = pd.read_csv('https://github.com/tugangui/heatmap/raw/main/structures.csv')


def splitSlice(sliceName):
    match = re.match(r"([0-9]+)([A-Z]+)", sliceName, re.I)
    items = ()
    if match:
        items = match.groups()
    return items[0]

for key in mappings:
    lowerbound = int(mappings[key]['lowerBound'])
    upperbound = int(mappings[key]['upperBound'])
    sliceNo = splitSlice(key)
    for i in range(lowerbound, upperbound):
      blobs[i] = sliceNo

def getBrainAreaID(key):
    row = structuresToBrainAreasDf.loc[structuresToBrainAreasDf.iloc[:,1]== key]
    if row.empty:
      return ""
    else:
      return (row.iloc[:,3]).iloc[0]

"""# Heatmaps using ARA ROI and all Cases"""

#@title
def create_heatmap(files, tracer):
    df = pd.concat((pd.read_csv('https://github.com/tugangui/heatmap/raw/main/'+f+'.csv') for f in files))
    df_m = df.copy()
    df_m = df_m[(df_m['ARA Level'] > 26) & (df_m['ARA Level'] < 99)]
    df_m['BRAIN AREA ID'] = df_m['REGION'].map(getBrainAreaID)
    brain_area_ids = df_m['BRAIN AREA ID']
    df_m = df_m.groupby(['Project Name','Tracer','REGION', 'BRAIN AREA ID'])[['OVERLAP']].sum()
    df_m = df_m.pivot_table(index=['BRAIN AREA ID', 'REGION'], columns=['Tracer','Project Name'], values='OVERLAP')
    plt.figure(figsize=(20, 60))

    cpalette = ''
    if tracer == 'EnvA Rabies':
        cpalette = "Reds"
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'rkrkrkrkr'))
    if tracer == 'AAV8':
        cpalette = 'Greens'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'gkgkgkgkg'))
    if tracer == 'AAV2Retro':
        cpalette = 'Purples'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'mkmkmkmkm'))
    elif tracer == 'TRIO':
        cpalette = 'YlGnBu'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'bkbkbkbkb'))
    g = sb.heatmap(df_m, cmap=cpalette, annot=False, fmt="g",annot_kws={'size':10}, linewidths=1, cbar_kws={'label': 'Cell Bodies'})

    for tick_label in g.axes.get_yticklabels():
      tick_text = tick_label.get_text().split("-")[0]
      if(len(tick_text)>0):
        tick_label.set_color(row_colors_dict[tick_text])

    if tracer == 'TRIO':
          #AAV8
          for i in range(2):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#98e698', lw=1))
          
          #AAVRetro
          for i in range(2,5):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#d9b3ff', lw=1))
          
          #EnvA RB
          for i in range(5, len(files)):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#ff8080', lw=1))


    # axes
    plt.xlabel('Case ID')
    plt.ylabel('Region')

    # title
    plt.title(tracer + 'Overlap Data', loc='center')

    plt.savefig('./heatmaps/ARA_ROI_ALL_CASES_'+tracer+'.png')
    #plt.show()
    plt.close()

"""Heatmap with all TRIO cases, all channels"""

#@title
create_heatmap(all_trio, 'TRIO')

"""TVA-GFP virus"""

#@title
create_heatmap(all_aav8, 'AAV8')

"""Retro-Cre"""

#@title
create_heatmap(all_aav2retro, 'AAV2Retro')

"""EnvA Rabies"""

#@title
create_heatmap(all_rabies, 'EnvA Rabies')

"""# ARA ROI/ARA Levels
## SW181217-01A

"""

def create_heatmap_with_levels(file, tracer):
    df = pd.read_csv('https://github.com/tugangui/heatmap/raw/main/'+file+'.csv')
    df_m = df.copy()
    df_m = df_m[(df_m['ARA Level'] > 26) & (df_m['ARA Level'] < 99)]
    df_m['BRAIN AREA ID'] = df_m['REGION'].map(getBrainAreaID)
    brain_area_ids = df_m['BRAIN AREA ID']
    df_m = df_m.groupby(['ARA Level','REGION', 'BRAIN AREA ID'])[['OVERLAP']].sum()
    df_m = df_m.pivot_table(index=['BRAIN AREA ID', 'REGION'], columns=['ARA Level'], values='OVERLAP')
    plt.figure(figsize=(20, 60))

    cpalette = ''
    if tracer == 'EnvA Rabies':
        cpalette = "Reds"
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'rkrkrkrkr'))
    if tracer == 'AAV8':
        cpalette = 'Greens'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'gkgkgkgkg'))
    if tracer == 'AAV2Retro':
        cpalette = 'Purples'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'mkmkmkmkm'))
    elif tracer == 'TRIO':
        cpalette = 'YlGnBu'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'bkbkbkbkb'))
    g = sb.heatmap(df_m, cmap=cpalette, annot=False, fmt="g",annot_kws={'size':10}, linewidths=1, cbar_kws={'label': 'Cell Bodies'})

    if tracer == 'TRIO':
          #AAV8
          for i in range(2):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#98e698', lw=1))
          
          #AAVRetro
          for i in range(2,5):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#d9b3ff', lw=1))
          
          #EnvA RB
          for i in range(5, len(files)):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#ff8080', lw=1))


    # axes
    plt.xlabel('ARA Level')
    plt.ylabel('ROI')

    # title
    caseId = file.split('_')[0]
    plt.title(caseId + ' ' + tracer + ' Overlap Data', loc='center')
    plt.savefig('./heatmaps/ARA_ROI_ARA_LEVELS_' + caseId + '_' + tracer + '.png')
    #plt.show()
    plt.close()

"""EnvA Rabies"""

for fileName in all_rabies:
  create_heatmap_with_levels(fileName, 'EnvA Rabies')

"""Retro-Cre"""

for fileName in all_aav2retro:
  create_heatmap_with_levels(fileName, 'AAV2Retro')

"""TVA-GFP"""

for fileName in all_aav8:
  create_heatmap_with_levels('SW181217-01A_aav8', 'AAV8')

"""# ARA ROI and Cemba slices
## SW181217-01A
"""

def get_cemba_slice(level):
    return ((level - 21) //6 ) + 1

def create_heatmap_with_cemba(file, tracer):
    df = pd.read_csv('https://github.com/tugangui/heatmap/raw/main/'+file+'.csv')
    df_m = df.copy()
    df_m['BRAIN AREA ID'] = df_m['REGION'].map(getBrainAreaID)
    df_m['CEMBA SLICE'] = df_m['ARA Level'].map(get_cemba_slice)
    brain_area_ids = df_m['BRAIN AREA ID']
    df_m = df_m.groupby(['CEMBA SLICE','REGION', 'BRAIN AREA ID'])[['OVERLAP']].sum()
    df_m = df_m.pivot_table(index=['BRAIN AREA ID', 'REGION'], columns=['CEMBA SLICE'], values='OVERLAP')
    plt.figure(figsize=(20, 60))

    cpalette = ''
    if tracer == 'EnvA Rabies':
        cpalette = "Reds"
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'rkrkrkrkr'))
    if tracer == 'AAV8':
        cpalette = 'Greens'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'gkgkgkgkg'))
    if tracer == 'AAV2Retro':
        cpalette = 'Purples'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'mkmkmkmkm'))
    elif tracer == 'TRIO':
        cpalette = 'YlGnBu'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'bkbkbkbkb'))
    g = sb.heatmap(df_m, cmap=cpalette, annot=False, fmt="g",annot_kws={'size':10}, linewidths=1, cbar_kws={'label': 'Cell Bodies'})

    if tracer == 'TRIO':
          #AAV8
          for i in range(2):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#98e698', lw=1))
          
          #AAVRetro
          for i in range(2,5):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#d9b3ff', lw=1))
          
          #EnvA RB
          for i in range(5, len(files)):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#ff8080', lw=1))


    # axes
    plt.xlabel('Cemba slice')
    plt.ylabel('ROI')

    # title
    caseId = file.split('_')[0]
    plt.title(caseId + ' ' + tracer + ' Overlap Data', loc='center')
    plt.savefig('./heatmaps/ARA_ROI_CEMBA_SLICES_' + caseId + '_' + tracer + '.png')
    plt.show()
    plt.close()

"""EnvA Rabies"""

for fileName in all_rabies:
  create_heatmap_with_cemba(fileName, 'EnvA Rabies')

"""TVA-GFP"""

for fileName in all_aav8:
  create_heatmap_with_cemba(fileName, 'AAV8')

"""Retro-Cre"""

for fileName in all_aav2retro:
  create_heatmap_with_cemba(fileName, 'AAV2Retro')

"""# ARA ROI/Cemba Slices, Ipsilateral & Contralateral
## SW181217-01A
"""

def create_heatmap_with_levels_hemisphere(file, tracer, hemisphere):
    df = pd.read_csv('https://github.com/tugangui/heatmap/raw/main/'+file+'.csv')
    df_m = df.copy()
    df_m = df_m[~df_m['(HEMISPHERE:R:G:B)'].str.contains(hemisphere)]
    compression_opts = dict(method='zip',archive_name='out.csv')  
    df_m.to_csv('out.zip',compression=compression_opts)
    df_m = df_m[(df_m['ARA Level'] > 26) & (df_m['ARA Level'] < 99)]
    df_m['BRAIN AREA ID'] = df_m['REGION'].map(getBrainAreaID)
    brain_area_ids = df_m['BRAIN AREA ID']
    df_m = df_m.groupby(['ARA Level','REGION', 'BRAIN AREA ID'])[['OVERLAP']].sum()
    df_m = df_m.pivot_table(index=['BRAIN AREA ID', 'REGION'], columns=['ARA Level'], values='OVERLAP')
    plt.figure(figsize=(20, 60))

    cpalette = ''
    if tracer == 'EnvA Rabies':
        cpalette = "Reds"
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'rkrkrkrkr'))
    if tracer == 'AAV8':
        cpalette = 'Greens'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'gkgkgkgkg'))
    if tracer == 'AAV2Retro':
        cpalette = 'Purples'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'mkmkmkmkm'))
    elif tracer == 'TRIO':
        cpalette = 'YlGnBu'
        row_colors_dict = dict(zip(brain_area_ids.unique(), 'bkbkbkbkb'))
    g = sb.heatmap(df_m, cmap=cpalette, annot=False, fmt="g",annot_kws={'size':10}, linewidths=1, cbar_kws={'label': 'Cell Bodies'})

    if tracer == 'TRIO':
          #AAV8
          for i in range(2):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#98e698', lw=1))
          
          #AAVRetro
          for i in range(2,5):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#d9b3ff', lw=1))
          
          #EnvA RB
          for i in range(5, len(files)):
            for j in range(700):
              g.add_patch(Rectangle((i, j), 1, 1, fill=False, edgecolor='#ff8080', lw=1))


    # axes
    plt.xlabel('ARA Level')
    plt.ylabel('ROI')

    # title
    caseId = file.split('_')[0]
    if(hemisphere == 'r'):
      plt.title(caseId + ' ' + tracer + ' Overlap Data: Contralateral', loc='center')
      plt.savefig('./heatmaps/ARA_ROI_CEMBA_SLICES_' + caseId + '_' + tracer + '_Contralateral.png')
    else:
      plt.title(caseId + ' ' + tracer + ' Overlap Data: Ipsilateral', loc='center')
      plt.savefig('./heatmaps/ARA_ROI_CEMBA_SLICES_' + caseId + '_' + tracer + '_Ipsilateral.png')

    plt.show()
    plt.close()

"""EnvA Rabies"""

for fileName in all_rabies:
  create_heatmap_with_levels_hemisphere(fileName, 'EnvA Rabies', 'l')
  create_heatmap_with_levels_hemisphere(fileName, 'EnvA Rabies', 'r')

for fileName in all_aav2retro:
  create_heatmap_with_levels_hemisphere(fileName, 'AAV2Retro', 'l')
  create_heatmap_with_levels_hemisphere(fileName, 'AAV2Retro', 'r')

for fileName in all_aav8:
  create_heatmap_with_levels_hemisphere(fileName, 'AAV8', 'l')
  create_heatmap_with_levels_hemisphere(fileName, 'AAV8', 'r')