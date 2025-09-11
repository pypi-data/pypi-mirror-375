/* eslint new-cap: "off" */
function copyToClipboard(text, el) {
    var copyTest = document.queryCommandSupported('copy');
    var elOriginalText = el.attr('data-original-title');

    if (copyTest === true) {
        var copyTextArea = document.createElement('textarea');
        copyTextArea.value = text;
        document.body.appendChild(copyTextArea);
        copyTextArea.select();
        try {
            var successful = document.execCommand('copy');
            var msg = successful ? 'Copied!' : 'Whoops, not copied!';
            el.attr('data-original-title', msg).tooltip('show');
        } catch (err) {
            window.alert('Oops, unable to copy');
        }
        document.body.removeChild(copyTextArea);
        el.attr('data-original-title', elOriginalText);
    } else {
        // Fallback if browser doesn't support .execCommand('copy')
        window.prompt('Copy to clipboard: Ctrl+C or Command+C, Enter', text);
    }
}

function ppb_to_freq(freq, drift) {
    var freq_obs = freq + ((freq * drift) / Math.pow(10, 9));
    return Math.round(freq_obs);
}

function freq_to_ppb(freq_obs, freq) {
    if (freq == 0) {
        return 0;
    } else {
        return Math.round(((freq_obs / freq) - 1) * Math.pow(10, 9));
    }
}

function format_freq(freq) {
    var frequency = +freq;
    if (frequency < 1000) {
        // Frequency is in Hz range
        return frequency.toFixed(3) + ' Hz';
    } else if (frequency < 1000000) {
        return (frequency / 1000).toFixed(3) + ' kHz';
    } else {
        return (frequency / 1000000).toFixed(3) + ' MHz';
    }
}

function chart_recent_data(results) {
    // Split timestamp and data into separate arrays. Since influx does not
    // have a native way to calculate total data points, we have to iterate
    // on an unknown number of fields returned
    var labels = [];
    var data = [];
    results['series']['0']['values'].forEach(function (point) {
        // First point is unixtime (label)
        // the API returns all decoded points and we only want to count individual frames
        // with good data so we have to look for a data point and avoid dupes in the frame
        var i;
        var pointPlaceholder = 0;
        for (i = 0; i < point.length; i++) {
            if (i == 0) {
                var date = new Date(point[i] * 1000);
                var formattedDate = '' + date.getUTCFullYear() + '/' + (date.getUTCMonth()+1) + '/' + date.getUTCDate();
                labels.push(formattedDate);
            } else {
                if (point[i] > pointPlaceholder) {
                    pointPlaceholder = point[i];
                }
            }
        }
        data.push(pointPlaceholder);
    });

    var tempData = {
        labels: labels,
        datasets: [{
            label: 'Decoded Data Frames',
            borderColor: 'rgba(101,111,219,0.2)',
            backgroundColor: 'rgba(101,111,219,0.5)',
            data: data
        }]
    };

    // un-hide the canvas element
    $('#dataChart').removeClass('d-none');
    // Get the context of the canvas element we want to select
    var ctx = document.getElementById('dataChart').getContext('2d');

    // Instantiate a new chart, requires chart.js
    /*global Chart*/
    new Chart(ctx, {
        type: 'line',
        data: tempData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    type: 'logarithmic',
                }]
            }
        }
    });
}

