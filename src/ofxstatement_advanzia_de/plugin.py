import pdfplumber
import re
from datetime import datetime
from decimal import Decimal as D

from typing import Iterable

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import Statement, StatementLine


# day, month, year, info, amount
EXTRACTOR = re.compile(r"^(\d{2}\.\d{2}\.\d{4}) (.+) (-?[\.\d]+,\d{2})$")

class AdvanziaDEPlugin(Plugin):
    """ofxstatement plugin to import German Advanzia statements (Schmetterling Mastercard)"""

    def get_parser(self, filename: str) -> "AdvanziaDEParser":
        return AdvanziaDEParser(filename)


class AdvanziaDEParser(StatementParser[str]):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename

    def parse(self) -> Statement:
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        with pdfplumber.open(self.filename) as pdf:
            self.pdf = pdf
            stmt = super().parse()
            stmt.bank_id = "ADVZLULLXXX"
            stmt.currency = "EUR"
            return stmt

    def split_records(self) -> Iterable[str]:
        """Return iterable object consisting of a line per transaction"""
        txns = []
        state = 0 # 0 = outside table, 1 = inside table
        for page in self.pdf.pages:
            chars = []
            for obj in page.chars:
                chars.append((-round(obj["y0"]), obj["x0"], obj["text"]))
            chars.sort()
            lines = {}
            lastx = 0
            for c in chars:
                y = c[0]
                if y not in lines:
                    lines[y] = ""
                if c[1] - lastx > 9.4:
                    lines[y] = lines[y] + " "
                lines[y] = lines[y] + c[2]
                lastx = c[1]
            for y in sorted(lines.keys()):
                line = lines[y]
                if line.startswith("ALTER SALDO"):
                    state = 1
                    continue
                if "NEUER SALDO" in line:
                    state = 0
                    continue
                if state == 1:
                    txns.append(line)
        return txns

    def parse_record(self, line: str) -> StatementLine:
        """Parse given transaction line and return StatementLine object"""
        print("parse?", line)
        m = EXTRACTOR.match(line)
        if not m:
            print("WARNING: could not parse", line)
            return None
        date = datetime.strptime(m.group(1), "%d.%m.%Y")
        info = m.group(2)
        amount = D(m.group(3).replace(".", "").replace(",", "."))

        memo = None
        payee = None
        if info == 'ZAHLUNG AUFS GIROKONTO' or info == 'SOLLZINSEN' or info == 'Zahlung per Lastschrift':
            memo = info
        else:
            payee = info

        line = StatementLine(hex(hash(info))[2:10],
            date=date,
            memo=memo,
            amount=-amount
        )
        line.payee = payee
        if payee:
            line.trntype = "CREDIT"
        else:
            line.trntype = "XFER"
        return line
