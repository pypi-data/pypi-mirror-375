# Python Library for helping to create Python services from Google APIs

Something I have to do a lot is create connections to Google Service
endpoints. This generally requires a fair amount of boiler-plate code that io
just copied and pasted from other locations. Also any time a new service is
needed, I need to find that specific implementation of the service builder and
add the new endpoint.

Obviously this can lead to potential errors and if a bug is found, I have to
remember where I created these services and fix it in many projects.

This has led me to create a small helper library to make the process easier.
Included in the library is a complete and updated (at time of publishing) list
of all the Google APIs along with their versions and endpoints as `Enum`s
ready for use.

## Usage

`service_builder.build_service()` needs two mandatory pieces of information:

| Parameter | Type | Description |
| :-: | - | - |
| key | str | The credentials to use to authenticate the user to the service it has to create. |
| service | Service | The Google API endpoint it is trying to connect to. |
| api_key | _See below_ | _Optional_ An API key for those services which require an API key in addition to credentials. |
| extra_scopes | List[str] | _Optional_ Extra OAuth scopes needed. |

### `key`

These can be supplied in one of 4 ways.

1. A valid `google.oauth2.Credentials` object, created and passed to the
   service builder.
1. A `str` which is the name of a local file containing the `json`
   representation of an OAuth credentials object.
1. A `Mapping` object which is a `json` keyfile `dict`
2. An `OAuthKey` object from this package, which is a `dataclass` object
   comprising of the minimum fields necessary to perform the OAuth connection.

### `service`

This is an Enum in the `service_framework.service` module, which defines
the Google service you're planning to connect to. All the standard Google
services are included (as of the date listed in the `Services.py` file).

If a
new service has been added but this library has yet to be updated, you can
request it by using either `Service('<UNLISTED SERVICE>')` or
`Service.from_value('<UNLISTED SERVICE>')`. This will cause the library to
attempt to fetch the service's definition from Google and will create an
entry in the enum for this new service.

### Examples

#### 1. Using `Credentials`
```
from service_framework.services import Service
from service_framework import service_builder
from google.oauth2 import credentials as oauth

credentials = oauth.Credentials(
   access_token="<YOUR ACCESS TOKEN>",
   refresh_token="<YOUR REFRESH TOKEN>",
   token_uri="https://oauth2.googleapis.com/token",
   client_id="<YOUR CLIENT ID>",
   client_secret="<YOUR CLIENT SECRET>"
)

service = service_builder.build_service(service=Service.CHAT, key=credentials)
```

#### 2. Using an `OAuthKey`
```
from service_framework.services import Service
from service_framework import service_builder

key = service_builder.OAuthKey(
   access_token="<YOUR ACCESS TOKEN>",
   refresh_token="<YOUR REFRESH TOKEN>",
   token_uri="https://oauth2.googleapis.com/token",
   client_id="<YOUR CLIENT ID>",
   client_secret="<YOUR CLIENT SECRET>"
)

service = service_builder.build_service(service=Service.GMAIL, key=key)
```

Here, we are creating the key as an `OAuthKey` object as we have clearly got the
tokens and client_[id|secret] from elsewhere. Creating the service is then as
simple as invoking the `service_builder.build_service` method which will return
you a service you can use.
