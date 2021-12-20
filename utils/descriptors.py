"""
A useful set of descriptors to implement property validation
"""
import numbers
import datetime


class RealNumber:
    """
    Validates real numbers with optional bounds.
    """

    def __init__(self, min_value=None, max_value=None, *, sterilize_attr=None):
        """

        Args:
            min_value (float): optional, minimum value
            max_value (float): optional, maximum value
            sterilize_attr (iterable): optional, instance attributes to sterilize when calling set method
        """
        if sterilize_attr is None:
            sterilize_attr = []
        self.min_value = min_value
        self.max_value = max_value
        self.sterilize_attr = sterilize_attr

    def __set_name__(self, owner, name):
        self.property_name = name

    def __set__(self, instance, value):
        if not isinstance(value, numbers.Real):
            raise TypeError(f"{self.property_name} must be a Real Number.")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.property_name} must be at least {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.property_name} cannot exceed {self.max_value}.")
        instance.__dict__[self.property_name] = value
        if self.sterilize_attr:
            for attr in self.sterilize_attr:
                instance.__dict__[attr] = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.property_name, None)


class FutureDate:
    """
    Validates time format and cast input to datetime.date
    """

    # TODO: check for datetime offset (Time zone)
    def __init__(self, date_format="%Y-%m-%d", *, sterilize_attr=None):
        """

        Args:
            date_format (str): date format, default equal to "%Y-%m-%d"
            sterilize_attr (iterable): optional, instance attributes to sterilize when calling set method
        """
        if sterilize_attr is None:
            sterilize_attr = []
        self.date_format = date_format
        self.sterilize_attr = sterilize_attr

    def __set_name__(self, owner, name):
        self.property_name = name

    def __set__(self, instance, value):
        if isinstance(value, datetime.datetime):
            if value > datetime.datetime.utcnow():
                instance.__dict__[self.property_name] = value.date()
            else:
                raise ValueError(f"{self.property_name} must be a future date.")
        elif isinstance(value, datetime.date):
            if value > datetime.date.today():
                instance.__dict__[self.property_name] = value
            else:
                raise ValueError(f"{self.property_name} must be a future date.")
        else:
            try:
                value = datetime.datetime.strptime(value, self.date_format)
            except ValueError as err:
                raise ValueError(err)
            if value < datetime.datetime.utcnow():
                raise ValueError(f"{self.property_name} must be a future date.")
            instance.__dict__[self.property_name] = value.date()
        if self.sterilize_attr:
            for attr in self.sterilize_attr:
                instance.__dict__[attr] = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.property_name)