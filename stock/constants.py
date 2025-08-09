from enum import Enum


class KaratChoices(Enum):
    SIX = '6'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    TWELVE = '12'
    FOURTEEN = '14'
    FIFTEEN = '15'
    EIGHTEEN = '18'
    TWENTY = '20'
    TWENTY_ONE = '21'
    TWENTY_TWO = '22'
    TWENTY_FOUR = '24'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]


class MaterialChoices(Enum):
    GOLD = 'Gold'
    SILVER = 'Silver'
    DIAMOND = 'Diamond'
    PLATINUM = 'Platinum'
    RUBY = 'Ruby'
    OTHER = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class CategoryChoices(Enum):
    NECKLACE_SET = 'Necklace Set'
    PENDANT_SET = 'Pendant Set'
    MANGALSUTRA = 'Mangalsutra'
    FINGER_RING = 'Finger Ring'
    NOSE_PIN = 'Nose Pin'
    NECKWEAR = 'Neckwear'
    BRACELET = 'Bracelet'
    EARRING = 'Earring'
    PENDANT = 'Pendant'
    BANGLE = 'Bangle'
    CHAIN = 'Chain'
    COIN = 'Coin'
    OTHER = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class PaymentMethodChoices(Enum):
    CASH = 'Cash'
    CARD = 'Card'
    UPI = 'UPI'
    OTHER = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class DiscountChoices(Enum):
    NONE = ''
    FIXED = 'Fixed'
    PERCENTAGE = 'Percentage'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class LabourOrMakingChargeChoices(Enum):
    NONE = ''
    FIXED = 'Fixed'
    PERGRAM = 'Per Gram'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class LockerNumberChoices(Enum):
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.title()) for choice in cls]
