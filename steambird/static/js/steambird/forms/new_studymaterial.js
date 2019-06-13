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

/**
 * @param response {{
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
    $("#book-add-image").val(book.img);
    $("#book-add-show-image").attr("src", book.img);
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


    $('#paper-add-isbn-search').click(() => {
        searchIsbn($('#paper-add-isbn').val());
    });

    $('#paper-add-doi-search').click(() => {
        searchDoi(($('#paper-add-doi').val()))
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


/**
 * @param doi {string}
 */
function searchDoi(doi) {
    $.ajax({
        url: "/teacher/api/doi/search",
        data: {
            doi,
        },
    }).done(updateArticle);
}

/**
 * @param response {{
 *     info: {
 *         DOI: string
 *         ISSN: Array of strings
 *         URL: string
 *         'alternative-id': Array of strings
 *         author: {
 *             given: string
 *             family: string
 *         }
 *         'container-title': string Name of journal/book/conference
 *         issue: string
 *         issued: {
 *             'date-parts':{
 *                 0:{
 *                     0 : number year
 *                     1 : number month
 *                 }
 *             }
 *         }
 *         language: string
 *         page: string range of pages
 *         prefix: string DOI prefix
 *         'publish=print': Array
 *         publisher: string
 *         'short-container-title': string often abbreviated title of container
 *         subject: Array of strings
 *         title: Array of strings
 *         type: string type of DOI
 *         volume: string
 *     }
 * }}
 */
function updateArticle(response) {
    let article = response.info;

    const authors = article.author.map(author => {
        if (author.given && author.family) {
            return author.given + " " + author.family;
        }

        if (author.given) {
            return author.given;
        }

        if (author.family) {
            return author.family;
        }
    }).join(", ");

    $("#material-type").val($('#type-add').val());
    $("#paper-add-doi").val(article.DOI);
    $("#paper-add-title").val(article.title);
    $("#paper-add-author").val(authors);
    $("#paper-add-year").val(article.issued["date-parts"][0][0]);
    $("#paper-add-url").val(article.URL);
}
