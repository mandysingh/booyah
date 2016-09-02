/**
 * jTinder initialization
 */

// createslideDiv(); 
$("#tinderslide").jTinder({
	// dislike callback
    onDislike: function (item) {
	    // set the status text
        $('#status').html('Image Rejected ' + (item.index()+1));
    },
	// like callback
    onLike: function (item) {
	    // set the status text
        $('#status').html('Image Accepted ' + (item.index()+1));
    },
	animationRevertSpeed: 200,
	animationSpeed: 400,
	threshold: 1,
	likeSelector: '.like',
	dislikeSelector: '.dislike'
});

/**
 * Set button action to trigger jTinder like & dislike.
 */
$('.actions .like, .actions .dislike').click(function(e){
	e.preventDefault();
	$("#tinderslide").jTinder($(this).attr('class'));
});