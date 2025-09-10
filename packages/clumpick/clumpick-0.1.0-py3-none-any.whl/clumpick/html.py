
import csv
import json
import os
import webbrowser
import re
import time
import datetime
import logging


def generate_html_content(data_json, alignment_json):

# Step 2: Generate the HTML content
    

    # Now to load in the colors 
    def load_color_palette(filepath):
        colors = []
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("//") or line.startswith("#") and len(line) > 7:
                    continue  # Skip blank lines or comments
                color = line.split()[0]  # Only grab the hex code
                colors.append(color)
        return colors
    color_palette = load_color_palette(os.path.join("clumpick","default_palette.txt"))
    color_palette_js = json.dumps(color_palette)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>D3 Multi-Chart Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">


  <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>


<style>
  
body {{
  font-family: Helvetica, sans-serif;
  display: flex;
  flex-wrap: wrap;
  gap: 20px; 
  background-color: #dfdfdf;
}}
#header-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 55%;
  height: 80px;
  margin-bottom: 10px;
  border-bottom: 8px solid #ccc;
  background-color:#425A63;
  border-radius: 8px;

}}
h1{{
    font-family: "Helvetica", sans-serif;
    font-weight: bold;
    color:#F5eebb;
    margin: 30px;
}}

#pageTitle {{
  font-family: "Helvetica", sans-serif;
  font-weight: bold;
  color:#F5eebb;
  margin: 30px;

  cursor: text;            /* I-beam cursor */
  caret-color: #F5eebb;    
  outline: none;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 700px;       
}}

#pageTitle:focus {{
  box-shadow: inset 0 -6px 0 rgba(245, 238, 187, 0.35);

  }}

#pageTitle[contenteditable="true"]:empty::before {{
content: attr(data-placeholder);
color: rgba(245, 238, 187, 0.6);
}}

#toggleNetworkBtn {{
display: relative;
width: 90px;
height: 90px;
font-family: "Helvetica", sans-serif;
font-weight: bold;
text-align: center;
justify-content: center;
align-items: center;
border: none;
color: #425A63;
background-color: #F5eebb;
border-radius: 50%;
margin-left: 20px;
margin-right: 20px;
}}

#resetZoomBtn {{
display: relative;
width: 90px;
height: 90px;
font-family: "Helvetica", sans-serif;
font-weight: bold;
text-align: center;
justify-content: center;
align-items: center;
border: none;
color: #425A63;
background-color: #F5eebb;
border-radius: 50%;
margin-left: 10px;
margin-right: 45px;
}}


#toggleNetworkBtn:hover, #resetZoomBtn:hover {{
background-color: #9A8A40;
box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3);
}}


#sidebar {{
position: relative;
margin-right: 20px;
width: 240px;
background-color: #EDEED1; 
border-radius: 16px;
padding: 10px;
font-family: "Helvetica", sans-serif;
z-index: 100;
overflow-wrap: break-word;
max-height: 30vh;
overflow-y: auto;
border-top: 20px solid #ccc;
}}

#sidebar h2 {{
margin-top: 0;
font-size: 8px;
text-align: center;
font-weight: normal;
color: #003264;
}}

#tab-cluster h2,
#tab-colors h2 {{
font-size: 16px;      
text-align: left;
font-weight: bold;  
padding-bottom: 10px; 
margin-top: 10px;        
margin-bottom: 30px; 
border-bottom: 2px solid #425A63; 
}}


#legend-content {{
  display: flex;
  flex-wrap:wrap;
  gap: 12px;
}}
  #zoom-wrapper {{
  width: 73vw;
  height: 77vh;
  overflow: auto;
  border-radius:8px;
  position: relative;
  background-color: #fff;
  touch-action: none;
}}
/* allow pinch/drag gestures to be captured by d3-zoom instead of scrolling the page */
#zoom-wrapper {{ touch-action: none; cursor: grab; }}
#zoom-wrapper.panning {{ cursor: grabbing; }}

