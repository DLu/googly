import googly

BASIC_FIELDS = ['names', 'emailAddresses', 'phoneNumbers']


class PeopleAPI(googly.API):
    # https://developers.google.com/people/v1/contacts

    class Scope(googly.Scope):
        CONTACTS = 1
        CONTACTS_OTHER_READONLY = 2

    def __init__(self, scopes=Scope.all(), **kwargs):
        googly.API.__init__(self, 'people', 'v1', scopes, **kwargs)

    def get_contact_list(self, fields=BASIC_FIELDS, limit=0, sortOrder='LAST_MODIFIED_DESCENDING'):
        yield from self.get_paged_result(
            self.service.people().connections().list,
            'connections',
            max_results=limit,
            resourceName='people/me',
            sortOrder=sortOrder,
            personFields=','.join(fields)
        )

    def get_other_contacts(self, fields=BASIC_FIELDS, limit=0):
        yield from self.get_paged_result(
            self.service.otherContacts().list,
            'otherContacts',
            max_results=limit,
            readMask=','.join(fields),
        )
