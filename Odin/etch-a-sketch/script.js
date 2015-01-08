var main = function () {
	console.log('READY');

	//Create Canvas
	$('#canvas').click(
		function(){
			console.log("Creating Brush...")
			var $frame = $('.frame');
			$('.pixel').remove();
			
			var brush = +$('#brush').val();
			var s = 1000/brush;

			for (var i = 0; i < s*s; i++) {
				$frame.append("<div class='pixel'></div>");
			};

			$('.pixel').css({
				height: brush + 'px',
				width: brush +'px'
			});
		}
	);

	//Draw
	$('body').on('mouseenter', '.pixel', function(){
		var level = $(this).css('background-color').match(/\d+/);
		var opacity = +$('#opacity').val();
		opacity = Math.round(256*(opacity/100));
		level = Math.max(0,level-opacity);
		level = level +','+ level +','+ level;
		$(this).css('background-color', 'rgb('+level+')');
	});

	//Clears Canvas
	$('#clear').click(
		function(){
			console.log('Cleaning up..');
			$('.pixel').css('background-color', 'rgb(255,255,255)');
		}
	);
};


$(document).ready(main);