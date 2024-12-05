from shiny import App, render, ui
import pandas as pd
from shinywidgets import render_altair, output_widget
import altair as alt
import numpy as np

#path = r"/Users/evylanai/Documents/GitHub/python_final_project/df.csv"

path = r"C:\Users\msald\OneDrive\Documents\GitHub\python_final_project/df.csv"

df = pd.read_csv(path)
# Add a column for the >20% new teachers condition
df['>20 Percent New Teachers'] = df['Experience_None'] >= 20

# Define available student groups
student_groups = {
    "District": "All",
    "AfricanAmerican": "African American",
    "Hispanic": "Hispanic",
    "White": "White",
    "SpecialEd": "Special Education",
    "EcoDis": "Economically Disadvantaged",
    "EBEL": "English Learners",
}

# Define the UI
app_ui = ui.page_fluid(
    ui.row(
        # Left column for inputs
        ui.column(
            3,  # This column takes 4/12 of the width
            ui.input_radio_buttons(
                "subject",
                "Select Test Subject:",
                {"Math": "Math", "ELA": "Reading"},
                selected="Math",
            ),
            ui.input_radio_buttons(
                "student_group",
                "Select Student Group:",
                student_groups,
                selected="District",
            ),
            ui.input_checkbox("show_line", "Show Line of Best Fit", value=False),
        ),
        # Right column for the graph
        ui.column(
            9,  # This column takes 8/12 of the width
            output_widget("scatter_plot"),
        ),
    )
)

# Define the server logic
def server(input, output, session):
    @render_altair
    def scatter_plot():
        # Get the selected subject and student group
        subject = input.subject()
        student_group = input.student_group()
        
        # Construct the column name based on the selected inputs
        selected_var = f"All_{subject}_{student_group}_Meets"

        # Ensure the selected column is numeric
        df[selected_var] = pd.to_numeric(df[selected_var], errors='coerce')
        
         # Filter out rows where the y-axis value is less than 0 because that is a missing value
        filtered_df = df[df[selected_var] >= 0]
        
        # Create base Altair scatter plot
        scatter = alt.Chart(filtered_df).mark_circle(size=100).encode(
            x=alt.X('Years_Experience_Teachers:Q', title="Average Teacher's Years of Experience"),
            y=alt.Y(selected_var + ':Q', title="% of Students Meeting Grade Level"),
            color=alt.Color(
                '>20 Percent New Teachers:N',
                scale=alt.Scale(domain=[True, False], range=['red', 'blue']),
                legend=alt.Legend(title=">20% New Teachers")
            )
        )
        
        # Create the regression line if checkbox is checked
        if input.show_line():
            regression_line = alt.Chart(filtered_df).transform_regression(
                'Years_Experience_Teachers', selected_var
            ).mark_line(color='black').encode(
                x='Years_Experience_Teachers:Q',
                y=selected_var + ':Q'
            )

            # Combine scatter and regression line
            chart = alt.layer(scatter, regression_line)
        else:
            chart = scatter

        # Apply global configurations to the combined chart
        return chart.properties(
            title=f"Teacher Experience vs. Proficiency ({student_groups[student_group]} - {subject})",
            width=1100,
            height=800
        ).configure_title(
            fontSize=25
        ).configure_axis(
            titleFontSize=18,
            labelFontSize=14
        )

# Create the Shiny app
app = App(app_ui, server)

