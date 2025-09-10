import requests
from typing import List, Optional, Callable, Any


from .models import User, Template, Gift, Campaign, CardResponse, CardsResponse, CampaignResponse, CampaignMultiResponse, Card, Contact, Mailing, CreditTransaction
from . import exceptions
from . import __helpers as helpers


DOMAIN = 'https://amcards.com'

FIXED_COUNTRY = {
    # US fixes
    'USA': 'US', 'UNITED STATES': 'US', 'UNITED STATES OF AMERICA': 'US', 'THE UNITED STATES OF AMERICA': 'US', 'AMERICA': 'US',
    # GB fixes
    'ENGLAND': 'GB',
}


class AMcardsClient:
    """Client for AMcards API."""
    def __init__(self, access_token: str, oauth_config: Optional[dict] = None, callback: Optional[Callable[[str, str, int], Any]] = None) -> None:
        """Client for AMcards API.

        :param str access_token: Your AMcards access token. Generate one `here <https://amcards.com/user/generate-access-token/>`_.
        :param Optional[dict] oauth_config: Your OAuth configuration, this is optional, but if you choose to include it, it must include all of the following keys:

            .. code-block::

                {
                    'refresh_token': 'yourrefreshtoken',
                    'expiration': 1671692131130,                    # Note that expiration is specified as a unix timestamp in ms.
                    'client_id': 'yourapplicationclientid',
                    'client_secret': 'yourapplicationclientsecret'
                }

        :param Optional[Callable[[str, str, int], Any]] callback: This function will be called by the client when you have ``oauth_config`` defined, and the client refreshes the ``access_token`` before making a request. This can be useful when you need perform some logic when the client refreshes the specified ``access_token`` (like updating your database to reflect the new access_token and refresh_token). ``callback`` is optional, but if you choose to include it, it needs to accept the following keyword arguments: ``access_token`` ``refresh_token`` ``expiration``. ``callback`` will be called by the client as follows: ``callback(access_token='newaccesstoken', refresh_token='newrefreshtoken', expiration=1671692135130)``, note that ``expiration`` is specified as a unix timestamp in ms.

        """
        self._access_token = access_token
        self._oauth_config = oauth_config
        self._callback = callback

    def _token_expired(self) -> bool:
        return self._oauth_config is not None and helpers.current_timestamp() >= self._oauth_config['expiration']

    def _refresh_token(self) -> None:
        # Refresh the tokens
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self._oauth_config['refresh_token'],
            'client_id': self._oauth_config['client_id'],
            'client_secret': self._oauth_config['client_secret'],
        }
        res = requests.post(url=f'{DOMAIN}/oauth2/token/', data=payload)

        # Make sure the refresh was successful
        if not res.ok:
            raise exceptions.OAuthTokenRefreshError('Something went wrong when attempting to refresh AMcards access_token')

        # Update the access_token, refresh_token, and expiration
        res_json = res.json()
        self._access_token = res_json['access_token']
        self._oauth_config['refresh_token'] = res_json['refresh_token']
        self._oauth_config['expiration'] = helpers.current_timestamp() + res_json['expires_in'] * 1000

        # If specified, call the callback
        if self._callback is not None:
            self._callback(
                access_token=self._access_token,
                refresh_token=self._oauth_config['refresh_token'],
                expiration=self._oauth_config['expiration'],
            )

    @property
    def _HEADERS(self) -> dict:
        if self._token_expired():
            self._refresh_token()

        return {
            'Authorization': f'Bearer {self._access_token}',
        }

    def user(self) -> User:
        """Fetches client's AMcards user.

        :return: The client's :py:class:`user <amcards.models.User>`.
        :rtype: :py:class:`User <amcards.models.User>`

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/user/', headers=self._HEADERS)
        if not res.ok:
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        user_json = res.json().get('objects', [{}])[0]
        return User._from_json(user_json)

    def credit_transactions(self, limit: int = 25, skip: int = 0, filters: dict = None) -> List[CreditTransaction]:
        """Fetches client's AMcards credit transactions.

        :param int limit: Defaults to ``25``. Max number of credit transactions to be fetched.
        :param int skip: Defaults to ``0``. Number of credit transactions to be skipped.
        :param Optional[dict] filters: Defaults to ``None``. Filters to be applied when fetching credit transactions.

            A common use case is to use ``filter = {'amount_paid_int__gt': 0}``, this will count all credit transactions that have ``amount_paid > 0``.

        :return: The client's :py:class:`credit transactions <amcards.models.CreditTransaction>`.
        :rtype: List[:py:class:`CreditTransaction <amcards.models.CreditTransaction>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        params = {
            'limit': limit,
            'offset': skip,
        } | (filters or {})

        res = requests.get(url=f'{DOMAIN}/.api/v1/credittransaction/', headers=self._HEADERS, params=params)
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching credit transactions. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        credit_transactions_json = res.json().get('objects', [])
        return [CreditTransaction._from_json(credit_transaction_json) for credit_transaction_json in credit_transactions_json]

    def credit_transaction_count(self, filters: dict = None) -> int:
        """Fetches count of client's AMcards credit transactions.

        :param Optional[dict] filters: Defaults to ``None``. Filters to be applied when counting credit transactions.

            A common use case is to use ``filter = {'amount_paid_int__gt': 0}``, this will count all credit transactions that have ``amount_paid > 0``.

        :return: The count of client's credit transactions.
        :rtype: int

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        params = {
            'limit': 1,
        } | (filters or {})

        res = requests.get(url=f'{DOMAIN}/.api/v1/credittransaction/', headers=self._HEADERS, params=params)
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching credit transaction count. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        return res.json()['meta']['total_count']

    def templates(self, limit: int = 25, skip: int = 0) -> List[Template]:
        """Fetches client's AMcards templates.

        :param int limit: Defaults to ``25``. Max number of templates to be fetched.
        :param int skip: Defaults to ``0``. Number of templates to be skipped.

        :return: The client's :py:class:`templates <amcards.models.Template>`.
        :rtype: List[:py:class:`Template <amcards.models.Template>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/template/', headers=self._HEADERS, params={'limit': limit, 'offset': skip})
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching templates. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        templates_json = res.json().get('objects', [])
        return [Template._from_json(template_json) for template_json in templates_json]

    def template(self, id: str | int) -> Template:
        """Fetches client's AMcards template with a specified id.

        :param str or int id: Unique id for the :py:class:`template <amcards.models.Template>` you are fetching.

        :return: The client's :py:class:`template <amcards.models.Template>` with specified ``id``.
        :rtype: :py:class:`Template <amcards.models.Template>`

        :raises ForbiddenTemplateError: When the template for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/template/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenTemplateError('The template for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        template_json = res.json()
        return Template._from_json(template_json)

    def quicksends(self, limit: int = 25, skip: int = 0) -> List[Template]:
        """Fetches client's AMcards quicksend templates.

        :param int limit: Defaults to ``25``. Max number of quicksend templates to be fetched.
        :param int skip: Defaults to ``0``. Number of quicksend templates to be skipped.

        :return: The client's :py:class:`quicksend templates <amcards.models.Template>`.
        :rtype: List[:py:class:`Template <amcards.models.Template>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/quicksendtemplate/', headers=self._HEADERS, params={'limit': limit, 'offset': skip})
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching quicksends. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        templates_json = res.json().get('objects', [])
        return [Template._from_json(template_json) for template_json in templates_json]

    def quicksend(self, id: str | int) -> Template:
        """Fetches client's AMcards quicksend template with a specified id.

        :param str or int id: Unique id for the :py:class:`quicksend template <amcards.models.Template>` you are fetching.

        :return: The client's :py:class:`quicksend template <amcards.models.Template>` with specified ``id``.
        :rtype: :py:class:`Template <amcards.models.Template>`

        :raises ForbiddenTemplateError: When the quicksend template for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/quicksendtemplate/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenTemplateError('The quicksend template for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        template_json = res.json()
        return Template._from_json(template_json)

    def campaigns(self, limit: int = 25, skip: int = 0) -> List[Campaign]:
        """Fetches client's AMcards drip campaigns.

        :param int limit: Defaults to ``25``. Max number of drip campaigns to be fetched.
        :param int skip: Defaults to ``0``. Number of drip campaigns to be skipped.

        :return: The client's :py:class:`drip campaigns <amcards.models.Campaign>`.
        :rtype: List[:py:class:`Campaign <amcards.models.Campaign>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/campaign/', headers=self._HEADERS, params={'limit': limit, 'offset': skip})
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching campaigns. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        campaigns_json = res.json().get('objects', [])
        return [Campaign._from_json(campaign_json) for campaign_json in campaigns_json]

    def campaign(self, id: str | int) -> Campaign:
        """Fetches client's AMcards drip campaign with a specified id.

        :param str or int id: Unique id for the :py:class:`drip campaign <amcards.models.Campaign>` you are fetching.

        :return: The client's :py:class:`drip campaign <amcards.models.Campaign>` with specified ``id``.
        :rtype: :py:class:`Campaign <amcards.models.Campaign>`

        :raises ForbiddenCampaignError: When the drip campaign for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/campaign/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenCampaignError('The drip campaign for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        campaign_json = res.json()
        return Campaign._from_json(campaign_json)

    def cards(self, limit: int = 25, skip: int = 0, filters: dict = None) -> List[Card]:
        """Fetches client's AMcards cards.

        :param int limit: Defaults to ``25``. Max number of cards to be fetched.
        :param int skip: Defaults to ``0``. Number of cards to be skipped.
        :param Optional[dict] filters: Defaults to ``None``. Filters to be applied when fetching cards.

            A common use case is to use ``filter = {'third_party_contact_id': 'some_target_id'}``, this will fetch all cards that were shipped to a recipient with a ``third_party_contact_id == 'some_target_id'``.

        :return: The client's :py:class:`cards <amcards.models.Card>`.
        :rtype: List[:py:class:`Card <amcards.models.Card>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        params = {
            'limit': limit,
            'offset': skip,
        } | (filters or {})

        res = requests.get(url=f'{DOMAIN}/.api/v1/card/', headers=self._HEADERS, params=params)
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching cards. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        cards_json = res.json().get('objects', [])
        return [Card._from_json(card_json) for card_json in cards_json]

    def card(self, id: str | int) -> Card:
        """Fetches client's AMcards card with a specified id.

        :param str or int id: Unique id for the :py:class:`card <amcards.models.Card>` you are fetching.

        :return: The client's :py:class:`card <amcards.models.Card>` with specified ``id``.
        :rtype: :py:class:`Card <amcards.models.Card>`

        :raises ForbiddenCardError: When the card for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/card/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenCardError('The card for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        card_json = res.json()
        return Card._from_json(card_json)

    def card_count(self, filters: dict = None) -> int:
        """Fetches count of client's AMcards cards.

        :param Optional[dict] filters: Defaults to ``None``. Filters to be applied when counting cards.

            A common use case is to use ``filter = {'third_party_contact_id': 'some_target_id'}``, this will fetch all cards that were shipped to a recipient with a ``third_party_contact_id == 'some_target_id'``.

        :return: The count of client's cards.
        :rtype: int

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        params = {
            'limit': 1,
        } | (filters or {})

        res = requests.get(url=f'{DOMAIN}/.api/v1/card/', headers=self._HEADERS, params=params)
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException(f'Something went wrong when fetching card count. AMcards Status Code: {res.status_code}, AMcards Body: {res.text}.')

        return res.json()['meta']['total_count']

    def mailing(self, id: str | int) -> Mailing:
        """Fetches client's AMcards mailing with a specified id.

        :param str or int id: Unique id for the :py:class:`mailing <amcards.models.Mailing>` you are fetching.

        :return: The client's :py:class:`mailing <amcards.models.Mailing>` with specified ``id``.
        :rtype: :py:class:`Mailing <amcards.models.Mailing>`

        :raises ForbiddenMailingError: When the mailing for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/mailing/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenMailingError('The mailing for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        mailing_json = res.json()
        return Mailing._from_json(mailing_json)

    def contacts(self, limit: int = 25, skip: int = 0, filters: dict = None) -> List[Contact]:
        """Fetches client's AMcards contacts.

        :param int limit: Defaults to ``25``. Max number of contacts to be fetched.
        :param int skip: Defaults to ``0``. Number of contacts to be skipped.
        :param Optional[dict] filters: Defaults to ``None``. Filters to be applied when fetching contacts.

            A common use case is to use ``filter = {'last_name': 'Smith'}``, this will fetch all contacts with ``last_name == 'Smith'``.

        :return: The client's :py:class:`contacts <amcards.models.Contact>`.
        :rtype: List[:py:class:`Contact <amcards.models.Contact>`]

        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        params = {
            'limit': limit,
            'offset': skip,
        } | (filters or {})

        res = requests.get(url=f'{DOMAIN}/.api/v1/contact/', headers=self._HEADERS, params=params)
        if not res.ok:
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        contacts_json = res.json().get('objects', [])
        return [Contact._from_json(contact_json) for contact_json in contacts_json]

    def contact(self, id: str | int) -> Contact:
        """Fetches client's AMcards contact with a specified id.

        :param str or int id: Unique id for the :py:class:`contact <amcards.models.Contact>` you are fetching.

        :return: The client's :py:class:`contact <amcards.models.Contact>` with specified ``id``.
        :rtype: :py:class:`Contact <amcards.models.Contact>`

        :raises ForbiddenContactError: When the contact for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.get(url=f'{DOMAIN}/.api/v1/contact/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenContactError('The contact for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

        contact_json = res.json()
        return Contact._from_json(contact_json)

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        address_line_1: str,
        city: str,
        state: str,
        postal_code: str,
        country: Optional[str] = None,
        notes: Optional[str] = None,
        email: Optional[str] = None,
        organization: Optional[str] = None,
        phone: Optional[str] = None,
        birth_year: Optional[str] = None,
        birth_month: Optional[str] = None,
        birth_day: Optional[str] = None,
        anniversary_year: Optional[str] = None,
        anniversary_month: Optional[str] = None,
        anniversary_day: Optional[str] = None,
    ) -> None:
        """Creates a new contact for the client.

        :param str first_name: Contact's first name.
        :param str last_name: Contact's last name.
        :param str address_line_1: Contact's primary address line.
        :param str city: Contact's city.
        :param str state: Contact's state.
        :param str postal_code: Contact's postal code.
        :param Optional[str] country: Contact's country.
        :param Optional[str] notes: Contact's notes.
        :param Optional[str] email: Contact's email address.
        :param Optional[str] organization: Contact's organization.
        :param Optional[str] phone: Contact's phone number. In the form ``"12223334444"``.
        :param Optional[str] birth_year: Contact's birth year. In the form ``"YYYY"``.
        :param Optional[str] birth_month: Contact's birth month. In the form ``"MM"``.
        :param Optional[str] birth_day: Contact's birth day. In the form ``"DD"``.
        :param Optional[str] anniverary_year: Contact's anniversary year. In the form ``"YYYY"``.
        :param Optional[str] anniverary_month: Contact's anniversary month. In the form ``"MM"``.
        :param Optional[str] anniverary_day: Contact's anniversary day. In the form ``"DD"``.

        :raises AMcardsException: When something unexpected occurs.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        user_id = self.user().id
        body = {
            'first_name': first_name,
            'last_name': last_name,
            'address_line_1': address_line_1,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'owner': f'/.api/v1/user/{user_id}/',
            'notes': '',
            'groups': '',
        }

        if country is not None: body |= {'country': country}
        if notes is not None: body |= {'notes': notes}
        if email is not None: body |= {'email_address': email}
        if organization is not None: body |= {'organization': organization}
        if phone is not None: body |= {'phone_number': phone}
        if birth_year is not None: body |= {'birth_year': birth_year}
        if birth_month is not None: body |= {'birth_month': birth_month}
        if birth_day is not None: body |= {'birth_day': birth_day}
        if anniversary_year is not None: body |= {'anniversary_year': anniversary_year}
        if anniversary_month is not None: body |= {'anniversary_month': anniversary_month}
        if anniversary_day is not None: body |= {'anniversary_day': anniversary_day}

        res = requests.post(url=f'{DOMAIN}/.api/v1/contact/', json=body, headers=self._HEADERS)
        if not res.ok:
            if res.status_code == 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            raise exceptions.AMcardsException('Something went wrong when trying to create a contact')

    def delete_contact(self, id: str | int) -> None:
        """Deletes client's AMcards contact with a specified id.

        :param str or int id: Unique id for the :py:class:`contact <amcards.models.Contact>` you are deleting.

        :raises ForbiddenContactError: When the contact for the specified ``id`` either does not exist or is not owned by the client's user.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.

        """
        res = requests.delete(url=f'{DOMAIN}/.api/v1/contact/{id}/', headers=self._HEADERS)
        if not res.ok:
            if res.status_code in (403, 404):
                raise exceptions.ForbiddenContactError('The contact for the specified id either does not exist or is not owned by the client\'s user')
            raise exceptions.AuthenticationError('Access token provided to client is unauthorized')

    def send_card_cost(
        self,
        template_id: str | int,
        shipping_address: dict,
        return_address: dict = None,
        send_date: str = None,
    ) -> int:
        """Get cost for a card send. Without actually sending the card.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_card_cost(
                ...     template_id='123',
                ...     shipping_address={
                ...         'first_name': 'Ralph',
                ...         'last_name': 'Mullins',
                ...         'address_line_1': '2285 Reppert Road',
                ...         'city': 'Southfield',
                ...         'state': 'MI',
                ...         'postal_code': '48075',
                ...         'country': 'US'
                ...     }
                ... )
                >>> res
                442

        :param str or int template_id: Unique id for the :py:class:`template <amcards.models.Template>` you are getting cost for.
        :param dict shipping_address: Dict of shipping details. Here's an example how the dict might look, make sure you include all of the `required` keys:

            .. code-block::

                {
                    'first_name': 'Ralph',
                    'last_name': 'Mullins',
                    'address_line_1': '2285 Reppert Road',
                    'city': 'Southfield',
                    'state': 'MI',
                    'postal_code': '48075',
                    'country': 'US',
                    'organization': 'Google',                # OPTIONAL
                    'third_party_contact_id': 'crmid1453131' # OPTIONAL
                }

        :param Optional[dict] return_address: Dict of return details that will override the client's AMcards user default return details. Here's an example how the dict might look, all of the keys are optional:

            .. code-block::

                {
                    'first_name': 'Ralph',                   # OPTIONAL
                    'last_name': 'Mullins',                  # OPTIONAL
                    'address_line_1': '2285 Reppert Road',   # OPTIONAL
                    'city': 'Southfield',                    # OPTIONAL
                    'state': 'MI',                           # OPTIONAL
                    'postal_code': '48075',                  # OPTIONAL
                    'country': 'US',                         # OPTIONAL
                }

        :param Optional[str] send_date: The date the card should be sent. If not specified, the card will be scheduled for the following day. The format should be: ``"YYYY-MM-DD"``.

        :return: Cost for sending card in `cents`.
        :rtype: ``int``

        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ForbiddenTemplateError: When the client does not own the :py:class:`template <amcards.models.Template>` specified by ``template_id``.
        :raises ShippingAddressError: When ``shipping_address`` is missing some `required` keys.
        :raises DateFormatError: When one of the dates provided is not in ``"YYYY-MM-DD"`` format.

        """
        # Validate shipping address
        missings = helpers.get_missing_required_shipping_address_fields(shipping_address)
        if missings:
            error_message = 'Missing the following required shipping address fields: ' + ', '.join(missings)
            raise exceptions.ShippingAddressError(error_message)

        # Validate send date
        if send_date is not None and not helpers.is_valid_date(send_date):
            error_message = 'Invalid send_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)

        # Sanitize shipping address and return address
        shipping_address = helpers.sanitize_shipping_address_for_card_send(shipping_address)
        if return_address is not None:
            return_address = helpers.sanitize_return_address(return_address)
            # prefix return address fields with return_
            return_address = {f'return_{key}': value for key, value in return_address.items()}

        user = self.user()
        shipping_country = _fix_country(shipping_address['country'])
        return_country = _fix_country(user.country)
        if return_address is not None and 'return_country' in return_address:
            return_country = _fix_country(return_address['return_country'])

        # If this card is domestic charge domestic postage
        if shipping_country in user.domestic_postage_countries and return_country in user.domestic_postage_countries:
            return user.greeting_card_cost + user.domestic_postage_cost
        # Otherwise charge international postage
        return user.greeting_card_cost + user.international_postage_cost

    def send_card(
        self,
        template_id: str | int,
        initiator: str,
        shipping_address: dict,
        return_address: dict = None,
        send_date: str = None,
        message: str = None,
        extra_data: dict = None,
    ) -> CardResponse:
        """Attempt to send a card.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_card(
                ...     template_id='123',
                ...     initiator='myintegration123',
                ...     shipping_address={
                ...         'first_name': 'Ralph',
                ...         'last_name': 'Mullins',
                ...         'address_line_1': '2285 Reppert Road',
                ...         'city': 'Southfield',
                ...         'state': 'MI',
                ...         'postal_code': '48075',
                ...         'country': 'US'
                ...     }
                ... )
                >>> res.card_id
                1522873
                >>> res.total_cost
                442
                >>> res.message
                'Card created successfully!'
                >>> res.user_email
                'example@example.com'
                >>> res.shipping_address
                {'last_name': 'Mullins', 'address_line_1': '2285 Reppert Road', 'first_name': 'Ralph', 'country': 'US', 'state': 'MI', 'postal_code': '48075', 'city': 'Southfield'}

        :param str or int template_id: Unique id for the :py:class:`template <amcards.models.Template>` you are sending.
        :param str initiator: Unique identifier of client's user so if multiple users use a single AMcards.com account, a card can be identified per person.
        :param dict shipping_address: Dict of shipping details. Here's an example how the dict might look, make sure you include all of the `required` keys:

            .. code-block::

                {
                    'first_name': 'Ralph',
                    'last_name': 'Mullins',
                    'address_line_1': '2285 Reppert Road',
                    'city': 'Southfield',
                    'state': 'MI',
                    'postal_code': '48075',
                    'country': 'US',
                    'organization': 'Google',                # OPTIONAL
                    'third_party_contact_id': 'crmid1453131',# OPTIONAL
                    'address_line_2': 'Apt 2'                # OPTIONAL
                }

        :param Optional[dict] return_address: Dict of return details that will override the client's AMcards user default return details. Here's an example how the dict might look, all of the keys are optional:

            .. code-block::

                {
                    'first_name': 'Ralph',                   # OPTIONAL
                    'last_name': 'Mullins',                  # OPTIONAL
                    'address_line_1': '2285 Reppert Road',   # OPTIONAL
                    'city': 'Southfield',                    # OPTIONAL
                    'state': 'MI',                           # OPTIONAL
                    'postal_code': '48075',                  # OPTIONAL
                    'country': 'US',                         # OPTIONAL
                }

        :param Optional[str] send_date: The date the card should be sent. If not specified, the card will be scheduled for the following day. The format should be: ``"YYYY-MM-DD"``.
        :param Optional[str] message: A message to add to the card. This will be added to the inside bottom or inside right panel on the card and will not replace any message that is currently on the template.
        :param Optional[dict] extra_data: Extra data for merge fields. This is useful when you want to dynamically pass custom data to your templates. For example, if you pass in the example JSON, you would want to have your template contain a merge field in the form of *|data.carMake|*

            .. code-block::

                {
                    'carMake': 'Honda',                      # OPTIONAL
                }

        :return: AMcards' :py:class:`response <amcards.models.CardResponse>` for sending a single card.
        :rtype: :py:class:`CardResponse <amcards.models.CardResponse>`

        :raises CardSendError: When something goes wrong when attempting to send a card.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ForbiddenTemplateError: When the client does not own the :py:class:`template <amcards.models.Template>` specified by ``template_id``.
        :raises ShippingAddressError: When ``shipping_address`` is missing some `required` keys.
        :raises DateFormatError: When one of the dates provided is not in ``"YYYY-MM-DD"`` format.
        :raises InsufficientCreditsError: When the client's user has insufficient credits in their balance.

        """
        # Validate shipping address
        missings = helpers.get_missing_required_shipping_address_fields(shipping_address)
        if missings:
            error_message = 'Missing the following required shipping address fields: ' + ', '.join(missings)
            raise exceptions.ShippingAddressError(error_message)

        # Validate send date
        if send_date is not None and not helpers.is_valid_date(send_date):
            error_message = 'Invalid send_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)

        # Sanitize shipping address and return address
        shipping_address = helpers.sanitize_shipping_address_for_card_send(shipping_address)
        if return_address is not None:
            return_address = helpers.sanitize_return_address(return_address)
            # prefix return address fields with return_
            return_address = {f'return_{key}': value for key, value in return_address.items()}

        # Sanitize extra_data
        extra_data = helpers.sanitize_extra_data(extra_data)

        # Build request json payload
        body = {
            'template_id': template_id,
            'initiator': initiator,
        } | shipping_address

        if return_address is not None:
            body |= return_address

        if send_date is not None:
            body |= {'send_date': send_date}

        if message is not None:
            body |= {'message': message}

        if extra_data is not None:
            body |= {'extra_data': extra_data}

        res = requests.post(f'{DOMAIN}/cards/open-card-form-oa/', json=body, headers=self._HEADERS)

        # Check for errors
        match res.status_code:
            case 400:
                raise exceptions.CardSendError('Something went wrong when attempting to send a card')
            case 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            case 402:
                raise exceptions.InsufficientCreditsError('Clients\' user has insufficient credits, no card was scheduled')
            case 403:
                raise exceptions.ForbiddenTemplateError(f'Clients\' user does not own given template with id of {template_id}')

        res_json = res.json()
        return CardResponse._from_json(res_json | {
            'shipping_address': shipping_address,
        })

    def send_campaign_cost(
        self,
        campaign_id: str | int,
        shipping_address: dict,
        return_address: dict = None,
        send_date: str = None,
    ) -> int:
        """Get cost for a campaign send. Without actually sending the campaign.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_campaign_cost(
                ...     campaign_id='123',
                ...     shipping_address={
                ...         'first_name': 'Ralph',
                ...         'last_name': 'Mullins',
                ...         'address_line_1': '2285 Reppert Road',
                ...         'city': 'Southfield',
                ...         'state': 'MI',
                ...         'postal_code': '48075',
                ...         'country': 'US'
                ...     }
                ... )
                >>> res
                442

        :param str or int campaign_id: Unique id for the :py:class:`drip campaign <amcards.models.Campaign>` you are getting cost for.
        :param dict shipping_address: Dict of shipping details. Here's an example how the dict might look, make sure you include all of the `required` keys:

            .. code-block::

                {
                    'first_name': 'Ralph',
                    'last_name': 'Mullins',
                    'address_line_1': '2285 Reppert Road',
                    'city': 'Southfield',
                    'state': 'MI',
                    'postal_code': '48075',
                    'country': 'US',
                    'organization': 'Google',                # OPTIONAL
                    'phone_number': '15556667777',           # OPTIONAL
                    'birth_date': '2003-12-25',              # OPTIONAL
                    'anniversary_date': '2022-10-31',        # OPTIONAL
                    'third_party_contact_id': 'crmid1453131' # OPTIONAL
                }

        :param Optional[dict] return_address: Dict of return details that will override the client's AMcards user default return details. Here's an example how the dict might look, all of the keys are optional:

            .. code-block::

                {
                    'first_name': 'Ralph',                   # OPTIONAL
                    'last_name': 'Mullins',                  # OPTIONAL
                    'address_line_1': '2285 Reppert Road',   # OPTIONAL
                    'city': 'Southfield',                    # OPTIONAL
                    'state': 'MI',                           # OPTIONAL
                    'postal_code': '48075',                  # OPTIONAL
                    'country': 'US',                         # OPTIONAL
                }

        :param Optional[str] send_date: The date the drip campaign should be sent, in ``"YYYY-MM-DD"`` format. If not specified, the drip campaign will be scheduled for the following day.

        :return: Cost for sending campaign in `cents`.
        :rtype: ``int``

        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ForbiddenCampaignError: When the client does not own the :py:class:`campaign <amcards.models.Campaign>` specified by ``campaign_id``.
        :raises ShippingAddressError: When ``shipping_address`` is missing some `required` keys.
        :raises DateFormatError: When one of the dates provided is not in ``"YYYY-MM-DD"`` format.
        :raises PhoneFormatError: When the ``phone_number`` is not a digit string of length 10.

        """
        # Validate shipping address
        missings = helpers.get_missing_required_shipping_address_fields(shipping_address)
        if missings:
            error_message = 'Missing the following required shipping address fields: ' + ', '.join(missings)
            raise exceptions.ShippingAddressError(error_message)

        # Validate send date
        if send_date is not None and not helpers.is_valid_date(send_date):
            error_message = 'Invalid send_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)

        # Sanitize shipping address and return address
        shipping_address = helpers.sanitize_shipping_address_for_campaign_send(shipping_address)
        if return_address is not None:
            return_address = helpers.sanitize_return_address(return_address)
            # prefix return address fields with return_
            return_address = {f'return_{key}': value for key, value in return_address.items()}

        # Validate birth_date
        if 'birth_date' in shipping_address and not helpers.is_valid_birthdate(shipping_address['birth_date']):
            error_message = 'Invalid birth_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)
        # Validate anniversary_date
        if 'anniversary_date' in shipping_address and not helpers.is_valid_date(shipping_address['anniversary_date']):
            error_message = 'Invalid anniversary_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)
        # Validate phone_number
        if 'phone_number' in shipping_address and not helpers.is_valid_phone(shipping_address['phone_number']):
            error_message = 'Invalid phone_number format, please specify phone as a 10 number string with no special formatting (ex. 15556667777), or omit it'
            raise exceptions.PhoneFormatError(error_message)

        # Build request json payload
        body = {
            'campaign_id': campaign_id,
            'recipients': [shipping_address],
        }

        if return_address is not None:
            body |= return_address

        if send_date is not None:
            body |= {'send_date': send_date}

        if 'birth_date' in shipping_address:
            body['recipients'][0]['birth_day'] = shipping_address['birth_date'][-2:]
            body['recipients'][0]['birth_month'] = shipping_address['birth_date'][-5:-3]

        res = requests.post(f'{DOMAIN}/campaigns/calculate-campaign-price/', json=body, headers=self._HEADERS)

        # Check for errors
        match res.status_code:
            case 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            case 403:
                raise exceptions.ForbiddenCampaignError(f'Clients\' user does not own given campaign with id of {campaign_id}')

        return res.json()['pricing']['total_cost']

    def send_campaign(
        self,
        campaign_id: str | int,
        initiator: str,
        shipping_address: dict,
        return_address: dict = None,
        send_date: str = None,
        extra_data: dict = None,
    ) -> CampaignResponse:
        """Attempt to send a drip campaign.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_campaign(
                ...     campaign_id='123',
                ...     initiator='myintegration123',
                ...     shipping_address={
                ...         'first_name': 'Ralph',
                ...         'last_name': 'Mullins',
                ...         'address_line_1': '2285 Reppert Road',
                ...         'city': 'Southfield',
                ...         'state': 'MI',
                ...         'postal_code': '48075',
                ...         'country': 'US'
                ...     }
                ... )
                >>> res.card_ids
                [1528871, 1528872]
                >>> res.mailing_id
                29693
                >>> res.message
                'Thanks! Your cards have been scheduled and $8.84 was debited from your credits.'
                >>> res.user_email
                'example@example.com'
                >>> res.shipping_address
                {'country': 'US', 'state': 'MI', 'postal_code': '48075', 'first_name': 'Ralph', 'city': 'Southfield', 'address_line_1': '2285 Reppert Road', 'last_name': 'Mullins'}

        :param str or int campaign_id: Unique id for the :py:class:`drip campaign <amcards.models.Campaign>` you are sending.
        :param str initiator: Unique identifier of client's user so if multiple users use a single AMcards.com account, a drip campaign can be identified per person.
        :param dict shipping_address: Dict of shipping details. Here's an example how the dict might look, make sure you include all of the `required` keys:

            .. code-block::

                {
                    'first_name': 'Ralph',
                    'last_name': 'Mullins',
                    'address_line_1': '2285 Reppert Road',
                    'city': 'Southfield',
                    'state': 'MI',
                    'postal_code': '48075',
                    'country': 'US',
                    'organization': 'Google',                # OPTIONAL
                    'phone_number': '15556667777',           # OPTIONAL
                    'birth_date': '2003-12-25',              # OPTIONAL
                    'anniversary_date': '2022-10-31',        # OPTIONAL
                    'third_party_contact_id': 'crmid1453131',# OPTIONAL
                    'address_line_2': 'Apt 2'                # OPTIONAL
                }

        :param Optional[dict] return_address: Dict of return details that will override the client's AMcards user default return details. Here's an example how the dict might look, all of the keys are optional:

            .. code-block::

                {
                    'first_name': 'Ralph',                   # OPTIONAL
                    'last_name': 'Mullins',                  # OPTIONAL
                    'address_line_1': '2285 Reppert Road',   # OPTIONAL
                    'city': 'Southfield',                    # OPTIONAL
                    'state': 'MI',                           # OPTIONAL
                    'postal_code': '48075',                  # OPTIONAL
                    'country': 'US',                         # OPTIONAL
                }

        :param Optional[str] send_date: The date the drip campaign should be sent, in ``"YYYY-MM-DD"`` format. If not specified, the drip campaign will be scheduled for the following day.
        :param Optional[dict] extra_data: Extra data for merge fields. This is useful when you want to dynamically pass custom data to your templates. For example, if you pass in the example JSON, you would want to have your template contain a merge field in the form of *|data.carMake|*

            .. code-block::

                {
                    'carMake': 'Honda',                      # OPTIONAL
                }

        :return: AMcards' :py:class:`response <amcards.models.CampaignResponse>` for sending a single drip campaign.
        :rtype: :py:class:`CampaignResponse <amcards.models.CampaignResponse>`

        :raises CampaignSendError: When something goes wrong when attempting to send a drip campaign.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ForbiddenCampaignError: When the client does not own the :py:class:`campaign <amcards.models.Campaign>` specified by ``campaign_id``.
        :raises ShippingAddressError: When ``shipping_address`` is missing some `required` keys.
        :raises DateFormatError: When one of the dates provided is not in ``"YYYY-MM-DD"`` format.
        :raises PhoneFormatError: When the ``phone_number`` is not a digit string of length 10.
        :raises InsufficientCreditsError: When the client's user has insufficient credits in their balance.
        :raises DuplicateCampaignError: When AMcards detects this :py:class:`campaign <amcards.models.Campaign>` specified by ``campaign_id`` is a duplicate and ``send_if_duplicate`` in :py:class:`Campaign <amcards.models.Campaign>` is ``False``.

        """
        # Validate shipping address
        missings = helpers.get_missing_required_shipping_address_fields(shipping_address)
        if missings:
            error_message = 'Missing the following required shipping address fields: ' + ', '.join(missings)
            raise exceptions.ShippingAddressError(error_message)

        # Validate send date
        if send_date is not None and not helpers.is_valid_date(send_date):
            error_message = 'Invalid send_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)

        # Sanitize shipping address and return address
        shipping_address = helpers.sanitize_shipping_address_for_campaign_send(shipping_address)
        if return_address is not None:
            return_address = helpers.sanitize_return_address(return_address)
            # prefix return address fields with return_
            return_address = {f'return_{key}': value for key, value in return_address.items()}

        # Validate birth_date
        if 'birth_date' in shipping_address and not helpers.is_valid_birthdate(shipping_address['birth_date']):
            error_message = f'Invalid birth_date format of "{shipping_address["birth_date"]}", please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)
        # Validate anniversary_date
        if 'anniversary_date' in shipping_address and not helpers.is_valid_date(shipping_address['anniversary_date']):
            error_message = f'Invalid anniversary_date format of "{shipping_address["anniversary_date"]}", please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)
        # Validate phone_number
        if 'phone_number' in shipping_address and not helpers.is_valid_phone(shipping_address['phone_number']):
            error_message = 'Invalid phone_number format, please specify phone as a 10 number string with no special formatting (ex. 15556667777), or omit it'
            raise exceptions.PhoneFormatError(error_message)
        # Sanitize extra_data
        extra_data = helpers.sanitize_extra_data(extra_data)

        # Build request json payload
        body = {
            'campaign_id': campaign_id,
            'initiator': initiator,
        } | shipping_address

        if return_address is not None:
            body |= return_address

        if send_date is not None:
            body |= {'send_date': send_date}

        if extra_data is not None:
            body |= {'extra_data': extra_data}

        res = requests.post(f'{DOMAIN}/campaigns/open-campaign-form/', json=body, headers=self._HEADERS)

        # Check for errors
        match res.status_code:
            case 400:
                raise exceptions.CampaignSendError('Something went wrong when attempting to send a drip campaign')
            case 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            case 402:
                raise exceptions.InsufficientCreditsError('Clients\' user has insufficient credits, no cards were scheduled')
            case 403:
                raise exceptions.ForbiddenCampaignError(f'Clients\' user does not own given campaign with id of {campaign_id}')
            case 409:
                raise exceptions.DuplicateCampaignError('Duplicates were detected, no cards were scheduled')

        res_json = res.json()
        return CampaignResponse._from_json(res_json | {
            'shipping_address': shipping_address,
        })

    def send_campaign_multi(
        self,
        campaign_id: str | int,
        initiator: str,
        contacts: List[dict],
    ) -> CampaignMultiResponse:
        """Attempt to send a drip campaign to multiple contacts.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_campaign_multi(
                ...     campaign_id='123',
                ...     initiator='myintegration123',
                ...     contacts=[
                ...         {
                ...             'first_name': 'Ralph',
                ...             'last_name': 'Mullins',
                ...             'address_line_1': '2285 Reppert Road',
                ...             'city': 'Southfield',
                ...             'state': 'MI',
                ...             'postal_code': '48075',
                ...             'country': 'US'
                ...         },
                ...         {
                ...             'first_name': 'Keith',
                ...             'last_name': 'May',
                ...             'address_line_1': '364 Spruce Drive',
                ...             'city': 'Philadelphia',
                ...             'state': 'PA',
                ...             'postal_code': '19107',
                ...             'country': 'US'
                ...         }
                ...     ]
                ... )
                >>> res.mailing_id
                29695
                >>> res.contacts_scheduled_count
                2
                >>> res.duplicate_contacts_count
                0
                >>> res.message
                'Cards scheduled successfully. Debited $8.84 credits. This may take a few minutes to complete.'

        :param str or int campaign_id: Unique id for the :py:class:`drip campaign <amcards.models.Campaign>` you are sending.
        :param str initiator: Unique identifier of client's user so if multiple users use a single AMcards.com account, a drip campaign can be identified per person.
        :param List[dict] contacts: List of contact details. Here's an example how the list might look, make sure you include all of the `required` keys for each dict in the list:

            .. code-block::

                [
                    {
                        'first_name': 'Ralph',
                        'last_name': 'Mullins',
                        'address_line_1': '2285 Reppert Road',
                        'city': 'Southfield',
                        'state': 'MI',
                        'postal_code': '48075',
                        'country': 'US',
                        'organization': 'Google',                 # OPTIONAL
                        'phone_number': '15556667777',            # OPTIONAL
                        'birth_date': '2003-12-25',               # OPTIONAL
                        'anniversary_date': '2022-10-31',         # OPTIONAL
                        'third_party_contact_id': 'crmid1453131', # OPTIONAL
                        'address_line_2': 'Apt 2',                # OPTIONAL
                        'extra_data': {                           # OPTIONAL
                            'carMake': 'Honda',                   # OPTIONAL
                        }                                         # OPTIONAL
                    },
                ]

        :return: AMcards' :py:class:`response <amcards.models.CampaignMultiResponse>` for sending a drip campaign to multiple contacts.
        :rtype: :py:class:`CampaignMultiResponse <amcards.models.CampaignMultiResponse>`

        :raises CampaignMultiSendError: When something goes wrong when attempting to send a drip campaign.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ShippingAddressError: When none of the provided contacts are valid after validation. Contacts missing required fields or with invalid optional fields are skipped.
        :raises InsufficientCreditsError: When the client's user has insufficient credits in their balance.

        """
        contacts_to_send = []

        # Validate contacts
        for contact in contacts:
            missings = helpers.get_missing_required_shipping_address_fields(contact)
            if not missings:
                contacts_to_send.append(contact)

        # Sanitize contacts
        contacts_to_send = [helpers.sanitize_contact_for_campaign_multi_send(contact) for contact in contacts_to_send]

        valid_contacts = []
        for contact in contacts_to_send:
            # Validate birth_date
            if 'birth_date' in contact and not helpers.is_valid_birthdate(contact['birth_date']):
                continue
            # Validate anniversary_date
            if 'anniversary_date' in contact and not helpers.is_valid_date(contact['anniversary_date']):
                continue
            # Validate phone_number
            if 'phone_number' in contact and not helpers.is_valid_phone(contact['phone_number']):
                continue
            if 'extra_data' in contact:
                contact['extra_data'] = helpers.sanitize_extra_data(contact['extra_data'])
            valid_contacts.append(contact)

        if not valid_contacts:
            raise exceptions.ShippingAddressError('No valid contacts to send')

        # Build request json payload
        body = {
            'campaign_id': campaign_id,
            'initiator': initiator,
            'contacts': valid_contacts,
        }

        res = requests.post(f'{DOMAIN}/campaigns/open-campaign-multi-form/', json=body, headers=self._HEADERS)

        # Check for errors
        match res.status_code:
            case 400:
                raise exceptions.CampaignMultiSendError('Something went wrong when attempting to send a drip campaign')
            case 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            case 402:
                raise exceptions.InsufficientCreditsError('Clients\' user has insufficient credits, no cards were scheduled')

        res_json = res.json()
        return CampaignMultiResponse._from_json(res_json)

    def send_cards(
        self,
        template_id: str | int,
        initiator: str,
        shipping_addresses: List[dict],
        return_address: dict = None,
        send_date: str = None,
        send_if_error: bool = False,
    ) -> CardsResponse:
        """Attempt to send multiple cards.

            .. code-block::

                >>> from amcards import AMcardsClient
                >>> client = AMcardsClient('youraccesstoken')
                >>> res = client.send_cards(
                ...     template_id='123',
                ...     initiator='myintegration123',
                ...     shipping_addresses=[
                ...         {
                ...             'first_name': 'Ralph',
                ...             'last_name': 'Mullins',
                ...             'address_line_1': '2285 Reppert Road',
                ...             'city': 'Southfield',
                ...             'state': 'MI',
                ...             'postal_code': '48075',
                ...             'country': 'US',
                ...             'organization': 'Google',
                ...             'third_party_contact_id': 'crmid1453131'
                ...         },
                ...         {
                ...             'first_name': 'Keith',
                ...             'last_name': 'May',
                ...             'address_line_1': '364 Spruce Drive',
                ...             'city': 'Philadelphia',
                ...             'state': 'PA',
                ...             'postal_code': '19107',
                ...             'country': 'US'
                ...         }
                ...     ]
                ... )
                >>> res.mailing_id
                29694
                >>> res.message
                "You can check the mailing_uri. When the 'status' is '0' (aka Completed) you can then read the 'report' field for a list
                of cards that were created. See each card's 'status' to make sure that it was created. If the status is 'fail' there will be a 'message' stating the issue with that recipient."
                >>> res.user_email
                'example@example.com'
                >>> res.shipping_addresses
                [{'country': 'US', 'state': 'MI', 'postal_code': '48075', 'first_name': 'Ralph', 'city': 'Southfield', 'address_line_1': '2285 Reppert Road', 'last_name': 'Mullins', 'organization': 'Google', 'third_party_contact_id': 'crmid1453131'}, {'country': 'US', 'state': 'PA', 'postal_code': '19107', 'first_name': 'Keith', 'city': 'Philadelphia', 'address_line_1': '364 Spruce Drive', 'last_name': 'May'}]

        :param str or int template_id: Unique id for the :py:class:`template <amcards.models.Template>` you are sending.
        :param str initiator: Unique identifier of client's user so if multiple users use a single AMcards.com account, a card can be identified per person.
        :param List[dict] shipping_addresses: List of shipping details. Here's an example how the list might look, make sure you include all of the `required` keys for each dict in the list:

            .. code-block::

                [
                    {
                        'first_name': 'Ralph',
                        'last_name': 'Mullins',
                        'address_line_1': '2285 Reppert Road',
                        'city': 'Southfield',
                        'state': 'MI',
                        'postal_code': '48075',
                        'country': 'US',
                        'organization': 'Google',                # OPTIONAL
                        'third_party_contact_id': 'crmid1453131' # OPTIONAL
                    },
                    {
                        'first_name': 'Keith',
                        'last_name': 'May',
                        'address_line_1': '364 Spruce Drive',
                        'city': 'Philadelphia',
                        'state': 'PA',
                        'postal_code': '19107',
                        'country': 'US'
                    }
                ]

        :param Optional[dict] return_address: Dict of return details that will override the client's AMcards user default return details. Here's an example how the dict might look, all of the keys are optional:

            .. code-block::

                {
                    'first_name': 'Ralph',                   # OPTIONAL
                    'last_name': 'Mullins',                  # OPTIONAL
                    'address_line_1': '2285 Reppert Road',   # OPTIONAL
                    'city': 'Southfield',                    # OPTIONAL
                    'state': 'MI',                           # OPTIONAL
                    'postal_code': '48075',                  # OPTIONAL
                    'country': 'US',                         # OPTIONAL
                }

        :param Optional[str] send_date: The date the card should be sent, If not specified, the card will be scheduled for the following day. The format should be: ``"YYYY-MM-DD"``.
        :param bool send_if_error: Defaults to False. If False, when sending cards to several recipients, if one of the card sends fails, all other card sends will be haulted. If True, only the cards that fail will be haulted, the rest will be scheduled as normal.

        :return: AMcards' :py:class:`response <amcards.models.CardsResponse>` for sending multiple cards.
        :rtype: :py:class:`CardsResponse <amcards.models.CardsResponse>`

        :raises CardsSendError: When something goes wrong when attempting to send cards.
        :raises AuthenticationError: When the client's ``access_token`` is invalid.
        :raises ForbiddenTemplateError: When the client does not own the :py:class:`template <amcards.models.Template>` specified by ``template_id``.
        :raises ShippingAddressError: When some items in ``shipping_addresses`` are missing some `required` keys.
        :raises DateFormatError: When one of the dates provided is not in ``"YYYY-MM-DD"`` format.
        :raises InsufficientCreditsError: When the client's user has insufficient credits in their balance.

        """
        # Validate shipping addresses
        for idx, shipping_address in enumerate(shipping_addresses):
            missings = helpers.get_missing_required_shipping_address_fields(shipping_address)
            if missings:
                error_message = f'Missing the following required shipping address fields at shipping_addresses[{idx}]: ' + ', '.join(missings)
                raise exceptions.ShippingAddressError(error_message)

        # Validate send date
        if send_date is not None and not helpers.is_valid_date(send_date):
            error_message = 'Invalid send_date format, please specify date as "YYYY-MM-DD", or omit it'
            raise exceptions.DateFormatError(error_message)

        # Sanitize shipping addresses and return address
        shipping_addresses = [helpers.sanitize_shipping_address_for_card_send(shipping_address) for shipping_address in shipping_addresses]
        if return_address is not None:
            return_address = helpers.sanitize_return_address(return_address)
            # prefix return address fields with return_
            return_address = {f'return_{key}': value for key, value in return_address.items()}

        # Build request json payload
        body = {
            'template_id': template_id,
            'initiator': initiator,
            'recipients': shipping_addresses,
            'send_even_if_error': 'true' if send_if_error else 'false',
            'offset_type': 'before', # This is arbitrary, but we must add it as per https://amcards.com/docs/open-mailing-form/
            'date_offset': '0', # This is arbitrary, but we must add it as per https://amcards.com/docs/open-mailing-form/
            'send_type': 'immediate',
            'send_date': helpers.today(),
        }

        if return_address is not None:
            body |= return_address

        if send_date is not None:
            body |= {'send_type': 'specific_date', 'send_date': send_date}

        res = requests.post(f'{DOMAIN}/cards/open-mailing-form/', json=body, headers=self._HEADERS)

        # Check for errors
        match res.status_code:
            case 400:
                raise exceptions.CardsSendError('Something went wrong when attempting to send cards')
            case 401:
                raise exceptions.AuthenticationError('Access token provided to client is unauthorized')
            case 402:
                raise exceptions.InsufficientCreditsError('Clients\' user has insufficient credits, no card was scheduled')
            case 403:
                raise exceptions.ForbiddenTemplateError(f'Clients\' user does not own given template with id of {template_id}')

        res_json = res.json()
        return CardsResponse._from_json(res_json | {
            'shipping_addresses': shipping_addresses,
        })

def _fix_country(country: str) -> str:
    if not isinstance(country, str): return ''
    country = country.upper()
    return FIXED_COUNTRY.get(country, country)
