/*
 * Core library functions available throughout yangsuite.
 */

$.when(getPromise('/gtm')).then(function(retObj)
{
  if (retObj.enable_gtm) {
    dataLayer = [{
        'userId': retObj.userid,
        'company': retObj.company,
        'devices': retObj.device_count,
    }];
  (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer', retObj.gtmid);
    $('#ys-gtm').attr('src',
        'https://www.googletagmanager.com/ns.html?id='+retObj.gtmid)
  }
  else if (retObj.error == 'no_email') {
    $('#ytool-email-dialog').dialog({
      modal: true,
      open: function(event, ui) {   // It'll hide Close button
        $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
      },
      buttons: {
        'Save': function () {
          var email = $('input[name="Email-ID"]').val();
          storeEmail(email);
        }
      }
    });
  }
  else if (retObj.error == 'invalid_email') {
    $('#ytool-email-id').text('Provided Email is not valid!!! Please provide a valid Company Email-ID')
    $('#ytool-email-dialog').dialog ({
      modal: true,
      buttons: {
        'Save': function () {
          var email = $('input[name="Email-ID"]').val();
          storeEmail(email);
          $(this).dialog('close');
        }
      }
    });
  }
  else if (retObj.error == 'company') {
    $('#ytool-email-id').text('Please provide a valid company Email-ID')
    $('#ytool-email-dialog').dialog ({
      modal: true,
      buttons: {
        'Save': function () {
          var email = $('input[name="Email-ID"]').val();
          storeEmail(email);
          $(this).dialog('close');
        }
      }
    });
  }
});

/**
 * Save the email id to the database
 */
function storeEmail(email){
    $.when(getPromise('/save_email', {"email": email}))
            .then(function(retObj) {
                if (retObj.reply) {
                  popDialog("Email saved successfully");
                  $('#ytool-email-dialog').dialog('close')
                }
            }, function(retObj) {
                popDialog('Error' + retObj.status + ':' + retObj.statusText);
            });
}

/**
 * Check whether the given HTTP method is 'safe' (no CSRF protection needed)
 */
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/**
 * Construct a POST request that expects a JSON response.
 * Add the X-CSRFToken header if needed.
 *
 * @param {string} uri URI to send the request to
 * @param {Object} data key/value pairs to pass in the request
 * @param {string} contentType Input data format (defaults to form-encoded)
 * @return {jqXHR} As in $.ajax()
 */
function getPromise(uri, data,
                    contentType='application/x-www-form-urlencoded; charset=UTF-8') {
    var csrf = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        }
    });

    return $.ajax({url: uri,
                   data: data,
                   type: 'POST',
                   dataType: "json",
                   contentType: contentType});

}

/**
 * Convenience wrapper for getPromise() that uses a json contentType instead
 * of the default form-encoded contentType.
 */
function jsonPromise(uri, data) {
    return getPromise(uri, JSON.stringify(data), contentType="application/json");
}

/**
 * Queries the given URI and updates the progressbar element with the response.
 *
 * @param {string} uri URI to query
 * @param {selector} progress Element to update.
 * @param {object} params Any parameters to include in the GET request.
 */
function updateProgress(uri, progress, params={}) {
    if (!progress.progressbar("instance")) {
        /* progressbar is not currently active */
        return;
    }

    $.getJSON(uri, params, function(data) {
        if (!progress.progressbar("instance")) {
            /* There was an updateProgress here. It's gone now. */
            return;
        }
        if (data.value < data.max) {
            /*
             * We set the value and max to a base of 1 instead of 0,
             * because the data.info text won't be displayed if value == 0
             */
            progress.progressbar("option", "max", data.max + 1);
            progress.progressbar("option", "value", data.value + 1);
        } else {
            /*
             * Since value == max, either we're nearly done,
             * or no actual value/max are known.
             * Either way, display as indeterminate.
             */
            progress.progressbar("option", "value", false);
        }
        setProgressText(progress, data.info);

    }).fail(function(retObj, textStatus, error) {
        // Switch to indeterminate and continue, as actual request may be OK
        progress.progressbar("option", "value", false);
        // No clearInterval(progressInterval) as this may be transient issue
    });
}

