from googly import PeopleAPI
from creds import get_credentials
import pytest


def test_basic_access():
    api = PeopleAPI(**get_credentials())

    contacts = list(api.get_contact_list())

    assert len(contacts) == 1
    rick = contacts[0]
    name = rick['names'][0]
    assert name['givenName'] == 'Rick'
    assert name['familyName'] == 'Roll'

    email = rick['emailAddresses'][0]
    assert email['value'] == 'never@gonnagiveyou.up'

    phones = rick['phoneNumbers']
    assert len(phones) == 2
    canonicals = [d['canonicalForm'] for d in phones]
    assert '+12484345508' in canonicals
    assert '+12263361437' in canonicals

    other_contacts = list(api.get_other_contacts())
    assert other_contacts

    for contact in other_contacts:
        if contact['resourceName'] != 'otherContacts/c7856614118042321724':
            continue
        assert contact['names'][0]['displayName'] == 'David Lu!!'
        assert contact['emailAddresses'][0]['value'] == 'davidvlu@gmail.com'


def test_search_and_edit():
    api = PeopleAPI(**get_credentials())

    people = list(api.search_contacts('Rick'))
    assert len(people) == 1

    rick = people[0]
    emails = rick['emailAddresses']
    assert len(emails) == 1

    # Edit
    emails.append({'value': 'never@gonnaletyou.down'})
    api.update_contact(rick['resourceName'], rick['etag'],
                       emailAddresses=emails)

    # Check
    rick = list(api.search_contacts('never@gonnagiveyou.up'))[0]
    emails = rick['emailAddresses']
    assert len(emails) == 2

    # Edit
    emails = emails[:1]
    api.update_contact(rick['resourceName'], rick['etag'],
                       emailAddresses=emails)

    # Check
    rick = list(api.search_contacts('Rick'))[0]
    emails = rick['emailAddresses']
    assert len(emails) == 1

    # Edit badly
    with pytest.raises(RuntimeError):
        api.update_contact(rick['resourceName'], rick['etag'],
                           email_addys=emails)
