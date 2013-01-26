// when the DOM is ready:
$(document).ready(function() {
	var time = 500;
	// find the div.fade elements and hook the hover event
	$('div.delete').hover(function() {
		// on hovering over, find the element we want to fade *up*
		var fade = $('> div', this);

		// if the element is currently being animated (to a fadeOut)...
		if (fade.is(':animated')) {
			// ...take it's current opacity back up to 1
			fade.stop().fadeTo(time / 4, 1);
		} else {
			// fade in quickly
			fade.fadeIn(time / 4);
		}
	}, function() {
		// on hovering out, fade the element out
		var fade = $('> div', this);
		if (fade.is(':animated')) {
			fade.stop().fadeTo(time, 0);
		} else {
			// fade away slowly
			fade.fadeOut(time);
		}
	});
});