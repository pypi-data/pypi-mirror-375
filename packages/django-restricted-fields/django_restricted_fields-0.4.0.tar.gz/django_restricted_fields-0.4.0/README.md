django-restricted-fields
========================

Usage
-----

Add this package to your virtual environment. In your Django application's `forms.py`,
import the field(s) you want to use (currently only `RestrictedDateField` and
`RestrictedDateTimeField`). These offer additional options:

-  `future_allowed=False` – inhibit the input of dates / times that are in the future

-  `past_allowed=False` – inhibit the input of dates / times that are in the past

-  `min_value=X`, `max_value=X` – inhibit the input of dates / times before / after X,
   where X can be a Python date / datetime value or a callable that returns such a value

Most browsers will display a date and / or time picker whose range is limited by these
options.

Other than with Django's native fields, dates (and times) should be formatted according to
the locale settings of the browser (which normally is the right thing to do).
