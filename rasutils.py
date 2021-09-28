#Import functions 
import numpy as np
import h5py
import win32com.client
import os
import pandas as pd
import matplotlib.pyplot as plt

########################## GEOMETRY INPUTS ########################## 

########################## HEC-RAS Options ########################## 

def getLocations(fileName):
       """
       getLocations takes a filename as input (fileName). filename is a txt file 
       that is structured like this: 
       location1: 1,2,3,4
       location2: 3,4,5,6
       where the numbers are specific cells, cell faces, or face points 
       the function returns a dictionary (locations) where the key is the location i.e location 1 and the key 
       is the cells or faces for that location, i.e 1,2,3,4.
   
       """
       infile = open(fileName, 'r') # Open text file 
       locations = {} # Create dictionary  
       # For loop 
       for line in infile.readlines():
           location = line.split(":")[0] # Split into location and cell values [0] left of colon 
           locations[location] = list(map(int,line.split(":")[1].split(','))) # [1] Right of colon number  
           
       infile.close()
       
       return locations
        
def runHECResults(minDepth, optionsfile = "", scenariosfile = "", geometryfile = "", RASfile = "", cellsfile = "", facesfile = "", faceptsfile = "", HECresultsfile = "" ):
    """
    runHECResults takes the inputs for HEC-RAS file, scenarios, and results locations.  HEC-RAS runs 
    through each scenario and calculates depth, velocity, stream power, percent time inundated, and 
    duration using the HEC-RAS hdf file.  
    
    Inputs: 
    minDepth = Minimum depth value to be considered inundated or "wet"
    optionsfile = Text file that includes the terrain and geometry options (culverts, bridges, etc.)
    scenariosfile =  Text file that includes the scenario combinations by number 
    geometryfile =  Starting geometry file template for HEC-RAS
    RASfile = HEC-RAS project file 
    cellsfile = Cell numbers for each location 
    facesfile = Face numbers for each of the cells
    faceptsfile = Face point numbers for each of the cells
    HECresultsfile = Results file, must be the same file that is loaded into model running
  
    Return: 
    depth = Calculated depth results at each location
    velocity = Calculated velocity results at each location
    duration = Calculated duration results at each location
    percent_time_innundated = Calculated percent time inundated at each location
    stream_power = Calculated percent time inundated at each location (only valid in stream though. Results can then
                                                                       be altered for plots to only include those locations)
    
    """
    
    # Dictionary to hold the HEC-RAS options
    allOptionsKeys = [] # Hold all the keys for the allOptions dictionary
    allOptions = {}
    
    # Open options file and read in all the lines
    optionsInfile = open(optionsfile,'r') # Open file with HEC-RAS options listed 
    lines = optionsInfile.readlines() # Read lines from optionsInfile to list
    
    ##### Read Terrain Options (should be listed as first options in file) #####
    # Initialize key and values
    key=""
    value=""
    index=0
    # Go through lines and store the terrain options where
    # the key is the name of the option and the value is the value to put in the geometry file
    # keys and values are stored in the allOptions dictionary
    for line in lines: 
        if "geometry" in line.lower():
            break
        if "option" in line.lower():
            key = line
            allOptionsKeys.append(key)
        if "FileName" in line:
            value = line
            allOptions[key] = value.split("=")[1]
        index+=1

##### Read Structure Options (culverts, bridges, etc., options should be listed after all terrain options) #####
# After terrain options in template file go through structure options
# The key is the name of the structure options 
# The value in the template to put in the geometery file for that option
# Keys and values stored in the allOptions dictionary
    key=""
    line=""
    for line in lines[index:]:
        if "option" in line.lower():
            key = line
            allOptionsKeys.append(key)
            continue
        if key!="":
            try:
                allOptions[key].append(line)
            except:
                allOptions[key] = [line]
    
    # Close file
    optionsInfile.close()

