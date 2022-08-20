$(document).ready(function () {
    $('#dtDynamicVerticalScrollExample').DataTable({
    "scrollY": "50vh",
    "scrollCollapse": true,
    });
    $('.dataTables_length').addClass('bs-select');
    });

$("#dtDynamicVerticalScrollExample").bind("DOMSubtreeModified", function() {
    alert("Hurrey table changed");
    $('#dtDynamicVerticalScrollExample').DataTable({
        "scrollY": "50vh",
        "scrollCollapse": true,
        });
        $('.dataTables_length').addClass('bs-select');
});