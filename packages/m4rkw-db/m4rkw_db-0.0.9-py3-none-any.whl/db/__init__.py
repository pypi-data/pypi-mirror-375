import re
import sys
from typing import Any, Callable, Self, cast

import MySQLdb  # type: ignore[import-untyped]


class DB():

    def __getattr__(self, name: str) -> Callable[..., dict[str, Any] | None]:
        match = re.match(r'^find_([\w]+)_by_(.*?)$', name)

        if match:
            table = match.group(1)
            fields = match.group(2).split('_and_')

            def find_object_by_fields(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
                sql = "select * from `" + table + "` where "

                for i in range(0, len(fields)):
                    if i >0:
                        sql += " and "
                    sql += "`" + fields[i] + "` = %s"

                return self.one(sql, cast(list[Any], args))

            return find_object_by_fields
        else:
            print("DB class method missing: %s" % (name))
            sys.exit(1)


    def __init__(self, config: dict[str, str | int]) -> None:
        self.config = config
        self.orderBy: str | None = None
        self.orderDir: str | None = None


    def connect(self) -> None:
        self.db = MySQLdb.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            passwd=self.config['password'],
            db=self.config['database'],
            charset='utf8',
            use_unicode=True,
            ssl={}
        )
        self.cur = self.db.cursor()


    def query(self, sql: str, params: list[Any] = []) -> list[dict[str, Any]] | None:
        self.connect()
        self.cur.execute((sql), params)

        if sql[0:6].lower() == "select":
            self.db.commit()
            return self.build_rows(self.cur.fetchall())

        self.db.commit()

        return None


    def one(self, sql: str, params: list[Any] = []) -> dict[str, Any] | None:
        rows = self.query(sql, params)

        if rows is None:
            return None

        if len(rows) >0:
            return rows[0]

        return None


    def build_row(self, data: list[Any]) -> dict[str, Any]:
        row = {}

        for i in range(0, len(self.cur.description)):
            row[self.cur.description[i][0]] = data[i]

        return row


    def build_rows(self, data: list[list[Any]]) -> list[dict[str, Any]]:
        rows = []

        for item in data:
            rows.append(self.build_row(item))

        return rows


    def find(self, table: str) -> Self:
        self.sel = '*'
        self.query_table = table
        self.whereClauses: list[str] = []
        self.whereParams: list[Any] = []
        self.whereType = 'and'
        self.orderBy = None
        self.orderDir = None
        self._join: list[dict[str, str]] = []
        self._leftJoin: list[dict[str, str]] = []

        return self


    def select(self, select_str: str) -> Self:
        self.sel = select_str

        return self


    def where(self, where: str, *whereParams: list[Any]) -> Self:
        self.whereClauses.append(where)
        self.whereParams += whereParams

        return self


    def orderby(self, field: str, direction: str = 'asc') -> Self:
        self.orderBy = field
        self.orderDir = direction

        return self


    def join(self, join_table: str, join_left_col: str, join_right_col: str | None = None) -> Self:
        if join_right_col:
            self._join.append({
                'table': join_table,
                'join_left_col': join_left_col,
                'join_right_col': join_right_col
            })
        else:
            self._join.append({
                'table': join_table,
                'clause': join_left_col
            })

        return self


    def leftJoin(self, join_table: str, join_left_col: str, join_right_col: str | None = None) -> Self:
        if join_right_col:
            self._leftJoin.append({
                'table': join_table,
                'join_left_col': join_left_col,
                'join_right_col': join_right_col
            })
        else:
            self._leftJoin.append({
                'table': join_table,
                'clause': join_left_col
            })

        return self


    def orWhere(self, whereClause: str, whereParams: list[Any] = []) -> Self:
        self.whereType = 'or'

        return self.where(whereClause, whereParams)


    def prepare(self) -> str:
        sql = "select " + self.sel + " from `" + self.query_table + "`"

        for join in self._join:
            sql += " join `" + join['table'] + "` on "

            if 'clause' in join:
                sql += join['clause']
            else:
                sql += join['join_left_col'] + " = " + join['join_right_col']

        for join in self._leftJoin:
            sql += " left join `" + join['table'] + "` on "

            if 'clause' in join:
                sql += join['clause']
            else:
                sql += join['join_left_col'] + " = " + join['join_right_col']

        for i in range(0, len(self.whereClauses)):
            if i >0:
                sql += " " + self.whereType + " "
            else:
                sql += " where "

            sql += self.whereClauses[i]

        if self.orderBy:
            sql += " order by `" + self.orderBy + "`"

        if self.orderDir:
            sql += " " + self.orderDir

        return sql


    def getone(self) -> dict[str, Any] | None:
        sql = self.prepare() + " limit 1"

        return self.one(sql, self.whereParams)


    def getall(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        result = self.query(self.prepare(), self.whereParams)

        if result is None:
            return rows

        for row in result:
            rows.append(row)

        return rows


    def get_raw_query(self) -> str:
        sql = self.prepare()

        raw_sql = ''

        n = 0
        skip = False

        for i in range(0, len(sql)):
            if skip:
                skip = False
                continue

            if sql[i:i+2] == '%s':
                raw_sql += "'" + self.whereParams[n] + "'"
                n += 1
                skip = True
            else:
                raw_sql += sql[i]

        return raw_sql
