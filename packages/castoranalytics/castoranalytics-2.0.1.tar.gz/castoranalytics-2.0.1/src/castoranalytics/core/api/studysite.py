class StudySite:
    def __init__(self, study_site_data):
        self._study_site_data = study_site_data

    def get_id(self):
        return self._study_site_data['site_id']
    
    def get_name(self):
        return self._study_site_data['name']

    def get_abbreviation(self):
        return self._study_site_data['abbreviation']

    def get_country_id(self):
        return self._study_site_data['country_id']
    
    def get_country_code(self):
        return self._study_site_data['country_code']

    def get_nr_records(self):
        return self._study_site_data['nr_records']

    def get_completion_percentage(self):
        return int(round(self._study_site_data['completion_percentage'], 0))
    
    def __str__(self):
        return 'StudySite(name={}, abbreviation={}, country_id={}, country_code={}, nr_records={}, completion_percentage={})'.format(
            self.get_name(),
            self.get_abbreviation(),
            self.get_country_id(),
            self.get_country_code(), 
            self.get_nr_records(),
            self.get_completion_percentage(),
        )