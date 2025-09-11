/* global Choices, prepareTransmitterForm */

const classNames = {
    containerOuter: ['choices', 'flex-grow-1', 'd-flex'],
    containerInner: ['choices__inner', 'bg-white'],
    input: ['choices__input'],
    inputCloned: ['choices__input--cloned'],
    list: ['choices__list'],
    listItems: ['choices__list--multiple'],
    listSingle: ['choices__list--single'],
    listDropdown: ['choices__list--dropdown'],
    item: ['choices__item'],
    itemSelectable: ['choices__item--selectable'],
    itemDisabled: ['choices__item--disabled'],
    itemChoice: ['choices__item--choice'],
    description: ['choices__description'],
    placeholder: ['choices__placeholder'],
    group: ['choices__group'],
    groupHeading: ['choices__heading'],
    button: ['choices__button'],
    activeState: ['is-active'],
    focusState: ['is-focused'],
    openState: ['is-open'],
    disabledState: ['is-disabled'],
    highlightedState: ['is-highlighted'],
    selectedState: ['is-selected'],
    flippedState: ['is-flipped'],
    loadingState: ['is-loading'],
    notice: ['choices__notice'],
    addChoice: ['choices__item--selectable', 'add-choice'],
    noResults: ['has-no-results'],
    noChoices: ['has-no-choices'],
};

function validateFormAndSubmit(formURL, container, extraFormSetup) {
    /* This function works with  BSModal*View views. Those views will only validate and
     * not save an object when they receive an XHR Post request. So if the ajax submitted
     * form is validated and has no errors, it is submitted normally (without xhr)
     */
    const form = container.find('form');
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: new FormData(form[0]),
        contentType: false,
        processData: false,
        beforeSend: function () {
            form.find('button[type="submit"]').prop('disabled', true);
        },
        success: function (response) {
            if ($(response).find('.invalid').length > 0) {  // If it has errors, re-render the form
                formSetup(response, formURL, container, extraFormSetup);
            } else {
                form.submit();  // If not, submit it without xhr
            }
        }
    });
}

function formSetup(response, formURL, container, extraFormSetup) {
    container.html(response);
    const form = container.find('form');
    form.attr('action', formURL);
    form.on('submit', function (event) {
        if (event.originalEvent !== undefined) {    // Prevent loop at submission
            event.preventDefault();
            validateFormAndSubmit(formURL, container, extraFormSetup);
            return false;
        }
    });
    // Attach handler to cancelButton that exists in the form
    document.getElementById('cancelButton').addEventListener('click', function () {
        history.go(-1);
    });
    if(extraFormSetup && typeof extraFormSetup === 'function') {
        extraFormSetup();
    }
    var citationField = document.getElementById('id_citation');
    citationField.value = '';
}

function loadForm(formURL, extraFormSetup) {
    const container = $('#form-container');

    // Destroy cancel button that exists before form load when type === 'transmitter'
    const cancelButton = document.getElementById('cancelButton');
    if (cancelButton) {
        cancelButton.remove();
    }
    $.ajax({
        type: 'GET',
        url: formURL,
        success: function (response) {
            formSetup(response, formURL, container, extraFormSetup);
        }
    });
}

$(document).ready(function() {
    'use strict';

    const suggestionTypeSelect = document.getElementById('suggestion-type-select');
    const satelliteSelect = document.getElementById('satellite-select');
    const satelliteSelectDiv = document.getElementById('satellite-select-div');
    const formContainer = document.getElementById('form-container');
    let satPk = parseInt(formContainer.dataset['satelliteEntryPk']);
    const transmitterPk = parseInt(formContainer.dataset['transmitterPk']);
    const copyFromPk = parseInt(formContainer.dataset['copyFromPk']);
    const suggestionType = formContainer.dataset['type'];
    const suggestionMode = formContainer.dataset['mode'];
    let satelliteChoices = undefined;

    const SATELLITE_CREATE_FORM_URL = '/create_satellite/';
    const TRANSMITTER_CREATE_FORM_BASE_URL = '/create_transmitter/';
    const SATELLITE_UPDATE_FORM_URL = `/update_satellite/${satPk}/`;
    const TRANSMITTER_UDPATE_FORM_URL = `/update_transmitter/${transmitterPk}`;

    if (suggestionMode === 'create') {
    // if a satellite is specified without transmitter type selected, it is ignored
        if(suggestionType !== 'transmitter') {
            satPk = null;
        }

        if (!suggestionType || suggestionType === 'satellite') {
            suggestionTypeSelect.value = 'satellite';
            loadForm(SATELLITE_CREATE_FORM_URL);
        } else if (suggestionType === 'transmitter') {
            satelliteSelectDiv.style.display = 'flex';

            // Attach handler to cancel button that exists before transmitter form is loaded
            document.getElementById('cancelButton').addEventListener('click', function () {
                history.go(-1);
            });
            if (satPk) {
                loadForm(`${TRANSMITTER_CREATE_FORM_BASE_URL}${satPk}`, prepareTransmitterForm);
            }
        }

        // If a satellite is not specified, setup the satellite select
        if (!satPk) {
            const fetchOptions = (query) => {
                return fetch(`/satellite-search/?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        satelliteChoices.clearChoices();
                        satelliteChoices.setChoices(data);
                    })
                    .catch(error => console.error('Error fetching options:', error));
            };

            satelliteChoices = new Choices(satelliteSelect, {
                placeholderValue: '-----------------------------------',
                searchFloor: 3,
                searchPlaceholderValue: 'Search for satellites',
                noChoicesText: 'Start typing 3 characters minimum in the search field to load options',
                classNames: classNames
            });

            satelliteSelect.addEventListener('search', function (event) {
                const searchTerm = event.detail.value;
                fetchOptions(searchTerm);
            });
        }

        suggestionTypeSelect.addEventListener('change', () => {
            if (suggestionTypeSelect.value === 'transmitter') {
                satelliteSelectDiv.style.display = 'flex';
                formContainer.innerHTML = '<div class="p-3"><p>Select a satellite</p></div>';

            } else {
                satelliteChoices.removeActiveItems();
                satelliteSelectDiv.style.display = 'none';
            }

            if (suggestionTypeSelect.value === 'satellite') {
                loadForm(SATELLITE_CREATE_FORM_URL);
            }
        });

        satelliteSelect.addEventListener('change', e => {
            loadForm(`${TRANSMITTER_CREATE_FORM_BASE_URL}${e.target.value}`, prepareTransmitterForm);
        });
    } else if (suggestionMode == 'copy') {
        if(suggestionType === 'satellite') {
            loadForm(`${SATELLITE_CREATE_FORM_URL}?from=${copyFromPk}`);
        } else {
            loadForm(`${TRANSMITTER_CREATE_FORM_BASE_URL}${satPk}?from=${copyFromPk}`, prepareTransmitterForm);
        }
    } else {
        if(suggestionType === 'satellite') {
            loadForm(SATELLITE_UPDATE_FORM_URL);
        } else {
            loadForm(TRANSMITTER_UDPATE_FORM_URL, prepareTransmitterForm);
        }
    }
});
