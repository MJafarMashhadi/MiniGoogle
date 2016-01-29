// Show/hide clusters
$(function () {
    $('.ch-cluster').on('change', function (e) {
        var self = $(this);
        console.log("change shod :D");
        var cluster_number = self.attr('name').substr('ch-cluster-'.length);
        var $cluster_items = $('.cluster-' + cluster_number);
        if (this.checked) {
            $cluster_items.fadeIn(200);
            self.parent('.btn').addClass('active');
        } else {
            $cluster_items.fadeOut(200);
            self.parent('.btn').removeClass('active');
        }
    });
    $('label.btn').on('click', function (e) {
        var self = $(this);
        self.children('.ch-cluster').trigger('click');
    })
});

// Pagination
$(function () {
    window.$results_page = 1;
    $('#load_more').on('click', function (e) {
        var self = $(this);
        self.addClass('disabled');
        $.ajax({
            url: '/search/' + (window.$results_page+1) + window.location.href.slice(window.location.href.indexOf('?')),
            complete: function () {
                self.removeClass('disabled');
            },
            success: function (ajax_results) {
                $('.results-table').append(ajax_results);
                window.$results_page++;
                console.log('Current page = ' + window.$results_page);
            }
        })
    });
});

// Abstract text
$(function () {
    var showChar = 300;
    $('p.abstract').each(function() {
        var content = $(this).html();

        if(content.length > showChar) {

            var c = content.substr(0, showChar);
            var h = content.substr(showChar-1, content.length - showChar);

            var html = c + '<span class="see-more">... (click to see more)</span><span class="more">'+h+'</span>';

            $(this).html(html);
        }

    }).on('click', function() {
        $(this).children('.see-more').toggle();
        $(this).children('.more').toggle();
    });

    $('p.abstract>span.more').hide();
});

// Author clusters
$(function () {
    var cache = {};

    $('.author-class').on('click', function (e) {
        var self = $(this);
        var name = self.data('name');
        name = name.replace(/\//g, '');
        $('.author-class').popover('hide');
        if (cache[name]) {
            self.popover('toggle');
        } else {
            $.ajax({
                url: '/author/' + name,
                success: function (ajax_result) {
                    cache[name] = ajax_result;
                    self.popover({
                        html: true,
                        content: ajax_result,
                        placement: 'top'
                    }).popover('toggle');
                }
            });
        }
        e.preventDefault();
    });
});