# GMail

## Reading Messages
```python
from googly import GMailAPI
api = GMailAPI()

threads = api.get_threads()
```

This method returns a dictionary, where the keys are `threadId`s and the values are lists of [Messages](https://developers.google.com/gmail/api/reference/rest/v1/users.messages). You can also iterate over the messages directly (without the threading) using the `get_messages()` method.
