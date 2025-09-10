/* =========================================================================
   TABLE OF CONTENTS
   [1] GLOBAL CONSTANTS AND SET UP
   [2] USER INTERACTIVITY
   [3] RENDERING
   [4] NETWORK CONNECTIONS
   [5] DOMINANT SORTING FUNCTION
   [6] LEGEND INTERACTIONS (legends/reorder/sort/zoom/download)
   [7] RENDERING (charts/rows/refresh)
   [8] IMAGE EXPORTING FUNCTIONALITY
   [9] REFRESH ALL CHARTS FUNCTION 
   ========================================================================= */

// [1] GLOBAL CONSTANTS AND SET UP=========================================================================

// make a tooltip 
const mouseTip = d3.select("body")
  .append("div")
  .attr("id", "mouseTip")
  .style("position", "absolute")
  .style("background", "#f9f9f9")
  .style("border", "1px solid #ccc")
  .style("padding", "8px")
  .style("border-radius", "4px")
  .style("font-size", "14px")
  .style("color", "#333")
  .style("pointer-events", "none");

const tooltip = d3.select("body").append("div")
  .attr("id", "cluster-tooltip")
  .style("position", "absolute")
  .style("background", "rgba(0,0,0,0.7)")
  .style("color", "white")
  .style("padding", "5px 8px")
  .style("border-radius", "4px")
  .style("pointer-events", "none")
  .style("font-size", "12px")
  .style("display", "none");


// ORGANIZE CHART DATA 
const allK = Object.keys(allChartData).sort((a, b) => +a.slice(1) - +b.slice(1));
const lastK = allK[allK.length - 1];

const firstMode = Object.values(allChartData[lastK])[0];
const firstRow = firstMode[0];
const clusterKeys = Object.keys(firstRow).filter(k => k.startsWith("Cluster")); // initial ordering of the clusters
const allUniquePopulations = Array.from(new Set(firstMode.map(d => d.Population))); // all detected populations


// color palette
let clusterColorScale = {}; 
clusterKeys.forEach((key, i) => {
  clusterColorScale[key] = pastelWithDarks[i];
});

//SETTING VARIABLES UP FOR LATER

// Set up for the zooming later
const wrapper = d3.select("#zoom-wrapper");
const chartGrid = d3.select("#chart-grid");
const gridRect = chartGrid.node().getBoundingClientRect();
const wrapperRect = wrapper.node().getBoundingClientRect();

// For Network Connections later
let overlaySvg;
const chartMap = {};

// For mapping alignment edges
const chartPositions = [];

// For vertical stacking reordering 
let clusterOrder = [];
clusterOrder = [...clusterKeys]; // the default initial order
let draggedCluster = null;
// If true: legend order is flipped for the stack
let lastClusterOrderSource = "legend"; // can be either legend or dominant (after dominant sorting), default is the legend

// For population initial ordering and relevant for the reordering function later, first take the population groups then remember to make a UI 
let populationOrder = allUniquePopulations; //initial order
let draggedPopulation = null;

// For user input labels
const clusterLabels = {};  // store user inputs here
let currentIndex = 0;

// For the Hovering Legend
let selectedClusterKey = null;

// For the editable page title
const pageTitle = document.getElementById("pageTitle");
  pageTitle.addEventListener('keydown', e => { if (e.key === 'Enter') e.preventDefault(); });
  pageTitle.addEventListener('blur', () => localStorage.setItem('title', (pageTitle.textContent.trim()||'Untitled')));
  pageTitle.textContent = localStorage.getItem('title') || pageTitle.textContent;

// For dominantly sorting and assigning orders within populations. Using window seems to be cleaner than assigning new constants
let domSortOn = false;
window.perPopClusterOrder = new Map();     // Cluster order within the population (this will be sorted by the largest membership cluster)
window.perPopIndividualOrder = new Map();  // indiviual ordering within each population


// INITIALIZATION creating the vertical stacking legend, hovering tab with the custom colors behind it, cluster naming panel, Population reordering button
renderClusterStackLegend(clusterKeys);
renderClusterHoverLegend(clusterKeys); 
renderColorPickers();
renderSingleLabelInput(clusterKeys);
renderPopulationReorderUI();




//[2] USER INTERACTIVITY=========================================================================

//make the info box (styling on the front page)
document.querySelector(".info-icon").addEventListener("click", () => {
  document.getElementById("infoBox").classList.toggle("hidden");
});

document.getElementById("closeInfo").addEventListener("click", () => {
  document.getElementById("infoBox").classList.add("hidden");
});


// Dominant Sort button on button click
d3.select("#openDomSort").on("click", () => setDominantSort(!domSortOn));

// Dominant Sort button turning off, escape turns it off
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && domSortOn) setDominantSort(false);
});


// Set up zooming and panning across the chart grid, sometimes gets a bit laggy

const zoom = d3.zoom()
  .scaleExtent([0.1, 2])
  .on("zoom", (event) => {
    chartGrid.style(
      "transform",
      `translate(${event.transform.x}px, ${event.transform.y}px) scale(${event.transform.k})`
    );
  });

wrapper.call(zoom);


// tip for the pencil box only - just giving more information 
const pencil = d3.select(".pencil-box");

pencil.on("mouseover", (event) => {
  d3.select("body").append("div")
    .attr("id", "tooltip")
    .style("position", "absolute")
    .style("padding", "6px 10px")
    .style("background", "#333")
    .style("color", "white")
    .style("border-radius", "6px")
    .style("font-size", "13px")
    .style("pointer-events", "none")
    .style("top", (event.pageY - 40) + "px")
    .style("left", (event.pageX + 15) + "px")
    .html("Drag and drop the colors in the vertical bar <br> below to customize cluster stacking order.");
})
.on("mousemove", (event) => {
  d3.select("#tooltip")
    .style("top", (event.pageY - 40) + "px")
    .style("left", (event.pageX + 15) + "px");
})
.on("mouseout", () => {
  d3.select("#tooltip").remove();
});


// Population reordering for the x-axis, UI for button clicking

document.querySelector(".population-toggle-icon").addEventListener("click", () => {
  document.getElementById("populationReorderBox").classList.toggle("hidden");
});

document.getElementById("closePopulationBox").addEventListener("click", () => {
  document.getElementById("populationReorderBox").classList.add("hidden");
});


// The tab button for switching in between the panel of custom colors and the hovering legend
document.querySelectorAll(".tab-btn").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    // Add active class to clicked button
    button.classList.add("active");

    // Hide all tab contents
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.add("hidden"));
    // Show selected tab
    const tabId = button.getAttribute("data-tab");
    document.getElementById(tabId).classList.remove("hidden");
  });
});

