import streamlit as st

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px

from enum import Enum

st.set_page_config(page_title="Live data updates", layout="wide")


@st.cache_data
def getdata():
    timestamp = pd.date_range(start="2024-01-01", end="2024-12-31", freq="15min")
    data = np.random.randint(230, 240, size=timestamp.shape[0])
    return pd.DataFrame({
        "timestamp":timestamp,
        "data":data
    })

df = getdata()


class SelectionChoice(str, Enum):
    APPLY_DATE = "Apply date"
    SELECT_BOX = "Selectbox"
    
class SelectBoxOptions(Enum):
    LAST_5_MINUTES = timedelta(minutes=5)
    LAST_15_MINUTES = timedelta(minutes=15)
    LAST_30_MINUTES = timedelta(minutes=30)
    LAST_1_HOUR = timedelta(hours=1)
    LAST_3_HOURS = timedelta(hours=3)
    LAST_6_HOURS = timedelta(hours=6)
    LAST_12_HOURS = timedelta(hours=12)
    LAST_24_HOURS = timedelta(hours=24)
    LAST_2_DAYS = timedelta(days=2)
    LAST_7_DAYS = timedelta(days=7)
    LAST_30_DAYS = timedelta(days=30)
    YESTERDAY = timedelta(days=1)
    

class MultiDateTimePicker:
    def __init__(self, key) -> None:
        self.defaultValue = self.get_default_date_range()
        self.key = key 

        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.date_input("Select a date range", value=self.defaultValue, key=f'date_range_picker_{self.key}', on_change=self.On_applyDate)
                if f"_date_range_picker_{self.key}" not in st.session_state:
                    st.session_state[f'_date_range_picker_{self.key}'] = self.defaultValue 
                              
            with col2:
                self._selectBox = st.selectbox("Select a value", [e.name for e in SelectBoxOptions] ,index =None, key=f'selectbox_{self.key}')
                
            with col1:
                st.write(self.displayText)
            
    def get_default_date_range(self):
        today_at_midnight    = datetime.combine(datetime.today(), datetime.min.time())
        tomorrow_at_midnight = today_at_midnight + timedelta(days=1)
        return [today_at_midnight, tomorrow_at_midnight]
                
    def On_applyDate(self):
        self.date_range_picker = st.session_state[f'date_range_picker_{self.key}']
        
        
    @property
    def date_range_picker(self):
        return [datetime.combine(st.session_state[f'_date_range_picker_{self.key}'][0], datetime.min.time()) , datetime.combine(st.session_state[f'_date_range_picker_{self.key}'][1], datetime.min.time())]
    
    @date_range_picker.setter
    def date_range_picker(self, value):
        if value is not None and len(value) == 2:
            st.session_state[f'_date_range_picker_{self.key}'] = value
            st.session_state[f'selectbox_{self.key}'] = None
        
    @property
    def selectBox(self):
        if self._selectBox is not None:
            return SelectBoxOptions[self._selectBox]
        else:
            return None
        
    @property
    def selectChoice(self):
        if self._selectBox is not None:
            return SelectionChoice.SELECT_BOX
        else:
            return SelectionChoice.APPLY_DATE
        
    @property
    def displayText(self):
        _displayText = f"Displaying data from "
        if self.selectChoice == SelectionChoice.SELECT_BOX:
            choice =  f" **(:green[{self.selectBox.name}])** :"
        elif self.selectChoice == SelectionChoice.APPLY_DATE:
            choice = f" **(:green[{SelectionChoice.APPLY_DATE.name}])**: "
        else:
            choice = ": "
        
        return _displayText + choice + f" **:red[{self.chooseRange[0]}]** - **:red[{self.chooseRange[1]}]**" 
    
    @property
    def chooseRange(self):
        if self.selectChoice ==  SelectionChoice.SELECT_BOX:
            now = datetime.now().replace(second=0, microsecond=0)
            return [now - self.selectBox.value, now]
        elif self.selectChoice == SelectionChoice.APPLY_DATE:
            return self.date_range_picker
    
    
grafana = MultiDateTimePicker("grafana")


def filterDF(df: pd.DataFrame, date_range):
    endDate    = df['timestamp'] < date_range[1]
    startDate  = df['timestamp'] > date_range[0]
    return df.loc[endDate & startDate]


_df = filterDF(df, grafana.chooseRange)

fig = px.line(_df, x='timestamp', y='data')

tab1, tab2 = st.tabs(["Plot",'Table'])
tab1.plotly_chart(fig, use_container_width=True)
tab2.dataframe(_df, use_container_width=True)


