class CountryCodes:
    def __init__(self):
        self._codes = {}

    def add_country(self, country):
        self._codes[country.get_id()] = {
            'tld': country.get_tld_code(),
            'two_digit': country.get_two_digit_code(),
            'three_digit': country.get_three_digit_code(),
        }

    def get_tld_for(self, country_id):
        return self._codes[country_id]['tld']
    
    def get_two_digit_code_for(self, country_id):
        return self._codes[country_id]['two_digit']
    
    def get_three_digit_code_for(self, country_id):
        return self._codes[country_id]['three_digit']
    
    def __str__(self):
        return f'CountryCodes(codes={self._codes})'