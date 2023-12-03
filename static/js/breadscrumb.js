// JavaScript code for generating breadcrumbs
document.addEventListener('DOMContentLoaded', function () {
    generateBreadcrumbs();
});

function generateBreadcrumbs() {
    var breadcrumbContainer = document.getElementById('breadcrumb-container');
    var pathArray = window.location.pathname.split('/').filter(function (path) {
        return path !== '';
    });

    var breadcrumbHtml = '<a href="/">Home</a>';
    var path = '/';
    for (var i = 0; i < pathArray.length; i++) {
        path += pathArray[i] + '/';
        breadcrumbHtml += ' > <a href="' + path + '">' + pathArray[i].charAt(0).toUpperCase() + pathArray[i].slice(1) + '</a>';
    }

    breadcrumbContainer.innerHTML = breadcrumbHtml;
}