########################## Scenarios ########################## 
    
    scenarioOptions = {} # Dictionary to hold the scenario options
    scenarioInfile = open(scenariosfile,'r') # Open scenarios file
    
    # Read lines from scenarios file to list
    lines = scenarioInfile.readlines()
    
    # The key is the scenario options name
    # The value is the list of options for that scenario (these correspond with the options in allOptions)
    for line in lines:
        key = line.split(":")[0] # The scenario name
        value = line.split(":")[1] # the options
        scenarioOptions[key] = list(map(int,value.split(','))) # Map the options to a list of integers
        
    scenarioInfile.close() # Close file 
   
    allOptionsKeys = np.array(allOptionsKeys) # These are the names for all the options
    
    # Create dictionaries for results files
    percent_time_innundated = {} # Percent time innundated 
    duration = {} # Duration 
    depth = {} # Depth
    velocity = {} # Velocity 
    stream_power = {} # Stream power 
    
    # Go through all the different scenarios 
    # Scenario is the scenario name
    # Options is the list of options that correspond in the allOptions dictionary
    
    for scenario, options in scenarioOptions.items(): 
        choices = allOptionsKeys[np.array(options)-1] # All possible choices we do -1 for indexing since 
        # the options start at 1. For example [1,2,3,4]-1 = [0,1,2,3]
        print (scenario)    
        
        # Open the geometry file and read it into a list for each line
        geometryInfile = open(allOptions[choices[0]].split('\n')[0],'r')
        lines = geometryInfile.readlines()
        geometryInfile.close() # Close file
        
        # Save the geometry HDF file to the .g01 extension 
        # The geometry HDF file includes the terrain so the extension must 
        # match the geometry text file which is saved as .g01 for all runs
        # The geometry HDF file is then saved back to its' original extension at the end of the loop 
        # so that it can be used in future scenarios 
        finalHDF = geometryfile +'.g01.hdf' # Geometry HDF file name for HEC-RAS runs that include correct terrain for the scenario
        geometryHDFfile = allOptions[choices[0]] # Pick terrain file
        fileEnding  = os.path.splitext(geometryHDFfile)[1] # Split the file name and get the extension value
        fileEnding = fileEnding.replace('\n', '') # Delete extra new line 
        
        geometryOrigHDF = geometryfile + fileEnding +'.hdf'  # Split the geometry HDF file for the particular scenario
        splitHDFname = os.path.splitext(geometryOrigHDF)[0] # Split name and take off .hdf
        splitagain = os.path.splitext(splitHDFname)[0] # Split name and toke off .g0#
        os.rename(geometryOrigHDF, splitagain + '.g01' + '.hdf') # Resave file as the geometry file .g01.hdf to be used as the terrain file for that scenario run
        
        index = 0 # Index to know where to insert
        for line in lines:
            if "rating curve" in line.lower(): # This is where to put the options below this
                # Once you get to this spot insert options
                for geoChoiceName in choices[1:]: # Insert all options
                    # Insert all options into list at index, by passing the key (name) to the dictionary
                    lines[index:index] = allOptions[geoChoiceName]
                break
            
            index+=1
                    
        # Open edited geometry file with added random options from above 
        geometryOutfile = open(geometryfile + '.g01','w') # Saved template geometry file  
        geometryOutfile.writelines(lines)
        geometryOutfile.close() # Close file
        
        ########################## RUN HEC-RAS ########################## 
        
        # HEC-RAS Controller Code referenced from "Application of Python Scripting 
        # Techniques for Control and Automation of HEC-RAS Simulations" by Tomasz Dysarz 2018
       
        # RAS Controller for HEC-RAS 5.07
        hec = win32com.client.Dispatch("RAS507.HECRASController")
        hec.ShowRas()
        # HEC-RAS file name
        RASProject = os.path.join(os.getcwd(), RASfile) # Name of HEC-RAS file 
        hec.Project_Open(RASProject) 
        hec.Compute_CurrentPlan()
        while hec.Compute_Complete() == False: # Compute each scenario before closing and starting next scenario
            continue    
        
        ########################## CALCULATE RESULTS ########################## 
        
        pathnameDepth = "Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/2D Flow/Depth" # Path to Depth in HDF results file
        pathnameVelocity = "Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/2D Flow/Face Velocity" # Path to Velocity in HDF results file
        pathnameShearStress = "Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/2D Flow/Face Shear Stress" # Path to Shear Stress in HDF results file
        pathnameVelocity_X = "Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/2D Flow/Node X Vel" # Path to Velocity Node X in HDF results file
        pathnameVelocity_Y = "Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/2D Flow/Node Y Vel" # Path to Velocity Node Y in HDF results file
       
        # cellLocations holds all the cell locations where the key is 
        # the location name and the values are a list of the cells
        cellLocations = getLocations(cellsfile)
        # faceLocations holds all the face locations where the key is 
        # the location name and the values are a list of the faces
        faceLocations = getLocations(facesfile)
        # facepoints holds all the face point values for each cell
        # where the key is the location name and the values are a list of the face points
        facePoints = getLocations(faceptsfile)
        
        hecFile = h5py.File(HECresultsfile, 'r') # Creates a dictonary type object of HEC-RAS results file
        
        
        dataDepth = hecFile[pathnameDepth] # Depth
        dataVelocity = hecFile[pathnameVelocity] # Velocity
        dataShearStress = hecFile[pathnameShearStress] # Shear stress 
        dataVelocity_X = hecFile[pathnameVelocity_X] # Velocity Node X
        dataVelocity_Y = hecFile[pathnameVelocity_Y] # Velocity Node Y
        
    # CALCULATE PERCENT TIME INUNDATED AND DURATION 
    # Use cell values to calculate percent time inundated and duration
    # If cells are "wet" count as inundated (cell value for depth is greater than zero or can specify
    # another minimum depth value (minDepth))
        
        for location, cellFaces in cellLocations.items():
            total = 0 # Initialize total variable for percent time inundated calculation
            totalDuration = 0 # Initialize totalDuration variable for duration calculation 
            for cellFace in cellFaces:
                inundatedTimesHEC = dataDepth[:,cellFace] # Cell face index 
                inundatedTimes = inundatedTimesHEC[()] > minDepth # Check if depth is greater than the minimum depth at each time step for each cell
                numInundated = np.count_nonzero(inundatedTimes) # If depth of a cell is greater than minimum depth, will show a 1 so add up the ones
                percentInundated = numInundated/inundatedTimesHEC.size # Calculate percent time inundated by dividing by total inundated time steps
                total += percentInundated # Keep track of percent time inundated
                totalDuration += numInundated # Keep track of duration 
            
            percent_time_innundated[(location, scenario)] = (total/len(cellFaces))*100 # Percent Time Innundated for each location and scenario
            duration[(location, scenario)] =   (totalDuration/len(cellFaces))    # Duration for each location and scenario
                
    # CALCULATE DEPTH
    # Use cell values to calculate depth
    # Depth values are calculated by cell in HEC-RAS hdf file 
    # Take maximum depth value for each cell specified for each location and find the average to get an 
    # average depth value for each location  
        for location, cellFaces in cellLocations.items():
            total = 0 # Initialize total variable for depth calculation 
            for cellFace in cellFaces:
                dataDepthCell = dataDepth[:,cellFace] # Cell face index 
                total += max(dataDepthCell[()]) # Take depth value for cell 
            depth[(location, scenario)] = total/len(cellFaces) # Average depth value for each location 
    
    # CALCULATE STREAM POWER 
    # Use cell face values to calculate stream power
    # Velocity and shear stress are calculated at each cell face value in the HEC-RAS hdf file 
    # Stream power is calculated as velocity times shear stress in HEC-RAS but is not calculated
    # explicitly in the hdf file
    # To calculate stream power for each face value, the maximum shear stress is multiplied by the maximum velocity at each time step
    # The maximum stream power value is calculated for each of the cell faces for each of the locations
    # The maximum cell face value is considered the stream power for the location
    
        for location, faces in faceLocations.items():
            maxStreampower = 0 # Initialize maxStreampower variable for stream power calculation 
           
            for face in faces:
                dataShearFace = dataShearStress[:,face] # Cell face index for shear stress
                maxShear = max(abs(dataShearFace)) # Take maximum of absolute value of face shear stress over model time frame
                dataVelocityFace = dataVelocity[:,face] # Cell face index for face veloicty 
                maxVelocityFace = max(abs(dataVelocityFace)) # Take maximum of absolute value of face velocity over model time frame
                
                newMaxStreampower = (maxShear*maxVelocityFace) # Stream power = shear stress * velocity for each cell face for each time step
                
                # Keep maximum cell face value for each location
                if newMaxStreampower > maxStreampower:
                    maxStreampower= newMaxStreampower
               
            stream_power[(location, scenario)] = maxStreampower # Stream Power is equal to the maximum cell face value for each location
        
          # CALCULATE VELOCITY
          # Velocity is calculated using the face points Node X and Node Y values 
          # The maximum values at each face point was found over the time series
          # The Pythagorean Theorem is used to find the resultant velocity between the Node X and Node Y values
          # The maximum face point resultant vecotr for each location is considered the velocity for that cell 
                
        for location, facePts in facePoints.items():
                maxVelocity = 0 # Initialize maxVelocity variable for velocity calculation 
                for facePt in facePts:
                    dataVelocityFace_X = np.array(dataVelocity_X[:,facePt]) # Cell face index for X node
                    dataVelocityFace_Y = np.array(dataVelocity_Y[:,facePt]) # Cell face index for Y node
                    
                    max_X = max(abs(dataVelocityFace_X)) # Take maximum of absolute value of velocity for node X over model time frame
                    max_Y = max(abs(dataVelocityFace_Y))  # Take maximum of absolute value of velocity for node y over model time frame
                    
                    # Use Pythagorean Theorem to find resultant velocity 
                    velocity_XY = np.sqrt(max_X**2 + max_Y**2)
                    
                    newMaxVelocity = velocity_XY # Take resultant velocity vector as maximum for that face point
                   
                    # Keep maximum face point value for each location
                    if newMaxVelocity > maxVelocity:
                        maxVelocity = newMaxVelocity
                    
                velocity[(location, scenario)] = maxVelocity # Maximum velocity of the face points of each cell is consideedr the velocity for that location 
        
        
        hecFile.close() # Close the HEC-RAS file
        hec.QuitRas() # Close HEC-RAS
        del hec # Delete HEC-RAS controller
        
        # Geometry HDF file must be saved back to it's original extension in order to be used for other scenarios 
        splitfinalHDFname = os.path.splitext(finalHDF)[0]  # Split name and take off .hdf
        splitagainfinal = os.path.splitext(splitfinalHDFname)[0] # Split name and toke off .g0#
        os.rename(finalHDF, splitagainfinal +  fileEnding + '.hdf')  # Resave file with the original geometry HDF file extension 
        
    return depth, velocity, duration, percent_time_innundated, stream_power 
   