// [3] RENDERING=========================================================================

// MAIN INDIVIDUAL BAR CHART RENDERING FUNCTION
// First set the dimensions and margins of the graph
// Group the rows by population and a default cluster order (but there are also cluster orders from stacking legend and dominant sorting functions)
// X-axis ordering of individuals (order of importance is: optional argument, dominant sorting, population reordering, then the original order in the data)
// Set up the scales
// drawing each population separately and rendering the bars with the correct cluster order (taking from dominant sort first then stacking legend then local)
// Organizing labels for populations, drawing lines to mark the separation of populations, titles, border
// Storing info for later network connections
function renderStackedBarChart(data, container, chartTitle, opts = {}) {
  const width = 1600;
  const height = 400;
  const margin = { top: 60, right: 50, bottom: 100, left: 280 };
  const svg = container
    .append("div")
    .attr("class", "chart-container")
    .append("svg")
    .style("background", "transparent")
    .attr("width", width)
    .attr("height", height+120);

  // Group individuals by population
  const populationGroups = {};
  data.forEach(d => {
    if (!d.Population) return;
    if (!populationGroups[d.Population]) {
      populationGroups[d.Population] = [];
    }
    populationGroups[d.Population].push(d);
  });
  // Get a default cluster order
  const localClusterKeys = Object.keys(data[0]).filter(k => k.startsWith("Cluster"));



  // Sorting out the x-axis ordering 
  const xNames = [];
  populationOrder.forEach(pop => {
  const inPop = data.filter(d => d.Population === pop);
  if (inPop.length === 0) return;

  // Determine the desired order of individuals in this population
  const desiredNames = (opts?.getIndividualsOrder && opts.getIndividualsOrder(pop)) || perPopIndividualOrder.get(pop) || inPop.map(d => d.name); // fallback: current order in the data
  // keep only names that exist in this population
  desiredNames.forEach(n => {
    if (inPop.some(d => d.name === n)) xNames.push(n);
  });
  });


  // Setting up the scales!
  const xScale = d3.scaleBand()
    .domain(xNames)
    .range([margin.left, width - margin.right])
    .padding(-1);    
  // Y scale: sum of clusters
  const yScale = d3.scaleLinear()
    .domain([0, 1])
    .nice()
    .range([height - margin.bottom, margin.top]);
  


// Draw each population separately
Object.entries(populationGroups).forEach(([popName, individuals]) => {
  // Determine the order of individuals in this population
  // Dominant sort has precedence over individual sorting, then the optional argument, then the original order
  const orderedNamesinThisPopulation =
  (lastClusterOrderSource === "dominant"
    ? (perPopIndividualOrder.get(popName) || null)
    : null)
  || (opts.getIndividualsOrder?.(popName) || null)
  || individuals.map(d => d.name);

  // Map the ordered names to the actual individual objects, will feed this to stack the data
  const orderedIndividuals = orderedNamesinThisPopulation
    .map(n => individuals.find(d => d.name === n))
    .filter(Boolean);

  // Determine the cluster order for stacking the bars
  // between the dominant sorting function and the stacking legend which is also the global order
  // otherwise use the default local order
  const dominantKeys = perPopClusterOrder.get(popName);
  const legendKeys = (clusterOrder && clusterOrder.length) ? clusterOrder : localClusterKeys; //global order from stacking legend if it exists
  const baseKeys = (lastClusterOrderSource === "dominant" && dominantKeys && dominantKeys.length) // if dominantKeys is turned on and is not empty
    ? dominantKeys
    : legendKeys.slice().reverse(); // the legend has to be reversed for it to line up visually
  const keysForStack = baseKeys.slice();

  // Build the series
  const series = d3.stack().keys(keysForStack)(orderedIndividuals);

  // Draw the bars
  svg.append("g")
    .attr("class", "population-group")
    .selectAll("g")
    .data(series)
    .join("g")
    .attr("class", d => `cluster-series cluster-${d.key}`)
    .selectAll("rect")
    .data(d => d)
    .join("rect")
    //.attr("class", d => `bar cluster-${d3.select(this.parentNode).datum()?.key || ''}`) // or set class via outer selection
    .attr("x", (d, i) => xScale(orderedIndividuals[i].name))
    .attr("y", d => yScale(d[1]))
    .attr("height", d => Math.max(0, yScale(d[0]) - yScale(d[1])))
    .attr("width", xScale.bandwidth())
    // after: .selectAll("rect").data(d => d).join("rect")
    .attr("class", function () {
      // parent <g> has the series data with the key
      const key = this.parentNode && this.parentNode.__data__ ? this.parentNode.__data__.key : null;
      return `bar ${key ? `cluster-${key}` : ''}`;
    })
    .attr("fill", function () {
      const key = this.parentNode && this.parentNode.__data__ ? this.parentNode.__data__.key : null;
      return key ? clusterColorScale[key] : null;
    })
    .on("mouseover", function (event, d) {
      mouseTip
        .html(
          `<strong><br/>Name: ${d.data.name}</strong><br/>Population: ${d.data.Population}<br/>` +
          localClusterKeys.map(key => {
              const clusterNum = key.match(/\d+$/)[0];
              const label = clusterLabels[key] || `Cluster ${clusterNum}`;
              return `${label}: ${(d.data[key] * 100).toFixed(2)}%`;
    })
    .join("<br/>"))
    .style("visibility", "visible");
    d3.select(this).attr("opacity", 0.7);
    })
    .on("mousemove", function (event) {
      mouseTip
        .style("top", (event.pageY - 40) + "px")
        .style("left", (event.pageX + 15) + "px");
    })
    .on("mouseout", function () {
      mouseTip.style("visibility", "hidden");
      d3.select(this).attr("opacity", 1);
    });
  });


  // Organization for the populations (labels and dashed line separation)
  const popLabelPosition = height - margin.bottom + 50;
  const popLabelGroup = svg.append("g");
  const guideGroup = svg.append("g").attr("class", "pop-guides");

  // Map each individual name to its population (once)
  const nameToPop = new Map(data.map(d => [d.name, d.Population]));

  //Search for the boundaries between populations, manual since sometimes individuals within populations' order gets switched around by dominant sort
  const popRanges = []; // just storing the population and its starting and ending index
  let start = 0;
  for (let i = 0; i < xNames.length; i++) {
    const p = nameToPop.get(xNames[i]);
    const nextP = i + 1 < xNames.length ? nameToPop.get(xNames[i + 1]) : null;
    if (p !== nextP) {
      popRanges.push({ pop: p, start, end: i });
      start = i + 1;
    }
  }
  // Draw labels and guide lines
  popRanges.forEach(({ pop, start, end }) => {
    const xStart = xScale(xNames[start]);
    const xEnd   = xScale(xNames[end]) + xScale.bandwidth();
    const xCenter = (xStart + xEnd) / 2;

    // label
    popLabelGroup.append("text")
      .attr("x", xCenter + 11)
      .attr("y", popLabelPosition)
      .attr("text-anchor", "end")
      .attr("transform", `rotate(-33, ${xCenter}, ${popLabelPosition})`)
      .style("font-size", "50px")
      .style("font-weight", "bold")
      .style("fill", "black")
      .text(pop);

    // need to add a line to the last member of each population
    guideGroup.append("line")
      .attr("x1", xEnd)
      .attr("x2", xEnd)
      .attr("y1", margin.top)
      .attr("y2", height - margin.bottom)
      .attr("stroke", "black")
      .attr("stroke-width", 3)
      .attr("stroke-dasharray", "4 2"); //styled as a dashed line
  });

    // X axis - technically invisible for now but can be changed
    svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale).tickSize(0).tickFormat(""));

    // Y axis - also invisible but can be changed
    svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale).ticks(0));

    // Title
    svg.append("text")
      .attr("x", 180)
      .attr("y", margin.top / 2 + 20)
      .attr("text-anchor", "middle")
      .style("font-size", "70px")
      .style("font-family", "Gill Sans, GillSans, 'Gill Sans MT', Calibri, sans-serif")
      .text(chartTitle);

    // Border
    svg.append("rect")
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", width - margin.left - margin.right)
      .attr("height", height - margin.top - margin.bottom)
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("stroke-width", 7);

    // Store the SVG node for network connections later
    chartPositions.push({
      key: chartTitle.replace(/\s/g, ""),
      svg: svg.node()
    });
    svg.datum(data);
}

