from datetime import date, datetime, timezone
from django.core.exceptions import ValidationError
from django.forms import DateInput, DateTimeInput, DateField, DateTimeField
from typing import Any, Optional


class NativeDateTimeInput(DateTimeInput):
    input_type = "datetime-local"
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        new_value = value
        if value and not isinstance(value, str):
                new_value = value.isoformat()
        return super().render(name, new_value, attrs=attrs, renderer=renderer)


class NativeDateInput(DateInput):
    input_type = "date-local"
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        new_value = value
        if value and not isinstance(value, str):
                new_value = value.isoformat()
        return super().render(name, new_value, attrs=attrs, renderer=renderer)


class RestrictedDateTimeField(DateTimeField):
    def __init__(self, *args,
            future_allowed: bool = True,
            past_allowed: bool = True,
            min_value: Optional[datetime] = None,
            max_value: Optional[datetime] = None,
            **kwargs):
        kwargs.setdefault("widget", NativeDateTimeInput)
        if kwargs.get("initial") == "today":
            # A shortcut to insert the current date (and time)
            kwargs["initial"] = lambda: datetime.now(timezone.utc).isoformat()
        self.future_allowed = future_allowed
        self.past_allowed = past_allowed
        if min_value is not None:
            if callable(min_value):
                _min = min_value()
            else:
                _min = min_value
            self.min_value = _min
        else:
            self.min_value = None
        if max_value is not None:
            if callable(max_value):
                _max = max_value()
            else:
                _max = max_value
            self.max_value = _max
        else:
            self.max_value = None
        super().__init__(*args, **kwargs)
    
    def widget_attrs(self, widget):
        """Sets additional attributes for the widget for this field.
        
        Nothing is changed if the widget is not the standard one for this field.
        """
        attrs = super().widget_attrs(widget)
        if isinstance(widget, NativeDateTimeInput):
            now = datetime.now(timezone.utc)
            
            # is there a min restriction?
            _min = None
            if not self.past_allowed:
                _min = now
            if self.min_value is not None and (_min is None or self.min_value > _min):
                _min = self.min_value
            if _min is not None:
                attrs["min"] = f"{_min:%Y-%m-%dT%H:%M:%S}"
            
            # is there a max restriction?
            _max = None
            if not self.future_allowed:
                _max = now
            if self.max_value is not None and (_max is None or self.max_value < _max):
                _max = self.max_value
            if _max is not None:
                attrs["max"] = f"{_max:%Y-%m-%dT%H:%M:%S}"
        
        return attrs
    
    def validate(self, value: Any) -> None:
        """Validates the form input for this field."""
        super().validate(value)
        now = datetime.now(timezone.utc)
        if not self.future_allowed and value > now:
            raise ValidationError("must not be in the future")
        if not self.past_allowed and value < now:
            raise ValidationError("must not be in the past")
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"must not be later than {self.max_value:%Y-%m-%d %H:%M:%S}")
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"must not be before {self.min_value:%Y-%m-%d %H:%M:%S}")


class RestrictedDateField(DateField):
    def __init__(self, *args,
            future_allowed: bool = True,
            past_allowed: bool = True,
            min_value: Optional[date] = None,
            max_value: Optional[date] = None,
            **kwargs):
        kwargs.setdefault("widget", NativeDateInput)
        if kwargs.get("initial") == "today":
            # A shortcut to insert the current date – caution, in the UTC timezone!
            kwargs["initial"] = lambda: datetime.now(timezone.utc).date().isoformat()
        self.future_allowed = future_allowed
        self.past_allowed = past_allowed
        if min_value is not None:
            if callable(min_value):
                _min = min_value()
            else:
                _min = min_value
            self.min_value = _min
        else:
            self.min_value = None
        if max_value is not None:
            if callable(max_value):
                _max = max_value()
            else:
                _max = max_value
            self.max_value = _max
        else:
            self.max_value = None
        super().__init__(*args, **kwargs)
    
    def widget_attrs(self, widget):
        """Sets additional attributes for the widget for this field.
        
        Nothing is changed if the widget is not the standard one for this field.
        """
        attrs = super().widget_attrs(widget)
        if isinstance(widget, NativeDateInput):
            now = datetime.now(timezone.utc).date()  # wrt UTC!
            
            # is there a min restriction?
            _min = None
            if not self.past_allowed:
                _min = now
            if self.min_value is not None and (_min is None or self.min_value > _min):
                _min = self.min_value
            if _min is not None:
                attrs["min"] = f"{_min:%Y-%m-%d}"
            
            # is there a max restriction?
            _max = None
            if not self.future_allowed:
                _max = now
            if self.max_value is not None and (_max is None or self.max_value < _max):
                _max = self.max_value
            if _max is not None:
                attrs["max"] = f"{_max:%Y-%m-%d}"
        
        return attrs
    
    def validate(self, value: Any) -> None:
        """Validates the form input for this field."""
        super().validate(value)
        now = datetime.now(timezone.utc).date()
        if not self.future_allowed and value > now:
            raise ValidationError("must not be in the future")
        if not self.past_allowed and value < now:
            raise ValidationError("must not be in the past")
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"must not be later than {self.max_value:%Y-%m-%d}")
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"must not be before {self.min_value:%Y-%m-%d}")
