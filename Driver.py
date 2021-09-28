# Import functions 
import numpy as np
import os
import matplotlib.pyplot as plt
import rasutils  

# User must update the input options for the HEC-RAS model and results under the HEC-RAS Analysis.
# User must update the heat map and 3D plot x and y plot labels as well as num_locations, num_locations_SP, and num_scenarios
# variables for the 3D plot under the Results Analysis.  
# Stream power locations must be updated for the stream power inputs (stream_power_heatplot and stream_power_plot) in order
# to plot only the locations in the stream.  The values are the indexes in the stream power matrix.  Suggest putting all of the 
# stream locations at the end of the locations list inorder to be able to grab the last columns. 
# Note that csv files must be closed or an error will occur when trying to resave the results in a new run.  If you would like to 
# save the results, rename the csv results files under Results Analysis for each variable. 
# Plots will also save over itself if the names aren't changed in the function calls (last input) for each of the plots and variables. 
# Always check HEC-RAS is completely closed before starting.  Going to task manager is a good way to check this.
# If errors occur during a run it may be necessary to go to the task manager and close HEC-RAS from there (even if you think you closed it and it seems like you did
# it can be running in the background).  
# In the results analysis locations have to be reordered in the correct order.  Suggest putting in all of the location names and then can copy this down to the plots axis label. 

########################## HEC-RAS ANALYSIS ########################## 
                     
                   ######## User Input ########
# Input options for the HEC-RAS model and results
# See example files for formatting 
# The geometryfile must be the most basic file (only include bridges and culverts that are there for all scenarios). Anything that changes 
# must be included as an option and placed back on the geometry file with the scenarios file.  
# The HECresultsfile will determine which storm is run.  Set the plan you would like to run in the
# "Unsteady Flow Analysis" window. Update the .p# to the plan that you would like to run. Save HEC-RAS with that
# plan loaded and close out of HEC-RAS. 
# To calculate the velocity, the face nodes need to be written to the hdf file.  In HEC-RAS open the Unsteady
# Flow Analysis window. Go to Options -- Output Options.  Click on the "HDF5 Write Parameters" tab.  Check the 
# box "Write Velocity data at the face node locations in 2D Meshes" 
# To get the cell and face numbers for the "cells.txt" and "faces.txt" files go to RasMapper. Under Geometries click on the 2D Flow Area
# that will be used in the analysis.  Right click on the cell or face. Click on Plot Property Table and click on one of the cell or face options to identify which 
# cell or face number it is. 
# To get the face point numbers for the "facepts.txt" file go to RasMapper.  Under a results file utilizing the same geometry.  Click on the 2D Flow Area.  Right click 
# on a face point.  Click on Plot Time Series and click on Face Point: Velocity which will give the face point number for that point.  


optionsfile = "Options.txt" # Text file that includes the terrain and geometry options (culverts, bridges, etc.)
scenariosfile = "Scenarios3.txt" # Text file that includes the scenario combinations by number 
geometryfile = "BlackCreekModel" # Geometry file template for HEC-RAS (name should match text and HDF file name)
RASfile = 'BlackCreekModel.prj' # HEC-RAS project file name
cellsfile = "cells.txt" # Cell numbers for each location 
facesfile = "faces.txt" # Face numbers for each of the cells
faceptsfile = 'facepts.txt' # Face points numbers for each of the cells 
HECresultsfile = 'BlackCreekModel.p07.hdf' # Results file, must be the same file that is loaded into model running
minDepth = .00508 # Minimum depth value to be considered inundated or "wet" 
                      ########################
geomHDF = geometryfile +'.g01.hdf' # If the geometry template file isn't .g01, lines 155, 163, and 177 in the rasutils must be updated with the correct geometry file template number as well 
os.remove(geomHDF)
# Run HEC-RAS for all scenarios and calculate results using the resulting hdf file.  Call runHECResults function. 
depth, velocity, duration, percent_time_innundated, stream_power = rasutils.runHECResults(minDepth, optionsfile, scenariosfile, geometryfile, RASfile, cellsfile, facesfile, faceptsfile, HECresultsfile)