########################## RESULTS ANALYSIS ########################## 
# Function to set up data in correct matrix: 
def toPandas(dictionary):
    """
        toPandas takes a dictionary (for each data variable of interest calculated above)
        It returns a dataframe for each data input 
        
        """
    depth_Matrix = list(dictionary.items())
    lists = list(zip(*depth_Matrix)) # Lists the matrix
    data = lists[1] # Values
    names = lists[0] # Scenario/locations
    locations, scenarios = zip(*names) 
    locations = list(locations) # Split locaiton values
    scenarios = list(scenarios) # Split scenario values
    df = pd.DataFrame(data, columns = ['depths']) # Create data frame
    df['locations'] = locations # Add locations to data frame
    df['scenarios'] = scenarios # Add scenarios to data frame
    df2 = df.pivot(index = 'scenarios', columns = 'locations', values = 'depths') # Matrix, Scneario x Location
    
    return df2

# Function to calculate percent difference: 
def percentDifference(pandasDataframe):
    """
    percentDifference calculates the percent difference compared to Scenario 1 
    (assuming Scenario 1 is the original or whichever scenario you would like to do the comparison on)
    
    The pandasDataframe created from toPandas can be used for each of the variables to calculate the
    percent difference
    It returns a dataFrame of the percent difference results 
    
    """
    
    df2 = pandasDataframe
    percentDiff = {} # Dictionary to hold percent difference
    rows, columns = df2.shape    
    for row in range(1,rows): 
        rowName = df2.index[row]
        for column in range(columns):
            colName = df2.columns[column]
            percentDiff[(colName,rowName)] = ((df2.iloc[row,column] - df2.iloc[0,column]) / df2.iloc[0,column]) * 100 # Calculate percent difference compared to Scenario 1
        
    dataFrame =  toPandas(percentDiff) # Convert to dataframe  
    return dataFrame
 
