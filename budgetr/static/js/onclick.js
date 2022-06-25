$(function () {
    $('table tr').click(function () {
        window.location.href = $(this).data('url');
    });
})