import os
import tempfile
import webbrowser
from dataclasses import dataclass, field
from functools import lru_cache
from html import escape
from typing import Dict, Any, List, Callable

import pandas as pd
import pytest

from cooper_epic_jungle import COOPER_EPIC_JUNGLE
from mipi_datamanager import JinjaRepo
import sqlglot
from sqlglot.errors import ParseError

def _show_html(html: str, title: str) -> None:
    _html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    </head>
    <body>
    {html}
    </body>
    </html>"""

    # Write HTML to a temporary file and open it in the default browser
    with tempfile.NamedTemporaryFile('w', suffix=".html", delete=False, encoding='utf-8') as f:
        f.write(_html)
        path = f.name
    url = f"file://{os.path.abspath(path)}"
    # new=2 tries to open a new browser window
    webbrowser.open(url, new=2)

@dataclass
class DefaultCase:
    name: str
    sql_checks:              List[str]                            = field(default_factory=list)
    df_checks:               List[Callable[[pd.DataFrame], bool]] = field(default_factory=list)

@dataclass
class CustomCase:
    name: str
    params: Dict[str, Any]
    sql_checks:              List[str]                            = field(default_factory=list)
    df_checks:               List[Callable[[pd.DataFrame], bool]] = field(default_factory=list)
    show_df_rows: int = None
    show_sql: bool = False


class Base:
    SCRIPT: str = None
    JUNGLE: JinjaRepo  = None
    DEFAULT_PARAMS: dict  = {}
    SHOW_DF_ROWS: int = None
    SHOW_SQL: bool = False
    CASES: list = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._updated_params = cls._calculate_jinja_params()
        cls.validate_config()

    @classmethod
    def validate_config(cls):

        if not getattr(cls, "JUNGLE", None) or not getattr(cls, "SCRIPT", None):
            return

        try:
            cfg = cls.JUNGLE.get_config(cls.SCRIPT)
        except KeyError as e:
            raise KeyError(f"Config {e} not found in JUNGLE")

        try:
            meta: dict = cfg.get("meta", {})
            population: bool = meta.get("population")
            join_key = meta.get("join_key")
        except KeyError as e:
            raise Exception(f"Config invalid {e} not found in config")

        if not population:
            temp_table_name = join_key # FIXME needs to supoort multiple keys
            if temp_table_name not in cls.DEFAULT_PARAMS.keys() or []:
                raise AssertionError(f"Invalid test: {cls.SCRIPT} requires DEFAULT_PARAMETER: {temp_table_name} for inserts")



    @classmethod
    def _calculate_jinja_params(cls):
        params = {}

        if cls.DEFAULT_PARAMS is not None:
            params.update(**cls.DEFAULT_PARAMS)

        return params

    @classmethod
    def _add_bases(cls):

        if cls.CASES:

            # as
            base = type("BaseInjectTests",(type,),)

            cls.__bases__ += base
        pass

class BaseExecute(Base):


    @classmethod
    def _show_df(cls, df: pd.DataFrame, title: str) -> None:
        html = df.head(cls.SHOW_DF_ROWS).to_html()
        _show_html(html, title)

    @classmethod
    @lru_cache
    def _execute_query(cls):
        df = cls.JUNGLE.execute_file(cls.SCRIPT, jinja_parameters_dict= cls._updated_params)
        if cls.SHOW_DF_ROWS:
            cls._show_df(df, "Query Base")
        return df

    @pytest.fixture(scope = "class")
    def default_df(self):
        return self._execute_query()

    @pytest.mark.query_df
    def test_default_df_is_dataframe(self):
        assert isinstance(self._execute_query(), pd.DataFrame)

    @pytest.mark.query_df
    def test_query_checks_default(self, case: DefaultCase, default_df: pd.DataFrame):
        for check in case.df_checks:
            check(default_df), f"DataFrame check {check!r} failed for case {case.name}"

    @pytest.mark.query_df
    def test_query_checks_custom(self, case: CustomCase):
        df = self.JUNGLE.execute_file(self.SCRIPT, jinja_parameters_dict= case.params)
        if case.show_df_rows:
            self._show_df(df, f"Query {case.name}")
        for check in case.df_checks:
            check(df), f"DataFrame check {check!r} failed for case {case.name}"


class BaseRender(Base):


    @classmethod
    def _display_sql(cls, sql, title: str) -> None:
        safe_sql = escape(sql)
        html = (
            "<pre style='white-space: pre-wrap; font-family: monospace;'>"
            f"{safe_sql}"
            "</pre>"
        )
        _show_html(html, title)

    @classmethod
    @lru_cache
    def _resolve_sql(cls):
        sql = cls.JUNGLE.resolve_file(cls.SCRIPT, jinja_parameters_dict= cls._updated_params)
        if cls.SHOW_SQL:
            cls._display_sql(sql, "Render Base")
        return sql

    @pytest.fixture(scope = "class")
    def default_resolved_sql(self):
        return self._resolve_sql()

    @pytest.mark.query_df
    def test_default_sql_is_string(self):
        sql = self.JUNGLE.resolve_file(self.SCRIPT)
        assert type(sql) == str

    @pytest.mark.query_df
    def test_default_sql_no_hanging_jinja_tags(self, default_resolved_sql):
        JINJA_TAGS = ["{{", "{%", "{#", "#}", "%}", "}}"]

        for t in JINJA_TAGS:
            assert t not in default_resolved_sql, f"Error Jinja Tag: {t} found in resolved sql"

    @pytest.mark.query_df
    def test_is_valid_sql(self, default_resolved_sql):

        try:
            sqlglot.parse(default_resolved_sql, read='tsql')
        except ParseError as e:
            pytest.fail(f"T‑SQL syntax error in {self.SCRIPT!r}: {e}")

    @pytest.mark.render_sql
    def test_render_checks_default(self, case: DefaultCase, default_resolved_sql: str):
        for check in case.sql_checks:
            check(default_resolved_sql), f"SQL check {check!r} failed for case {case.name}"

    @pytest.mark.render_sql
    def test_render_checks_custom(self, case: CustomCase):
        sql = self.JUNGLE.resolve_file(self.SCRIPT, jinja_parameters_dict= case.params)
        if case.show_sql:
            self._display_sql(sql, f"Render {case.name}")
        for check in case.sql_checks:
            check(sql), f"SQL check {check!r} failed for case {case.name}"

class BaseConfig(Base):

    @pytest.mark.config
    def test_config_path_matches(self):
        sql_path = os.path.join(self.JUNGLE.root_dir,self.SCRIPT)
        assert os.path.exists(sql_path), f"Expected SQL file {sql_path!r} to exist"

    @pytest.mark.config
    def test_config_has_required_keys(self):
        EXPECTED_KEYS = ["jinja_parameters_dict", "meta"]
        cfg = self.JUNGLE.get_config(self.SCRIPT)
        assert all([k in cfg.keys() for k in EXPECTED_KEYS])

        EXPECTED_META_KEYS = ["name", "join_key", "connection", "description", "population"]
        meta = cfg.get("meta")
        assert all([k in meta.keys() for k in EXPECTED_META_KEYS])

class BaseTests(BaseExecute, BaseRender, BaseConfig):
    JUNGLE = COOPER_EPIC_JUNGLE