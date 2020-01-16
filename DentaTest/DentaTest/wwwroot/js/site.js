// Please see documentation at https://docs.microsoft.com/aspnet/core/client-side/bundling-and-minification
// for details on configuring this project to bundle and minify static web assets.

function countFiles() {
    var curFiles = document.getElementById("files").files;
    var label = document.getElementById("lab");

    if (curFiles.length === 0) {
        label.innerText = 'Выберите фотографии';
    } else {
        label.innerText = 'Выбрано фотографий: ' + curFiles.length;
    }
}
