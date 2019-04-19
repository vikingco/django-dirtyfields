import pytest
import pytz
from datetime import datetime

from django.utils import timezone
from django.test.utils import override_settings

from .models import TestDatetimeModel, TestCurrentDatetimeModel


@override_settings(USE_TZ=True, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_naive_current_value():
    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1, tzinfo=pytz.utc))

    # Adding a naive datetime
    tm.datetime_field = datetime(2016, 1, 1)

    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1, tzinfo=pytz.utc)}


@override_settings(USE_TZ=False)
@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_aware_current_value():
    tm = TestDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1))

    # Adding an aware datetime
    tm.datetime_field = datetime(2016, 1, 1, tzinfo=pytz.utc)

    assert tm.get_dirty_fields() == {'datetime_field': datetime(2000, 1, 1)}


@pytest.mark.django_db
def test_datetime_fields_when_aware_db_and_aware_current_value():
    aware_dt = timezone.now()
    tm = TestDatetimeModel.objects.create(datetime_field=aware_dt)

    tm.datetime_field = timezone.now()

    assert tm.get_dirty_fields() == {'datetime_field': aware_dt}


@pytest.mark.django_db
def test_datetime_fields_when_naive_db_and_naive_current_value():
    naive_dt = datetime.now()
    tm = TestDatetimeModel.objects.create(datetime_field=naive_dt)

    tm.datetime_field = datetime.now()

    assert tm.get_dirty_fields() == {'datetime_field': naive_dt}


@override_settings(USE_TZ=True, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_with_current_timezone_conversion():
    tm = TestCurrentDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.utc))

    # Adding a naive datetime, that will be converted to local timezone.
    tm.datetime_field = datetime(2000, 1, 1, 6, 0, 0)

    # Chicago is UTC-6h, this field shouldn't be dirty, as we will automatically set this naive datetime
    # with current timezone and then convert it to utc to compare it with database one.
    assert tm.get_dirty_fields() == {}


@override_settings(USE_TZ=False, TIME_ZONE='America/Chicago')
@pytest.mark.django_db
def test_datetime_fields_with_current_timezone_conversion_without_timezone_support():
    tm = TestCurrentDatetimeModel.objects.create(datetime_field=datetime(2000, 1, 1, 12, 0, 0))

    # Adding an aware datetime
    chicago_timezone = pytz.timezone('America/Chicago')
    tm.datetime_field = chicago_timezone.localize(datetime(2000, 1, 1, 6, 0, 0), is_dst=None)

    # If the database is naive, then we consider that it is defined as in UTC.
    assert tm.get_dirty_fields() == {}
