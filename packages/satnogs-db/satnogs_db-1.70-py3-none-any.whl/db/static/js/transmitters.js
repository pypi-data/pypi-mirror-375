/* global renderTransmittersChart */

function ppb_to_freq(freq, drift) {
    var freq_obs = freq + ((freq * drift) / Math.pow(10,9));
    return Math.round(freq_obs);
}

function format_freq(frequency_string) {
    var frequency = Number(frequency_string);
    if (isNaN(frequency) || frequency == ''){
        return 'None';
    } else if (frequency < 1000) {
    // Frequency is in Hz range
        return frequency.toFixed(3) + ' Hz';
    } else if (frequency < 1000000) {
        return (frequency/1000).toFixed(3) + ' kHz';
    } else {
        return (frequency/1000000).toFixed(3) + ' MHz';
    }
}
/* eslint-enable no-unused-vars */

// Extra filters for transmitter's status
const transmitter_extra_status_filters = `
<div class="d-flex">
    <div class="dropdown mr-1">
    <button class="btn btn-primary dropdown-toggle" type="button" id="transmitter-filter-status" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Filter</button>
        <div class="dropdown-menu">

            <div class="dropdown-item">
                <input type="checkbox" id="toggleInvalidTransmitters">
                <label for="toggleInvalidTransmitters"> Invalid</label><br>
            </div>

            <div class="dropdown-item">
                <input type="checkbox" id="toggleInactiveTransmitters">
                <label for="toggleInactiveTransmitters"> Inactive</label><br>
            </div>

            <div class="dropdown-item">
                <input type="checkbox" id="toggleUnconfirmedTransmitters">
                <label for="toggleUnconfirmedTransmitters"> Unconfirmed</label><br>
            </div>

        </div>
    </div>
</div>
`;

// Custom filtering function to show/hide invalid & inactive transmitters
$.fn.dataTable.ext.search.push(function (settings, data) {
    const invalidTransmitterToggle = $('#toggleInvalidTransmitters');
    const inactiveTransmitterToggle = $('#toggleInactiveTransmitters');
    const toggleUnconfirmedTransmitters = $('#toggleUnconfirmedTransmitters');

    const invalid_statement = invalidTransmitterToggle.is(':checked');
    const inactive_statement = inactiveTransmitterToggle.is(':checked');
    const unconfirmed_statement = toggleUnconfirmedTransmitters.is(':checked');

    if(invalid_statement) {
        if (inactive_statement) {
            if(unconfirmed_statement) {
                return true;
            } else {
                return data[14] === 'False';
            }
        } else {
            if(unconfirmed_statement) {
                return data[13] !== 'inactive';
            } else {
                return data[13] !== 'inactive' && data[14] === 'False';
            }
        }
    } else {
        if (inactive_statement) {
            if(unconfirmed_statement) {
                return data[13] !== 'invalid';
            } else {
                return data[13] !== 'invalid' && data[14] === 'False';
            }
        } else {
            if(unconfirmed_statement) {
                return data[13] !== 'invalid' && data[13] !== 'inactive';
            } else {
                return data[13] !== 'invalid' && data[14] === 'False' && data[13] !== 'inactive';
            }
        }
    }
});

