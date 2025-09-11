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

const satelliteSuggestionFilters = `
<div class="d-flex">
    <div class="dropdown mr-1">
    <button class="btn btn-primary dropdown-toggle" type="button" id="suggestion-filter-new-existing" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Filter</button>
        <div class="dropdown-menu">

            <div class="dropdown-item">
                <input type="checkbox" id="toggleNewSatelliteSuggestions" checked>
                <label for="toggleNewSatelliteSuggestions"> New</label><br>
            </div>

            <div class="dropdown-item">
                <input type="checkbox" id="toggleExistingSatelliteSuggestions" checked>
                <label for="toggleExistingSatelliteSuggestions"> Existing</label><br>
            </div>

        </div>
    </div>
</div>
`;

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
        const newSatelliteSuggestionToggle = document.getElementById('toggleNewSatelliteSuggestions');
        const existingSatelliteSuggestionToggle = document.getElementById('toggleExistingSatelliteSuggestions');

        if (!newSatelliteSuggestionToggle || !existingSatelliteSuggestionToggle) {
            return true;
        }

        const newChecked = newSatelliteSuggestionToggle.checked;
        const existingChecked = existingSatelliteSuggestionToggle.checked;

        let satelliteFilter = false;

        if (newChecked) {
            satelliteFilter = data[3] === 'New';
        }
        if (existingChecked) {
            satelliteFilter = satelliteFilter || data[3] === 'Existing';
        }
        return satelliteFilter;

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
            transmitterFilter = data[6] === 'New';
        }
        if (existingChecked) {
            transmitterFilter = transmitterFilter || data[6] === 'Existing';
        }
        return transmitterFilter;
    }

    return true;
});



/* eslint new-cap: "off" */
$(document).ready(function() {

    // Format all frequencies
    $('.frequency').each(function() {
        var to_format = $(this).html();
        $(this).html(format_freq(to_format));
    });

    const satellitesTable = $('#satellites-table').DataTable( {
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
                targets: [0, 1, 2, 3, 4, 5]
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

    $('#satellites .dt-buttons').append(satelliteSuggestionFilters);
    const newSatelliteSuggestionToggle = $('#toggleNewSatelliteSuggestions');
    const existingSatelliteSuggestionToggle = $('#toggleExistingSatelliteSuggestions');

    newSatelliteSuggestionToggle.on('click', function() {
        satellitesTable.draw();
    });

    existingSatelliteSuggestionToggle.on('click', function() {
        satellitesTable.draw();
    });

    $('#transmitters .dt-buttons').append(transmitterSuggestionFilters);
    const newTransmitterSuggestionToggle = $('#toggleNewTransmitterSuggestions');
    const existingTransmitterSuggestionToggle = $('#toggleExistingTransmitterSuggestions');

    newTransmitterSuggestionToggle.on('click', function() {
        transmittersTable.draw();
    });

    existingTransmitterSuggestionToggle.on('click', function() {
        transmittersTable.draw();
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
        if (hash == '#satellites') {
            newUrl = url.split('#')[0];
        } else {
            newUrl = url.split('#')[0] + hash;
        }
        history.replaceState(null, null, newUrl);
    });
} );