// End of individual chart rendering function, now organizing how to render through modes and by K

const allModesSet = new Set(); // find all available modes
Object.values(allChartData).forEach(cluster => {
  Object.keys(cluster).forEach(mode => allModesSet.add(mode)); // Then we dynamically add each mode going through each cluster
}); 
const allModes = Array.from(allModesSet).sort((a, b) => +a.slice(1) - +b.slice(1)); // Sort by mode number by chopping off the M


function renderRowOfModes(kNumber, clusterData) {
  const row = d3.select("#chart-grid")
    .append("div")
    .style("display", "flex")
    .style("gap", "80px")
    .style("font-family", "Gill Sans, GillSans, 'Gill Sans MT', Calibri, sans-serif")
    .style("align-items", "flex-start");

  //Make labeling neater  
  const kLabel = `K=${kNumber.slice(1)}`;  // "K=4" if it was "K4"

  // Add a label for the row
  row.append("div")
    .style("width", "60px")
    .style("text-align", "right")
    .style("font-size", "90px")
    .style("font-family", "Gill Sans, GillSans, 'Gill Sans MT', Calibri, sans-serif")
    .style("font-weight", "bold")
    .style("padding-right", "30px")
    .text(kLabel);
     
  // Dynamically loop over all detected modes
  allModes.forEach(mode => {
    if (clusterData[mode]) {
      const chartCell = row.append("div") 
      .attr("class", "chart-cell")   
      .attr("data-mode", mode) 
      .attr("data-k", kNumber) 
      .style("width", "1800px") //since I determined the width to be 1600px for each plot
      .style("height", "700px") // IMPORTANT FOR LAYOUT - spacing in between rows is controlled here
      .style("flex-shrink", "0");   // apparently to prevent resizing

      renderStackedBarChart(clusterData[mode], chartCell, `${kNumber} ${mode}`); 
    }
  });
} 


// Now loop through all the clusters and draw charts
if (typeof allChartData === 'undefined') {
  console.error("Data is missing. Ensure Python injected it into the page.");
} else {
Object.keys(allChartData)
  .sort((a, b) => +a.slice(1) - +b.slice(1)) // Sort by K number 
  .forEach(kNumber => {
    renderRowOfModes(kNumber, allChartData[kNumber]); // then we can draw the whole row for each K
  });

}


// [4] NETWORK CONNECTIONS=========================================================================

const edgeBase = new Map();

// Helping to calculate positions
function getLayoutNode(hi) {
  const node = hi?.node ? hi.node() : hi; //d3 selection or DOM node
  return node.closest?.(".chart-tile") || node.parentElement || node; //have some backups
}

function getBaseEndpoints(fromEl, toEl) {
  const a = getLayoutNode(fromEl);
  const b = getLayoutNode(toEl);

  const x1 = a.offsetLeft + a.offsetWidth  / 2;
  const y1 = a.offsetTop  + a.offsetHeight + 20; // below A 
  const x2 = b.offsetLeft + b.offsetWidth  / 2;
  const y2 = b.offsetTop;                        // above B

  return { x1, y1, x2, y2 };
}

