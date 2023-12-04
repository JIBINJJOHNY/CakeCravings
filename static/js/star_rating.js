$(document).ready(function () {
    let selectedRating = 0;

    $('.star-rating i').click(function () {
        const rating = $(this).data('rating');
        selectedRating = rating;
        updateStars(selectedRating);
    });

    function updateStars(rating) {
        $('.star-rating i').removeClass('checked');
        $('.star-rating i').each(function () {
            if ($(this).data('rating') <= rating) {
                $(this).addClass('checked');
            }
        });
        $('#rating').val(rating);
    }
});