$(document).ready(function () {
    // Calculate the drifted frequencies
    $('.drifted').each(function () {
        var drifted = ppb_to_freq($(this).data('freq_or'), $(this).data('drift'));
        $(this).html(drifted);
    });

    $('.uplink-drifted-sugedit').on('change click', function () {
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('input[name=\'uplink_low\']:visible').val());
        $('.uplink-ppb-sugedit').val(freq_to_ppb(freq_obs, freq));
    });

    $('.downlink-drifted-sugedit').on('change click', function () {
        var freq_obs = parseInt($(this).val());
        var freq = parseInt($('input[name=\'downlink_low\']:visible').val());
        $('.downlink-ppb-sugedit').val(freq_to_ppb(freq_obs, freq));
    });

    // Format all frequencies
    $('.frequency').each(function () {
        var to_format = $(this).html();
        $(this).html(format_freq(to_format));
    });

    // Copy UUIDs
    $('.js-copy').click(function () {
        var text = $(this).attr('data-copy');
        var el = $(this);
        copyToClipboard(text, el);
    });

    let modal_open = false;
    // Update Satellite
    $('.update-satellite-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#update-satellite-modal'
        });

        $('#update-satellite-modal').on('hidden.bs.modal', function () {
            modal_open = false;
        });

        $('#update-satellite-modal').on('show.bs.modal', function () {
            modal_open = true;
        });
    });

    // Update Transmitter
    $('.update-transmitter-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#update-transmitter-modal'
        });

        $('#update-transmitter-modal').on('hidden.bs.modal', function () {
            modal_open = false;
        });

        $('#update-transmitter-modal').on('show.bs.modal', function () {
            modal_open = true;
        });
    });

    // New transmitter links
    $('.create-transmitter-link').each(function () {
        $(this).modalForm({
            formURL: $(this).data('form-url'),
            modalID: '#create-transmitter-modal'
        });

        $('#create-transmitter-modal').on('hidden.bs.modal', function () {
            modal_open = false;
        });

        $('#create-transmitter-modal').on('show.bs.modal', function () {
            modal_open = true;
        });
    });

    // Prevent navigate to new url if a modal is open
    $(window).on('beforeunload', function() {
        if (modal_open === true) {
            return true;
        }

        return undefined;
    });

    // Ask for help in a toast if this Satellite object is flagged as in need
    if ($('#satellite_name').data('needshelp') == 'True') {
        $(document).Toasts('create', {
            title: 'Please Help!',
            class: 'alert-warning',
            autohide: true,
            delay: 6000,
            icon: 'fas fa-hand-holding-medical',
            body: 'This Satellite needs editing. <a href="https://wiki.satnogs.org/Get_In_Touch" target="_blank">Contact us</a> to become an editor.'
        });
    }

    var satid = $('#dataChart').data('satid');
    if (Number.isInteger(satid)){
        $.ajax({
            url: '/ajax/recent_decoded_cnt/' + satid,
            dataType: 'json',
        }).done(function (response) {

            try {
            // Check if the response has zero results
                if (response.series && response.series.length > 0) {
                // Process and display the results
                    chart_recent_data(response);
                } else {
                // Handle zero results
                    $('#dataChartError').removeClass('d-none');
                }
            } catch (e) {
                // unhide the placeholder message if the chart errors out
                $('#dataChartError').removeClass('d-none');
            }
        });
    } else {
        $('#dataChartError').removeClass('d-none');
    }

    // Handle deep linking of tabbed panes
    let url = location.href.replace(/\/$/, '');
    history.replaceState(null, null, url);

    if (location.hash) {
        const hash = url.split('#');
        $('#tabs a[href="#' + hash[1] + '"]').tab('show');
        url = location.href.replace(/\/#/, '#');
        history.replaceState(null, null, url);
        setTimeout(() => {
            $(window).scrollTop(0);
        }, 400);
    }

    $('a[data-toggle="tab"]').on('click', function () {
        let newUrl;
        const hash = $(this).attr('href');
        if (hash == '#profile') {
            newUrl = url.split('#')[0];
        } else {
            newUrl = url.split('#')[0] + hash;
        }
        history.replaceState(null, null, newUrl);
    });

    // this is a nav-tab link outside of nav tabs
    $('.outside-tab-link').click(function () {
        const hash = $(this).attr('href');
        $('#tabs a[href="' + hash + '"]').tab('show');
    });

    // Show/hide invalid transmitters
    let invalidTransmittersDiv = $('#invalidTransmitters');
    invalidTransmittersDiv.hide();
    $('#showInvalidCheckbox').on('click', function() {
        invalidTransmittersDiv.fadeToggle('fast', 'linear');
    });

    // Suggestion Tables
    const transmitterSuggestionFilters = `
    <div class="d-flex">
        <div class="dropdown mr-1">
        <button class="btn btn-primary dropdown-toggle" type="button" id="suggestion-filter-new-existing" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Filter</button>
            <div class="dropdown-menu">

                <div class="dropdown-item">
                    <input type="checkbox" id="toggleNewTransmitterSuggestions" checked>
                    <label for="toggleNewTransmitterSuggestions"> New</label><br>
                </div>

                <div class="dropdown-item">
                    <input type="checkbox" id="toggleExistingTransmitterSuggestions" checked>
                    <label for="toggleExistingTransmitterSuggestions"> Existing</label><br>
                </div>

            </div>
        </div>
    </div>
    `;

    $.fn.dataTable.ext.search.push(function (settings, data) {
        if (settings.nTable.id === 'satellites-table') {
            return true;
        } else if (settings.nTable.id === 'transmitters-table') {
            const newTransmitterSuggestionToggle = document.getElementById('toggleNewTransmitterSuggestions');
            const existingTransmitterSuggestionToggle = document.getElementById('toggleExistingTransmitterSuggestions');

            if (!newTransmitterSuggestionToggle || !existingTransmitterSuggestionToggle) {
                return true;
            }

            const newChecked = newTransmitterSuggestionToggle.checked;
            const existingChecked = existingTransmitterSuggestionToggle.checked;

            let transmitterFilter = false;

            if (newChecked) {
                transmitterFilter = data[5] === 'New';
            }
            if (existingChecked) {
                transmitterFilter = transmitterFilter || data[5] === 'Existing';
            }
            return transmitterFilter;
        }

        return true;
    });

    $('#satellites-table').DataTable( {
        // the dom field controls the layout and visibility of datatable items
        // and is not intuitive at all. Without layout we have dom: 'Bftrilp'
        // https://datatables.net/reference/option/dom
        dom :'<"row"<"d-none d-md-block col-md-6"B><"col-sm-12 col-md-6"f>>' +
        '<"row"<"col-sm-12"tr>>' +
        '<"row"<"col-sm-12 col-xl-3 align-self-center"i><"col-sm-12 col-md-6 col-xl-3 align-self-center"l><"col-sm-12 col-md-6 col-xl-6"p>>',
        buttons: [
            'colvis'
        ],
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRow,
                type: 'column'
            }
        },
        columnDefs: [
            {
                type: 'natural',
                targets: [0, 1]
            }
        ],
        language: {
            search: 'Filter:',
            buttons: {
                colvis: 'Columns',
            }
        },
        order: [0, 'desc'],
        pageLength: 25
    } );


    const transmittersTable = $('#transmitters-table').DataTable( {
        dom :'<"row"<"d-none d-md-block col-md-6"B><"col-sm-12 col-md-6"f>>' +
            '<"row"<"col-12"tr>>' +
            '<"row"<"col-sm-12 col-xl-3 align-self-center"i><"col-sm-12 col-md-6 col-xl-3 align-self-center"l><"col-sm-12 col-md-6 col-xl-6"p>>',
        buttons: [
            'colvis'
        ],
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRow,
                type: 'column'
            }
        },
        columnDefs: [
            {
                type: 'natural',
                targets: [0, 1, 2, 3, 4, 5 ]
            }
        ],
        language: {
            search: 'Filter:',
            buttons: {
                colvis: 'Columns',
            }
        },
        order: [0, 'desc'],
        pageLength: 25
    } );

    $('#history-table').DataTable( {
        // the dom field controls the layout and visibility of datatable items
        // and is not intuitive at all. Without layout we have dom: 'Bftrilp'
        // https://datatables.net/reference/option/dom
        dom :'<"row"<"d-none d-md-block col-md-6"B><"col-sm-12 col-md-6"f>>' +
        '<"row"<"col-sm-12"tr>>' +
        '<"row"<"col-sm-12 col-xl-3 align-self-center"i><"col-sm-12 col-md-6 col-xl-3 align-self-center"l><"col-sm-12 col-md-6 col-xl-6"p>>',
        buttons: [
            'colvis'
        ],
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRow,
                type: 'column'
            }
        },
        columnDefs: [
            {
                type: 'natural',
                targets: [0, 1, 2, 3, 4]
            }
        ],
        language: {
            search: 'Filter:',
            buttons: {
                colvis: 'Columns',
            }
        },
        order: [1, 'desc'],
        pageLength: 25
    } );

    $('#transmitters-table_wrapper .dt-buttons').append(transmitterSuggestionFilters);
    const newTransmitterSuggestionToggle = $('#toggleNewTransmitterSuggestions');
    const existingTransmitterSuggestionToggle = $('#toggleExistingTransmitterSuggestions');

    newTransmitterSuggestionToggle.on('click', function() {
        transmittersTable.draw();
    });

    existingTransmitterSuggestionToggle.on('click', function() {
        transmittersTable.draw();
    });

    const transmitterHistorySelect = document.getElementById('transmitter-history-select');
    if (transmitterHistorySelect) {
        transmitterHistorySelect.addEventListener('change', () => {
            if (transmitterHistorySelect.value) {
                loadTransmitterHistoryTable(transmitterHistorySelect.value);
            } else {
                document.getElementById('transmitter-suggestion-history-div').innerHTML = '';
            }
        });
    }
});