// MAIN NETWORK DRAWING FUNCTION
function drawNetworkConnections() {
  console.log("Drawing network connections..."); //easier to check if working 

  //Setting up the overlaying lines SVG
  const originalLayout  = d3.select("#chart-grid");
  const gridNode = originalLayout.node();

  let overlaySvg = originalLayout.select(".connector-overlay");
  if (overlaySvg.empty()) {
    overlaySvg = originalLayout.append("svg")
      .attr("class", "connector-overlay")
      .style("position", "absolute")
      .style("top", 0)
      .style("left", 0)
      .style("pointer-events", "none")
      .style("z-index", 9999);
  }
  overlaySvg
    .attr("width",  gridNode.scrollWidth)
    .attr("height", gridNode.scrollHeight);

  // Clear previous lines
  overlaySvg.selectAll("*").remove();

  // Map chart keys to SVG nodes 
  chartPositions.forEach(chart => {
    chartMap[chart.key] = chart.svg;
  });

  //Make a scale for the opacities so they are relative to each other
  const allCosts = Object.values(alignmentMatrix).map(v => parseFloat(v.cost));
  const minCost = Math.min(...allCosts); //find the original min and max alignemnt costs
  const maxCost = Math.max(...allCosts);
  
  //Make my scale function
  const opacityScale = d3.scaleLinear()
    .domain([minCost, maxCost])
    .range([0.10, 1]); //Even if the cost is 0, just make it show up super lightly

  // Build edges that are across K (will use the alignment cost data)
  chartPositions.forEach(source => {
    //Know the next K 
    const sourceKey = source.key;
    const sourceK   = parseInt(sourceKey.match(/K(\d+)/)[1], 10);
    const nextK     = sourceK + 1;

    Object.entries(alignmentMatrix).forEach(([edgeKey, value]) => {
      
      const cost_use = parseFloat(value.cost);//for the alignment opacity

      const [from, to] = edgeKey.split("-");
      const toK = parseInt(to.match(/K(\d+)/)[1], 10);
      if (from !== sourceKey || toK !== nextK) return;

      const targetSvg = chartMap[to];
      if (!targetSvg) return;

      // Grab the original coordinates for each line (point to point)
      let base = edgeBase.get(edgeKey);
      if (!base) {
        base = getBaseEndpoints(source.svg, targetSvg);
        edgeBase.set(edgeKey, base);
      }
      const { x1, y1, x2, y2 } = base;


      // visible line
      overlaySvg.append("line")
        .attr("x1", x1)
        .attr("y1", y1)
        .attr("x2", x2)
        .attr("y2", y2)
        .attr("stroke", "black")
        .attr("stroke-width", 8)
        .attr("opacity", opacityScale(cost_use));

      // invisible hover line to make it easier to grab the display box
      overlaySvg.append("line")
        .attr("x1", x1)
        .attr("y1", y1)
        .attr("x2", x2)
        .attr("y2", y2)
        .attr("stroke", "transparent")
        .attr("stroke-width", 100)
        .attr("opacity", 1)
        .style("pointer-events", "all")
        .on("mouseover", function () {
          mouseTip
            .html(`<strong>${from} → ${to}</strong><br/>Alignment cost: ${cost_use.toFixed(5)}`)
            .style("visibility", "visible");
          d3.select(this).attr("stroke", "#3d9900").attr("stroke-width", 12).attr("opacity", 1);
        })
        .on("mousemove", function (event) {
          mouseTip
            .style("top", (event.pageY - 20) + "px")
            .style("left", (event.pageX + 15) + "px");
        })
        .on("mouseout", function () {
          mouseTip.style("visibility", "hidden");
          d3.select(this).attr("stroke", "transparent").attr("stroke-width", 100).attr("opacity", 1);
        });
    });
  });
}

drawNetworkConnections(); //Initial drawing!


// [5] DOMINANT SORTING FUNCTION=========================================================================
// After turning on the Dominant Sorting button, hovering over any plot will allow double clicking
// which will sort the individuals within each population by their descending order of their membership in the largest cluster of their population.
// Then the new order of the individuals from the selected plot will be applied to all the other charts.

// Enabling and disabling the interactions
function allowDominantSortInteractions(enabled) {
  const cells = d3.selectAll(".chart-cell"); //finding all the plots

  //Be neat and clear everything first
  cells.on(".domSort", null)
       .classed("preselect", false)
       .classed("highlighted", false);
  
  // If it needs to be off
  if (!enabled) {
    mouseTip?.style?.("visibility", "hidden");
    return;
  }

  // If it needs to be on then have the event listeners and interactivity!
  cells
    .on("mouseover.domSort", function (event) {
      d3.select(this).classed("preselect", true);
      mouseTip
        .html(`<strong>Double-click</strong> to run Dominant Sort for <em>${this.dataset.k} ${this.dataset.mode}</em>`)
        .style("visibility", "visible");
    })
    .on("mousemove.domSort", function (event) {
      mouseTip
        .style("top",  (event.pageY - 20) + "px")
        .style("left", (event.pageX + 15) + "px");
    })
    .on("mouseout.domSort", function () {
      d3.select(this).classed("preselect", false);
      mouseTip.style("visibility", "hidden");
    })
    .on("dblclick.domSort", function () {
      const k = this.dataset.k;
      const mode = this.dataset.mode;

      d3.selectAll(".chart-cell").classed("highlighted", false);
      d3.select(this).classed("highlighted", true);

      //Now sort the double clicked chart
      runDominantSort(k, mode);
    });
}

// Turn on or off the dominant sorting interactions from the button
function setDominantSort(enabled) {
  domSortOn = !!enabled; //need to turn it on

  const btn = d3.select("#openDomSort");
  const baseLabel = "Dominant Sort";
  btn.attr("data-base-label", baseLabel);

  btn.classed("armed", domSortOn)
     .attr("aria-pressed", domSortOn ? "true" : "false")
     .text(domSortOn ? `${baseLabel} (OFF)` : baseLabel); //trying out new way of updating activity!

  allowDominantSortInteractions(domSortOn);
}

// Make sure the interactions are re-enabled after rerendering (will call this in refreshAllCharts later)
function afterChartsRerendered() {
  allowDominantSortInteractions(domSortOn);
}

// MAIN SORTING FUNCTION
function runDominantSort(kNumber, mode) {
  const data = allChartData[kNumber][mode]; //find the relevant dataset 
  const byPop = d3.group(data, d => d.Population); //group by population

  // Clear previous orders
  window.perPopClusterOrder = new Map();
  window.perPopIndividualOrder = new Map();

  // Then for each population, determine the dominant cluster and sort individuals accordingly
  byPop.forEach((rows, pop) => {
    // Sum clusters for this population
    const sums = {};
    clusterKeys.forEach(k => { sums[k] = d3.sum(rows, r => +r[k]); }); //loop over each cluster and sum the memberships

    // Rank clusters by total
    const clustersRanked = Object.keys(sums).sort((a, b) => sums[b] - sums[a]);
    const dominant = clustersRanked[0];

    perPopClusterOrder.set(pop, clustersRanked);

    // Sort individuals by their value in the dominant cluster (and then by name just in case)
    const sortedNames = rows.slice()
      .sort((a, b) => (+b[dominant]) - (+a[dominant]) || d3.ascending(a.name, b.name))
      .map(d => d.name);

    perPopIndividualOrder.set(pop, sortedNames);
  });

  lastClusterOrderSource = "dominant"; // so it doesn't fight with the renderStackLengend 


  // Re-render everything so every chart now reads from the per-pop maps
  rerenderAllChartsByPopulation();
}




// [6] LEGEND INTERACTIONS (legends/reorder/sort/zoom)=========================================================================
// Cluster hovering legend, Population Reordering, Color pickers, Restacking legend
 
