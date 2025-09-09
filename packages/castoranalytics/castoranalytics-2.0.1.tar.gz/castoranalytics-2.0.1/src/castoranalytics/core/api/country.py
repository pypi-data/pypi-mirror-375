class Country:
    def __init__(self, country_data):
        self._country_data = country_data

    def get_id(self):
        return int(self._country_data['country_id'])
    
    def get_name(self):
        return self._country_data['country_name']
    
    def get_tld_code(self):
        return self._country_data['country_tld']

    def get_two_digit_code(self):
        return self._country_data['country_cca2']
    
    def get_three_digit_code(self):
        return self._country_data['country_cca3']