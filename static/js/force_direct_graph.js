var width = 960,
    height = 500,
    radius = 6;

var fill = d3.scale.category20();

var force = d3.layout.force()
    .gravity(.05)
    .charge(-240)
    .linkDistance(50)
    .size([width, height]);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json("./static/data/d3_force_graph.json", function(error, graph) {
  if (error) throw error;

  var link = svg.selectAll("line")
      .data(graph.links)
    .enter().append("line");

  var node = svg.selectAll("circle")
      .data(graph.nodes)
    .enter().append("circle")
      .attr("r", radius - .75)
      .style("fill", function(d) { return fill(d.group); })
      .style("stroke", function(d) { return d3.rgb(fill(d.group)).darker(); })
      .call(force.drag);

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .on("tick", tick)
      .start();

  function tick() {
    node.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
        .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });

    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
  }
});