/* eslint new-cap: "off" */
$(document).ready(function() {

    // Calculate the drifted frequencies
    $('.drifted').each(function() {
        var drifted = ppb_to_freq($(this).data('freq_or'),$(this).data('drift'));
        $(this).html(drifted);
    });

    // Format all frequencies
    $('.frequency').each(function() {
        var to_format = $(this).html();
        $(this).html(format_freq(to_format));
    });

    const table = $('#transmitters').DataTable( {
        // the dom field controls the layout and visibility of datatable items
        // and is not intuitive at all. Without layout we have dom: 'Bftrilp'
        // https://datatables.net/reference/option/dom
        dom: '<"row"<"d-none d-md-block col-md-6"B><"col-sm-12 col-md-6"f>>' +
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
                className: 'control',
                orderable: false,
                targets:   0
            },
            {
                type: 'natural',
                targets: [5, 6, 7, 8, 11]
            }
        ],
        language: {
            search: 'Filter:',
            buttons: {
                colvis: 'Columns',
            }
        },
        order: [ 1, 'asc' ],
        pageLength: 25
    } );

    // .dt-buttons is the columns dropdown
    $('.dt-buttons').append(transmitter_extra_status_filters);
    let invalidTransmitterToggle = $('#toggleInvalidTransmitters');
    let inactiveTransmitterToggle = $('#toggleInactiveTransmitters');
    let unconfirmedTransmitterToggle = $('#toggleUnconfirmedTransmitters');

    invalidTransmitterToggle.hide();
    inactiveTransmitterToggle.hide();
    unconfirmedTransmitterToggle.hide();

    // Event listener to redraw the table if invalid transmitter visibility is toggled
    invalidTransmitterToggle.on('click', function() {
        table.draw();
    });

    // Event listener to redraw the table if inactive transmitter visibility is toggled
    inactiveTransmitterToggle.on('click', function() {
        table.draw();
    });

    // Event listener to redraw the table if unconfirmed transmitter visibility is toggled
    unconfirmedTransmitterToggle.on('click', function() {
        table.draw();
    });

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
        if (hash == '#list') {
            newUrl = url.split('#')[0];
        } else {
            newUrl = url.split('#')[0] + hash;
        }
        history.replaceState(null, null, newUrl);
    });

    var transmitters;
    var satellites;
    var transmittersChart;
    var transmitter_filters = {};
    var satellite_filters = { 'status': 'alive' };
    const transmitter_status_dropdown = $('#transmitter-status-filter');
    const satellite_status_dropdown = $('#satellite-status-filter');

    $('.transmitter-status-filter-option').on('click', function (e) {
        e.stopPropagation();
        e.stopImmediatePropagation();

        var val = $(this).data('val');
        if (val === 'all') {
            delete transmitter_filters['status'];
        } else {
            transmitter_filters = { 'status': val };
        }

        var label = $(this).text();

        transmitter_status_dropdown.html('Show Transmitters: ' + label);
        $('#transmitters-chart-container').empty();
        transmittersChart = renderTransmittersChart({
            el: document.querySelector('#transmitters-chart-container'),
            transmitters: JSON.parse(JSON.stringify(transmitters)),
            satellites_list: JSON.parse(JSON.stringify(satellites)),
            transmitter_filters: transmitter_filters,
            satellite_filters: satellite_filters,
        });

        $(this).parent().dropdown('toggle');
    });

    $('.satellite-status-filter-option').on('click', function (e) {
        e.stopPropagation();
        e.stopImmediatePropagation();

        var val = $(this).data('val');
        if (val === 'all') {
            delete satellite_filters['status'];
        } else {
            satellite_filters = { 'status': val };
        }

        var label = $(this).text();

        satellite_status_dropdown.html('Show Satellites: ' + label);
        $('#transmitters-chart-container').empty();
        transmittersChart = renderTransmittersChart({
            el: document.querySelector('#transmitters-chart-container'),
            transmitters: JSON.parse(JSON.stringify(transmitters)),
            satellites_list: JSON.parse(JSON.stringify(satellites)),
            transmitter_filters: transmitter_filters,
            satellite_filters: satellite_filters,
        });

        $(this).parent().dropdown('toggle');
    });

    $('#spectrum-filters').hide();

    function load_spectrum_tab() {
        Promise.all([
            fetch('/api/transmitters/?format=json')
                .then((response) => response.json()),
            fetch('/api/satellites/?format=json')
                .then((response) => response.json()),
        ]).then((responses) => {
            transmitters = responses[0];
            satellites = responses[1];

            $('#spectrum-spinner').remove();

            transmittersChart = renderTransmittersChart({
                el: document.querySelector('#transmitters-chart-container'),
                transmitters: JSON.parse(JSON.stringify(transmitters)),
                satellites_list: JSON.parse(JSON.stringify(satellites)),
                transmitter_filters: transmitter_filters,
                satellite_filters: satellite_filters,
            });

            transmittersChart.zoom(
                434.5,
                438.5
            );

            $('#spectrum-filters').show();

            document.querySelector('#zoom-all').addEventListener('click', () => {
                transmittersChart.zoom(0,30000);
            });
            document.querySelector('#zoom-vhf').addEventListener('click', () => {
                transmittersChart.zoom(143,147);
            });
            document.querySelector('#zoom-uhf').addEventListener('click', () => {
                transmittersChart.zoom(434.5,438.5);
            });
        });
    }

    $('a[href="#spectrum"]').on('shown.bs.tab', function () {
        load_spectrum_tab();
        $('a[href="#spectrum"]').off('shown.bs.tab');
    });
} );
