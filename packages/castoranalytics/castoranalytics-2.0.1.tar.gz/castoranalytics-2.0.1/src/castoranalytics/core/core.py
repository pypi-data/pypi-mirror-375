import json
import threading

from concurrent.futures import ThreadPoolExecutor

from castoranalytics.core.singleton import singleton
from castoranalytics.core.api.study import Study
from castoranalytics.core.api.studydetails import StudyDetails
from castoranalytics.core.api.studysite import StudySite
from castoranalytics.core.api.country import Country
from castoranalytics.core.api.countrycodes import CountryCodes
from castoranalytics.core.logging import LogManager
from castoranalytics.core.cache import Cache
from castoranalytics.core.api.castorapiclient import CastorApiClient
from castoranalytics.core.utils import current_time_in_seconds, elapsed_time_in_seconds

LOG = LogManager()


@singleton
class Core:
    def __init__(self, client_id, client_secret, token_url, api_base_url):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._api_base_url = api_base_url
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._callbacks_lock = threading.Lock()
        self._callbacks = {}
        self._cache = Cache()

    # HELPERS

    def ready(self):
        return self._client_id is not None and self._client_secret is not None and self._token_url is not None and self._api_base_url is not None
    
    def set_api_credentials(self, client_id, client_secret, token_url, api_base_url):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._api_base_url = api_base_url
    
    def read_from_cache(self, name):
        return self._cache.get(name)
    
    def write_to_cache(self, name, value):
        self._cache.set(name, value)

    # COUNTRIES
    
    def get_countries(self):
        start_time = current_time_in_seconds()
        countries = self.read_from_cache('countries')
        if countries:
            # LOG.info(f'Core.get_countries(): {elapsed_time_in_seconds(start_time)}')
            return countries
        with CastorApiClient(self._client_id, self._client_secret, self._token_url, self._api_base_url) as client:
            countries = []
            for country_data in client.get_countries():
                countries.append(Country(country_data))
            self.write_to_cache('countries', countries)
            LOG.info(f'Core.get_countries(): {elapsed_time_in_seconds(start_time)}')
            return countries
        
    def get_country_codes(self):
        start_time = current_time_in_seconds()
        country_codes = self.read_from_cache('country_codes')
        if country_codes:
            # LOG.info(f'Core.get_country_codes(): {elapsed_time_in_seconds(start_time)}')
            return country_codes
        countries = self.get_countries()
        country_codes = CountryCodes()
        for country in countries:
            country_codes.add_country(country)
        self.write_to_cache('country_codes', country_codes)
        LOG.info(f'Core.get_country_codes(): {elapsed_time_in_seconds(start_time)}')
        return country_codes
    
    # STUDIES

    def get_studies(self):
        start_time = current_time_in_seconds()
        studies = self.read_from_cache('studies')
        if studies:
            # LOG.info(f'Core.get_studies(): {elapsed_time_in_seconds(start_time)}')
            return studies
        with CastorApiClient(self._client_id, self._client_secret, self._token_url, self._api_base_url) as client:
            studies = []
            for study_data in client.get_studies():
                studies.append(Study(study_data))
            self.write_to_cache('studies', studies)
            LOG.info(f'Core.get_studies(): {elapsed_time_in_seconds(start_time)}')
            return studies
        
    def get_study(self, study_id):
        start_time = current_time_in_seconds()
        study = self.read_from_cache(f'studies/{study_id}')
        if study:
            # LOG.info(f'Core.get_study(): {elapsed_time_in_seconds(start_time)}')
            return study
        with CastorApiClient(self._client_id, self._client_secret, self._token_url, self._api_base_url) as client:
            study_data = client.get_study(study_id)
            study_statistics = client.get_statistics(study_id)
            fields = client.get_fields(study_id)
            study_data['nr_sites'] = client.get_number_of_sites(study_id)
            study_data['nr_participants'] = study_statistics['records']['total_count']
            study_data['nr_fields'] = len(fields)
            study = StudyDetails(study_data)
            self.write_to_cache(f'studies/{study_id}', study)
            LOG.info(f'Core.get_study(): {elapsed_time_in_seconds(start_time)}')
            return study
        
    # SITES

    def get_participant_site_abbreviations(self, participants):
        site_abbreviations = {}
        for participant in participants:
            site_abbreviations[participant['participant_id']] = participant['_embedded']['site']['abbreviation']
        return site_abbreviations
    
    def get_nr_records_per_site(self, participant_progress, participant_site_abbreviations):
        nr_records_per_site = {}
        for item in participant_progress:
            site_abbreviation = participant_site_abbreviations[item['participant_id']]
            if site_abbreviation not in nr_records_per_site.keys():
                nr_records_per_site[site_abbreviation] = 0
            nr_records_per_site[site_abbreviation] += 1
        return nr_records_per_site
    
    def get_completion_percentages_per_site(self, participant_progress, participant_site_abbreviations):
        completion_percentages_per_site = {}
        for item in participant_progress:
            site_abbreviation = participant_site_abbreviations[item['participant_id']]
            if site_abbreviation not in completion_percentages_per_site.keys():
                completion_percentages_per_site[site_abbreviation] = 0
            cummulative_progress = 0
            for form in item['forms']:
                cummulative_progress += int(form['progress'])
            completion_percentage = cummulative_progress / float(len(item['forms']))
            completion_percentages_per_site[site_abbreviation] += completion_percentage
        return completion_percentages_per_site
        
    def update_nr_records(self, site_abbreviation, nr_records_per_site):
        nr_records = 0
        if site_abbreviation in nr_records_per_site.keys():
            nr_records = nr_records_per_site[site_abbreviation]
        return nr_records
    
    def update_completion_percentage(self, site_, nr_records, completion_rates_per_site):
        completion_rate = 0.0
        if site_ in completion_rates_per_site.keys():
            completion_rate = float(completion_rates_per_site[site_] / float(nr_records)) if nr_records > 0 else 0.0
        return completion_rate
    
    def update_country_code(self, country_id):
        country_codes = self.get_country_codes()
        return country_codes.get_three_digit_code_for(country_id)

    def get_study_sites(self, study_id):
        start_time = current_time_in_seconds()
        study_sites = self.read_from_cache(f'studies/{study_id}/sites')
        if study_sites:
            # LOG.info(f'Core.get_study_sites(): {elapsed_time_in_seconds(start_time)}')
            return study_sites
        with CastorApiClient(self._client_id, self._client_secret, self._token_url, self._api_base_url) as client:

            start_time2 = current_time_in_seconds()
            study_sites_data = client.get_study_sites(study_id)
            LOG.info(f'Core.get_study_sites() client.get_study_sites(): {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            participants = client.get_participants(study_id)
            LOG.info(f'Core.get_study_sites() client.get_participants(): {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            participant_site_abbreviations = self.get_participant_site_abbreviations(participants)
            LOG.info(f'Core.get_study_sites() client.get_participant_site_abbreviations(): {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            participant_progress = client.get_participant_progress(study_id)
            LOG.info(f'Core.get_study_sites() client.get_participant_progress(): {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            nr_records_per_site = self.get_nr_records_per_site(participant_progress, participant_site_abbreviations)
            LOG.info(f'Core.get_study_sites() calculate nr. records per site: {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            completion_percentages_per_site = self.get_completion_percentages_per_site(participant_progress, participant_site_abbreviations)
            LOG.info(f'Core.get_study_sites() calculate completion percentages per site: {elapsed_time_in_seconds(start_time2)}')

            start_time2 = current_time_in_seconds()
            for study_site_data in study_sites_data:
                study_site_data['nr_records'] = self.update_nr_records(study_site_data['abbreviation'], nr_records_per_site)
                study_site_data['completion_percentage'] = self.update_completion_percentage(study_site_data['abbreviation'], study_site_data['nr_records'], completion_percentages_per_site)
                study_site_data['country_code'] = self.update_country_code(study_site_data['country_id'])
            LOG.info(f'Core.get_study_sites() site info updated: {elapsed_time_in_seconds(start_time2)}')

            study_sites = []
            for study_site_data in study_sites_data:
                study_site = StudySite(study_site_data)
                study_sites.append(study_site)

            self.write_to_cache(f'studies/{study_id}/sites', study_sites)
            LOG.info(f'Core.get_study_sites() elapsed: {elapsed_time_in_seconds(start_time)}')
            return study_sites    
        
    # ASYNCHRONOUS METHODS
        
    def get_countries_async(self, callback):
        self.run_background_task(self.get_countries, callback)

    def get_studies_async(self, callback):
        self.run_background_task(self.get_studies, callback)

    def get_study_async(self, callback, *args):
        self.run_background_task(self.get_study, callback, *args)

    def get_study_sites_async(self, callback, *args):
        self.run_background_task(self.get_study_sites, callback, *args)

    # HELPERS

    def run_background_task(self, func, callback, *args, **kwargs):
        future = self._executor.submit(func, *args, **kwargs)
        with self._callbacks_lock:
            self._callbacks[future] = callback
        future.add_done_callback(self.handle_task_done)

    def handle_task_done(self, future):
        result, error = None, None
        try:
            result = future.result()
        except Exception as e:
            error = e
        with self._callbacks_lock:
            callback = self._callbacks.pop(future, None)
        if callback:
            callback(result, error)