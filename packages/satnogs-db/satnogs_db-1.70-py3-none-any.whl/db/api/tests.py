"""SatNOGS DB API test suites"""
import json
import os
from io import BytesIO

import pytest
from django.contrib.auth.models import User  # pylint: disable=E5142
from django.test import TestCase
from rest_framework import status

from db.base.helpers import get_api_token
from db.base.models import OpticalIdentification, OpticalObservation
from db.base.tests import DemodDataFactory, ModeFactory, SatelliteFactory, TransmitterFactory


@pytest.mark.django_db(transaction=True)
class ModeViewApiTest(TestCase):
    """
    Tests the Mode View API
    """
    mode = None

    def setUp(self):
        self.mode = ModeFactory()
        self.mode.save()

    def test_list(self):
        """Test the API modes list"""
        response = self.client.get('/api/modes/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        """Test the API mode retrieval"""
        response = self.client.get('/api/modes/{0}/'.format(self.mode.id), format='json')
        self.assertContains(response, self.mode.name)


@pytest.mark.django_db(transaction=True)
class SatelliteViewApiTest(TestCase):
    """
    Tests the Satellite View API
    """
    satellite = None

    def setUp(self):
        self.satellite = SatelliteFactory()
        self.satellite.save()

    def test_list(self):
        """Test the Satellite API listing"""
        response = self.client.get('/api/satellites/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_with_norad_id(self):
        """Test the Satellite API retrieval with NORAD ID"""
        response = self.client.get(
            '/api/satellites/{0}/'.format(self.satellite.satellite_entry.norad_cat_id),
            format='json'
        )
        self.assertContains(response, self.satellite.satellite_entry.name)

    def test_retrieve_with_satellite_id(self):
        """Test the Satellite API retrieval with Satellite Identifier"""
        response = self.client.get(
            '/api/satellites/{0}/'.format(self.satellite.satellite_identifier.sat_id),
            format='json'
        )
        self.assertContains(response, self.satellite.satellite_entry.name)

    def test_retrieve_nonexistent_satellite(self):
        """Tests for a non existent satellite"""
        response = self.client.get('/api/satellites/{0}/'.format('BADBADBADBAD'), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_jsonld_satellites(self):
        """Tests the return of a satellite via JSONLD browsable renderer"""
        response = self.client.get('/api/satellites/?format=json-ld')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_browse_jsonld_satellites(self):
        """Tests the return of a satellite via JSONLD browsable renderer"""
        response = self.client.get('/api/satellites/?format=browse-json-ld')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db(transaction=True)
class TransmitterViewApiTest(TestCase):
    """
    Tests the Transmitter View API
    """
    transmitter = None

    def setUp(self):
        TransmitterFactory.create_batch(size=50)
        self.transmitter = TransmitterFactory(status='active')
        self.transmitter.uuid = 'test'
        self.transmitter.save()

    def test_list(self):
        """Test the Transmitter API listing"""
        response = self.client.get('/api/transmitters/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_active(self):
        """Test the Transmitter API listing with active filter"""
        response = self.client.get('/api/transmitters/?Alive=true&format=json')
        self.assertContains(response, '\"active\"')

    def test_list_inactive(self):
        """Test the Transmitter API listing with inactive"""
        response = self.client.get('/api/transmitters/?Alive=false&format=json')
        self.assertContains(response, '\"inactive\"')

    def test_retrieve(self):
        """Test the Transmitter API retrieval"""
        response = self.client.get(
            '/api/transmitters/{0}/'.format(self.transmitter.uuid), format='json'
        )
        self.assertContains(response, self.transmitter.description)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
class TelemetryViewApiTest(TestCase):
    """
    Tests the Telemetry View API
    """
    datum = None
    satellite = None

    frame = '60A060A0A46E609C8262A6A640E082A0A4A682A86103F02776261C6C201C5'
    frame += '3495D41524953532D496E7465726E6174696F6E616C2053706163652053746174696F6E3D0D'

    def setUp(self):
        self.datum = DemodDataFactory()
        self.datum.save()
        self.satellite = SatelliteFactory()
        self.satellite.save()

    def test_list_anonymous(self):
        """Test the Telemetry API listing"""
        response = self.client.get('/api/telemetry/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        """Test the Telemetry API retrieval"""
        response = self.client.get('/api/telemetry/{0}/'.format(self.datum.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post(self):
        """Test the network posting capability"""
        norad = self.satellite.satellite_entry.norad_cat_id

        data = {
            'frame': self.frame,
            'locator': 'longLat',
            'latitude': '06.12S',
            'longitude': '59.34W',
            'noradID': str(norad),
            'source': 'T3ST',
            'timestamp': '2021-03-15T13:14:04.940Z',
            'version': '1.2.3',
            'observation_id': '123456789',
            'satnogs_network': 'true',
            'station_id': '2'
        }
        response = self.client.post('/api/telemetry/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_numerical_latlng(self):
        """Test the SiDS posting capability without a N/S and E/W identifier"""
        norad = self.satellite.satellite_entry.norad_cat_id

        data = {
            'frame': self.frame,
            'locator': 'longLat',
            'latitude': '06.12',
            'longitude': '59.34',
            'noradID': str(norad),
            'source': 'T3ST',
            'timestamp': '2021-03-15T13:14:04.940Z'
        }
        response = self.client.post('/api/telemetry/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_new_satellite(self):
        """Test the SiDS posting capability while creating a new satellite"""

        data = {
            'frame': self.frame,
            'locator': 'longLat',
            'latitude': '06.12S',
            'longitude': '59.34W',
            'noradID': '999999',
            'source': 'T3ST',
            'timestamp': '2021-03-15T13:14:04.940Z',
            'version': '1.2.3'
        }
        response = self.client.post('/api/telemetry/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_bad_new_satellite(self):
        """Test the SiDS upload while creating a new satellite with bad NORAD"""

        data = {
            'frame': self.frame,
            'locator': 'longLat',
            'latitude': '06.12S',
            'longitude': '59.34W',
            'noradID': 'STR999999',
            'source': 'T3ST',
            'timestamp': '2021-03-15T13:14:04.940Z',
            'version': '1.2.3'
        }
        response = self.client.post('/api/telemetry/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_post(self):
        """Test the SiDS posting capability with bad data"""
        norad = self.satellite.satellite_entry.norad_cat_id

        data = {
            'frame': '',
            'locator': 'longLat',
            'latitude': '206.12S',
            'longitude': '59.34WE',
            'noradID': str(norad),
            'source': '',
            'timestamp': ''
        }
        response = self.client.post('/api/telemetry/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db(transaction=True)
class LoginView(TestCase):
    """
    Tests various API endpoints with authentication
    """
    datum = None

    def setUp(self):
        DemodDataFactory.create_batch(size=18)
        self.datum = DemodDataFactory()
        self.datum.save()
        self.client.force_login(User.objects.get_or_create(username='testuser')[0])

    def test_auth_telemetry_list_without_filter(self):
        """Test the Telemetry API listing and pagination with authentication"""
        response = self.client.get('/api/telemetry/?page=1')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth_telemetry_list_with_satellite_filter(self):
        """Test the Telemetry API listing and pagination with authentication"""
        norad_id = self.datum.satellite.satellite_entry.norad_cat_id
        response = self.client.get('/api/telemetry/?page=1&satellite=' + str(norad_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_telemetry_list_with_sat_id_filter(self):
        """Test the Telemetry API listing and pagination with authentication"""
        sat_id = self.datum.satellite.satellite_identifier.sat_id
        response = self.client.get('/api/telemetry/?page=1&sat_id=' + sat_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db(transaction=True)
class OpticalObservationView(TestCase):
    """
    Tests the OpticalObservationViewSet
    """

    def setUp(self):
        self.satellite = SatelliteFactory()
        self.satellite.save()
        self.data_contents = {
            "site_id": 12345,
            "latitude": 52.8344,
            "longitude": 6.3785,
            "height": 10.0,
            "observer": "Test Observer",
            "start": "2023-01-19T17:48:40.145",
            "exptime": 9.885658979415894,
            "teststring": "testme",
            "satellites": [
                {
                    "satno": self.satellite.satellite_entry.norad_cat_id,
                    "cospar": "20 038Q",
                    "tlefile": "starlink.tle",
                    "catalogname": "starlink",
                    "measurements": [
                        {
                            "time": "2023-01-19T17:48:40.595",
                            "ra": 31.801019053449075,
                            "dec": 4.145373899094505,
                            "drxdt": 0.4770998044346823,
                            "drydt": 0.18227470853764619
                        }
                    ],
                    "iod_lines": [
                        "45744 20 038Q   4171 G 20230119174840595 17 25 0207204+040872 37 S"
                    ]
                }, {
                    "satno": 90909,
                    "cospar": "20 019BA",
                    "tlefile": "starlink.tle",
                    "catalogname": "starlink",
                    "measurements": [
                        {
                            "time": "2023-01-19T17:48:40.595",
                            "ra": 26.965978594291723,
                            "dec": 2.2683156734867644,
                            "drxdt": 0.4711258931653056,
                            "drydt": -0.174851943865609
                        }
                    ],
                    "iod_lines": [
                        "45408 20 019BA  4171 G 20230119174840595 17 25 0147864+021610 37 S"
                    ]
                }
            ]
        }

        with open('test.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.data_contents, json_file, indent=4)
        self.diagnostic_plot = BytesIO(
            b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00"
            b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00"
        )
        self.diagnostic_plot.name = "testimage.gif"
        user = User.objects.create(username='testuser')
        token = get_api_token(user)
        self.headers = {"HTTP_AUTHORIZATION": f"Token {token}"}

    def test_create_observation(self):
        """Test the creation of an observation and the respective identifications"""
        with open("test.json", "rb") as test_data:
            response = self.client.post(
                '/api/optical-observations/', {
                    "data": test_data,
                    "diagnostic_plot": self.diagnostic_plot
                }, **self.headers
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(OpticalObservation.objects.all().count(), 1)
            self.assertEqual(OpticalIdentification.objects.all().count(), 2)
            identifications = OpticalIdentification.objects.all()
            self.assertEqual(identifications[0].satellite.id, self.satellite.id)
            self.assertEqual(identifications[1].satellite, None)

            self.diagnostic_plot.seek(0)
        with open("test.json", "rb") as test_data:
            response2 = self.client.post(
                '/api/optical-observations/', {
                    "data": test_data,
                    "diagnostic_plot": self.diagnostic_plot
                }, **self.headers
            )
            self.assertEqual(response2.status_code, 403)
            self.assertContains(
                response2,
                "Observation with the same start time and station_id already exists",
                status_code=403
            )

    def tearDown(self):
        os.remove("test.json")