// CLUSTER HOVERING LEGEND
// When you hover over a color circle, it will highlight the corresponding clusters across all the plots
// Also made it clickable too!
function renderClusterHoverLegend(clusterKeys) {
  const legendBox = d3.select("#legend-content");
  legendBox.selectAll("*").remove();

  clusterKeys.forEach((key, i) => {
    const item = legendBox.append("div")
      .style("display", "flex")
      .style("align-items", "center")
      .style("gap", "6px")
      .style("cursor", "pointer")
      .on("mouseover", function() {
        if (!selectedClusterKey) {
          clusterKeys.forEach(otherKey => {
            d3.selectAll(`.cluster-${otherKey}`)
              .attr("opacity", otherKey === key ? 1 : 0.33); //darken the other ones to 33%
          });
        }
      })
      .on("mouseout", function() {
        if (!selectedClusterKey) {
          clusterKeys.forEach(otherKey => {
            d3.selectAll(`.cluster-${otherKey}`)
              .attr("opacity", 1);
          });
        }
      })
      .on("click", function() {
        if (selectedClusterKey === key) {
          // Deselect
          selectedClusterKey = null;
          clusterKeys.forEach(otherKey => {
            d3.selectAll(`.cluster-${otherKey}`)
              .attr("opacity", 1);
          });
        } else {
          // Select
          selectedClusterKey = key;
          clusterKeys.forEach(otherKey => {
            d3.selectAll(`.cluster-${otherKey}`)
              .attr("opacity", otherKey === key ? 1 : 0.33);
          });
        }
      });

    item.append("div")
      .style("width", "50px")
      .style("height", "50px")
      .style("background", clusterColorScale[key])
      .style("border", "none")
      .style("border-radius", "50%")
      .style("display", "flex")
      .style("align-items", "center")
      .style("justify-content","center")
      .style("font-family", "Helvetica, sans-serif")
      .style("font-size", "23px")
      .style("font-weight", "bold")
      .style("color", "white")
      .style("margin-left", "10px")
      .text(key.slice(-1)); // Show only the cluster number
  });
}

//COLOR PICKERS - customize colors with the color picker widget from HTML and then commit the changes with the OK button
function renderColorPickers() {
  const container = d3.select("#color-pickers").html("");

  const commitRecolor = () => {
    renderClusterStackLegend(clusterOrder);
    refreshAllCharts();
    renderClusterHoverLegend(clusterOrder);
  };

  clusterKeys.forEach((key, i) => {
    const current = clusterColorScale[key] || pastelWithDarks[i % pastelWithDarks.length]; // if I run out of colors, just recycle
    const labelText = (key.match(/\d+$/) || [key])[0];

    const row = container.append("div")
      .style("display", "flex")
      .style("gap", "8px")
      .style("align-items", "center")
      .style("margin-bottom", "6px");

    row.append("label")
      .text(`Cluster ${labelText}`)
      .style("font-weight", "bold")
      .style("width", "110px");

    const picker = row.append("input")
      .attr("type", "color") // use the color widget input
      .attr("value", current);

    row.append("button")
      .text("OK")
      .attr("title", "Apply this color")
      .style("padding", "2px 8px")
      .style("font-size", "12px")
      .style("line-height", "1")
      .style("height", "24px")
        .style("background-color", "#425A63")
      .style("color", "#F5eebb")
      .style("font-family", "Helvetica, sans-serif")
      .style("font-weight", "bold")
      .style("border", "none")
      .style("padding", "6px 12px")
      .style("border-radius", "6px")
      .style("cursor", "pointer")
      .on("click", () => {
        clusterColorScale[key] = picker.node().value; // commit chosen color
        commitRecolor(); // recolor all the affected elements
      });
  });
}


// USER INPUT LABELS

function renderSingleLabelInput(clusterKeys) {
  const container = d3.select("#label-input-container");
  container.selectAll("*").remove();

  const key = clusterKeys[currentIndex];
  const clusterNum = key.match(/\d+$/)[0];

  const labelGroup = container.append("div");
  
  labelGroup.append("label")
    .attr("for", `label-for-${clusterNum}`)
    .text(`Cluster ${clusterNum}:`)
    .style("display", "block")
    .style("margin-bottom", "6px");

  labelGroup.append("input")
    .attr("type", "text") //textbox input
    .attr("id", `label-for-${clusterNum}`)
    .attr("data-cluster", key) //save info on which cluster it is (used in stacking legend too)
    .attr("placeholder", "Enter Name")
    .property("value", clusterLabels[key] || "")
    .style("width", "90px")
    .on("input", function () {
      clusterLabels[key] = this.value.trim(); // save the label and it will update to both hovering on the vertical stacking legend and when hovering on the charts
    });
}

// Button handlers 
d3.select("#prev-label").on("click", () => {
  currentIndex = (currentIndex - 1 + clusterKeys.length) % clusterKeys.length;
  renderSingleLabelInput(clusterKeys);
});
d3.select("#next-label").on("click", () => {
  currentIndex = (currentIndex + 1) % clusterKeys.length;
  renderSingleLabelInput(clusterKeys);
});


// CLUSTER STACK LEGEND 
// Vertical stacking legend that is draggable to reorder the clusters and updates all the charts accordingly
// The order top to bottom is the order of stacking in the charts
// Hovering over each segment will show the cluster label, and it can be renamed with renaming box in the bottom left corner

function renderClusterStackLegend(clusterKeys) {
  const container = d3.select("#cluster-reorder-bar");
  container.selectAll("*").remove(); // clear previous

  container
    .style("display", "flex")
    .style("flex-direction", "column")
    .style("align-items", "stretch")
    .style("border", "none")
    .style("width", "50px")
    .style("height", "85%")
    .style("background", "transparent")
    .style("padding", "0")
    .style("margin-right", "35px");

  clusterKeys.forEach(key => {
    //Take the number from the cluster key, neater for the hovering part
    const clusterNum = key.match(/\d+$/)[0];

    container.append("div")
      .attr("draggable", true)
      .attr("data-cluster", key)
      .style("background", clusterColorScale[key])
      .style("flex", "1") // equal height segments
      .style("margin", "0")
      .style("border", "none")
      .style("cursor", "move")
      .style("position", "relative")  // needed for absolutely positioned number
      .on("dragstart", clusterDragStart)
      .on("dragover", clusterDragOver)
      .on("drop", clusterDropped)
      .on("mouseover", (event) => {
        const label = clusterLabels[key] || `Cluster ${clusterNum}`;
        tooltip.style("display", "block")
          .text(label);
      })
      .on("mousemove", (event) => {
        tooltip.style("top", (event.pageY + 10) + "px")
          .style("left", (event.pageX + 10) + "px");
      })
      .on("mouseout", () => {
        tooltip.style("display", "none");
      })
      .append("span")
        .text(clusterNum)
        .style("position", "absolute")
        .style("bottom", "4px")
        .style("right", "6px")
        .style("color", "white")
        .style("font-weight", "bold")
        .style("font-size", "18px")
        .style("pointer-events", "none");
  });
}

//Make the drag and drop parts
function clusterDragStart(e) {
  draggedCluster = e.target.dataset.cluster;
}

function clusterDragOver(e) {
  e.preventDefault(); // allow dropping
}