########################## HEAT MAP ########################## 
def heatmap(array, labels_scenario, labels_location, title ="", saveFigName = ""): 
# Code for heatmap was referenced from the page "Creating annotated heatmaps" 
# https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
    """
    heatmap uses the results of each variable and creates a plot displaying the percent change from 
    scenario 1 for each location 
    
    Inputs: 
    array = percent difference data in data frame format
    labels_scenario = name of scenarios to appear on plot
    labels_location = name of labels to appear on plot
    title = title to appear on plot. Must be entered in quotes
    saveFigName = name that figure will save to in file. Must be entered in quotes  
    
    """
    
    array = np.round(array,1)
    data_plot = np.array(array)
    fig, ax = plt.subplots()
    im = ax.imshow(data_plot, cmap = "YlOrBr") # Color of heat map
    
    # Show tick Marks 
    ax.set_xticks(np.arange(len(labels_location)))
    ax.set_yticks(np.arange(len(labels_scenario)))
    
    # Label tick marks
    ax.set_xticklabels(labels_location)
    ax.set_yticklabels(labels_scenario)
    
    # Rotate the tick labels and set alignment 
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    text_value = (np.amax(data_plot) - abs(np.amin(data_plot)))/2 # Change text color for color bar
    
    # Loop over data dimensions and create text 
    for i in range(len(labels_scenario)): 
        for j in range(len(labels_location)): 
            if data_plot[i,j] < text_value: # Less than midpoint value print black text
                text = ax.text(j,i, np.round(data_plot[i,j],1), ha="center", va="center", color = "k", fontsize = 6) # Change change font color w = white, b = blue, r = red, k = black 
            else:  # Greater than midpoint value print white text
                text = ax.text(j,i, np.round(data_plot[i,j],1), ha="center", va="center", color = "k", fontsize = 6)         
                      
    # Create a colorbar
    color_bar = ax.figure.colorbar(im, ax=ax)
    color_bar.ax.set_ylabel("Percent Difference", rotation = -90, va="bottom")
    
    # Print figure 
    ax.set_title(title) # Title
    fig.tight_layout()
    plt.savefig(saveFigName) # Save figure
    plt.show()
    
