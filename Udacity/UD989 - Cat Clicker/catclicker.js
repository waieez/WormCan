$(document).ready(function(){

	var photos = {}

	function Clicker (name, url) {
		this.clicks = 0;
		this.name = name;
		this.url = url;
	}
	
	photos.chewie = new Clicker('chewie', 'https://lh3.ggpht.com/kixazxoJ2ufl3ACj2I85Xsy-Rfog97BM75ZiLaX02KgeYramAEqlEHqPC3rKqdQj4C1VFnXXryadFs1J9A=s0#w=640&h=496');
	photos.hans = new Clicker('hans', "http://img1.wikia.nocookie.net/__cb20100129155042/starwars/images/thumb/0/01/Hansoloprofile.jpg/400px-Hansoloprofile.jpg");

	var count = 5;

	for( photo in photos ){

		if (count > 0) {
			var obj = photos[photo];

			$('.gallery').append( "<img name="+ obj.name +" src="+ obj.url +"/>");
			count--;
		}

	};
		
	
	
	//alt one add listener to all photos. traverse dom to get id, fetch data from photos array to update and display

	$('.gallery').on('click', 'img', function(){

		$('.main').empty();

		var name = $(this).attr('name');
		var url = $(this).attr('src');

		$('.main').append("<h1>"+name+"</h1><img name="+ name +" src="+ url +"/><p>"+photos[name].clicks+"</p>");
	});

	$('.main').on('click','img', function(){
		var name = $(this).attr('name');
		$('p').text( photos[name].clicks++ );
	});

});