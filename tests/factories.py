import factory

from oscar.apps.address import models as address_models
from oscar.apps.order import models as order_models




class Country(factory.Factory):
    iso_3166_1_a2 = 'GB'
    name = "UNITED KINGDOM"

    class Meta:
        model = address_models.Country
        strategy = factory.BUILD_STRATEGY


class ShippingAddress(factory.Factory):
    title = "Dr"
    first_name = "Barry"
    last_name = 'Barrington'
    line1 = "1 King Road"
    line4 = "London"
    postcode = "SW1 9RE"
    country = factory.SubFactory(Country)

    class Meta:
        model = order_models.ShippingAddress
        strategy = factory.BUILD_STRATEGY


class BillingAddress(factory.Factory):
    title = "Dr"
    first_name = "Barry"
    last_name = 'Barrington'
    line1 = "1 King Road"
    line4 = "London"
    postcode = "SW1 9RE"
    country = factory.SubFactory(Country)

    class Meta:
        model = order_models.BillingAddress
        strategy = factory.BUILD_STRATEGY
