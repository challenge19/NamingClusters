# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:03:38 2019

@author: Zhesi Shen(zhesi.shen@live.com)
"""

__all__ = ['add_background','map_cate_color']

# load package
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm

import plotly.graph_objs as go
from plotly import tools
import chart_studio.plotly as py


    ### 绘制领域背景轮廓
def map_cate_color(cate,alpha=None):
    norm = mpl.colors.Normalize(vmin=0, vmax=10)
    cmap = cm.tab10

    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    def map_cluster_color(color,alpha=None):
        r,g,b,a = color
        if alpha:
            a = alpha
        color = f'rgba({r*255},{g*255},{b*255},{a})'
        return color
    return map_cluster_color(m.to_rgba(cate),alpha=1)

# function：绘制领域区域背景 ad_background(traces)
def add_background():
    import matplotlib as mpl
    import matplotlib.cm as cm

    ### 绘制领域背景轮廓
    norm = mpl.colors.Normalize(vmin=0, vmax=10)
    cmap = cm.tab10

    m = cm.ScalarMappable(norm=norm, cmap=cmap)

    patches = []
    polygons = {1:[[-0.3054,  0.4882],
           [ -0.06558,  0.6176],
           [-0.00106 ,  0.8943],
           [-0.2701,  0.96708],
           [-0.3588,  0.969],
           [-0.4284,  0.8409],
           [-0.6663,  0.5846],
           [-0.6471,  0.5094],
           [-0.6141,  0.4173]],
               2:[[-0.0152, -0.3535],
           [-0.332,  0.2955],
           [-0.6042,  0.5645],
           [-0.6388,  0.5538],
           [-0.7638,  0.491 ],
           [-1.0806,  0.0317],
           [-1.0525, -0.228 ],
           [-0.9927, -0.3101],
           [-0.884 , -0.3724],
           [-0.6641, -0.4634],
           [-0.3267, -0.5432]],
               3:[
           [0.4755,-0.05],
           [-0.0228, -0.2386],
           [-0.0877, -0.2473],
           [-0.0568, -0.4285],
           [ 0.1058, -0.4901],
           [ 0.6413, -0.4705],
           [ 0.8089, -0.4637],
           [ 1.021 , -0.3942],
           [ 1.173 , -0.3011],
           [ 1.277, -0.2181],
           [ 1.385013, -0.0166],
           [ 1.3406,  0.168 ],
           [ 1.23115,  0.256],
           [ 0.9702,  0.3622],
           ],
               4:[[-0.2009,  0.1008],
           [-0.2615,  0.07615],
           [-0.2948,  0.0613],
           [-0.3695, -0.13  ],
           [-0.4882, -0.3824],
           [-0.4418, -0.4051],
           [ 0.5906, -0.1585],
           [ 0.8886,  0.0777],
           [ 0.8468,  0.1636],
           [ 0.2977,  0.29306]],
               5:[[0.5635, 0.2838],
           [0.9986, 0.1296],
           [1.31315, 0.2288],
           [1.3778, 0.4191],
           [1.3707, 0.44968],
           [1.1269 , 0.5053],
           [0.8315, 0.62005881],
           [0.2388, 0.581 ],
           [0.3391, 0.4194]]}
    polygons = {i:np.array(polygons[i]) for i in polygons}
    
    labels = {1:'Social sciences and humanities',
          2:'Biomedical and health sciences',
          3:'Physical sciences and engineering',
          4:'Life and earth sciences',
          5:'Mathematics and computer sciense'}
    
    def map_cluster_color(color,alpha=None):
        r,g,b,a = color
        if alpha:
            a = alpha
        color = f'rgba({r*255},{g*255},{b*255},{a})'
        return color

    for i in [1,2,3,4,5]:
        trace = go.Scatter(x=polygons[i][:,0],y=polygons[i][:,1],
                           fill='toself',
                           #fillcolor='rgba(240,0,0,0.1)',
                           fillcolor=map_cluster_color(m.to_rgba(i),alpha=0.3),
                           #line_color=map_cluster_color(m.to_rgba(i),alpha=1),
                           hoveron='points',
                           mode= 'none',
                           hoverinfo = "none",
                           name=f"{labels[i]}"
                           )
        patches.append(trace)
    return patches