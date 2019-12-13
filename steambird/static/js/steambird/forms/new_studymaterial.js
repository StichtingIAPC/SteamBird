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
    response = $.ajax({
        url: "/api/isbn/search",
        data: {
            isbn,
        },
    }).done(updateBook).fail(invalidISBN)

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
    $('#book-add-isbn-search').html('Search');
    let book = response.meta;


    $("#book-add-isbn input").removeClass("is-invalid").addClass("is-valid").val(book["ISBN-13"]);
    $("#book-add-title input").val(book.Title);
    $("#book-add-author input").val(book.Authors.join(", "));
    $("#book-add-year input").val(book.Year);
    $("#book-add-image input").val(book.img);
    $("#book-add-show-image").attr("src", book.img);

}

function invalidISBN(jqxhr, textstatus, error) {
    $('#book-add-isbn-search').html('Search');
    if (jqxhr.status == 400) {
        $("#book-add-isbn input").removeClass("is-valid").addClass("is-invalid");
        $("#book-add-isbn > .invalid-feedback").html("The entered ISBN does not pass the checksum and is therefore invalid. Please make sure you typed it correctly.")
    } else {
        $("#book-add-isbn input").removeClass("is-invalid").addClass("is-valid");

        $("#book-add-title input").val('');
        $("#book-add-author input").val('');
        $("#book-add-year input").val('');
        $("#book-add-edition input").val('');
        $("#book-add-image input").val('');
        $("#book-add-show-image").attr("src", '');
    }
}



$(($) => {
    $('#book-add-isbn').enterKey(ev => {
        searchIsbn(ev.target.value);
    });

    $('#book-add-isbn-search').click(() => {
        searchIsbn($('#book-add-isbn input').val());
        $('#book-add-isbn-search').html('Searching...');
    });

    $('#book-add-image').change(event => {
        $("#book-add-show-image").attr("src", event.target.value);
    });


    $('#paper-add-isbn-search').click(() => {
        searchIsbn($('#book-add-isbn input').val());
    });

    $('#paper-add-doi-search').click(() => {
        searchDoi(($('#paper-add-doi input').val()))
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
        url: "/api/doi/search",
        data: {
            doi,
        },
    }).done(updateArticle);
}

/**
 * @param article : {{
 *      DOI: string
 *      ISSN: Array of strings
 *      URL: string
 *      'alternative-id': Array of strings
 *      author: {
 *          given: string
 *          family: string
 *      }
 *      'container-title': string Name of journal/book/conference
 *      issue: string
 *      issued: {
 *          'date-parts':{
 *              0:{
 *                  0 : number year
 *                  1 : number month
 *              }
 *          }
 *      }
 *      language: string
 *      page: string range of pages
 *      prefix: string DOI prefix
 *      'publish=print': Array
 *      publisher: string
 *      'short-container-title': string often abbreviated title of container
 *      subject: Array of strings
 *      title: Array of strings
 *      type: string type of DOI
 *      volume: string
 * }}
 */
function updateArticle(article) {
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

    $("#paper-add-doi input").val(article.DOI);
    $("#paper-add-title input").val(article.title);
    $("#paper-add-author input").val(authors);
    $("#paper-add-year input").val(article.issued["date-parts"][0][0]);
    $("#paper-add-url input").val(article.URL);
}
