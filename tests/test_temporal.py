from app.temporal import extract_dates_from_text, looks_historical, resolve_query_dates


def test_parse_april_15():
    ds = extract_dates_from_text("What was true on April 15, 2025?")
    assert ds[0].isoformat() == "2025-04-15"


def test_historical_without_date_errors():
    v, s, err = resolve_query_dates("What was the control state as of last quarter?", None, None)
    assert err is not None
    assert "April 15" in err


def test_non_historical_allows_missing_date():
    v, s, err = resolve_query_dates("Why did CC6.1 fail?", None, None)
    assert err is None
    assert v is None


def test_separate_valid_system_from_request():
    from datetime import date

    v, s, err = resolve_query_dates("posture", date(2025, 4, 15), date(2025, 5, 1))
    assert err is None
    assert v == date(2025, 4, 15)
    assert s == date(2025, 5, 1)
