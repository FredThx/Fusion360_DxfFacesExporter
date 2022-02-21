import adsk.core


class MyFusion360:
    '''Mes utilitaires Fusion 360
    '''
    #https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-b8af2def-f673-4cd4-baec-3c9912059547
    languages = {
        0 : 'zh', # Peoples Republic of China Chinese
        1 : 'zh', #Taiwan Chinese
        2 : 'cs', #	Czech
        3 : 'en', #	English
        4 : 'fr', #	French
        5 : 'de', #	German
        6 : 'hu', #	Hungarian
        7 : 'it', #	Italian
        8 : 'ja', #	Japanese
    	9 : 'ko', #	Korean
        10 : 'pl', # Polish
        11 : 'pt', # Brazilian Portuguese
        12 : 'ru', # Russian
        13 : 'es', # Spanish
    }

    def __init__(self):
        self.app = adsk.core.Application.get()

    def get_language(self):
        return self.languages[self.app.preferences.generalPreferences.userLanguage]