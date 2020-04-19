$(document).ready(
    $(".like a").on('click', function () {
        $(this).toggleClass('fas');;
    }),
        $(".unlike a").on('click', function () {
        $(this).toggleClass('far');;
    })
);