let progressIntervals = {};
let progressBars = {};
let progressCloneCounter = 0;

/**
 * Start a timer to call updateProgress once per second.
 * Stops any existing timer to avoid contention over the progressbar.
 *
 * @param {selector} progress Element to update.
 * @param {string} uri OPTIONAL URI to GET for periodic updates
 * @param {object} params OPTIONAL Any parameters to include in the GET request.
 * @param {string} progressBarText OPTIONAL Text to be displayed on progress bar.
 */
function startProgress(progress, uri=undefined, params={}, progressBarText) {
    let id = progress.attr("id");
    if (progressBars[id] || progressIntervals[id]) {

        //create new progress bar and assign new id to it.
        let parentId = "#" + $("#"+id).parent().attr("id");
        id = id + "-" + progressCloneCounter++;
        progress = $(progress).clone().empty();

        progress[0].id = id;
        progress.selector = "div#" + id + '';
        progress.appendTo(parentId);
    }
    progressBars[id] = true;
    progress.progressbar({value: false});
    setProgressText(progress, progressBarText);

    if (uri) {
        progressIntervals[id] = setInterval(function() {
            updateProgress(uri, progress, params);
        }, 1000);
    }

    return progress;
}

/**
 * Mark the given progressbar as complete and display the given message.
 * After 5 seconds, destroy the progressbar.
 *
 * @param {selector} progress Element owning the progressbar.
 * @param {string} message Message to display.
 */
function progressComplete(progress, message) {
    let id = progress.attr("id");
    if (progressIntervals[id]) {
        clearInterval(progressIntervals[id]);
        progressIntervals[id] = null;
    }

    // Mark progressbar as completed
    progress.progressbar("option", "max", 100);
    progress.progressbar("option", "value", 100);

    setProgressText(progress, message);

    // After 5000 ms, destroy the progressbar
    progressIntervals[id] = setTimeout(function() {
        stopProgress(progress);
    }, 5000);
}

/**
 * Stop and destroy the progressbar and/or timer created by startProgress.
 *
 * @param {selector} progress Element owning the progressbar.
 */
function stopProgress(progress) {
    let id = progress.attr("id");
    if (progressIntervals[id]) {
        clearInterval(progressIntervals[id]);
        progressIntervals[id] = null;
    }
    if (progressBars[id] && progress.progressbar("instance")) {
        progress.progressbar("destroy");
        progressBars[id] = false;
    }

    //check and remove additional div (eg."ys-progress-0") created from the page.
    let divLastChar = id.substr(id.length - 1);
    if(!(isNaN(divLastChar))){
        progress.remove();
    }
}

/**
 * Utility function the opens a simple dialog box on a ytool-dialog div.
 *
 * @param {str} text for internal of dialog box
 * @param {boolean} true to force user to close box before doing anything
 */
function popDialog(text, modal=false) {
    $("#ytool-dialog").empty();
    if (!text || !text.length) {
        "No text for this dialog box!";
    }
    $("#ytool-dialog").dialog({modal: modal,
                               height: "auto",
                               maxHeight: $(window).height() * 0.9,
                               minWidth: 100,
                               //Removes default focus from the close button of dialog
                               open: function( e, ui ) {
                                  $( this ).siblings( ".ui-dialog-titlebar" )
                                           .find( "button" ).blur();
                              }
                             });

    $("#ytool-dialog").html(text);
    $("#ytool-dialog").dialog("open");
}

/**
 * Utility function to close ytool-dialog div.
 */
function popDialogClose() {
    $("#ytool-dialog").dialog("close");
}

/**
 * Display the message on the progress bar while loading.
 */
function setProgressText(progress, progressBarText){
    if(progressBarText == undefined){
        progressBarText = "";
    }

    value_div = progress.progressbar("widget").children('.ui-progressbar-value');
    if (value_div.children('.ui-progressbar-text').length == 0) {
        value_div.prepend('<div class="ui-progressbar-text"></div>');
    }
    value_div.children('.ui-progressbar-text').html(progressBarText);
}
