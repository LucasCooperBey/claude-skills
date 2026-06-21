---
name: d3js-visualization
description: Creates data visualizations with D3.js including custom charts, network diagrams, geographic maps, and publication-quality interactive graphics.
---
# D3.js Data Visualization

Create sophisticated, interactive data visualizations using D3.js.

## When to Use D3.js

- Custom visualizations requiring unique layouts
- Complex interactions (brushing, zooming, linking)
- Network diagrams and force-directed graphs
- Geographic visualizations
- Publication-quality graphics with precise control

## Core Workflow

### 1. Import D3

```javascript
// ES modules
import * as d3 from 'd3';

// CDN
<script src="https://d3js.org/d3.v7.min.js"></script>
```

### 2. Basic Structure

```javascript
// Set dimensions
const margin = { top: 20, right: 30, bottom: 40, left: 50 };
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Create SVG
const svg = d3.select('#chart')
  .append('svg')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)
  .append('g')
  .attr('transform', `translate(${margin.left},${margin.top})`);

// Create scales
const xScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.x)])
  .range([0, width]);

const yScale = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.y)])
  .range([height, 0]);

// Add axes
svg.append('g')
  .attr('transform', `translate(0,${height})`)
  .call(d3.axisBottom(xScale));

svg.append('g')
  .call(d3.axisLeft(yScale));
```

## Common Chart Patterns

### Bar Chart

```javascript
svg.selectAll('rect')
  .data(data)
  .join('rect')
  .attr('x', d => xScale(d.category))
  .attr('y', d => yScale(d.value))
  .attr('width', xScale.bandwidth())
  .attr('height', d => height - yScale(d.value))
  .attr('fill', 'steelblue');
```

### Line Chart

```javascript
const line = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value));

svg.append('path')
  .datum(data)
  .attr('fill', 'none')
  .attr('stroke', 'steelblue')
  .attr('stroke-width', 2)
  .attr('d', line);
```

### Scatter Plot

```javascript
svg.selectAll('circle')
  .data(data)
  .join('circle')
  .attr('cx', d => xScale(d.x))
  .attr('cy', d => yScale(d.y))
  .attr('r', 5)
  .attr('fill', d => colorScale(d.category));
```

### Force-Directed Network

```javascript
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id))
  .force('charge', d3.forceManyBody().strength(-100))
  .force('center', d3.forceCenter(width / 2, height / 2));

const link = svg.selectAll('line')
  .data(links)
  .join('line')
  .attr('stroke', '#999');

const node = svg.selectAll('circle')
  .data(nodes)
  .join('circle')
  .attr('r', 10)
  .attr('fill', d => colorScale(d.group));

simulation.on('tick', () => {
  link
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);

  node
    .attr('cx', d => d.x)
    .attr('cy', d => d.y);
});
```

## Interactivity

### Tooltips

```javascript
const tooltip = d3.select('body')
  .append('div')
  .attr('class', 'tooltip')
  .style('opacity', 0);

svg.selectAll('circle')
  .on('mouseover', (event, d) => {
    tooltip.transition().duration(200).style('opacity', .9);
    tooltip.html(`Value: ${d.value}`)
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 28) + 'px');
  })
  .on('mouseout', () => {
    tooltip.transition().duration(500).style('opacity', 0);
  });
```

### Zoom & Pan

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.5, 10])
  .on('zoom', (event) => {
    svg.attr('transform', event.transform);
  });

d3.select('svg').call(zoom);
```

## Transitions

```javascript
svg.selectAll('rect')
  .data(newData)
  .transition()
  .duration(750)
  .attr('y', d => yScale(d.value))
  .attr('height', d => height - yScale(d.value));
```

## Responsive Sizing

```javascript
function resize() {
  const container = document.getElementById('chart');
  const width = container.clientWidth;

  svg.attr('width', width);
  xScale.range([0, width - margin.left - margin.right]);

  // Update elements
  svg.selectAll('rect').attr('width', xScale.bandwidth());
}

window.addEventListener('resize', resize);
```

## Performance Tips

- Use `canvas` for 1000+ elements
- Validate data before visualization
- Use `.join()` instead of enter/update/exit pattern
- Minimize DOM manipulation in animation loops

## Accessibility

```javascript
svg.attr('role', 'img')
   .attr('aria-label', 'Chart showing sales over time');

svg.selectAll('rect')
  .attr('role', 'listitem')
  .attr('aria-label', d => `${d.category}: ${d.value}`);
```
