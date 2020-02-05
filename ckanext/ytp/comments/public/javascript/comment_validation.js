function hideFormErrors()
{
    jQuery('.form_errors').addClass('hidden');
    jQuery('.form_errors li').addClass('hidden');
}

jQuery(document).ready(function() {

    jQuery('.module-content input[type="submit"]').on('click', function(e) {
        if (jQuery(this).hasClass('btn-primary')) {
            var form = jQuery(this).closest('form');
            var comment = form.find('textarea[name="comment"]').val();
            var display_errors = false;

            hideFormErrors();

            if (!comment || !comment.replace(/\s/g, '').length) {
                form.find('.error-comment').removeClass('hidden');
                display_errors = true;
            }
            if (display_errors) {
                form.find('.form-errors').removeClass('hidden');
                return false;
            }
        }
    });

});