#chart-grid {{
  transform-origin: 0 0;
  will-change: transform;
  /* If you had a CSS transition on transform, remove it: */
  transition: none;
  display: flex;
  background-color: white; /*rgba(0, 255, 0, 0.05);  Light tint for debugging */
  min-height: 100vh;
  flex-direction: column;
  gap: 40px;
  margin: 30px;
  width: max-content;
  position: relative;
}}
.chart-container {{
  
  padding: 5px;
}}
svg {{
  display: block;
}}


@media print {{
body, html {{
  -webkit-print-color-adjust: exact !important;
  print-color-adjust: exact !important;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: visible !important;
}}

/* Force a landscape single-page layout */
@page {{
  size: landscape;
  margin: 1cm;
}}


/* Prevent splitting */
#zoom-wrapper, #chart-grid, .chart-container {{
page-break-inside: avoid !important;
break-inside: avoid !important;
}}

svg {{
  width: 100% !important;
  height: auto !important;
}}
}}

#downloadImgBtn {{
top: 155px;
position: fixed;
right: 150px;
z-index: 2000; /* above charts */
background-color: #425A63;
color: #F5eebb;
width: 55px;
height: 55px;
font-family: "Helvetica", sans-serif;
font-weight: bold;
text-align: center;
justify-content: center;
align-items: center;
border: none;
border-radius: 8px;

}}

  #toggleM1Btn {{
    display: flex;
    width: 150px;
    height: 90px;
    font-family: "Helvetica", sans-serif;
    font-weight: bold;
    text-align: center;
    justify-content: center;
    align-items: center;
    border: none;
    color: #F5eebb;
    background-color: #425A63;
    border-radius: 8px;
    margin-left: 15px;
    font-size: 18px;
    
  }}
  #downloadImgBtn:hover, #toggleM1Btn:hover {{
  background-color: #9A8A40;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3);
}}
  
.rightTopIcon-btn {{
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}}

.rightTopIcon-btn svg {{
  width: 28px;
  height: 28px;
}}


.info-container {{
  position: relative;
  margin-left: 15px;
  display: inline-block;
}}


.info-container2 {{
  position: relative;
  display: inline-block;
}}

.info-icon {{
  width: 32px;
  height: 32px;
  background-color: #F5EEBB;
  border-radius: 50%;
  border: none;
  font-weight: bold;
  font-family: "Helvetica", sans-serif;
  font-size: 22px;
  color: #425A63;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
 
}}

.info-box {{
  position: absolute;
  top: 30px;
  left: -500px;
  background: #FFFDD0;
  padding: 12px;
  width: 780px;
  z-index: 10000;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: none;                  /* remove border when open */
  font-family: Helvetica, sans-serif;
  font: 16px;
  color: #003264;
}}

.hidden {{
  display: none;
}}

.info-box h3 {{
  margin-top: 0;
}}

#closeInfo {{
 background-color: #003264;
  color: white;
  font-family: Helvetica, sans-serif;
  font-weight: bold;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}}

.population-toggle-icon {{

  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 240px;
  height: 50px;
  border-radius: 16px;
  padding: 10px;
  font-weight: bold;
  font-size: 19px;
  color: #EDEED1;
      z-index: 100;
      overflow-wrap: break-word;
      overflow-y: auto;
      /*border-top: 20px solid #EDEED1;*/
  background-color: #425A63;
  font-family: Helvetica, sans-serif;
  font-weight: bold;


}}

.population-box {{
  position: absolute;
  top: 30px;
  left: 30px;
  background: #FFFDD0;
  padding: 12px;
  width: 333px;
  z-index: 100;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: none;                  /* remove border when open */
  font-family: Helvetica, sans-serif;
  font: 16px;
  font-weight: bold;
  color: #003264;
}}

.population-box h3 {{
   color: #003264;
  font-family: Helvetica, sans-serif;
  font-weight: bold;
  margin-top: 0;
}}
#population-order-box div {{
  background-color: #75975e;
  color: white;
  font-family: Helvetica, sans-serif;
  font-weight: bold;
  padding: 10px 14px;
  border-radius: 6px;
  cursor: move;
  user-select: none;
  margin-bottom: 3px;
}}

