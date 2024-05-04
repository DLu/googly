import googly

BASIC_FIELDS = ['names', 'emailAddresses', 'phoneNumbers']
FIELDS = ['addresses', 'birthdays', 'emailAddresses', 'metadata', 'names', 'nicknames', 'phoneNumbers']


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

    def search_contacts(self, query, fields=BASIC_FIELDS, limit=10):
        assert limit != 0 and limit <= 30, 'Limit must be > 0 and <= 30'
        ret = self.service.people().searchContacts(
            query=query,
            pageSize=limit,
            readMask=','.join(fields)
        ).execute()
        return [result['person'] for result in ret['results']]

    def get_other_contacts(self, fields=BASIC_FIELDS, limit=0):
        yield from self.get_paged_result(
            self.service.otherContacts().list,
            'otherContacts',
            max_results=limit,
            readMask=','.join(fields),
        )

    def add_other_to_my_contacts(self, resourceName, fields=BASIC_FIELDS):
        self.service.copyOtherContactToMyContactsGroup(resourceName=resourceName, copyMask=','.join(fields))

    def update_contact(self, resourceName, eTag, check_fields=True,
                       **kwargs):
        body = {
            'etag': eTag
        }
        fields = []
        for field, v in kwargs.items():
            if check_fields and field not in FIELDS:
                raise RuntimeError(f'update_contact called with odd field: {field}')

            fields.append(field)
            body[field] = v

        self.service.people().updateContact(
            resourceName=resourceName,
            updatePersonFields=','.join(fields),
            body=body,
        ).execute()
