/* Copyright (C) tiksan - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by tiksan <webmaster@deek.sh> */

const key = document.currentScript.getAttribute('data-key')

$(document).ready(function() {
    var recruitTable = $("#recruits-table").DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "responsive": true,
        "ajax": {
            url: "/faction/recruits"
        }
    });

    var recruitersTable = $("#recruiters-table").DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "responsive": true,
        "ajax": {
            url: "/faction/recruiters"
        }
    });

    $.fn.dataTable.ext.pager.numbers_length = 5;

    $("#recruiter-add-form").submit(function(e) {
        e.preventDefault();

        const xhttp = new XMLHttpRequest();
        var value = $("#recruiter-tid").val();
        value = Number(value);

        xhttp.onload = function() {
            var response = xhttp.response

            if(response.code === 1) {
                generateToast("Request Successfully Sent", `The Tornium API server has responded with \"${response["message"]}\" to the submitted request.`);
                recruitersTable.ajax.reload();
            } else {
                generateToast("Request Failed", `The Tornium API server has responded with \"${response["message"]}\" to the submitted request.`);
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/faction/recruitment/recruiter");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            'user': value,
        }));
    });

    $("#recruiter-remove-form").submit(function(e) {
        e.preventDefault();

        const xhttp = new XMLHttpRequest();
        var value = $("#recruiter-remove-tid").val();
        value = Number(value);

        xhttp.onload = function() {
            var response = xhttp.response

            if(response.code === 1) {
                generateToast("Request Successfully Sent", `The Tornium API server has responded with \"${response["message"]}\" to the submitted request.`);
                recruitersTable.ajax.reload();
            } else {
                generateToast("Request Failed", `The Tornium API server has responded with \"${response["message"]}\" to the submitted request.`);
            }
        }

        xhttp.responseType = "json";
        xhttp.open("DELETE", "/api/faction/recruitment/recruiter");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            'user': value,
        }));
    });
});
