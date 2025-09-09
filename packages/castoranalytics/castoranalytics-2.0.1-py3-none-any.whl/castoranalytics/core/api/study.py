class Study:
    def __init__(self, study_data):
        self._study_data = study_data

    def get_id(self):
        return self._study_data['study_id']

    def get_name(self):
        return self._study_data['name']
    
    def get_created_on(self):
        return self._study_data['created_on']
    
    def __str__(self):
        return 'Study(id={}, name={}, created_on={})'.format(
            self.get_id(),
            self.get_name(),
            self.get_created_on(),
        )