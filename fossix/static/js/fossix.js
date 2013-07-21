// Some global variables

var flash_warn_timer;

function flash_error(string)
{
    html =
        '<div class="alert alert-error"><button type="button"\
class="close" data-dismiss="alert">&times;</button>\
<strong><big>O</big>ops! </strong>'+ string + '</div>';
    $('#message').html(html);
    $('#message').slideDown();

}

function clear_info()
{
    window.clearInterval(flash_warn_timer);
    c = $('#info').children('div').first();
    if (c != undefined) {
        c.delay(500).slideUp();
        c.remove();
    }

    // if ($('#info').children().length > 0) {
    //      flash_warn_timer = window.setInterval(clear_info, 5000);
    //  }
}

function flash_info(string)
{
    html =
        '<div class="alert alert-info"><button type="button" class="close"\
data-dismiss="alert">&times;</button>' + string + '</div>';
    $('#info').append(html);
    $('#info').slideDown();
    flash_warn_timer = window.setInterval(clear_info, 5000);
}

function dologin(event) {
    var target = event.data.target1;
    var form = $(this);

    event.preventDefault();

    $.ajax({
        type : form.attr("method"),
        url: form.attr("action"),
        data: {
            'email': $("#uemail").val(),
            'password': $("#passwd").val(),
            'j':$(location).attr('href'),
        },
        success :function(data) {
            if (data.error == 'true')
                flash_error(data.errortext);
            else {
                window.location.replace(location.href);
                $('#lform').slideUp();
            }
        },
        error : function(jqXHR, textStatus, errorThrown) {
        },
    });
    return (false);
}

function vote_comment(event) {
    var link = $(this).attr('data-url');

    $.ajax({
        type        : "GET",
        contentType : "application/json; charset=utf-8;",
        url         : link,
        datatype    : "json",
        success     : function(data) {
            count = data.count;
            id = data.id;
            count_id = "#vote_count" + id;
            $(count_id).text(count);
            $(count_id).delay(500).fadeIn();
        },
        error       : function(jqXHR, textStatus, errorThrown) {
            flash_error(errorThrown);
         }
    });

    return (false);
}

function like_content(event) {
    var link = $(this);

    $('#likecount').fadeOut();
    $('#like').fadeOut();

    $.ajax({
        type        : "GET",
        contentType : "application/json; charset=utf-8;",
        url         : link.attr("href"),
        datatype    : "json",
        success     : function(data) {
            count = data.count;
            $('#like').hide();
            $('#likecount').text(count);
            $('#likecount').delay(500).fadeIn();

        },
        error       : function(jqXHR, textStatus, errorThrown) {
            flash_error(errorThrown);
            $('#like').fadeIn();
        }
    });

    return (false);
}

function openid_login(provider)
{
    var link = $(this).attr('data-href');
    var type = $(this).attr('data-type');

    if (type == 'openid')
        $('input[name="openid"]').val(link);

    $('#openid-form').submit();
}

function scroll_hook(target, percent, callback)
{
    $(target).bind('scroll', function () {
        if ((($(target).scrollTop() / $(target).innerHeight()) * 100)
            >= percent) {
            callback();
        }
    });
}

function load_comments()
{
    // unbind the event, prevent multiple requests
    $(document).off('scroll');

    $('#loading').html("<p>Loading Comments &hellip;</p>");
    $('#loading').delay(300).fadeIn();

    var link = $('#comments').attr('data-url');
    var total = $('#comments').attr('data-total');

    $.ajax({
        type        : "GET",
        contentType : "application/json; charset=utf-8;",
        url         : link,
        datatype    : "json",
        success     : function(data) {
            last = data.last;
            html = data.html;
            parent = data.parent;
            $('#comments').append(html);
            $('#comments').attr('data-url', '/content/comment/'+parent+'/'+last);
            if (last < total) {
                scroll_hook(document, 40, load_comments);
            }
        },
        error       : function(jqXHR, textStatus, errorThrown) {
            flash_error(errorThrown);
        }
    });
    $('#loading').html("Done.");
    $('#loading').delay(1000).fadeOut();
}

function show_comment_box(event)
{
    parent_id = $(this).data("parent");
    article = $('#comments').data("parent");
    parent = $("#comment"+parent_id);
    var div = $("#comment-form");
    $('#comment-cancel').show();
    $('#comment-form #refers_to').val(parent_id);
    parent.append(div);

    return (false);
};

function watch_tag(event)
{
    var link = $(this).attr('href');

    $.ajax({
        type        : "PUT",
        contentType : "application/json; charset=utf-8;",
        url         : link,
        datatype    : "json",
        success     : function(data) {
            $('#watchtag').addClass('disabled');
            flash_info(data.message);
        },
        error       : function(jqXHR, textStatus, errorThrown) {
            flash_error(errorThrown);
        }
    });

    return (false);
}

function fossix_event_setup()
{
    $(document).on('click', '#like', like_content);
    $(document).on('click', '#watchtag', watch_tag);
    $(document).on('click', '.vote', vote_comment);
    $(document).on('click', '.comment-reply', show_comment_box);
    $(document).on('click', '#comment-cancel',
                   function(e) {
                       var div = $("#comment-form");
                       var article = $('#comments').data("parent");
                       $("#comment-cancel").hide();
                       $("#comment-form-main").append(div);
                       $('#comment-form #refers_to').val(article);
                   });

    scroll_hook(document, 40, load_comments);

    $(function ($) {
        $(".tooltips").tooltip();
        $(".popovers").popover();
        $('.tag').hover(
            function(){ $(this).toggleClass('label-inverse') },
            function(){ $(this).toggleClass('label-inverse') }
        );
    });

    $(document).on('click', '.openid-signin', openid_login);
}