function clusterDropped(e) {

  const parent = e.target.parentNode;
  const draggedEl = Array.from(parent.children).find(el => el.dataset.cluster === draggedCluster);
  parent.insertBefore(draggedEl, e.target);

  window.perPopClusterOrder?.clear(); // Clear previous orders since the dominant sorting may interfere

  function getClusterOrderFromUI() {
    return Array.from(document.querySelectorAll("#cluster-reorder-bar div"))
      .map(el => el.getAttribute("data-cluster"));
  }

  // Get updated order directly from DOM
  clusterOrder = getClusterOrderFromUI();
  lastClusterOrderSource = "legend"; // so it doesn't fight with the dominant sorting

  // Update legend UI and charts
  refreshAllCharts();
 

}

// POPULATION REORDERING 
// Allows for dragging and dropping populations on from a list, then applying it 
// which will change the x-axis ordering of populations for all the charts!

// The interactive part, located inside of the clickable box. Drag and drop to reorder!
function renderPopulationReorderUI() {
  const container = d3.select("#population-order-box");
  container.selectAll("*").remove();

  populationOrder.forEach(pop => {
    container.append("div")
      .attr("draggable", true)
      .attr("data-population", pop)
      .style("background", "#75975e")
      .style("padding", "10px")
      .style("border-radius", "8px")
      .style("border", "2px solid #222")
      .style("cursor", "move")
      .text(pop)
      .on("dragstart", populationDragStart)
      .on("dragover", populationDragOver)
      .on("drop", populationDropped);
  });
}

function populationDragStart(e) {
  draggedPopulation = e.target.dataset.population;
}

function populationDragOver(e) {
  e.preventDefault();
}

function populationDropped(e) {
  const parent = e.target.parentNode;
  const draggedEl = Array.from(parent.children).find(el => el.dataset.population === draggedPopulation);
  parent.insertBefore(draggedEl, e.target);

  populationOrder.length = 0;
  populationOrder.push(...Array.from(parent.children).map(el => el.dataset.population));

  
}
// Made an apply button so it doesn't get too messy
document.getElementById("applyPopulationOrder").addEventListener("click", function () {
  rerenderAllChartsByPopulation();
});

//MAIN POPULATION RERENDING FUNCTION - calling things after dropping and applying
function rerenderAllChartsByPopulation() {
  // Clear chart area
  d3.select("#chart-grid").selectAll("*").remove();
  chartPositions.length = 0;

  // Re-render all charts in the new population order for each K and mode
  Object.keys(allChartData)
    .sort((a, b) => +a.slice(1) - +b.slice(1))
    .forEach(kNumber => {
      const clusterData = allChartData[kNumber];
      const row = d3.select("#chart-grid")
        .append("div")
        .style("display", "flex")
        .style("gap", "80px")
        .style("align-items", "flex-start");

      row.append("div")
        .style("width", "60px")
        .style("text-align", "right")
        .style("font-size", "90px")
        .style("font-family", "Gill Sans")
        .style("font-weight", "bold")
        .style("padding-right", "30px")
        .text(kNumber);

      allModes.forEach(mode => {
        if (clusterData[mode]) {
          // Sort individuals within each mode by population order
          const sortedData = clusterData[mode].slice().sort((a, b) => {
            return populationOrder.indexOf(a.Population) - populationOrder.indexOf(b.Population);
          });

          const chartCell = row.append("div")
            .style("width", "1800px")
            .style("height", "700px")
            .style("flex-shrink", "0");

          renderStackedBarChart(sortedData, chartCell, `${kNumber} ${mode}`);
        }
      });
    });
  refreshAllCharts();
}


// [7] HEADER MINOR INTERACTIONS (reset zoom, downloading, etc.)=========================================================================
// First I'll have the button stylings here of the SVG icons for reset zoom, fullscreen, and download (grabbed from https://www.svgrepo.com/)

const resetZoomSVG=`<svg viewBox="0 0 32 32" id="i-zoom-reset" xmlns="http://www.w3.org/2000/svg" fill="none"
 stroke="currentcolor" stroke-linecap="round" stroke-linejoin="round" stroke-width="3">
  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
  <g id="SVGRepo_iconCarrier"> <circle cx="14" cy="14" r="12"></circle> 
  <path d="M23 23 L30 30"></path> 
  <path d="M9 12 L9 9 12 9 M16 9 L19 9 19 12 M9 16 L9 19 12 19 M19 16 L19 19 16 19">
    </path> </g></svg>`;

const openEyeSVG = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"
     xmlns="http://www.w3.org/2000/svg">
  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="#425A63" stroke-width="2" fill="none"/>
  <circle cx="12" cy="12" r="3" stroke="#425A63" stroke-width="2" fill="none"/>
</svg>`; 

const closedEyeSVG = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"
     xmlns="http://www.w3.org/2000/svg">
  <path d="M17.94 17.94C16.12 19.24 14.13 20 12 20c-7 0-11-8-11-8
           1.27-2.23 3.07-4.11 5.28-5.37M9.88 4.12C10.57 4.04 11.28 4 12 4
           c7 0 11 8 11 8-.63 1.11-1.38 2.13-2.24 3.03" 
        stroke="#425A63" stroke-width="2" fill="none"/>
  <line x1="1" y1="1" x2="23" y2="23" stroke="#425A63" stroke-width="2"/>
</svg>`; 

//COMPLETE VIEW BUTTON, which will set zoom to fit all charts in the view
const zoomBtn = document.getElementById("resetZoomBtn");
zoomBtn.classList.add("rightTopIcon-btn");
zoomBtn.innerHTML = resetZoomSVG;
zoomBtn.addEventListener("click", function () {
  const gridNode = chartGrid.node();
  const wrapperNode = wrapper.node();

  // Use natural size, not the transformed bounding box
  const gridWidth = gridNode.scrollWidth;
  const gridHeight = gridNode.scrollHeight;
  const wrapperWidth = wrapperNode.clientWidth;
  const wrapperHeight = wrapperNode.clientHeight;

  // Compute scale so the whole grid fits inside wrapper
  const scale = Math.min(
    wrapperWidth / gridWidth,
    wrapperHeight / gridHeight
  );

  // Compute translate so it is centered
  const translateX = (wrapperWidth - gridWidth * scale) / 2;
  const translateY = (wrapperHeight - gridHeight * scale) / 2;

  // Animate reset using d3.zoom
  wrapper.transition().duration(600).call(
    zoom.transform,
    d3.zoomIdentity
      .translate(translateX, translateY)
      .scale(scale)
  );
});

