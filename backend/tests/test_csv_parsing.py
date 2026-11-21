"""Unit tests for the shared CSV reading tools. No database is used."""

import pytest

from app.services.csv_parsing import ImportFileError, decode_csv, read_rows

COLUMNS = ("trade_date", "ticker", "side", "quantity", "price")
HEADER = ",".join(COLUMNS) + "\n"
LINE = "2026-03-16,BHP,BUY,100,45.25\n"
MAX_ROWS = 5


def read(text: str):
    return read_rows(text, COLUMNS, MAX_ROWS)


def test_rows_are_numbered_from_two_with_names_and_values_tidied():
    rows = read("Trade_Date, ticker ,side,quantity,price\n2026-03-16, bhp ,buy,100,45.25\n")

    assert rows == [
        (
            2,
            {
                "trade_date": "2026-03-16",
                "ticker": "bhp",
                "side": "buy",
                "quantity": "100",
                "price": "45.25",
            },
        )
    ]


def test_blank_lines_are_skipped_and_row_numbers_still_match_the_file():
    rows = read(HEADER + "\n" + LINE + ",,,,\n")

    assert [row_number for row_number, _ in rows] == [3]


def test_extra_columns_are_kept_and_short_rows_have_missing_keys():
    rows = read("trade_date,ticker,side,quantity,price,notes\n2026-03-16,BHP,BUY\n")

    assert rows == [(2, {"trade_date": "2026-03-16", "ticker": "BHP", "side": "BUY"})]


def test_empty_file_is_rejected():
    with pytest.raises(ImportFileError, match="empty"):
        read("")


def test_file_with_only_a_header_is_rejected():
    with pytest.raises(ImportFileError, match="no data rows"):
        read(HEADER)


def test_missing_required_column_is_rejected():
    with pytest.raises(ImportFileError, match="missing required columns: side, price"):
        read("trade_date,ticker,quantity\n2026-03-16,BHP,100\n")


def test_too_many_rows_are_rejected():
    assert len(read(HEADER + LINE * MAX_ROWS)) == MAX_ROWS
    with pytest.raises(ImportFileError, match=f"more than {MAX_ROWS} rows"):
        read(HEADER + LINE * (MAX_ROWS + 1))


def test_decode_removes_the_marker_excel_adds():
    assert decode_csv(b"\xef\xbb\xbfticker\n") == "ticker\n"


def test_decode_rejects_bytes_that_are_not_utf8():
    with pytest.raises(ImportFileError, match="UTF-8"):
        decode_csv(b"\xff\xfe\x00")
