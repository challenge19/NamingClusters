# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:17:18 2019

@author: Zhesi Shen(zhesi.shen@live.com)
"""

import dash
from dash_bootstrap_components._components.CardBody import CardBody
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
from dash import no_update
from flask import session, copy_current_request_context
from flask_login import logout_user, current_user

import pandas as pd
from dash.dependencies import Input, Output, State
import json
import codecs
from datetime import datetime
import plotly.graph_objs as go
from figure_plotly import *

# local imports
from auth import authenticate_user, validate_login_session
from server import app, server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'width':'45%',
        'display': 'inline-block'
    }
}


with codecs.open('./result/labeled_cluster_micro.txt','r','utf8') as f:
  labeled_cluster = json.load(f)

# write labeled cluster to file
def write_tofile(labeled_cluster,filename):
    with codecs.open(filename, 'w', 'utf8') as json_file:
      json.dump(labeled_cluster, json_file)


# load excel file for map
data_dir = "./data/"
level = "micro"
df_map = pd.read_excel(f"{data_dir}/{level}_for_dash.xlsx")


df_profile = {}
for level in ['micro']:
    df_profile[level] = pd.read_excel(f'{data_dir}/journal_profile_{level}_2019_cwts2020_compressed.xlsx')
    df_profile[level]['total'] = df_profile[level].groupby(level)['N'].transform('sum')
    df_profile[level]['frac'] = df_profile[level]['N']/df_profile[level]['total']

labels = {1:'Social sciences and humanities',
          2:'Biomedical and health sciences',
          3:'Physical sciences and engineering',
          4:'Life and earth sciences',
          5:'Mathematics and computer sciense'}


## load papers
df_tiab = pd.read_excel(f'{data_dir}/待判别62clusters.xlsx',sheet_name='主要论文与关键词')
target_clusters = list(df_tiab['micro_level_field_id'].unique())

df_ins = pd.read_excel(f'{data_dir}/待判别62clusters.xlsx',sheet_name='主要机构')
# formulate marker text

df_map['journals']=df_map['journals'].apply(lambda x:x.split(';'))
df_map['keywords']=df_map['keywords'].apply(lambda x:x.split(';'))
df_map['journals_tab'] = df_map['journals'].apply(lambda x:[html.Tr(f"{x[i].strip()}") for i in range(len(x))])
df_map['keywords_tab'] = df_map['keywords'].apply(lambda x:[html.Tr(f"{x[i].strip()}") for i in range(len(x))])
df_map['idx'] = df_map['id']
df_map.set_index('idx',inplace=True)

df_map = df_map[df_map['id'].isin(target_clusters)]

def text(row):
    journals = ["代表性期刊："]+[f"{jour}" for jour in row['journals']]+['','']
    terms = ["代表性关键词："]+[f"{term}" for term in row['keywords']]
    #y = [f'N:{row["N"]}',f'CSI:{row["CSI"]}',f'IF:{row["IF"]}',y]
    y = [f'主题编号：{row["label"]}','']+journals+terms
    y = '<br>'.join(y)
    return y
df_map['text'] = df_map.apply(lambda x:text(x), axis=1)




# login layout content
def login_layout():
    return html.Div(
        [
            dcc.Location(id='login-url',pathname='/login',refresh=False),
            html.H1(children=' Paper-level Cluster Mapping and Labeling'),

            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.H4('Login',className='card-title'),
                                    dbc.Input(id='login-user',placeholder='User name'),
                                    dbc.Input(id='login-password',placeholder='Assigned password',type='password'),
                                    dbc.Button('Submit',id='login-button',color='success',block=True),
                                    html.Br(),
                                    html.Div(id='login-alert')
                                ],
                                body=True
                            ),
                            width=6
                        ),
                        justify='center'
                    )
                ]
            )
        ]
    )




# home layout content
@validate_login_session
def app_layout():
    journal_tab = dbc.Card(
        dbc.CardBody(
            dcc.Graph(id='journal-treemap')
        ),
        className='mt-3',
    )

    wordcloud_tab = dbc.Card(
        dbc.CardBody(
            html.Div('wordcloud')
        ),
        className='mt-3',
    )

    inst_tab = dbc.Card(
        dbc.CardBody(
            html.Div(id='insts')
        ),
        className='mt-3',
    )

    paper_tab = dbc.Card(
        dbc.CardBody(
            html.Div(id='paper')
        ),
        className='mt-3',
    )

    
    user_name = session.get('username',None)



    return \
    html.Div([
        dcc.Location(id='home-url',pathname='/home'),
        html.H1(children=' Paper-level Cluster Mapping and Labeling'),
        dbc.Row(
            [
                dbc.Col(html.Div(children='  Visulization of CWTS paper-level clusters.'), width='auto'),
                dbc.Col([html.Div(id='showusername',children=f'login: {user_name}'),
                        html.Div(id='autosave',children='Not saved')], width='auto'),
                dbc.Col(
                        dbc.Button('Logout',id='logout-button',color='danger',block=True,size='m'),
                        width=2
                        ),
            ],
            justify='around',
        ),
        
        dcc.Interval(
            id='interval-component',
            interval=600*1000,
            n_intervals=0
        ),
        
        dcc.Graph(
            id='cluster-map',
        ),

        dbc.Row([
            dbc.Col([
                html.H6('主题编号'),
                html.Div(id='cluster',children='NA'),
                html.H6('标签'),
                html.Div(id='labeled-name'),
            ],width={'offset':1}),

            dbc.Col([
                html.H6("代表性期刊"),
                html.Div(id='journals',children='NA')
            ]),

            dbc.Col([
                html.H6("代表性关键词"),
                html.Div(id='terms',children='NA'),
            ]),

            dbc.Col([
                dcc.RadioItems(
                    id = 'if-show-all',
                    options=[
                        {'label': '显示所有节点', 'value': 'showall'},
                        {'label': '只显示未标注节点', 'value': 'notshowall'},
                    ],
                    value='showall',
                    #labelStyle={'display': 'inline-block'}
                    ),
                html.Label("请输入该节点标签"),
                html.Div(dcc.Input(id='label-input-box', type='text')),
                html.Label("是否属于分子生物与遗传领域?"),
                dcc.RadioItems(
                    id = 'if-cell',
                    options=[
                        {'label': '未知  ', 'value': 'unknown'},
                        {'label': '是  ', 'value': 'yes'},
                        {'label': '否  ', 'value': 'no'}
                    ],
                    value='unknown',
                    labelClassName="label__option",
                    inputClassName="input__option",
                    labelStyle={'display': 'inline-block'}
                ),
                    html.Button('提交', id='submit'),
            ])
        ],
        justify='around'),
        dbc.CardHeader(html.H5("其它辅助判断信息")),
        dbc.CardBody(
            dbc.Tabs(
                [
                    dbc.Tab(journal_tab, label='主要期刊'),
                    dbc.Tab(paper_tab, label='主要论文'),
                    dbc.Tab(wordcloud_tab, label='词云'),
                    dbc.Tab(inst_tab, label='主要机构'),
                    
                ]
            ),
        ),
    ])


# main app layout
app.layout = html.Div(
    [
        dcc.Location(id='url',refresh=False),
        html.Div(
            login_layout(),
            id='page-content'
        ),
    ]
)

###############################################################################
# utilities
###############################################################################
# router
@app.callback(
    Output('page-content','children'),
    [Input('url','pathname')]
)
def router(url):
    if url=='/home':
        return app_layout()
    elif url=='/login':
        return login_layout()
    else:
        return login_layout()

# authenticate 
@app.callback(
    [Output('url','pathname'),
     Output('login-alert','children')],
    [Input('login-button','n_clicks')],
    [State('login-user','value'),
     State('login-password','value')])
def login_auth(n_clicks,email,pw):
    '''
    check credentials
    if correct, authenticate the session
    otherwise, authenticate the session and send user to login
    '''
    if n_clicks is None or n_clicks==0:
        return no_update,no_update
    credentials = {'user':email,"password":pw}
    if authenticate_user(credentials):
        session['authed'] = True
        session['username'] = email
        return '/home',''
    session['authed'] = False
    return no_update,dbc.Alert('Incorrect credentials.',color='danger',dismissable=True)

@app.callback(
    Output('home-url','pathname'),
    [Input('logout-button','n_clicks')]
)
def logout_(n_clicks):
    '''clear the session and send user to login'''
    if n_clicks is None or n_clicks==0:
        return no_update
    session['authed'] = False
    return '/login'



###############################################################################
# callbacks
###############################################################################

@app.callback(
    [Output(component_id='cluster-map',component_property='figure')],
    [Input(component_id='if-show-all',component_property='value'),
     Input(component_id='submit', component_property='n_clicks')],
)
def upadate_cluster_map_showall(flag,clck):
    # trace for scatter plot
    print(flag)
    if flag == 'showall':
        data = []
        for cate,dfg in df_map.groupby('cluster'):
            sub = dict(
                    x = dfg['x'],
                    y = dfg['y'],
                    name=labels[cate],
                    text = dfg['text'],
                    mode='markers',
                    marker = dict(
                            color = map_cate_color(cate,alpha=1),
                            size = 15
                            )
                    )

            data.append(sub)
    else:
        user_name = session.get('username',None)
        if user_name in labeled_cluster:
            labeled_cluster_this_usr = [int(i) for i in labeled_cluster[user_name].keys()]
        else:
            labeled_cluster_this_usr = []
        data = []
        for cate,dfg in df_map[df_map['id'].apply(lambda x:False if x in labeled_cluster_this_usr else True)].groupby('cluster'):
            sub = dict(
                    x = dfg['x'],
                    y = dfg['y'],
                    name=labels[cate],
                    text = dfg['text'],
                    mode='markers',
                    marker = dict(
                            color = map_cate_color(cate,alpha=1),
                            size = 15
                            )
                    )

            data.append(sub)
    fig={   
            'data': data,
            'layout': {
                'clickmode': 'event+select',
                'hovermode':'closest'
            }
    }
    return fig,

@app.callback(
    [Output(component_id='cluster', component_property='children'),
     Output(component_id='journals', component_property='children'),
     Output(component_id='terms', component_property='children'),],
    [Input(component_id='cluster-map', component_property='clickData')],
)
def update_cluster_info(clickData):
    if clickData:
        label = int(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
        journals = df_map.loc[label,'journals_tab']
        keywords = df_map.loc[label,'keywords_tab']
        labeled_name = ['未标记']
        user_name = session.get('username',None)
        if user_name in labeled_cluster:
            if label in labeled_cluster[user_name]:
                labeled_name = labeled_cluster[user_name][label]
                labeled_name = [f"{labeled_name}"]
        return label,journals,keywords
    else:
        return ['NA'],['NA'],['NA']


# 更新label信息
@app.callback(
    [Output(component_id='labeled-name', component_property='children')],
    [Input(component_id='cluster-map', component_property='clickData'),
     Input(component_id='submit', component_property='n_clicks')],
    [State(component_id='label-input-box',component_property='value'),
     State(component_id='if-cell',component_property='value')])
def update_cluster_label(clickData,nclick,label_name,if_cell):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ['NA']
    else:
        trig_id = ctx.triggered[0]['prop_id'].split('.')[0]
    user_name = session.get('username',None)
    if trig_id == 'cluster-map':
        if clickData:
            #print(clickData)
            label = int(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
            labeled_name = ['未标记']
            label = str(label)
            if user_name in labeled_cluster:
                if label in labeled_cluster[user_name]:
                    labeled_name = labeled_cluster[user_name][label]['name']
                    labeled_name = [f"{labeled_name}"]
            return labeled_name
        else:
            return ['NA']
    elif trig_id == 'submit':
        if label_name==None:
            return ['未标记']
        clusterId = str(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
        print(clusterId,user_name,label_name)
        if user_name not in labeled_cluster:
            labeled_cluster[user_name] = {}
        labeled_cluster[user_name][clusterId] = {}
        labeled_cluster[user_name][clusterId]['name'] = label_name
        labeled_cluster[user_name][clusterId]['if-cell'] = if_cell
        write_tofile(labeled_cluster,f'./result/labeled_cluster_micro_{user_name}.txt')
        labeled_name = [f"{label_name}"]
        return labeled_name



@app.callback(
    [Output(component_id='journal-treemap',component_property='figure')],
    [Input(component_id='cluster-map', component_property='clickData')]
)
def update_treemap(clickData):
    if clickData:
        label = int(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
        dfsub = df_profile['micro'][df_profile['micro']['micro']==label]

        values = list(dfsub['N'])
        labels = list(dfsub['AbbrTitle'])
        treemap_trace = go.Treemap(
            labels=labels, parents=[""] * len(labels), values=values
        )
        treemap_layout = go.Layout({"margin": dict(t=10, b=10, l=5, r=5, pad=4)})
        treemap_figure = {"data": [treemap_trace], "layout": treemap_layout}
        return treemap_figure,
    else:
        return []




@app.callback(
    [Output(component_id='autosave',component_property='children')],
    [Input(component_id='interval-component',component_property='n_intervals')]
)
def autosave(n):
    write_tofile(labeled_cluster,f'./result/labeled_cluster_micro.txt')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return [f"autosaved {timestamp}"]



@app.callback(
    [Output(component_id='paper',component_property='children')],
    [Input(component_id='cluster-map', component_property='clickData')]
)
def update_paper_table(clickData):
    if clickData:
        label = int(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
        df_tiab_sub = df_tiab[df_tiab['micro_level_field_id']==label][['Title']]
        df_tiab_sub['id'] = range(df_tiab_sub.shape[0])
        df_tiab_sub = df_tiab_sub[['id','Title']]
        table = dash_table.DataTable(
            data=df_tiab_sub.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_tiab_sub.columns],
            style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'textAlign':'center'
            },  
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            style_cell_conditional=[
                {'if':{'column_id':'Title'},
                'width':'95%','textAlign': 'left'},
                {'if':{'column_id':'id'},
                'width':'5%','textAlign': 'center'},
            ],
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df_tiab_sub.to_dict('rows')
            ],
            tooltip_duration=None
        )
        return table,
    else:
        return []


@app.callback(
    [Output(component_id='insts',component_property='children')],
    [Input(component_id='cluster-map', component_property='clickData')]
) 
def update_ins_table(clickData):
    if clickData:
        label = int(clickData['points'][0]['text'].split('<br>')[0].split('：')[-1])
        df_ins_sub = df_ins[df_ins['micro_level_field_id']==label][['主要机构','发文量']]
        table = dash_table.DataTable(
            data=df_ins_sub.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_ins_sub.columns],
            style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'textAlign':'center'
            },  
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            style_cell_conditional=[
                {'if':{'column_id':'主要机构'},
                'width':'90%','textAlign': 'center'},
                {'if':{'column_id':'发文量'},
                'width':'10%','textAlign': 'center'},
            ],
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df_ins_sub.to_dict('rows')
            ],
            tooltip_duration=None
        )
        return table,
    else:
        return []
###############################################################################
# run app
###############################################################################

if __name__ == '__main__':
    app.run_server(debug=True,port=8432)
