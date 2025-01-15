# GMail

## Getting Label Names
```python
from googly import GMailAPI
api = GMailAPI()

for label in api.get_labels():
    print('{type:7} label: id={id:30} name={name}'.format(**label))
```

`get_labels` returns [Label objects](https://developers.google.com/gmail/api/reference/rest/v1/users.labels#Label), although only some fields are returned, namely:
 * `id`
 * `name`
 * `messageListVisibility`
 * `labelListVisibility`
 * `type`
 * `color` (in practice, though not according to the spec)

If you explicitly call `get_label` with the `id` returned above, it will return the other fields, including
 * `messagesTotal`
 * `messagesUnread`
 * `threadsTotal`
 * `threadsUnread`
 * `color`

## Reading Messages
```python
from googly import GMailAPI
api = GMailAPI()

threads = api.get_threads()
```

This method returns a dictionary, where the keys are `threadId`s and the values are lists of [Messages](https://developers.google.com/gmail/api/reference/rest/v1/users.messages). You can also iterate over the messages directly (without the threading) using the `get_messages()` method.

Alternatively, you can also use `get_message` to control more precisely what information you want retrieved on a per-message basis by setting the [`msg_format` argument](https://developers.google.com/gmail/api/reference/rest/v1/Format).

There also is functionality to retrieve attachments with `get_attachment`.

## Modify Labels
To modify the labels for a message, you need
 * The message id
 * The ids of the labels you want to add
 * The ids of the labels you want to remove

```python
from googly import GMailAPI
api = GMailAPI()

# Find msg id

# Add the awesome label
label_ids = [label['id'] for label in api.get_labels()
             if label['name'] == 'Awesome']
api.modify_labels(msg_id,
                  label_ids_to_add=label_ids,
                  label_ids_to_remove=[])
```

## Sending Emails
```python
from googly import GMailAPI
api = GMailAPI()
api.send_email('Greetings', 'Hello World', 'test@gmail.com')
```
The three arguments here are
 * Subject (a string)
 * Body (a string)
 * Recipient address (a string, or a list of strings for multiple recipients)

There are additional arguments for other common functionality.

### Additional Addresses
```python
api.send_email('Greetings', 'Hello World',
               send_to='test@gmail.com',
               cc='test2@gmail.com',
               bcc='test3@gmail.com',
               send_from='Strong Bad <strongbad@gmail.com>')
```

 * `send_to`, `cc` and `bcc` can be lists
 * Any of the addresses (notably `send_from`) can be specified with a name and [the email address in angle brackets](https://stackoverflow.com/a/4473881) (`<` and `>`). This sets the display name for each email address.
 * If you try any funny business where you send from an email address that is not your own, no nickname will be sent, and the sender will just be your email address.

### Attachments
```python
api.send_email('The Presentation', 'Here is that file',
               'test@gmail.com',
               files=['SalesFigures.ppt'])
```
(assumes each file contains the path to that file on the local filesystem)

### HTML Email
```python
api.send_email('Greetings', 'Hello <b>World</b>',
               'test@gmail.com', html=True)
```

### Email with inline images
```python
api.send_email('Email with Image',
               'Look here - <img src="cid:picture.gif"/>',
               'to@gmail.com',
               html=True,
               images={'picture.gif': 'path/to/local/image.gif'}
               )
```
 * In order to send an inline image, you must use `html=True`
 * In the body's html, we use a [special](http://www.faqs.org/rfcs/rfc1873.html) `src` attribute for the image, where we specify the content ID with the `cid:` prefix and then some string.
 * We then specify which image maps to that id with a dictionary.
