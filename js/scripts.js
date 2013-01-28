$(document).ready(function() {
	// set up hover panels
	// although this can be done without JavaScript, we've attached
	// these events
	// because it causes the hover to be triggered when the element is
	// tapped on a touch device
	$('.hover').hover(function() {
		$(this).addClass('flip');
	}, function() {
		$(this).removeClass('flip');
	});

	// set up click/tap panels
	$('.click').click(function(e) {
		if($(this).hasClass('cancelar'))
			$(this).parent().parent().parent().toggleClass('flip');
		else
			$(this).parent().parent().toggleClass('flip');
		e.preventDefault();
	});
});