########################## 3D PLOT ########################## 
def plot3d(num_locations, num_scenarios, ticks_x_labels, ticks_y_labels, data, title = "", zlabel = "", saveFigName = ""):
    """
    plot3d uses the results of each variable and creates a 3D plot of the raw results for each location
    and each scenario
    
    Inputs: 
    num_locations = number of locations that results are being calculated for
    num_scenarios = number of scenarios 
    tick_x_labels = scenario names to appear on graph
    tick_y_labels = location names to appear on graph
    data = raw data in data frame format
    title = title to appear on plot. Must be entered in quotes
    zlabel = variable being plotted name to appear as z axis label. Must be entered in quotes
    saveFigName = name that figure will save to in file. Must be entered in quotes
    
    """
    
    # Set 3D plot parameters 
    locations = num_locations
    scenarios = num_scenarios
    y = list(range(1,locations+1))
    x = list(range(1,scenarios+1))
    
    dx= 0.1  # Scale of bars
    dy=  0.1 # Scale of bars
    z = 0 # Start z values at 0
    
    # Set 3D plot parameters
    fig = plt.figure()
    ax = plt.axes(projection = '3d')
    ticks_x = ticks_x_labels
    ticks_y = ticks_y_labels
    plt.xticks(x,ticks_x, fontsize = 6)
    plt.yticks(y,ticks_y, fontsize = 6)
    
    data = np.array(data) # Create a numpy array 
    # Plot values 
    for k in range(0,scenarios): 
        for p in range(0,locations):
              ax.bar3d(x[k],y[p],z, dx, dy, data[k,p])
    # Plot        
    plt.xlabel('Scenario', fontsize = 8) # x label 
    plt.ylabel('Location', fontsize = 8) # y label
    ax.set_zlabel(zlabel, fontsize = 8) # z label
    plt.title(title) # Title 
    plt.savefig(saveFigName) # Save figure
 