/* Buttons */
#closePopulationBox,
#applyPopulationOrder {{
  background-color: #003264;
  color: white;
  font-family: Helvetica, sans-serif;
  font-weight: bold;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}}

#closePopulationBox:hover,
#applyPopulationOrder:hover {{
  background-color: #00508c;
}}
#label-input-panel {{
  position: relative;
  width: 240px;
  border-radius: 16px;
  padding: 10px;
  font-weight: bold;
  font-size: 22px;
  color: #425A63;
  z-index: 10;
  pointer-events: auto;
  overflow-wrap: break-word;
  max-height: 50vh;
  overflow-y: auto;
  border-top: 20px solid #425A63;
  background-color: #EDEED1;
  font-family: Helvetica, sans-serif;
  }}

.sidebar-panel-colors {{
  width: 240px;
  background-color: #EDEED1;
  border-radius: 16px;
  margin-right: 41px;
  padding: 10px;
  font-family: "Helvetica", sans-serif;
  color: #425A63;
  max-height: 45vh;
  overflow-y: auto;
  border-top: 20px solid #425A63;
}}

 .tab-container {{
      padding: 10px;
    }}


.tab-buttons {{
 display: flex;
 margin-bottom: 15px;
 border-radius: 8px;
  overflow: hidden;
  border: 2px solid #ccc;
}}

.tab-btn {{
  flex: 1;
 background-color: #ccc;
 border: none;
 padding: 12px 8px;
 font-weight: bold;
  font-size: 14px;
 cursor: pointer;
    color: #254261;
  transition: all 0.2s ease;
      border-right: 1px solid #999;
}}

.tab-btn:last-child {{
  border-right: none;
}}

.tab-btn.active {{
  background-color: #254261;
  color: white;
}}

.tab-btn.not(.active){{
  background-color: #B8B8B8;
  color: white;
}}
.tab-content {{
  display: block;
 
}}

.tab-content.hidden {{
  display: none;
}}

#cluster-reorder-bar {{
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: stretch;
  width: 100px;                  
  height: calc(100vh - 200px);  /* full height minus header */
  border-radius: 8px;
  margin-right: 20px;
  padding: 10px;
  box-sizing: border-box;
  background: transparent; 
}}
.pencil-box {{
  background: #425A63;         
  color: #EDEED1;                
  display: inline-flex;        
  align-items: center;
  justify-content: center;
  width: 50px;                 
  height: 50px;
  border-radius: 8px;         
  margin-bottom: 15px;         
  cursor: pointer;
}}

.pencil-box i {{
  font-size: 25px;             /* icon size */
  color: #EDEED1;                
}}


/* Fullscreen container */
.fullscreen-view {{
  display: none; /* hidden until opened */
  position: fixed;
  z-index: 10000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.95); /* dark backdrop */
  overflow: auto; /* allow scroll if big */
  padding: 20px;
}}

/* Close button */
.close-fullscreen {{
  position: absolute;
  top: 20px;
  right: 30px;
  color: white;
  font-size: 40px;
  font-weight: bold;
  cursor: pointer;
  z-index: 10001;
}}
.close-fullscreen:hover {{
  color: red;
}}

/* Ensure cloned chart grid scales nicely */
.fullscreen-view #chartGridFullscreenContent {{
  display: flex;
  flex-direction: column;
  align-items: center;
}}

#fullscreenBtn {{  
  position: fixed;
  top: 155px;
  right: 77px;
  width: 55px;
  height: 55px;
  z-index: 2000; /* above charts */
  background-color: #425A63;
  color: #F5eebb;
  border: none;
  border-radius: 8px;
  font-size: 24px;
  padding: 10px 16px;
  cursor: pointer;
}}

#fullscreenBtn:hover {{
  background-color: #9A8A40;
}}


.pulse-bottom {{
  animation: pulseFill 1.1s ease-in-out 2;
}}

