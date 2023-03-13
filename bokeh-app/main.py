from bokeh.io import curdoc, output_notebook
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, Div, RangeSlider
from bokeh.plotting import figure, show
import pandas as pd
from bokeh.palettes import Viridis6

df_sleep_efficiency = pd.read_csv('Data/Sleep_Efficiency.csv')

changed_df_sleep_efficiency = df_sleep_efficiency.copy()
changed_df_sleep_efficiency['Sleep efficiency'] = [round(num, 1) for num in changed_df_sleep_efficiency['Sleep efficiency']]
df_dummies_smoking= pd.get_dummies(changed_df_sleep_efficiency["Smoking status"])
changed_df_sleep_efficiency = pd.concat((df_dummies_smoking, changed_df_sleep_efficiency), axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.drop(["Smoking status"], axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.drop(["No"], axis=1)
changed_df_sleep_efficiency = changed_df_sleep_efficiency.rename(columns={"Yes": "Smoking status"})
   
axis_map = {
    "Caffeine Consumption (in mg)": "Caffeine consumption",
    "Alcohol Consumption (in oz)": "Alcohol consumption",
    "Smoking Status (0:No & 1:Yes)": "Smoking status",
    "Exercise Frequency (number of times per week)": "Exercise frequency",
}

title = Div(text='<h1 style="text-align: center">Machine Learning Project, Sleep Efficiency</h1>')
gender = Select(title="Gender:", options=["Male", "Female"], value="Male")
min_age = min(changed_df_sleep_efficiency['Age'])
max_age = max(changed_df_sleep_efficiency['Age'])
slider_range = RangeSlider(title="Choose age:", start=min_age, end=max_age, value=(min_age, max_age), step=1, width=450, height=50)
y_axis = Select(title="Variable to be compared with sleep efficiency: ", options=sorted(axis_map.keys()), value= "Caffeine Consumption (in mg)")

source = ColumnDataSource(data=dict(x=[], top=[]))
p = figure(height=600, title="", sizing_mode="stretch_width")
p.vbar(x = 'x', top = 'top', source = source, width = 0.08)

def select_gender():
    age_val_1 = slider_range.value[0]
    age_val_2 = slider_range.value[1]
    gender_val = gender.value
    selected = changed_df_sleep_efficiency[(changed_df_sleep_efficiency["Age"] >= age_val_1) & (changed_df_sleep_efficiency['Age'] <= age_val_2)]  
    selected = selected[selected.Gender.str.contains(gender_val)] 
    return selected

def update():
    y_name = axis_map[y_axis.value]
    df = select_gender()
  
    if y_name != "Smoking status":
        df_grouped = df.groupby('Sleep efficiency')[y_name].mean().reset_index()
        p.xaxis.axis_label = "Sleep Efficiency"
        p.yaxis.axis_label = y_axis.value
        p.title.text = "Sleep Efficiency VS " + y_name

        new_data = {
                'x': df_grouped["Sleep efficiency"].tolist(), 
                'top': round(df_grouped[y_name],2).tolist()
            }
        source.data = new_data
    else:
       df_grouped = df.groupby(y_name)["Sleep efficiency"].mean().reset_index()
       p.xaxis.axis_label = y_axis.value
       p.yaxis.axis_label = "Sleep Efficiency"
       p.title.text = "Sleep Efficiency VS " + y_name
       
       new_data_1 = {
                'x': df_grouped[y_name].tolist(), 
                'top': df_grouped["Sleep efficiency"].tolist()
            }
       source.data = new_data_1 

controls = [gender, slider_range, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=200, height=200)
layout = column(title, inputs, p, sizing_mode="stretch_width", height=800)

update()

curdoc().add_root(layout)
curdoc().title = "Sleep Efficiency"
