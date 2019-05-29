/**
 * @callback KeyPressCallback
 * @param element {HTMLElement}
 * @param event {Event}
 */

/**
 * Triggers fnc when the enter key is pressed.
 * @param fnc {KeyPressCallback}
 * @returns {any}
 */
$.fn.enterKey = function (fnc) {
    return this.each(function () {
        $(this).keypress(function (ev) {
            let keycode = (ev.keyCode ? ev.keyCode : ev.which);
            if (keycode == '13') {
                fnc.call(this, ev);
            }
        });
    });
};

/**
 * @param isbn {string}
 */
function searchIsbn(isbn) {
    $.ajax({
        url: "/teacher/api/isbn/search",
        data: {
           isbn,
        },
    }).done(updateBook);
}

/** @param response {{
 *    meta: {
 *      "ISBN-13": string,
 * 	    Title: string,
 *      Authors: [string],
 * 	    Publisher: string,
 * 	    Language: string,
 * 	    Year: string,
 * 	    smallThumbnail: string,
 * 	    thumbnail: string,
 * 	    img: string
 *    },
 *    desc: string,
 *    cover: cover,
 *  }}
 */
function updateBook(response) {
    let book = response.meta;

    $("#material-type").val($('#type-add').val());
    $("#book-add-isbn").val(book["ISBN-13"]);
    $("#book-add-title").val(book.Title);
    $("#book-add-author").val(book.Authors.join(", "));
    $("#book-add-year").val(book.Year);
    $("#book-add-image").val(book.thumbnail);
    $("#book-add-show-image").attr("src", book.thumbnail);
}

$(($) => {
    $('#book-add-isbn').enterKey(ev => {
        searchIsbn(ev.target.value);
    });

    $('#book-add-isbn-search').click(() => {
        searchIsbn($('#book-add-isbn').val());
    });

    $('#book-add-image').change(event => {
        $("#book-add-show-image").attr("src", event.target.value);
    });

    $('#type-add').change(event => {
        const type = event.target.value;

        $(`.form-add`).css('display', 'none');

        if (!type) {
            return;
        }

        $(`#${type}-add`).css('display', 'block');
    })
});
