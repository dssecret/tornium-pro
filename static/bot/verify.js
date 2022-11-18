/* Copyright (C) tiksan - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by tiksan <webmaster@deek.sh> */

const guildid = document.currentScript.getAttribute('data-guildid');
const key = document.currentScript.getAttribute('data-key');

$(document).ready(function() {
    $('[data-bs-toggle="tooltip"]').tooltip({
        html: true
    });

    let verificationConfig = null;

    var xhttp = new XMLHttpRequest();

    xhttp.onload = function() {
        let response = xhttp.response;

        if("code" in response) {
            generateToast("Discord Verification Config Not Located", response["message"])
            generateToast("Verification Loading Halted", "The lack of verification configs has prevented the page from loading.")
            throw new Error("Verification config error");
        } else {
            verificationConfig = response;

            xhttp.onload = function() {
                let response = xhttp.response;
        
                if("code" in response) {
                    generateToast("Discord Roles Not Located", response["message"]);
                } else {
                    $.each(response["roles"], function(role_id, role) {
                        if(verificationConfig["verified_roles"].includes(parseInt(role["id"]))) {
                            $("#verification-roles").get(0).innerHTML += `<option value="${role.id}" selected>${role.name}</option>`;
                        } else {
                            $("#verification-roles").get(0).innerHTML += `<option value="${role.id}">${role.name}</option>`;
                        }

                        $.each($(".verification-faction-roles"), function(index, item) {
                            if(verificationConfig["faction_verify"][parseInt(item.getAttribute("data-faction"))]["roles"].includes(parseInt(role["id"]))) {
                                item.innerHTML += `<option value=${role.id}" selected>${role.name}</option>`;
                            } else {
                                item.innerHTML += `<option value=${role.id}>${role.name}</option>`;
                            }
                        });
                    });

                    $(".discord-role-selector").selectpicker();

                    // xhttp.onload = function() {
                    //     let response = xhttp.response;
                
                    //     if("code" in response) {
                    //         generateToast("Discord Channels Not Located", response["message"]);
                    //     } else {
                    //         channels = response["channels"];
                    //     }
                    // }
                    
                    // xhttp.open("GET", `/api/bot/server/${guildid}/channels`);
                    // xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
                    // xhttp.setRequestHeader("Content-Type", "application/json");
                    // xhttp.send();
                }
            }

            xhttp.open("GET", `/api/bot/server/${guildid}/roles`);
            xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
            xhttp.setRequestHeader("Content-Type", "application/json");
            xhttp.send();
        }
    }

    xhttp.responseType = "json";
    xhttp.open("GET", `/api/bot/verify/${guildid}`);
    xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send();

    $("#verification-config-enable").on("click", function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Verification Enable Failed", `The Tornium API server has responded with \"${response["message"]}\".`)
            } else {
                generateToast("Verification Enable Successful", "The Tornium API server has been successfully enabled.")
                $("#verification-config-enable").prop("disabled", true);
                $("#verification-config-disable").prop("disabled", false);
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid
        }));
    });

    $("#verification-config-disable").on("click", function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Verification Enable Failed", `The Tornium API server has responded with \"${response["message"]}\".`)
            } else {
                generateToast("Verification Enable Successful", "The Tornium API server has been successfully enabled.")
                $("#verification-config-enable").prop("disabled", false)
                $("#verification-config-disable").prop("disabled", true)
            }
        }

        xhttp.responseType = "json";
        xhttp.open("DELETE", "/api/bot/verify");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid
        }));
    });

    $('#faction-verification-input').on('keypress', function(e) {
        if(e.which !== 13) {
            return;
        }

        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Faction Input Failed", `The Tornium API server has responded with \"${response["message"]}\".`);
            } else {
                generateToast("Faction Input Successful");
                window.location.reload(); // TODO: Replace with dynamically adding code
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify/faction");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "factiontid": $("#faction-verification-input").val()
        }));
    });

    $("#verification-log-channel").on('change', function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Log Channel Failed", `The Tornium API server has responded with \"${response["message"]}\".`);
            } else {
                generateToast("Log Channel Successful");
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify/log");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "channel": this.options[this.selectedIndex].value
        }));
    });

    $(".verification-faction-enable").on("click", function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {

            } else {
                generateToast("Faction Enabled Successfully");
                window.location.reload();
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify/faction");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "factiontid": this.getAttribute("data-faction")
        }));
    });

    $(".verification-faction-disable").on("click", function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {

            } else {
                generateToast("Faction Disabled Successfully");
                window.location.reload();
            }
        }

        xhttp.responseType = "json";
        xhttp.open("DELETE", "/api/bot/verify/faction");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "factiontid": this.getAttribute("data-faction")
        }));
    });

    $(".verification-faction-remove").on("click", function() {
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {

            } else {
                generateToast("Faction Removed Successfully");
                window.location.reload();
            }
        }

        xhttp.responseType = "json";
        xhttp.open("DELETE", "/api/bot/verify/faction");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "factiontid": this.getAttribute("data-faction"),
            "remove": true
        }));
    });


    $(".verification-faction-roles").on("change", function() {
        var selectedOptions = $(this).find(":selected");
        var selectedRoles = [];

        $.each(selectedOptions, function(index, item) {
            selectedRoles.push(item.getAttribute("value"));
        });

        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Role Add Failed");
            } else {
                generateToast("Role Add Successful");
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify/faction/roles");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "factiontid": this.getAttribute("data-faction"),
            "roles": selectedRoles
        }));
    });

    $("#verification-roles").on("change", function() {
        var selectedOptions = $(this).find(":selected");
        var selectedRoles = [];

        $.each(selectedOptions, function(index, item) {
            selectedRoles.push(item.getAttribute("value"));
        });

        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            let response = xhttp.response;

            if("code" in response) {
                generateToast("Role Add Failed");
            } else {
                generateToast("Role Add Successful");
            }
        }

        xhttp.responseType = "json";
        xhttp.open("POST", "/api/bot/verify/roles");
        xhttp.setRequestHeader("Authorization", `Basic ${btoa(`${key}:`)}`);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify({
            "guildid": guildid,
            "roles": selectedRoles
        }));
    });

    $(".verification-faction-edit").on("click", function() {
        console.log(this);
        const xhttp = new XMLHttpRequest();

        xhttp.onload = function() {
            document.getElementById("modal").innerHTML = this.responseText;
            var modal = new bootstrap.Modal($("#verify-settings-modal"));
            modal.show();
        }

        xhttp.open("GET", `/bot/dashboard/${guildid}/verify/faction/${this.getAttribute("data-faction")}`);
        xhttp.send();
    })
});
