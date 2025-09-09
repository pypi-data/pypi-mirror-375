from castoranalytics.core.api.study import Study


class StudyDetails(Study):
    def __init__(self, study_data):
        super(StudyDetails, self).__init__(study_data)

    def get_nr_sites(self):
        return self._study_data['nr_sites']

    def get_nr_participants(self):
        return self._study_data['nr_participants']

    def get_nr_fields(self):
        return self._study_data['nr_fields']
    
    def __str__(self):
        return 'StudyDetails(id={}, name={}, created_on={}, nr_sites={}, nr_participants={}, nr_fields={})'.format(
            self.get_id(),
            self.get_name(),
            self.get_created_on(),
            self.get_nr_sites(),
            self.get_nr_participants(),
            self.get_nr_fields(),
        )