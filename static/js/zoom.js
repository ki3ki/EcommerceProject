(function($) {
    $.fn.zoom = function() {
        this.each(function() {
            var originalSrc = $(this).attr('src');
            var zoomedImg = $('<img>').attr('src', originalSrc).addClass('zoomed');
            $('body').append(zoomedImg);
            zoomedImg.hide();

            $(this).on('mousemove', function(event) {
                var offsetX = event.offsetX / $(this).width() * 100;
                var offsetY = event.offsetY / $(this).height() * 100;
                zoomedImg.css({
                    'left': event.pageX + 10 + 'px',
                    'top': event.pageY + 10 + 'px',
                    'background-position': offsetX + '% ' + offsetY + '%'
                });
                zoomedImg.show();
            });

            $(this).on('mouseout', function() {
                zoomedImg.hide();
            });
        });
        return this;
    };
})(jQuery);
