$(function() {
    document.getElementById('cancelButton').addEventListener('click', function () {
        history.go(-1);
    });
});