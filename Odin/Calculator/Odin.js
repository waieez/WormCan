//ONSCREEN CALC
var Calc = {

	add: function(a, b){ return b + a; },

	subtract: function(a, b){ return b - a; },

	multiply: function(a, b){
		if ( a == 0 ) { return b }
		return b * a;
	},
	
	divide: function(a, b){
		if ( a == 0 ) { return b }
		return b / a;
	}

}

$(document).ready(function(){

	var a = '0', b, calc, sF;
	var $result = $('#result');

	//delete (CE)
	$('#clear').on('click', function(){
		a = $result.text().slice(0,-1)||0;
		$result.text(a);
		console.log(a, calc, b, sF);
	});

	//reset (C)
	$('#reset').on('click', function(){
		a = '0', b = 0, calc = undefined;
		$result.text(a);
		console.log(a, calc, b, sF);
	});

	// 0 - 9 
	$('.buttons .values').on('click', 'div', function(){
		var key = $(this).attr('id');
		if (key != '.' || a.indexOf('.') == -1) { a += key; }
		$result.text(a);
		sF = undefined;
		console.log(a, calc, b, sF);
	});

	// =
	$('#return').on('click', function(){
		if (sF) {
			b = sF(b);
		} else if (calc) {
			sF = Calc[calc].bind(null, parseFloat(a))
			b = sF(b);
			a = '0';
		}
		$result.text(b);
		console.log(a, calc, b, sF);
	});

	// + - * %
	$('.buttons .functions').on('click', '.function', function(){

		var thisFunc = $(this).attr('id');

		if (calc == undefined) {
			b = +a;
			calc = thisFunc;
		} else if ( calc == thisFunc ) {
			if (sF == undefined ) {sF = Calc[calc].bind(null, parseFloat(a))};
			b = sF(b);
		} else if (calc != thisFunc) {
			b = Calc[calc](parseFloat(a), b);
			sF = undefined;
			calc = thisFunc;
		}
		$result.text(b);
		a = '0';
		console.log(a, calc, b, sF);
	});
});