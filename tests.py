from TransferGuide.views import generateURL
def test():
    assert 1 == 1

def testGenerateURL():
    testUrl =generateURL("1228","Horton","CS")
    realUrl = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1238&instructor=Horton&subject=CS&'
    assert(testUrl==realUrl)