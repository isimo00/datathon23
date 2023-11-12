import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.offline as pyo
import re

df = pd.read_csv("./data/Results.csv")

df.replace({"Yes": 1, "No": 0})
df = df.replace(np.nan, "")
df.Center = df.Center.str.replace(r"[\w\s,]*\((.*)\)",r"\1", regex=True)
df.drop(df[(df["GoStage1"] == "")&(df["GoStage2"] == "")&(df["GoStage3"] == "")].index, inplace=True)

changes = {
    "FGC" : 2 ,
    "On foot" : 14 ,
    "Combustion vehicle (non-plug-in hybrid, electric or plug-in hybrid with non-renewable source charging)," : 11 ,
    "Underground" : 7 ,
    "Bus" : 3 ,
    "Combustion or electric motorcycle with non-renewable source charging" : 11 ,
    "Renfe" : 1 ,
    "Tram" : 8 ,
    "Bicycle" : 13 ,
    "Taxi" : 10 ,
    "Electric motorcycle" : 11 ,
    "Scooter (or other micro-mobility devices) with renewable charging" : 12 ,
    "Scooter (or other micro-mobility devices) with non-renewable charging" : 12 ,
    "Electric vehicle (with Zero label and renewable source charging)" : 11 ,
    "" : 100 ,
}
df[["GoStage1","GoStage2","GoStage3"] ] = df[["GoStage1","GoStage2","GoStage3"] ].replace(changes)
df["GoStage"] = df[["GoStage1","GoStage2","GoStage3"] ].min( axis = 1)
changes_back = {
    2 : "FGC" ,
    1 : "Tren",
    3 : "Bus",
    8 : "Tram",
    7 : "Underground",
    10 : "Taxi",
    11 : "Vehicle",
    12 : "Scooter",
    13 : "Bicycle",
    14 : "On foot",
    100 : ""
}
changes_back2 = {
    2 : "Público" ,
    1 : "Público",
    3 : "Público",
    8 : "Público",
    7 : "Público",
    10 : "Privado",
    11 : "Privado",
    12 : "Privado",
    13 : "Activa",
    14 : "Activa",
    100 : ""
}

df["GoStageAccum"] = df["GoStage"].replace(changes_back2)
df["GoStage"] = df["GoStage"].replace(changes_back)
df = df.drop(["GoStage1", "GoStage2", "GoStage3"], axis=1)

changes_center = {
    "FIB" : "Nord",
    "ETSETB" : "Nord",
    "ETSECCPB" : "Nord",
    "ETSEIB" : "Sud",
    "ETSAB" : "Sud",
    "ETSAV" : "Sant Cugat",
    "FME" : "Sud",
    "EPSEB" : "Sud",
    "EPSEVG" : "Vilanova",
    "FNB" : "Nàutica",
    "EEBE" : "Besòs",
    "EETAC" : "Castelldefels",
    "EEABB" : "Castelldefels",
    "ESEIAAT" : "Terrassa",
    "FOOT" : "Terrassa",
    "EPSEM" : "Manresa"
}

df["Campus"] = df["Center"].replace( changes_center)


initial_axis = "Center"
fixed_axis = "GoStage"
possible_axis = [
    "Gender",
    "Center",
    "Year",
    "Days",
    "ZipCode",
    "Campus"
]

# Create a function to update the heatmap based on the selected axis
def update_heatmap(selected_axis):
    pivot_df = df.pivot_table(index=fixed_axis, columns=selected_axis, aggfunc='count', fill_value=0)["Answer"]
    normalized = pivot_df.to_numpy() / pivot_df.to_numpy().max(axis=0)
    heatmap = go.Heatmap(
                x=pivot_df.columns,
                y=pivot_df.index,
                z=normalized,
                colorscale=['white','#599191']
              )
    return heatmap
def get_matrix(selected_axis):
    pivot_df = df.pivot_table(index=fixed_axis, columns=selected_axis, aggfunc='count', fill_value=0)["Answer"]
    pivot_df = pivot_df.to_numpy() / pivot_df.to_numpy().max(axis=0)
    return pivot_df

fig = go.Figure()
print(df[initial_axis].unique())
print(get_matrix(initial_axis))
for axis in possible_axis:
    fig.add_trace(update_heatmap(axis))
#fig.add_trace(update_heatmap(initial_axis))

fig.update_layout(
    updatemenus=[go.layout.Updatemenu(
        active=0,
        buttons=[
            dict(
                label=re.sub(r"(?<=\w)([A-Z])", r" \1", axis),
                method="update",
                args = [{
                        'visible' : [axis2 == axis for axis2 in possible_axis],
                        # 'x': df[axis].unique(),
                         #'y': df[fixed_axis].unique(),
                         #'z': get_matrix(axis)
                        },
                        {'title' : 'Heatmap with Count of Transport by Transport and ' + re.sub(r"(?<=\w)([A-Z])", r" \1", axis),
                         'showlegend': True}]
            )
        for axis in possible_axis]
    )]
)

fig.update_xaxes(autorange=True)

# Display the figure
pyo.iplot(fig)