//FULLSCREEN BUTTON
const fullscreenBtn = document.getElementById("fullscreenBtn");
const zoomWrapper = document.getElementById("zoom-wrapper");

fullscreenBtn.addEventListener("click", () => {
  if (!document.fullscreenElement) {
    zoomWrapper.requestFullscreen().catch(err => {
      console.error(`Error attempting fullscreen: ${err.message}`);
    });
    zoom.scaleExtent([0.2, 3]); // more generous in fullscreen
  } else {
    document.exitFullscreen();
    zoom.scaleExtent([0.5, 2]); // normal mode
  }
});

// MAJOR MODES BUTTON - will show only the Major Modes which is the first column
let showOnlyM1 = false;
d3.select("#toggleM1Btn").on("click", function() {
  showOnlyM1 = !showOnlyM1;

  if (showOnlyM1) {
    d3.select(this).html("Show All<br>Modes").style("font-size", "18px");
    // hide any chart cells whose data-mode is not M1
    d3.selectAll(".chart-cell")
      .style("display", function() {
        return d3.select(this).attr("data-mode") === "M1" ? null : "none";
      });
    // optional: hide overlay connectors to avoid stray lines
    d3.selectAll(".connector-overlay").style("display", "none");
  } else {
    d3.select(this).html("Major<br> Mode").style("font-size", "18px");
    d3.selectAll(".chart-cell").style("display", null); // restore
    d3.selectAll(".connector-overlay").style("display", "block");
  }
});

// Toggle network connections visibility
let networkVisible = true;
const NetworkBtn = document.getElementById("toggleNetworkBtn");
NetworkBtn.classList.add("rightTopIcon-btn");
NetworkBtn.innerHTML = openEyeSVG;

NetworkBtn.addEventListener("click", () => {
  networkVisible = !networkVisible;
  document.querySelector(".connector-overlay").style.display = networkVisible ? "block" : "none";
  NetworkBtn.innerHTML = networkVisible ? openEyeSVG : closedEyeSVG;
});

// DOWNLOAD IMAGE BUTTON - will export the entire zoom-wrapper div as a PNG image
const hoverDownButton = d3.select("#downloadImgBtn");
hoverDownButton.on("mouseover", (event) => {
  d3.select("body").append("div")
    .attr("id", "tooltip")
    .style("position", "absolute")
    .style("padding", "6px 10px")
    .style("background", "#333")
    .style("color", "white")
    .style("font-family", "Helvetica, sans-serif")
    .style("border-radius", "6px")
    .style("font-size", "13px")
    .style("pointer-events", "none")
    .style("z-index", 9999)
    .style("top", (event.pageY - 80) + "px")
    .style("left", (event.pageX - 200) + "px")
    .html("This may take a moment. <br> Please wait on an unresponsive page.");
})
.on("mousemove", (event) => {
  d3.select("#tooltip")
    .style("top", (event.pageY - 40) + "px")
    .style("left", (event.pageX -250) + "px");
})
.on("mouseout", () => {
  d3.select("#tooltip").remove();
});



// A couple hovering blurbs here
// D3 hover tooltip (convert to a D3 selection!), just describes what the button does (puts the charts in full view)
const btnSel2 = d3.select("#resetZoomBtn");
btnSel2
  .on("mouseenter.tooltip", (event) => {
    d3.select("body").append("div")
      .attr("id", "tooltip")
      .style("position", "absolute")
      .style("padding", "6px 10px")
      .style("background", "#333")
      .style("color", "white")
      .style("font-family", "Helvetica, sans-serif")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      //.style("z-index", 9999)
      .style("top", (event.pageY+30) + "px")
      .style("left", (event.pageX - 80) + "px")
      .html("View all charts in full display.");
  })
  .on("mousemove.tooltip", (event) => {
    d3.select("#tooltip")
      .style("top",  (event.pageY+30) + "px")
      .style("left", (event.pageX - 80) + "px");
  })
  .on("mouseleave.tooltip", () => {
    d3.select("#tooltip").remove();
  });

// small blurb for the fullscreen button
const btnSel = d3.select("#fullscreenBtn");
btnSel
  .on("mouseenter.tooltip", (event) => {
    d3.select("body").append("div")
      .attr("id", "tooltip")
      .style("position", "absolute")
      .style("padding", "6px 10px")
      .style("background", "#333")
      .style("color", "white")
      .style("font-family", "Helvetica, sans-serif")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("z-index", 9999)
      .style("top", (event.pageY-50) + "px")
      .style("left", (event.pageX - 80) + "px")
      .html("Open to Full Screen.");
  })
  .on("mousemove.tooltip", (event) => {
    d3.select("#tooltip")
      .style("top",  (event.pageY-50) + "px")
      .style("left", (event.pageX - 80) + "px");
  })
  .on("mouseleave.tooltip", () => {
    d3.select("#tooltip").remove();
  });

// Small blurb for the network toggle button
const btnSel1 = d3.select("#toggleNetworkBtn");
btnSel1
  .on("mouseenter.tooltip", (event) => {
    d3.select("body").append("div")
      .attr("id", "tooltip")
      .style("position", "absolute")
      .style("padding", "6px 10px")
      .style("background", "#333")
      .style("color", "white")
      .style("font-family", "Helvetica, sans-serif")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      //.style("z-index", 9999)
      .style("top", (event.pageY+30) + "px")
      .style("left", (event.pageX - 80) + "px")
      .html("Hide or Show Network Connections.");
  })
  .on("mousemove.tooltip", (event) => {
    d3.select("#tooltip")
      .style("top",  (event.pageY+30) + "px")
      .style("left", (event.pageX - 80) + "px");
  })
  .on("mouseleave.tooltip", () => {
    d3.select("#tooltip").remove();
  });



// [8] IMAGE EXPORTING FUNCTIONALITY=========================================================================
// Export the entire chart grid as a PNG image, using dom-to-image-more library

// helpers here
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const nextTick = () => new Promise(r => setTimeout(r, 0)); // let UI update
const idle = () => new Promise(r => (window.requestIdleCallback ? requestIdleCallback(r, { timeout: 200 }) : setTimeout(r, 0)));

// Compute a safe scale so W*H*scale^2 doesn't exceed a pixel cap
function safeScaleFor(node, desiredScale = 2, maxPixels = 15_000_000) { 
  const w = Math.max(node.scrollWidth, node.clientWidth);
  const h = Math.max(node.scrollHeight, node.clientHeight);
  const desiredPixels = w * h * desiredScale * desiredScale;
  if (desiredPixels <= maxPixels) return desiredScale;
  const s = Math.sqrt(maxPixels / (w * h));
  // Round to 2 decimals so it’s predictable
  return Math.max(1, Math.floor(s * 100) / 100);
}

