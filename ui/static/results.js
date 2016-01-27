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