function loadTransmitterHistoryTable(uuid) {
    const tableDiv = document.getElementById('transmitter-suggestion-history-div');
    fetch(`/transmitter-suggestion-history/${uuid}`).
        then(response => {
            // Check if the request was successful (status code in the 200-299 range)
            if (!response.ok) {
                tableDiv.innerHTML = 'Error fetching transmitter\'s history.';
                throw new Error('Error fetching transmitter\'s history.');
            }
            return response.text();
        })
        .then(html => {
            tableDiv.innerHTML = html;
        })
        .then(() => {
            $('#transmitter-history-table').DataTable( {
                // the dom field controls the layout and visibility of datatable items
                // and is not intuitive at all. Without layout we have dom: 'Bftrilp'
                // https://datatables.net/reference/option/dom
                dom :'<"row"<"d-none d-md-block col-md-6"B><"col-sm-12 col-md-6"f>>' +
                '<"row"<"col-sm-12"tr>>' +
                '<"row"<"col-sm-12 col-xl-3 align-self-center"i><"col-sm-12 col-md-6 col-xl-3 align-self-center"l><"col-sm-12 col-md-6 col-xl-6"p>>',
                buttons: [
                    'colvis'
                ],
                responsive: {
                    details: {
                        display: $.fn.dataTable.Responsive.display.childRow,
                        type: 'column'
                    }
                },
                columnDefs: [
                    {
                        type: 'natural',
                        targets: [0, 1, 2, 3, 4]
                    }
                ],
                language: {
                    search: 'Filter:',
                    buttons: {
                        colvis: 'Columns',
                    }
                },
                order: [1, 'desc'],
                pageLength: 25
            } );
        })
        .catch(() => {
            tableDiv.innerHTML = 'Error fetching transmitter\'s history.';
        });

}

// Prevent "are you sure you want to leave" popup on submit
$(document).ajaxComplete(function(){
    $('#satellite_update-form').submit(function() {
        $(window).unbind('beforeunload');
    });
});
