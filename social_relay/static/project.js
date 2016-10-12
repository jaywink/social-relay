$(function() {
    $("#show-tags-link").click(function(ev) {
        $(ev.currentTarget).hide();
        $('#tags-container').removeClass('hidden');
        return false;
    });
});
