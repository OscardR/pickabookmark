$(document).ready(function() {
	// set up hover panels
	// although this can be done without JavaScript, we've attached
	// these events because it causes the hover to be triggered
	// when the element is tapped on a touch device
	$('.hover').hover(function() {
		$(this).addClass('flip');
	}, function() {
		$(this).removeClass('flip');
	});

	// set up click/tap panels
	$('.click').click(function(e) {
		if ($(this).hasClass('cancelar'))
			$(this).parent().parent().parent().toggleClass('flip');
		else
			$(this).parent().parent().toggleClass('flip');
		e.preventDefault();
	});

	// Star rating system
	$('[id^=star]').click(function(e) {
		var input = $('[name=rating]');
		var old_rating = input.val();
		var rating = parseInt($(this).attr('id').charAt(4));

		for ( var i = 1; i <= rating; i++) {
			var star = $('#star' + i);
			if (rating == old_rating)
				star.addClass('no_star');
			else
				star.removeClass('no_star');
		}
		for ( var i = rating + 1; i <= 5; i++)
			$('#star' + i).addClass('no_star');

		if (rating == old_rating)
			rating = 0;

		input.val(rating);
		$('#r' + rating).prop('checked', 'checked');
		e.preventDefault();
	});
});