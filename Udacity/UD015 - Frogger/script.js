var FROGGER = (function(){
	
	var Thing = function(x, y, speed){
		this.x = x||0;
		this.y = y||0;
		this.speed = speed||1;
	}

	Thing.prototype.getPos = function(){
		return [this.x,this.y];
	}


	var Danger = function(x, y, speed, distance, direction){
		Thing.call(this, x, y, speed);
		this.delay = Math.floor(Math.random() * 2500); // delay anywhere from 0ms to 2.5sec -- currently not implemented
		this.startPos = direction == 'left' ? distance : 0;
		this.distance = distance;
		this.direction = direction;
	}

	Danger.prototype = Object.create(Thing.prototype);
	Danger.prototype.constructor = Danger;
	// Move method for dangers
	Danger.prototype.move = function(){
		if (this.direction == 'left'){
			this.x = this.x - this.speed >= 0 ? this.x - this.speed : this.startPos;
		} else {
			this.x = this.x + this.speed <= this.distance ? this.x + this.speed : this.startPos;
		}
	}


	var Frog = function(x, y, lives){
		Thing.call(this, x, y);
		this.lives = lives||3;
	}

	Frog.prototype = Object.create(Thing.prototype)
	Frog.prototype.constructor = Frog;

	Frog.prototype.isAlive = function(dangers){
		return dangers[this.y]['x'] != this.x ? true : false; // checks only the row frog is on
	}
	//Move method for frogs
	Frog.prototype.move = function(distance, direction){
		switch(direction){
			case 'w': // w
				this.y = Math.min(this.y + 1, distance);
				break;

			case 'a': // a
				this.x = Math.max(this.x - 1, 0)
				break;

			case 's':
				this.y = Math.max(this.y - 1, 0);
				break;

			case 'd': // d
				this.x = Math.min(this.x + 1, distance);
				break;
		}
	}

	return {
		CreateGame: function(size, difficulty){
			var frog = new Frog(Math.floor(size/2), 0),
					dangers = {};
					dangers[0] = 'start';
					dangers[size] = 'finish';
			switch(difficulty){
				case 'hard':
					for (var i = 1; i < size; i++) {
						// had to put random start point here
						dangers[i] = i < size/2 ? new Danger((Math.floor(Math.random()*size)), i, 1, size) : new Danger((Math.floor(Math.random()*size)), i, 1, size, 'left'); // Danger(x, y, speed, distance, direction)
					};
					break;

				default:
					for (var i = 1; i <= size-1; i++) {
						dangers[i] = new Danger(0, i, 1, size);
					};
			}
			return [frog, dangers];
		},
	}

})();


var main = function(){
	//Initializes Game Settings - Settings not implemented
	var size = 10,
			victory = false;
			timer = 1000 * 60; // not implemented
			[frog, dangers] = FROGGER.CreateGame(size,'hard');

	//Create UI for Frogger Game
	$('body').append('<div class="container"></div>')
	for (var i = 0; i < size; i++) {
		$('.container').prepend("<div class='y"+i+"'></div>")
		for (var j = 0; j < size; j++) {
			$('.y' + i).append("<div class='x"+j+"'></div>");
		};
	}

	// Draws the frog's current position
	var showFrog = function(frog, event){
		$('.frog').removeClass('frog');
		frog.move( size, String.fromCharCode(event.which) );
		var [x, y] = frog.getPos();
		$xy = $('.y'+y+' .x'+x);
		$xy.addClass('frog');	
	}

	// Draws the position of all dangers
	var showDanger = function(frog, dangers, size, victory){
		if(frog.isAlive(dangers) && !victory){
			$('.danger').removeClass('danger');
			for (var i = 1; i < size-1; i++) {
				dangers[i].move();
		 		var [x, y] = dangers[i].getPos();
		 		$xy = $('.y'+y+' .x'+x);
		 		$xy.addClass('danger');
			}
			}
		}
	

	$(document).on('keypress.frog', function(event){

		showDanger(frog, dangers, size, victory);
		showFrog(frog, event);

		if (frog.isAlive(dangers) == false){
			alert('OWNED');
			frog.lives--;
			frog.x = Math.floor(size/2);
			frog.y = 0;
			$(document).trigger('keypress.frog');
		};

		//Default 3 tries
		if (frog.lives <= 0){ 
			alert('You Lose!');
			$(document).off('keypress.frog');
		}

		//If finish line reached
		if (frog.y == size-1){
			victory = true;
			alert('VICTORY!')
			$(document).off('keypress.frog');
		}
	});

	$(document).trigger('keypress.frog');

}


$(document).ready(main);