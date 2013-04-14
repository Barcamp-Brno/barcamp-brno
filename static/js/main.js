// -------- start of jQuery document.ready() ---------- //
  
$(document).ready(function(){

	$(".program_table img").click(function(){
		$(".program_table tr.hide").hide();
		var element = $(this).parent().parent().parent().next();
		$(element).show();
		return false;
	});
	
/*
	$(".members_content .item") 
	    .hover(function() {
	    	$(".members_content .item").stop().animate({ opacity: 0.3 }, 200);
	        $(this).stop().animate({ opacity: 1.0 }, 100);
	    }, 
	    function() { 
	        $(".members_content .item").stop().animate({ opacity: 1.0 }, 200); 
    });
*/
    
    $(".error_bar, #flash_msg").click(function(){
		$(this).slideUp(300);
	});
/*	
	$('.fancybox').fancybox();
*/	
});