from worker import count_crimes_for_crime_type

def count_crimes_for_crime_type():
    result = count_crimes_for_crime_type("THEFT")
    assert isinstance(result, str)
