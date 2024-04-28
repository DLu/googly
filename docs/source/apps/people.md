# Google People

Commonly referred to as "Contacts"

## Listing Contacts

```python
from googly import PeopleAPI

api = PeopleAPI()
for contact in api.get_contact_list():
    print(contact)
```

This method returns [Person objects](https://developers.google.com/people/api/rest/v1/people#Person). By default, names, emails and phone numbers are returned. These can be overridden with the `fields` parameter, with values from [personFields](https://developers.google.com/people/api/rest/v1/people.connections/list#query-parameters). You can also modify the [`sortOrder`](https://developers.google.com/people/api/rest/v1/people.connections/list#SortOrder).

## Listing "Other" Contacts
These are all the contacts that the user hasn't added to their address book, but have still been interacted with. Has the same `fields` parameter as above.

```python
from googly import PeopleAPI

api = PeopleAPI()
for contact in api.get_other_contacts():
    print(contact)
```
