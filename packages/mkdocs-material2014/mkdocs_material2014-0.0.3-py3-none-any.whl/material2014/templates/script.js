$(document).ready(function () {
    $('.sidenav').sidenav();
    $('.collapsible.expandable').collapsible({
        accordion: false
    });
    $(".d-search-button").click(e => {
        e.preventDefault();
        $("nav").addClass("d-search-open");
    });
    $(".d-search-close-button").click(e => {
        e.preventDefault();
        $("nav").removeClass("d-search-open");
    });
    if (!$(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-seamless-cool-page-navbar");
    }
    $(".d-toc-wrapper").pushpin({
        top: 320,
        offset: 64
    })
    $('h1,h2,h3,.scollspy').scrollSpy();
    $('.tabs').tabs({
        swipeable: false,
        duration: 150
    });
});

$(document).scroll(function () {
    $('.navbar-fixed').removeClass("no-transition");
    if ($(document).scrollTop() >= 180 && $(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-no-text-cool-page-navbar");
    } else {
        $('.navbar-fixed').addClass("d-no-text-cool-page-navbar");
    }
    if ($(document).scrollTop() >= 240 && $(".d-cool-page-start").length) {
        $('.navbar-fixed').removeClass("d-seamless-cool-page-navbar");
    } else {
        $('.navbar-fixed').addClass("d-seamless-cool-page-navbar");
    }
});
