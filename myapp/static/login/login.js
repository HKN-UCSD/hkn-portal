$(document).ready(function() {
    function adjustLayout() {
        if ($(window).width() < 768) {
            $(".container").css({"flex-direction": "column"});
            $(".left-column").css({
                "height": "40vh", 
                "padding": "40px 20px"
            });
            $(".right-column").css({
                "height": "auto",
                "padding": "20px",
                "flex-direction": "column"
            });

            $(".hknmascot").css({
                "display": "none"
            });
        }
    }

    // Run function on page load and window resize
    adjustLayout();
    $(window).resize(adjustLayout);
});