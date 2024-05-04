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

## Searching Contacts
```python
from googly import PeopleAPI
api = PeopleAPI()
for contact in api.search_contacts('someone@gmail.com'):
    print(contact)
```
Can also set `fields` in the search.

## Listing "Other" Contacts
These are all the contacts that the user hasn't added to their address book, but have still been interacted with. Has the same `fields` parameter as above.

```python
from googly import PeopleAPI

api = PeopleAPI()
for contact in api.get_other_contacts():
    print(contact)
```

## Move from "Other" to Main
This promotes ALL of the other contacts to be in the main contacts list.

```python
from googly import PeopleAPI

api = PeopleAPI()
for contact in api.get_other_contacts(fields=['resourceName']):
    api.add_other_to_my_contacts(contact['resourceName'])
```

## Update Contact Information
```python
from googly import PeopleAPI

api = PeopleAPI()
contact = api.search_contacts('someone@gmail.com')[0]
emails = contact['emailAddresses']
emails.append({'value': 'someone@yahoo.com'})
api.update_contact(contact['resourceName'], contact['etag'], emailAddresses=emails)
```

To update a contact, you need two distinct pieces of identification, the `resourceName` and the `etag`. The fields that you want to update are specified as keyword arguments, with the same structure that are returned from `get_contact_list` and `search_contacts`.
