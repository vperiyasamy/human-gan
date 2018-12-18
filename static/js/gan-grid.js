
// This function is called whenever the user
// clicks the mouse in the view:

var points = [];

var num_points = 0;
var drawn_points = [];

var drawing = false; // guessing distribution

// set up the coordinate grid backdrop
var grid_raster = new Raster('/static/images/grid-small.png', new Point(10, 10));

// grid_raster.onLoad = function() {
// 	resizeGrid();
// }

// function resizeGrid() {
// 	var window_width = window.innerWidth;
// 	var window_height = window.innerHeight;

// 	var dimension = 0.75 * Math.min(window_width, window_height); 
// 	grid_raster.scale(dimension);
// }

//grid_raster.size = paper.view.viewSize;
grid_raster.position = paper.view.center;

// console.log(grid_raster.bounds.width);
// console.log(grid_raster.bounds.height);

// grid_left = grid_raster.position.x - (grid_raster.width / 2);
// grid_right = grid_raster.position.x + (grid_raster.width / 2);
// grid_top = grid_raster.position.y - (grid_raster.height / 2);
// grid_bottom = grid_raster.position.y + (grid_raster.height / 2);

grid_left = grid_raster.position.x - 300;
grid_right = grid_raster.position.x + 300;
grid_top = grid_raster.position.y - 300;
grid_bottom = grid_raster.position.y + 300;

console.log('grid left: ' + grid_left);
console.log('grid right: ' + grid_right);
console.log('grid top: ' + grid_top);
console.log('grid bottom: ' + grid_bottom);

window.onload = function() {
	// setup button click
	$('#queryButton').click(function() {
		console.log('pushed button');
		doWork();
	});
}

$(document).ready(function() {
	$('input[type="checkbox"]').click(function(){
        if($(this).is(":checked")){
            drawing = true;
        }
        else if($(this).is(":not(:checked)")){
            drawing = false;
        }
    });
});


$('#queryButton').click(function() {
	if(num_points < 4) {
		$('#message').text('Please choose at least 4 points');
		return;
	}
	console.log('pushed button');
	queryServer();
});

$('#guessButton').click(function() {
	if(!drawing) {
		$('#message').text('Please draw a rectangle first');
		return;
	}
	console.log('pushed button');
	guessDistribution();
});

function queryServer() {
	// ajax the JSON to the server
	console.log('entered worker function')

	$.ajax({
	    url: "query",
	    type: "POST",
	    contentType: "application/json",
	    data: JSON.stringify(points),
	    success: function(data){
	    	console.log('points sent successfully');
	    	$('#message').text(data);
	}});

	// stop link reloading the page
	event.preventDefault();
}

function guessDistribution() {
	// ajax the JSON to the server
	console.log('entered worker function')

	guessPoints = [];

	guessPoints.push({'x': (topLeft.x - grid_left), 'y': (topLeft.y - grid_top)});
	guessPoints.push({'x': (bottomRight.x - grid_left), 'y': (bottomRight.y - grid_top)});

	$.ajax({
	    url: "guessdistribution",
	    type: "POST",
	    contentType: "application/json",
	    data: JSON.stringify(guessPoints),
	    success: function(data){
	    	console.log('points sent successfully');
	    	$('#message').text(data);
	}});

	// stop link reloading the page
	event.preventDefault();
}

var distributionGuess = new Path.Rectangle(new paper.Rectangle(new Point(), new Point()));
var topLeft = new Point();
var bottomRight = new Point();

function onMouseDown(event) {
	console.log('You pressed the mouse!');
}

function onMouseDrag(event) {
	if(drawing) {

		// erase the old one
		distributionGuess.remove();

		// drawing a new rectangle
		var rect = new paper.Rectangle(event.downPoint, event.point);
		var path = new Path.Rectangle(rect);
		path.strokeColor = 'green';
		path.selected = true;
		distributionGuess = path;
		topLeft = event.downPoint;
		bottomRight = event.point;
		console.log(topLeft);
		console.log(bottomRight);
	}

	console.log('You dragged the mouse!');
}

function onMouseUp(event) {
	if(!drawing) {

		// draw circle
		var myCircle = new Path.Circle({
			center: event.point,
			radius: 3
		});
		myCircle.strokeColor = 'red';
		myCircle.fillColor = 'white';
		drawn_points.push(myCircle);
		num_points += 1;

		// erase old points
		if(num_points > 4) {
			oldCircle = drawn_points.shift();
			oldCircle.remove();

			points.shift();
		}

		// save new point coordinates
		points.push({'x': (event.point.x - grid_left), 'y': (event.point.y - grid_top)});
	}

	console.log('You released the mouse!');
}