// Render a node to PNG with overflow fix and filters
function toPNG(node, filename, { scale = 2, quality = 0.95 } = {}) {
  const width  = Math.max(node.scrollWidth,  node.clientWidth);
  const height = Math.max(node.scrollHeight, node.clientHeight);

  const prevOverflow = node.style.overflow;
  node.style.overflow = 'visible';

  const opts = {
    width: Math.round(width * scale),
    height: Math.round(height * scale),
    style: {
      transform: `scale(${scale})`,
      transformOrigin: 'top left',
      width: `${width}px`,
      height: `${height}px`,
      overflow: 'visible'
    },
    bgcolor: '#ffffff',
    quality,
    filter: (n) => {
      if (!n || !n.classList) return true;
      // Skip ephemeral/expensive layers
      return !n.classList.contains('tooltip') &&
             !n.classList.contains('hover-overlay') &&
             !n.classList.contains('no-export');
    }
  };

  return domtoimage.toPng(node, opts).then((dataUrl) => {
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = filename;
    a.click();
  }).finally(() => {
    node.style.overflow = prevOverflow;
  });
}

// A styled progress badge in the middle of the page, but not sure if it is helping with the unresponsiveness 
// Page is usually unresponsive twice
function showProgressBadge() {
  const el = document.createElement('div');
  el.id = 'export-progress';
  el.textContent = 'Exporting…';
  Object.assign(el.style, {
    position: "fixed", 
    right:"50%", 
    top:"50%", 
    transform: "translate(50%, -50%)",
    padding: '8px 12px', 
    borderRadius: '8px',
    background: '#425A63', 
    color: '#F5eebb', 
    font: '600 14px system-ui',
    zIndex: 999999, 
    boxShadow: '0 2px 8px rgba(0,0,0,.2)'
  });
  document.body.appendChild(el);
  return el;
}

// --- Button handler: export each row to its own JPEG, yielding between rows --- GO THROUGH AGAIN TO UNDERSTAND PROPER TWEAKS
document.getElementById("downloadImgBtn").addEventListener("click", async function () {
  const grid = document.getElementById("chart-grid");
  const rows = Array.from(grid.querySelectorAll(".k-row"));
  const reorderBar = document.getElementById("cluster-reorder-bar");

  // TUNING: default quality/scale
  const DESIRED_SCALE = 2;   // try 2 first; 3 is sharper but heavier
  const QUALITY = 0.95;     
  const MAX_PIXELS = 12_000_000; // cap total pixels to avoid freezes

  const badge = showProgressBadge();

  try {
    // If no row grouping yet, fall back to whole-grid export (still with safety cap)
    if (!rows.length) {
      const scale = safeScaleFor(grid, DESIRED_SCALE, MAX_PIXELS);
      badge.textContent = `Exporting grid (scale ${scale}×)…`;
      await toPNG(grid, "chart-grid.png", { scale, quality: QUALITY });
    } else {
      // Export each row (prevents massive single render)
      for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const k = row.getAttribute("data-k") || `row-${i+1}`;
        const scale = safeScaleFor(row, DESIRED_SCALE, MAX_PIXELS);

        badge.textContent = `Exporting ${k} (scale ${scale}×)… ${i+1}/${rows.length}`;
        await toPNG(row, `${k}.png`, { scale, quality: QUALITY });

        // Let the UI breathe between rows so you don't get the "unresponsive" dialog
        await nextTick();
        await idle();
      }
    }

    // Export the reorder bar last (usually small)
    if (reorderBar) {
      const scale = safeScaleFor(reorderBar, DESIRED_SCALE, MAX_PIXELS);
      badge.textContent = `Exporting reorder bar…`;
      await toPNG(reorderBar, "cluster-reorder-bar.jpg", { scale, quality: QUALITY });
    }
      badge.textContent = 'Done ✓';
      await sleep(600);
  }
  catch (err) {
    console.error("Export failed:", err);
    badge.textContent = 'Export failed';
    await sleep(1200);
    alert("Export failed — check console.");
  } finally {
    badge.remove();
    window.print();
  }
});

// [9] REFRESH ALL CHARTS FUNCTION - will be called after any major changes to re-render everything=========================================================================
// Will be called after any major changes (like reordering populations, changing cluster order, color changes, etc.)
// It clears the chart area and re-renders all charts based on the current populationOrder and clusterOrder
// It also rebuilds the UI components like legends and color pickers to reflect the current state!

function refreshAllCharts() {

  // Clear chart area
  d3.select("#chart-grid").selectAll("*").remove();
  chartPositions.length = 0;

  // Re-render all charts with current populationOrder and clusterOrder
  Object.keys(allChartData)
    .sort((a, b) => +a.slice(1) - +b.slice(1))
    .forEach(kNumber => {
      const clusterData = allChartData[kNumber];
      const row = d3.select("#chart-grid")
        .append("div")
        .style("display", "flex")
        .style("gap", "80px")
        .style("align-items", "flex-start");

      row.append("div")
        .style("width", "60px")
        .style("text-align", "right")
        .style("font-size", "90px")
        .style("font-weight", "bold")
        .style("padding-right", "30px")
        .text(kNumber);

      allModes.forEach(mode => {
        if (clusterData[mode]) {
          // Sort individuals by current population order
          const sortedData = clusterData[mode].slice().sort((a, b) => {
            return populationOrder.indexOf(a.Population) - populationOrder.indexOf(b.Population);
          });

          const chartCell = row.append("div")
            .attr("class", "chart-cell")
            .attr("data-mode", mode)
            .attr("data-k", kNumber)
            .style("width", "1800px")
            .style("height", "700px");

          renderStackedBarChart(sortedData, chartCell, `${kNumber} ${mode}`, {
          // clusters: Dominant (per-pop) if it was used last; otherwise the legend’s global order
          getClusterOrder: (pop) => (
            (window.lastClusterOrderSource === "dominant" && window.perPopClusterOrder.get(pop))
              ? window.perPopClusterOrder.get(pop)
              : (window.clusterOrder?.length ? window.clusterOrder : clusterKeys)
          ),
          // individuals: only use Dominant’s per-pop ordering when Dominant was used last
          getIndividualsOrder: (pop) => (
            window.lastClusterOrderSource === "dominant"
              ? (window.perPopIndividualOrder.get(pop) || null)
              : null
          ),
        });

        }
      });
    });

  // Rebuild UI components
  renderClusterHoverLegend(clusterOrder);
  renderClusterStackLegend(clusterOrder);
  renderColorPickers();
  drawNetworkConnections();
  afterChartsRerendered(); // reattach dominant sort mode if it was turned on

}

