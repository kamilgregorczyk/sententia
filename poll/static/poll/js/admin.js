var letters = 'abcdefghijklmnopqrstuvwxyz';
var numbers = '1234567890';
var charset = letters + letters.toUpperCase() + numbers;

function randomElement(array) {
    with (Math)
        return array[floor(random() * array.length)];
}

function randomString(length) {
    var R = '';
    for (var i = 0; i < length; i++)
        R += randomElement(charset);
    return R;
}
var select_tab = function (tab_id) {
    $('div[id^=tabs-]').hide()
    $(tab_id).show()

    $('#tabs ul li a').removeClass('ui-state-active');
    $('#tabs ul li a[href^=' + tab_id.replace(/([ #;?%&,.+*~\':"!^$[\]()=>|\/@])/g, '\\$1') + ']').addClass('ui-state-active')
};
$(function () {
    $('[name=_saveasnew]').text('Klonuj ankietę').attr("value", "Klonuj ankietę");

    $('#tabs > ul a').click(function () {
        select_tab($(this).attr('href'))

    });
    $('.roll').click(function () {
        if ($(this).attr('data-roll') == "rolled") {
            $(this).closest('.djn-item').find('.inline-group').slideDown();
            $(this).attr('data-roll', "not-rolled").text("ZWIŃ")
        } else {
            $(this).closest('.djn-item').find('.inline-group').slideUp();
            $(this).attr('data-roll', "rolled").text("ROZWIŃ")
        }

    })
    $('.roll-all').click(function (e) {
        e.preventDefault();
        if ($(this).attr('data-roll') == "rolled") {
            $(this).attr('data-roll', "not-rolled").text("Zwiń wszystkie")
            $('.roll').each(function (k, v) {
                $(v).closest('.djn-item').find('.inline-group').slideDown();
                $(v).attr('data-roll', "not-rolled").text("ZWIŃ")
            })
        } else {
            $(this).attr('data-roll', "rolled").text("Rozwiń wszystkie")
            $('.roll').each(function (k, v) {
                $(v).closest('.djn-item').find('.inline-group').slideUp();
                $(v).attr('data-roll', "rolled").text("ROZWIŃ")
            });
        }
    });
    if (window.location.hash) {
        select_tab(window.location.hash)
    } else {
        $('#tabs ul li:first-child a').addClass('ui-state-active');
    }

    $('.Tokeny .empty-form .field-code input').val(randomString(3));
    $('.Tokeny .add-row').click(function () {
        $('.Tokeny .empty-form .field-code input').val(randomString(3))
    });
    $('.field-type select').each(function (k, v) {
        var selected_value = $(v).find(':selected').text();
        if (selected_value == 'Pole tekstowe' || selected_value == 'Skala') {
            $(v).parent().parent().parent().parent().find('.djn-group-nested').hide()
        }
    });
    $('body').on('change', '.field-type select', function () {
        var selected_value = $(this).find(':selected').text();
        if (selected_value == 'Pole tekstowe' || selected_value == 'Skala') {
            $(this).parent().parent().parent().parent().find('.djn-group-nested').slideUp();
            $(this).parent().parent().parent().parent().find('.djn-group-nested').find('input[type=checkbox]').prop('checked', true)
        } else {
            $(this).parent().parent().parent().parent().find('.djn-group-nested').slideDown();
            $(this).parent().parent().parent().parent().find('.djn-group-nested').find('input[type=checkbox]').prop('checked', false)
        }
    })
});