@keyframes pulseFill {{
  0%   {{ opacity: 1; }}
  50% {{ opacity: 0.4; }}
  100% {{ opacity: 1; }}
}}
#openDomSort{{
  display: flex;
  width: 150px;
  height: 90px;
  font-family: "Helvetica", sans-serif;
  font-weight: bold;
  font-size: 18px;
  text-align: center;
  justify-content: center;
  align-items: center;
  border: none;
  color: #F5eebb;
  background-color: #425A63;
  border-radius: 8px;
  user-select: none;
}}
.chart-cell.preselect {{
  outline: 6px solid rgba(255, 200, 0, 0.8);
  outline-offset: 4px;
  cursor: pointer; 
}}
.chart-cell.highlighted {{
  box-shadow: 0 0 0 8px rgba(255, 200, 0, 0.95) inset; /*found this slightly glowing effect!*/
}}

</style>
</head> 
<body>

<!-- Top Right Buttons appearing on the chart-grid area: Fullscreen, Download -->
<button id="fullscreenBtn" title="Toggle fullscreen"><i class="fa-solid fa-expand"></i></button>
<button id="downloadImgBtn" class="download-btn" title="Download image"><i class="fas fa-download" style="font-size: 25px;"></i></button>

<!-- Things on the top row: Title, Info, Network Toggle, Major Mode Toggle, Dominant Sort -->

<div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; margin-bottom: 10px; width: 100%;">

<div id="header-row">
 <h1 id="pageTitle" contenteditable="true" spellcheck="false" data-placeholder="Type a title…">Clustering Modes</h1>

<div style="display: flex; align-items: center; gap: 12px; margin-right: 20px;">
<div class="info-container"><span class="info-icon">  ?  </span>
  <div class="info-box hidden" id="infoBox">
    <h3>How To Use This Tool:</h3>
    <p>
     <li> <b>Refresh</b> the page at any time to reset the view. </li>
     <li><b> Relabel the Page Title</b> by clicking on the text. </li>
     <br>
     <li> <b>Dominant Sort</b> allows the user to select one plot, for which the major cluster will be identified for each population, and within each population individuals will be reordered in descending memberships. Then, all plots will be rearranged according to the order of individuals from the Dominantly Sorted plot. </li>
     <li> <b>Major Modes</b> control the visibility of the minor modes for each of the K clusters. It will display only the primary mode of each K, and result in only one column. </li>
     <br>
     <li><b>Network Connection Visibility</b> is controlled by the circular eye button. It provides information reflected in the opacity of the line, for the alignment across K clusters. Opacity is the strength of the connection relative to all other connections. Hovering over a line will display the user-provided alignment cost. </li>
     <li><b>Complete Display</b> of all plots may be accessed through the magnify button, and Fullscreen may be accessed through the square button of the active chart. </li>
     <li><b>Downloading</b> will provide the user with two .PNG files - the full chart containing all modes and the Stacking Legend with user-specified cluster labels. Network connections can be hidden through the Network Connection Visibility button. Furthermore, it will open the print dialogue box, for which the user should select to include background graphics in settings. It is recommended to scale the plotting display with the Complete Display button before downloading. Note that the downloading requires a page that allows multiple file downloads, and typically takes 1-2 minutes. When prompted the user should wait on a page that displays an unresponsive box. Thank you for your patience. </li>
     <br>
     <li><b>Stacking Legend</b> is a vertical drag-and-drop bar that allows the user to designate the top down stacking order of the clusters across all plots. Hovering over a color reveals the user-input cluster label name. </li>
     <li><b>Cluster Key</b> is a hovering legend that highlights the corresponding cluster across all plots simultaneously, and Custom Colors allows the user to designate colors for each cluster. </li>
     <li><b>Cluster Name Relabeling</b> allows for the user to label Clusters, and this information will be updated to the hovering label of the Stacking Legend. </li>
    </p>
    <button id="closeInfo">Close</button>
  </div>
</div>
  
</div>
</div>


<div style="display: flex; align-items: flex-start; gap: 12px; margin-left: 5px; margin-right: 20px;">

