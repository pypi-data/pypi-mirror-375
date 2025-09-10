from typing import Dict, Any, List, Callable, Union
import pandas as pd
from mipi_datamanager.generate_inserts import generate_insert_records2


def _list_to_inserts(name: str, vals: list) -> pd.DataFrame:
    return pd.DataFrame({name: vals})


def _get_mrn():
    df_inserts = _list_to_inserts("MRN", ["10505737", "10505787", "10505789", "10505794", "10505799",
                                                    "10505802", "10505804", "10505823", "10505826"])
    return generate_insert_records2(df_inserts)

def _get_csn():
    df_inserts = _list_to_inserts("CSN", ["1083050372", "1083050372", "1083050372", "1083050372", "1083050372",
                                                    "1065756601", "1040651860", "1039034719", "1024913693", "1039034719"])
    return generate_insert_records2(df_inserts)

def _get_patid():
    df_inserts = _list_to_inserts("PAT_ID", ["Z1014673", "Z1014722", "Z1014725", "Z1014728", "Z1014734",
                                                      "Z1014736", "Z1014738", "Z1014757", "Z1014759"])
    return generate_insert_records2(df_inserts)

MRN_INSERTS = _get_mrn()
CSN_INSERTS = _get_csn()
PATID_INSERTS = _get_patid()

def _maybe_convert_to_list(val: str | List[str]) -> List[str]:
    if isinstance(val, str):
        return [val]
    elif isinstance(val, list):
        return val
    raise TypeError(f"Unsupported type {type(val)}")


def assert_sql_contains(substrings_: str | List[str], sql):
    _substrings = _maybe_convert_to_list(substrings_)
    for substring in _substrings:
        assert substring in sql, f"{substring} not in SQL"

def assert_sql_not_contains(substrings_: str | List[str], sql):
    _substrings = _maybe_convert_to_list(substrings_)
    for substring in _substrings:
        assert substring not in sql, f"{substring} was found in SQL"

def assert_dataframe_contains_columns(columns: str | List[str], df: pd.DataFrame):
    _columns = _maybe_convert_to_list(columns)
    for column in _columns:
        assert column in df.columns, f"Column {column!r} not in dataframe"

def assert_series_contains_values(values: str | List[str], series: pd.Series):
    _values = _maybe_convert_to_list(values)
    for value in _values:
        assert value in series.values, f"Value {value!r} not in series: {series.name!r}"

def assert_dataframe_columns_contain_values(contents: Dict[str, Union[str,List[str]]], df: pd.DataFrame):
    _contents = {k:_maybe_convert_to_list(v) for k,v in contents.items()}
    assert_dataframe_contains_columns(list(_contents.keys()), df)
    for column_name, expected_values in _contents.items():
        assert_series_contains_values(expected_values, df[column_name])

def check_sql_contains(substrings_: str | List[str]):
    return lambda sql: assert_sql_contains(substrings_, sql)

def check_sql_not_contains(substrings_: str | List[str]):
    return lambda sql: assert_sql_not_contains(substrings_, sql)

def check_dataframe_contains_columns(columns: str | List[str]):
    return lambda df: assert_dataframe_contains_columns(columns, df)

def check_dataframe_column_contains_values(values: str | List[str], column_name):
    return lambda df: assert_series_contains_values(values, df[column_name])

def check_dataframe_columns_contain_values(contents: Dict[str, Union[str,List[str]]]):
    return lambda df: assert_dataframe_columns_contain_values(contents, df)

