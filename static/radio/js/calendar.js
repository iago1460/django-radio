function loading(bool) {
    if (bool) {
        $('#loading').show();
        $('#loading-ok').hide();
    } else {
        $('#loading').hide();
        $('#loading-ok').show();

    }
}

 // using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
    // or any other URL that isn't scheme relative or absolute i.e relative.
    !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
        loading(true);
    },
    complete: function (data) {
		loading(false);
	}
});


$(document).ready(function () {

    var calendar = $('#calendar').fullCalendar({
        lang: 'es',
        eventDurationEditable: false,
        eventStartEditable: true,
        allDaySlot: false,
        firstDay: 1,
        axisFormat: 'HH:mm',
        timezone: false,
        scrollTime: '07:00:00',
        lazyFetching: false,
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'agendaWeek,agendaDay'
        },
        defaultView: 'agendaWeek',

        events: {
            url: URL_JSON_ALL_EVENTS,
            error: function() {
                alert('there was an error while fetching events!');
            },
        },
        droppable: true, // this allows things to be dropped onto the calendar !!!
        drop: function (date) { // this function is called when something is dropped

            // retrieve the dropped element's stored Event Object
            var originalEventObject = $(this).data('eventObject');

            // we need to copy it, so that multiple events don't have a reference to the same object
            var copiedEventObject = $.extend({}, originalEventObject);

            // assign it the date that was reported
            copiedEventObject.start = date;
            copiedEventObject.end = $.fullCalendar.moment(date).add('minutes', copiedEventObject.runtime);

            // create the event 
            $.ajax({
                type: "POST",
                url: "create_schedule",
                data: 'programmeId=' + copiedEventObject.programmeId + '&start=' + $.fullCalendar.moment(copiedEventObject.start).add('minutes', moment().zone()) + '&type=' +$("input[name='group1']:checked").val(),
                success: function (res) {
                    if (res.error) {
                        alert("Error en la peticion " + res.error);
                    } else {
                    	response =  res.response
                        copiedEventObject.id = response.scheduleId;
                        copiedEventObject.backgroundColor = response.backgroundColor;
                        copiedEventObject.textColor = response.textColor;
                        // render the event on the calendar
                        // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
                        $('#calendar').fullCalendar('renderEvent', copiedEventObject, true);
                    }
                },
                error: function (data) {
                    revertFunc();
                    alert("Error desconocido. Por favor recarge la pagina");
                },
            });

        },
        
        //remove all events (dropped events)
        viewRender: function( view, element ){
        	$('#calendar').fullCalendar( 'removeEvents')
        },

        eventClick: function (calEvent, jsEvent, view) {
            // change the border color just for fun
            //$(this).css('border-color', 'red');

        },


        eventDrop: function (event, revertFunc) {
            $.ajax({
                type: "POST",
                url: "change_event",
                data: 'id=' + event.id + '&start=' + $.fullCalendar.moment(event.start).add('minutes', moment().zone()),
                success: function (res) {
                    if (res.error) {
                        revertFunc();
                        alert("Error en la peticion " + res.error);
                    }
                },
                error: function (data) {
                    revertFunc();
                    alert("Error desconocido. Por favor recarge la pagina");
                },
            });
        },
        
        eventDragStop: function(event, jsEvent, ui, view) { 
            //console.log(event.id);
             if (isElemOverDiv(ui, $('div#delete-events'))) {
            	 $.ajax({
                     type: "POST",
                     url: "delete_schedule",
                     data: 'scheduleId=' + event.id,
                     success: function (res) {
                         if (res.error) {
                             alert("Error en la peticion " + res.error);
                         } else {
                        	 calendar.fullCalendar('removeEvents', event.id);
                         }
                     },
                     error: function (data) {
                         revertFunc();
                         alert("Error desconocido. Por favor recarge la pagina");
                     },
                 });
             }
         },

        loading: function (bool) {
            loading(bool)
        }



    })

});

window.onload = function () {
    $.getJSON('programmes', function (data) {
    	info = data.response
        for (var numero = 0; numero < info.length; numero++) {
            var eventObjectFromDB = info[numero];
            var eventToExternalEvents = {
                "title": eventObjectFromDB.title,
                "runtime": eventObjectFromDB.runtime,
                "programmeId": eventObjectFromDB.programmeId,
                "editable": true
            };

            $('#external-events').append("<div class='external-event' id='mec" + numero + "'>" + eventToExternalEvents.title + "</div>");
            var eventObject2 = {
                title: $.trim(eventToExternalEvents.title), // use the element's text as the event title
                runtime: eventToExternalEvents.runtime,
                programmeId: eventToExternalEvents.programmeId,
            };
            $('#mec' + numero).data('eventObject', eventObject2);
            
            $('.external-event').draggable({
                zIndex: 999,
                revert: true, // will cause the event to go back to its
                revertDuration: 0
            });
            //$('#calendar').fullCalendar('refetchEvents');
        }
    });
}


var isElemOverDiv = function(draggedItem, dropArea) {
    var dragged = $(draggedItem)[0].offset;

    var b = $(dropArea);
    var limitX = parseInt(b.offset().left) + parseInt(b.outerWidth());
    var limitY = parseInt(b.offset().top) + parseInt(b.outerHeight());

    // Compare
    if ( limitY >=   parseInt(dragged.top) 
        && limitX >=   parseInt(dragged.left) ) 
    { 
        return true; 
    }
    return false;
}