<div class="info-container2">
   <button id="toggleNetworkBtn">HIDE NETWORK</button>
   <button id="resetZoomBtn">RESET ZOOM</button>
</div>

<button id="openDomSort">Dominant Sort</button>
<button id="toggleM1Btn">Major<br>Mode</button>

</div>
</div>



<div style="display: flex;">

  <!-- LEFT SIDEBAR -->
  <div id="left-column" style="display: flex; flex-direction: column; gap: 20px;">
      <!-- Top button styled like a sidebar -->
      <div id="button-row style="display: flex; flex-direction: row; gap: 20px;">
      <div class="population-toggle-icon">Reorder Populations &nbsp;<i class="fa fa-pencil" aria-hidden="true"></i>
    </div>  

    <div class="population-box hidden" id="populationReorderBox">
      <h3>Population Order</h3>
      <div style="display:flex; gap:10px; margin-bottom:10px;">
        <button id="closePopulationBox">Close</button>
        <button id="applyPopulationOrder">Apply</button> 
      </div>
      <p>Drag to reorder populations:</p>
      <div id="population-order-box"></div>
    </div>
  </div>

  <!-- Tabbed Panel for the custom colors and hovering legend-->
  <div class="sidebar-panel-colors">
    <div class="tab-container">
      <div class="tab-buttons">
        <button class="tab-btn active" data-tab="tab-cluster">Cluster Key</button>
        <button class="tab-btn" data-tab="tab-colors">Custom Colors</button>
      </div>
      
      <div class="tab-content" id="tab-cluster">
        <h2>Hover to view corresponding clusters. </h2>
        <div id="legend-content"></div>
        <div id="hover-legend" style="margin-top: 20px;"></div>
      </div>
      
      <div class="tab-content hidden" id="tab-colors">
        <h2>Click to customize.</h2>
        <div id="color-pickers"></div>
      </div>
    </div>
  </div>

  <!-- Bottom panel for renaming clusters -->
  <div id="label-input-panel" style="position: relative; width: 240px; padding: 10px; border: 1px solid #ccc; border-radius: 10px; background: #EDEED1; font-family: Helvetica, sans-serif; color: #425A63; font-weight: bold;">
    <button id="prev-label" style="position: absolute; top: 40%; left: 25px; height: 30px; width: 30px;background-color:#425A63; color:#F5eebb;border:none; border-radius: 6px;">&#8592;</button>
    <div id="label-input-container" style="text-align: center; margin: 0 30px;"></div>
    <button id="next-label" style="position: absolute; top: 40%; right: 25px; height: 30px; width: 30px;background-color:#425A63; color:#F5eebb;border:none; border-radius: 6px;">&#8594;</button>
  </div>
</div>

<!-- Cluster Stacking Order Bar and Main Chart Grid -->
<div style="display: flex; flex-direction: column; gap: 6px;">
  <div class="pencil-box">
  <i class="fa-solid fa-arrows-up-down"></i>
  </div>
  <div id="cluster-reorder-bar"></div>
  </div>

  <!-- MAIN ZOOMABLE CONTENT -->
  <div id="zoom-wrapper">
  <div id="chart-grid" style="display: flex; flex-direction: column; gap: 40px;"></div>
  </div>
</div>

<!-- Fullscreen Chart Grid View -->
<div id="chartGridFullscreen" class="fullscreen-view">
  <span id="closeFullscreenBtn" class="close-fullscreen">&times;</span>
  <div id="chartGridFullscreenContent"></div>
</div>

  <script>
    const allChartData = {data_json}; 
    const alignmentMatrix = {alignment_json};
    const pastelWithDarks = {color_palette_js};

    console.log("Alignment Matrix:", alignmentMatrix);
  </script>

   <script src="clumpick/script.js"></script>
</a>



</body>
</html>
"""

    # Step 3: Write HTML file and open it
    output_file = "visualization.html"

    with open(output_file, "w") as file:
        file.write(html_content)

    # Open in browser
    full_path = os.path.abspath(output_file)
    webbrowser.open('file://' + full_path)



    return html_content