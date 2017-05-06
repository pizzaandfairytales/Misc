window.onload = function() {
    // Check if rot.js can work on this browser
    if (!ROT.isSupported()) {
        alert("The rot.js library isn't supported by your browser.");
    } else {
        // Create a display 80 characters wide and 20 characters tall
        var w = 80;
        var h = 30;
        var display = new ROT.Display({width:w, height:h});
        var container = display.getContainer();
        // Add the container to our HTML page
        document.body.appendChild(container);
        main(display, w, h);
    }
}

function Node(char, x, y){
    this.char = char;
    this.x = x;
    this.y = y;
}

function mapinit(map, w, h){
  for (var y = 0; y < h; y += 1){
    for (var x = 0; x < w; x += 1){
      var char;
      if (x == 0 || x == w-1 || y == 0 || y == h-1){
        char = '#';
      } else{
        char = ' ';
      }
      map[y][x] = new Node(char, x, y);
    }
  }
  return map;
}

function mazeInit(maze, w, h){
  for (var y = 0; y < h; y += 1){
    for (var x = 0; x < w; x += 1){
      maze[y][x] = new Node(' ', x, y);
    }
  }
  return maze;
}

function chooseOrientation(w, h){
    if (w > h){
      return 'h';
    } else if (w < h) {
      return 'w';
    } else {
      var coinFlip = Math.floor(Math.random() * 2);
      if (coinFlip == 0){
        return 'w';
      } else {
        return 'h';
      }
    }
}

function mazegen(maze, w, h, offsetW, offsetH, parentHole, orientation, depth, chartest){
  if (w < 3 || h < 3 || depth > 1){
    return maze;
  }
  if (orientation == 'h'){
    var wallPos = parentHole;
    while (wallPos == parentHole){
      wallPos = Math.floor(Math.random() * (w-2)) + 1;
    }
    var hole = Math.floor(Math.random() * h);
    for (var i = 0; i < h; i++){
      if (i != hole){
        maze[i][wallPos + offsetW].char = chartest;
      } else {
        maze[i][wallPos + offsetW].char = ' ';
      }
    }
    maze = mazegen(maze, w-wallPos, h, wallPos, offsetH, hole, 'w', depth + 1, '2');
    maze = mazegen(maze, wallPos, h, offsetW, offsetH, hole, 'w', depth + 1, '3');
  } else {
    var wallPos = parentHole;
    while (wallPos == parentHole){
      wallPos = Math.floor(Math.random() * (h-2)) + 1;
    }
    var hole = Math.floor(Math.random() * w);
    for (var i = 0; i < w; i++){
      if (i != hole){
        maze[wallPos + offsetH][i].char = chartest;
      } else {
        maze[wallPos + offsetH][i].char = ' ';
      }
    }
    maze = mazegen(maze, w, h - wallPos, offsetW, wallPos, hole, 'h', depth + 1, '4');
    maze = mazegen(maze, w, wallPos, offsetW, offsetH, hole, 'h', depth + 1, '5');
  }
  return maze;
}

function main(display, w, h){
  var map = Array(h).fill(0).map(() => Array(w).fill(' '));
  map = mapinit(map, w, h);
  var maze = Array(h-2).fill(0).map(() => Array(w-2).fill(' '));
  maze = mazeInit(maze, w-2, h-2);
  maze = mazegen(maze, w-2, h-2, 0, 0, 0, chooseOrientation(w-2, h-2), 0, '1');
  draw(display, w, h, 0, 0, map);
  draw(display, w-2, h-2, 1, 1, maze)
}

function draw(display, w, h, offsetW, offsetH, map){
  for (y = 0; y < h; y += 1){
    for (x = 0; x < w; x+= 1){
      display.draw(x + offsetW, y + offsetH, map[y][x].char)
    }
  }
}
