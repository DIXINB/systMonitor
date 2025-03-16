import dash
import json
import dash_bootstrap_components as dbc
from dash import html, dcc,  Input, Output
from dash.exceptions import PreventUpdate
from dash.dependencies import State
import pandas as pd
import psutil
import time
import logging
from collections import deque
import datetime as dttime
from datetime import datetime
import sys
from sqlalchemy import create_engine, Column, Integer,String, Table, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Define fixed-size lists (deque) to store the last 16 data points for RAM, CPU, Disk usage, and time
history = {
    'ram': deque(maxlen=16),
    'cpu': deque(maxlen=16),
    'disk': deque(maxlen=16),
    'time': deque(maxlen=16) 
}
# creating the base table
def get_system_stats():
    try:
        # Get memory stats
        memory = psutil.virtual_memory()
        ram = memory.percent

        # Get CPU usage
        cpu = psutil.cpu_percent(interval=0.2)

        # Get Disk usage
        disk = psutil.disk_usage('/').percent

        # Return RAM, CPU, and Disk data
        return {
            'RAM Usage (%)': ram,
            'CPU Usage (%)': cpu,
            'Disk Usage (%)': disk
        }
    except Exception as e:
        logging.error(f"Error fetching system stats: {e}")
        return {}

def dellcurrdata():
    q="DELETE  from current_data"
    try:
        session_del=Session()        
        query=text("DELETE  from current_data")       
        r_set=session_del.execute(query)
        session_del.commit() 

    except SQLAlchemyError as e:
    #print(e)
        error = str(e.__dict__['orig'])
        print(error)
    else:
        print("No of Records deleted : ",r_set.rowcount)


class Base(DeclarativeBase):pass

class Frame(Base):
  __tablename__='current_data'
  id=Column(Integer, primary_key=True)
  time=Column(String)
  cpu=Column(Integer)
  ram=Column(Integer)
  disk=Column(Integer)

class Sdata(Base):
  __tablename__='syst_data'
  id=Column(Integer, primary_key=True)
  frame=Column(Integer)
  time=Column(String)
  cpu=Column(Integer)
  ram=Column(Integer)
  disk=Column(Integer)
DATABASE_URL = 'sqlite:///syst_data.db' 
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session=sessionmaker(bind=engine)

frm=1
dd=[{'current_time':7, 'CPU Usage (%)':77777777777777,'RAM Usage (%)':7, 'Disk Usage (%)':77}]
df=pd.DataFrame.from_records(dd)
dd1=[{'CPU Usage (%)':77777777777777,'RAM Usage (%)':6, 'Disk Usage (%)':66}]
df1=pd.DataFrame.from_records(dd1)

app = dash.Dash()

green_style={'background-color':'green',
             'color':'white',
             'height':'25px',
             'width':'115px'
             }
red_style={'background-color':'red',
             'color':'white',
             'height':'25px',
             'width':'115px'
             }
white_style={'background-color':'white',
             'color':'blue',
             'height':'25px',
             'width':'115px'
             }

app.layout = html.Div(children=[
        dcc.Interval(
            id='min-interval',
            interval=1000,  # 1000 milliseconds (1 seconds)
            n_intervals=0,
            max_intervals=-1,
            disabled=False
        ),
    
    # Interval for updating the scorecard-table every 1 seconds
        dcc.Interval(
            id='interval',
            interval=1000,  # 1000 milliseconds (1 seconds)
            n_intervals=0,
            max_intervals=-1,
            disabled=True

        ),

    html.Div(dash.dash_table.DataTable(
                id='min-table',
                data=dd1,
                style_header={'backgroundColor':'#40E0D0', 'padding':'10px', 'color':'#AAAAAA'},
                columns=[{"name": i, "id": i} for i in df1.columns],
                style_table={'overflowX': 'auto',},
                style_data={
                  'whiteSpace': 'normal',
                  'height': 'auto'
                },    
                style_cell={
                  'text-align': 'center'
                },    
                fill_width=False
    )), 
    html.Br(),
    html.Br(),
    html.Div([
    html.Div([html.Button(id='button',children='Start',style=green_style)],style={'display':'inline-block'}),
    html.Div([html.Button(id='done-button',n_clicks=0,children='Done', style={'display':'none'})],style={'margin-left':'10px','display': 'inline-block'}),    
    html.Div([html.Span(id='elapsed-time',style={'background':'gold'})], style={'verticalAlign':'middle','margin-left':'10px','display': 'inline-block'})    
    ]),
    html.Div([
                html.Div(
                [dash.dash_table.DataTable(
                id='scorecard-table',
                data=df.to_dict('records'),
                style_header={'backgroundColor':'#305D91', 'padding':'10px', 'color':'#FFFFFF'},
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_data={
                  'whiteSpace': 'normal',
                  'height': 'auto'
                },    
                style_cell={
                  'text-align': 'center'
                },    
                fill_width=False
                )], style={'width': '45%', 'display': 'inline-block'}),
   
                html.Div(
                [dash.dash_table.DataTable(
                id='done-table',
                data=df.to_dict('records'),

                style_header={'backgroundColor':'#305D91', 'padding':'10px', 'color':'#FFFFFF'},
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_data={
                  'whiteSpace': 'normal',
                  'height': 'auto'
                },    
                style_cell={
                  'text-align': 'center'
                },    
                fill_width=False
                )], style={'width': '45%', 'display': 'inline-block'})   
         ])
])

