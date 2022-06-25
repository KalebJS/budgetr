$(function () {
    $('table tr.clickable').click(function () {
        window.location.href = $(this).data('url');
    });
})