########################## RESULTS ANALYSIS ##########################
# Get results data in the right format and create a percent difference matrix compared to sceanrio 1. 
# The results matrix is saved to a csv file.  

# Create percent difference matrix comparing each scenario to the existing conditions 
# Depth
depth_pandasDataFrame = rasutils.toPandas(depth)
# Organize columns in number order 
depth_pandasDataFrame = depth_pandasDataFrame[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percentdiff_depth = rasutils.percentDifference(depth_pandasDataFrame) # Calculate percent different compared to Scenario 1
# Organize columns in number order
percentdiff_depth = percentdiff_depth[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
depth_pandasDataFrame.to_csv("results_depth_FinalPaper.csv")   # Save raw results to a csv 

# Velocity 
velocity_pandasDataFrame = rasutils.toPandas(velocity)
# Organize columns in number order 
velocity_pandasDataFrame = velocity_pandasDataFrame[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percentdiff_velocity =  rasutils.percentDifference(velocity_pandasDataFrame) # Calculate percent different compared to Scenario 1
# Organize columns in number order
percentdiff_velocity = percentdiff_velocity[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
velocity_pandasDataFrame.to_csv("results_velocity_FinalPaper.csv")  # Save raw results to a csv 

# Duration 
duration_pandasDataFrame = rasutils.toPandas(duration)
# Organize columns in number order 
duration_pandasDataFrame = duration_pandasDataFrame[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percentdiff_duration =  rasutils.percentDifference(duration_pandasDataFrame) # Calculate percent different compared to Scenario 1
# Organize columns in number order
percentdiff_duration = percentdiff_duration[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]  
duration_pandasDataFrame.to_csv("results_duration_FinalPaper.csv") # Save raw results to a csv  

# Percent Time Inundated
percent_time_inundated_pandasDataFrame = rasutils.toPandas(percent_time_innundated)
# Organize columns in number order 
percent_time_inundated_pandasDataFrame = percent_time_inundated_pandasDataFrame[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percentdiff_percent_time_inundated =  rasutils.percentDifference(percent_time_inundated_pandasDataFrame) # Calculate percent different compared to Scenario 1
# Organize columns in number order
percentdiff_percent_time_inundated  = percentdiff_percent_time_inundated[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percent_time_inundated_pandasDataFrame.to_csv("results_timeinun_FinalPaper.csv") # Save raw results to a csv 

# Stream Power 
stream_power_pandasDataFrame = rasutils.toPandas(stream_power)
# Organize columns in number order 
stream_power_pandasDataFrame = stream_power_pandasDataFrame[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
percentdiff_stream_power = rasutils.percentDifference(stream_power_pandasDataFrame) # Calculate percent different compared to Scenario 1
# Organize columns in number order
percentdiff_stream_power = percentdiff_stream_power[["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]]
stream_power_pandasDataFrame.to_csv("results_streampower_FinalPaper.csv") # Save raw results to a csv 
 
########################## HEAT MAP ########################## 
# Create Heat Map for percent difference data 
# Each map will be saved as a .png file. 

                     ######## User Input ########
# Note: 
# Axis labels and titles can be updated in each of the function calls if desired.  
# Change the name of the figure name (last input) if you don't want figures to be saved over on each run. 
# Scenarios should be 1 less than total scenario values since comparing to original
scenario_labels = ["Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"] # MUST BE 1 LESS THAN TOTAL SCENARIOS

# Location labels for all sites
location_labels = ["Location 1", "Location 2", "Location 3", "Location 4", "Location 5",
                  "Location 6", "Location 7", "Location 8", "Location 9", "Location 10",
                  "Location 11", "Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]

# Location labels for stream power sites (location in river)
location_labels_SP = ["Location 12", "Location 13", "Location 14", "Location 15", "Location 16","Location 17"]
                      ########################   

# Plot heat maps for each variable. Call heatmap function. 
# Depth
plt.figure(1)
rasutils.heatmap(percentdiff_depth, scenario_labels, location_labels, "Percent Difference Depth", "HeatMap_Depth")
# Velocity 
plt.figure(2)
rasutils.heatmap(percentdiff_velocity, scenario_labels, location_labels, "Percent Difference Velocity", "HeatMap_Velocity")
# Duration 
plt.figure(3)
rasutils.heatmap(percentdiff_duration, scenario_labels, location_labels, "Percent Difference Duration", "HeatMap_Duration")   
# Percent Time Inundated
plt.figure(4)     
rasutils.heatmap(percentdiff_percent_time_inundated, scenario_labels, location_labels, "Percent Difference Percent Time Inundated", "HeatMap_Inundation")
# Stream Power
plt.figure(5)
# For stream power, create an array and specify locations that should have stream power calculated
stream_power_arrayheat = np.array(percentdiff_stream_power)
stream_power_heatplot = stream_power_arrayheat[:,11:18]
rasutils.heatmap(stream_power_heatplot, scenario_labels, location_labels_SP, "Percent Difference Stream Power", "HeatMap_StreamPower")

########################## 3D PLOT ########################## 
# Create 3D Plot for each scenario and location of raw data values.
# Each map will be saved as a .png file.

                   ######## User Input ########
# Note: 
# Axis labels and titles can be updated in each of the function calls if desired.  
# Change the name of the figure name (last input) if you don't want figures to be saved over on each run. 
# Scenario labels should be equal to the number of sceanrios for 3D plot, will be plotting the raw data
ticks_x = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5"]
# Location labels for all locations, shortened location for visual 
ticks_y =  ["Loc 1", "Loc 2", "Loc 3", "Loc 4", "Loc 5",
              "Loc 6", "Loc 7", "Loc 8", "Loc 9", "Loc 10",
              "Loc 11", "Loc 12", "Loc 13", "Loc 14", "Loc 15", "Loc 16", "Loc 17"]
# Location labels for locations to be cacluated for stream power 
ticks_y_StreamPower =  ["Loc 12", "Loc 13", "Loc 14", "Loc 15", "Loc 16", "Loc 17"]
    
num_locations = 17 # Number of locations
num_locations_SP = 6 # Number of locations only for stream power
num_scenarios = 5 # Number of scenarios

                    ########################

# Plot 3D plots for each variable.  Call plot3d function.  
# Depth
plt.figure(6)
rasutils.plot3d(num_locations , num_scenarios, ticks_x, ticks_y, depth_pandasDataFrame, "Depth" , "Depth (meters)", "3D_Plot_Depth") 
# Velocity
plt.figure(7)
rasutils.plot3d(num_locations , num_scenarios, ticks_x, ticks_y, velocity_pandasDataFrame, "Velocity" , "Velocity (meters/second)", "3D_Plot_Velocity")
# Duration
plt.figure(8)
rasutils.plot3d(num_locations , num_scenarios, ticks_x, ticks_y, duration_pandasDataFrame, "Duration" , "Duration (hours)", "3D_Plot_Duration")
# Percent Time Inundated 
plt.figure(9)
rasutils.plot3d(num_locations , num_scenarios, ticks_x, ticks_y, percent_time_inundated_pandasDataFrame, "Percent Time Inundated" , " Percent Time Inundated", "3D_Plot_Inundation") 
# Stream Power 
plt.figure(10)
# For stream power, create an array and specify locations that should have stream power calculated
stream_power_array = np.array(stream_power_pandasDataFrame)
stream_power_plot = stream_power_array[:,11:18]
rasutils.plot3d(num_locations_SP, num_scenarios, ticks_x, ticks_y_StreamPower, stream_power_plot, "Stream Power" , " Stream Power", "3D_Plot_Stream Power") 