@app.callback(
    [Output("interval", "disabled"),
     Output("button", "children"),
     Output("button", "style"),
     Output("done-button", "style"),
     Output('done-table', 'data'),
     Output("elapsed-time","children"),
     Output("done-button", "n_clicks")],     
    [Input("button", "n_clicks"),
    Input("done-button", "n_clicks")],
    State("interval", "disabled")
)
def toggle_interval(n,n2, disabled):                    
    global start_time_str
    global frm
    global n_clicks
    n_clicks=n2
    start_time=datetime.now()
    elapsed_time=datetime.now()-start_time
    js_elapsed_time=json.dumps(elapsed_time,default = str)
    
    dd=[{'current_time':' ', 'CPU Usage (%)':' ','RAM Usage (%)':' ', 'Disk Usage (%)':' '}]
    df1=pd.DataFrame.from_records(dd)
    if n is None:
        raise PreventUpdate
    if n%2 == 1:        
        if n!=1:
            frm += 1        
        dellcurrdata()
        disabled=not disabled
        button_text1="Stop"
        style1=red_style
        style2=dict(display='none')

        start_time=datetime.now()        
        start_time_str=start_time.strftime("%Y-%m-%d %H:%M:%S")
        
    elif n%2 == 0:           
        button_text1="Start"
        style1=green_style
        style2=white_style
        disabled=not disabled

        FMT="%Y-%m-%d %H:%M:%S"

        print('start_time_str : ',start_time_str)
        start_time=datetime.strptime(start_time_str, FMT)
        print('start_time : ',start_time)

        stop_time=datetime.now()
        print('stop_time: ',stop_time)
        elapsed_time=str(stop_time-start_time)
        print('elapsed_time: ',elapsed_time)
        js_elapsed_time=json.dumps(elapsed_time,default = str)

        if n2 == 0:                
            dd=[{'current_time':' ', 'CPU Usage (%)':' ','RAM Usage (%)':' ', 'Disk Usage (%)':' '}]
            df1=pd.DataFrame.from_records(dd)
            n_clicks=0
        else:
            disabled=True
            session_output=Session()
            dd_=session_output.query(Frame).all()           
            dd=[{'current_time':r.time, 'CPU Usage (%)':r.cpu,'RAM Usage (%)':r.ram, 'Disk Usage (%)':r.disk} for r in dd_]            
            df1=pd.DataFrame.from_records(dd)
            n_clicks=0
    elif n > 100:
        quit()
    
#    session_output.close()
    return disabled,button_text1,style1,style2,df1.to_dict('records'),js_elapsed_time,n_clicks

@app.callback(
    Output('min-table', 'data'),
    Input('min-interval', 'n_intervals')
)
def min_update_output(n):
    data = get_system_stats()
    dd1=[data]
    return dd1

# update the scorecard-table
@app.callback(
     Output('scorecard-table', 'data'),
     Input('interval', 'n_intervals')
)
def update_output(n):
  global frm

  data = get_system_stats()
  if n == 0:   
    dd=[{'current_time':7, 'CPU Usage (%)':77777777777777,'RAM Usage (%)':7, 'Disk Usage (%)':77}]
    df=pd.DataFrame.from_records(dd)
  else:  
    current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time as a string
    session_input=Session()
    current_data=Frame(time=current_time,cpu=data['CPU Usage (%)'],ram=data['RAM Usage (%)'],
                        disk=data['Disk Usage (%)'])
    session_input.add(current_data)
    hist_data=Sdata(frame=frm,time=current_time,cpu=data['CPU Usage (%)'],ram=data['RAM Usage (%)'],
                        disk=data['Disk Usage (%)'])
    session_input.add(hist_data)    
    session_input.commit()
    
    history['ram'].append(data['RAM Usage (%)'])
    history['cpu'].append(data['CPU Usage (%)'])
    history['disk'].append(data['Disk Usage (%)'])
    history['time'].append(current_time)
    if not data:
            logging.info("No data fetched")
            return {}

        # Log fetched data in the terminal
    logging.info(f"Fetched data: {data}")

    dd=[{'current_time':history['time'][i], 'CPU Usage (%)':history['cpu'][i],'RAM Usage (%)':history['ram'][i], 'Disk Usage (%)':history['disk'][i]} for i in range(len(history['time']))]
    table_disabled=False        
    df=pd.DataFrame.from_records(dd)

  return df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
