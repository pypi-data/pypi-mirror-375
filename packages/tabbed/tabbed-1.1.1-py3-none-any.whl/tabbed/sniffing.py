"""Tools for determining the dialect and structure of a csv file that may
contain metadata, a header, and a data section.
"""

import warnings
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time
from itertools import chain
from types import SimpleNamespace
from typing import IO, List, Optional, Tuple

import clevercsv
from clevercsv.dialect import SimpleDialect

from tabbed.utils import parsing
from tabbed.utils.mixins import ReprMixin
from tabbed.utils.parsing import CellTypes


@dataclass(frozen=True)
class Header:
    """An immutable dataclass representation of a text file's header.

    Attributes:
        line:
            The integer line number of this Header. If None, the header was not
            derived from a file.
        names:
            The string names of each of the columns comprising the header. If
            these names contain spaces or repeat, this representation
            automatically amends them.
        string:
            The original string that was split to create header names.  If None,
            the names were not derived from a file.
    """

    line: int | None
    names: List[str]
    string: str | None

    def __post_init__(self) -> None:
        """Amend the names during initialization."""

        # relabel the names to replace spaces, repeats etc.
        names = self._amend()
        super().__setattr__('names', names)

    def _amend(self):
        """Ensures header names have no spaces and are unique.

        Header names may not have spaces. This function replaces spaces with
        underscores. Header names must be unique. This function adds an
        underscore plus an integer to names that repeat.
        """

        # replace any blank chars with underscores
        names = [name.strip().replace(' ', '_') for name in self.names]

        # replace repeating names with name_i variants for i in [0, inf)
        counted = Counter(names)
        mapping = {
            name: (
                [name] if cnt < 2 else [name + '_' + str(v) for v in range(cnt)]
            )
            for name, cnt in counted.items()
        }

        result = [mapping[name].pop(0) for name in names]
        return result


@dataclass(frozen=True)
class MetaData:
    """An immutable dataclass representing a text file's metadata section.

    Attributes:
        lines:
            A 2-tuple of start and stop of file lines containing metadata. If
            None, the file does not contain a metadata section.
        string:
            The string of metadata with no conversion read from file instance.
            If None, the file does not contain a metadata section.
    """

    lines: Tuple[int, int | None]
    string: str | None


class Sniffer(ReprMixin):
    r"""A tool for inferring the dialect and structure of a CSV file.

    The formatting of CSV files can vary widely. Python's builtin Sniffer is
    capable of handling different dialects (separators, line terminators, quotes
    etc) but assumes the first line within the file is a header or a row of
    unheaded data. In practice, many CSV files contain metadata prior to the
    header or data section. While these files are not compliant with CSV
    standards (RFC-4180), their broad use necessitates file sniffing that infers
    both dialect and structure. To date, some csv readers such as Pandas
    read_csv allow metadata rows to be skipped but no formal mechanism for
    sniffing dialect, metadata and header information exist. This Sniffer
    supports these operations.

    Attributes:
        infile:
            An open file, an IO instance.
        line_count:
            The number of lines in infile.
        start:
            The start line of infile for collecting a sample of 'amount' number
            of lines.
        amount:
            The number of infile lines to sample for dialect, header and
            metadata detection. The initial value defaults to the smaller of
            line_count or 100 lines. The amount should be large enough to
            include some of the data section of the file.
        skips:
            Line numbers to ignore during sample collection.

    Examples:
        >>> import tempfile
        >>> delimiter = ';'
        >>> # make a metadata and add to text that will be written to tempfile
        >>> metadata = {'exp': '3', 'name': 'Paul Dirac', 'date': '11/09/1942'}
        >>> text = [delimiter.join([key, val]) for key, val in metadata.items()]
        >>> # make a header and row to skip and add to text
        >>> header = delimiter.join('group count color'.split())
        >>> to_skip = delimiter.join('please ignore this line'.split())
        >>> text.extend([header, to_skip])
        >>> # make some data rows and add to text
        >>> group = 'a c b b c a c b c a a c'.split()
        >>> count = '22 2 13 15 4 19 4 21 5 24 18 1'.split()
        >>> color = 'r g b b r r r g g  b b g'.split()
        >>> data = [delimiter.join(row) for row in zip(group, count, color)]
        >>> text.extend(data)
        >>> # create a temp file and dump our text
        >>> outfile = tempfile.TemporaryFile(mode='w+')
        >>> _ = outfile.write('\n'.join(text))
        >>> # create a sniffer
        >>> sniffer = Sniffer(outfile)
        >>> # change the sample amount to 10 lines and skip line 4
        >>> # you would know to do this by inspecting the sample property
        >>> # and seeing the problematic line 4
        >>> sniffer.amount = 10
        >>> sniffer.skips = [4]
        >>> sniffer.sniff()
        >>> print(sniffer.dialect)
        SimpleDialect(';', '"', None)
        >>> # ask the sniffer to return a Header
        >>> header = sniffer.header(poll=4)
        >>> print(header)
        ... #doctest: +NORMALIZE_WHITESPACE
        Header(line=3,
        names=['group', 'count', 'color'],
        string='group;count;color')
        >>> # ask sniffer for the metadata given the header
        >>> sniffer.metadata(header)
        ... #doctest: +NORMALIZE_WHITESPACE
        MetaData(lines=(0, 3),
        string='exp;3\nname;Paul Dirac\ndate;11/09/1942')
        >>> # ask for the column types and consistency of types
        >>> # by polling the last 4 rows
        >>> types, consistent = sniffer.types(poll=4)
        >>> print(types)
        [<class 'str'>, <class 'int'>, <class 'str'>]
        >>> print(consistent)
        True
        >>> # close the temp outfile resource
        >>> outfile.close()
    """

    # help users set sane values for the sniffer
    # pylint: disable-next=R0917, dangerous-default-value
    def __init__(
        self,
        infile: IO[str],
        start: int = 0,
        amount: int = 100,
        skips: Optional[List[int]] = None,
        delimiters: List[str] | None = [',', ';', '|', '\t'],
    ) -> None:
        """Initialize this sniffer.

        Args:
            infile:
                A I/O stream instance such as returned by open.
            start:
                The start line of infile for collecting a sample of lines.
            amount:
                The number of infile lines to sample for dialect detection and
                locating header and metadata positions. The initial value defaults
                to the smaller of the infiles length or 100 lines.
            skips:
                Line numbers to ignore during sample collection.
            delimiters:
                A restricted list of delimiter strings for improving dialect
                detection. If None, any character will be considered a valid
                delimiter.

        Raises:
            SoptIteration: is raised if start is greater than infile's size.

        Notes:
            Sniffer deviates from Python's Sniffer in that infile is strictly an
            IO stream, not a list because detecting the metadata and header
            structures requires movement within the file via 'seek'.
        """

        self.infile = infile
        self.infile.seek(0)
        self._start = start
        self._amount = amount
        self._skips = skips if skips else []
        # get sample for infile and sniff
        self._resample()
        self.sniff(delimiters)

    @property
    def start(self) -> int:
        """Returns the start line of this Sniffer's sample."""

        return self._start

    @start.setter
    def start(self, value: int) -> None:
        """Sets the start line & updates this Sniffer's sample

        Args:
            value:
                A new sample start line.
        """

        self._start = value
        self._resample()

    @property
    def amount(self) -> int:
        """Returns the number of lines in Sniffer's sample."""

        return self._amount

    @amount.setter
    def amount(self, value: int) -> None:
        """Sets the number of lines & updates this Sniffer's sample.

        Args:
            value:
                The new number of joined lines in the sample.
        """

        self._amount = value
        self._resample()

    @property
    def skips(self) -> List[int]:
        """Returns the skipped lines excluded from this Sniffer's sample."""

        return self._skips

    @skips.setter
    def skips(self, other: List[int]) -> None:
        """Sets the lines to exclude from this Sniffer's sample."""

        self._skips = other
        self._resample()

    @property
    def sample(self) -> str:
        """Returns this Sniffer's sample string."""

        return self._sample

    @property
    def lines(self) -> List[int]:
        """Returns a list of integer line numbers comprising the sample."""

        return self._lines

    @property
    def dialect(self) -> SimpleDialect | None:
        """Returns this Sniffer's dialect."""

        return self._dialect

    @dialect.setter
    def dialect(self, value: SimpleDialect | None) -> None:
        """Sets this Sniffer's dialect.

        Args:
            dialect:
                A clevercsv SimpleDialect instance containing a delimiter,
                escape character and quote character.

        Returns:
            None
        """

        if value:
            # python 3.11 deprecated '' for delimiter, escape & quotechars
            delimiter = '\r' if value.delimiter == '' else value.delimiter
            escapechar = None if value.escapechar == '' else value.escapechar
            quotechar = '"' if not value.quotechar else value.quotechar
            value.delimiter = delimiter
            value.escapechar = escapechar
            value.quotechar = quotechar

        self._dialect = value

    @property
    def rows(self) -> List[List[str]]:
        """Returns list of sample rows from this Sniffer's sample string.

        This method splits the sample string on new line chars, strips white
        spaces and replaces all double-quotes with single quotes.

        Returns:
            A list of list of strings from the sample string
        """

        if self.dialect is None:
            msg = "Dialect is unknown, please call sniff method or set dialect."
            raise TypeError(msg)

        result = []
        delimiter = self.dialect.delimiter

        # single column data uses carriage return delimiter
        if delimiter == '\r':
            return [
                [astr.replace('"', '')] for astr in self.sample.splitlines()
            ]

        # split sample_str on terminators, strip & split each line on delimiter
        for line in self.sample.splitlines():
            # lines may end in delimiter leading to empty trailing cells
            stripped = line.rstrip(delimiter)
            row = stripped.split(self.dialect.delimiter)
            # remove any double quotes
            row = [astring.replace('"', '') for astring in row]
            result.append(row)

        return result

    def _move(self, line: int) -> None:
        """Moves the line pointer in this file to line number.

        Args:
            line:
                A line number to move to within this Sniffer's infile.

        Returns:
            None but advances the line pointer to line.

        Raises:
            A StopIteration is issued if line is greater than Sniffer's infile
            size.
        """

        self.infile.seek(0)
        for _ in range(line):
            next(self.infile)

    def _resample(self) -> None:
        """Sample from infile using the start, amount and skip properties."""

        self._move(self.start)
        result = SimpleNamespace(indices=[], linestrs=[])
        amount = self.amount + len(self.skips)
        for current in range(self.start, amount + self.start):

            line = self.infile.readline()
            # only store non-blank lines
            if current not in self.skips and line:
                result.linestrs.append(line)
                result.indices.append(current)

        # move line pointer back to start of the file
        self._move(0)
        sampled = ''.join(result.linestrs)
        self._sample: str = sampled
        self._lines: List[int] = result.indices

    def sniff(self, delimiters: Optional[List[str]] = None) -> None:
        """Returns a clevercsv SimpleDialect from this instances sample.

        Dialect is detected using clevercsv's sniffer as it has shown improved
        dialect detection accuracy over Python's csv sniffer built-in.

        Args:
            delimiters:
                A string of possibly valid delimiters see csv.Sniffer.sniff.

        Returns:
            A SimpleDialect instance (see clevercsv.dialect) or None if sniffing
            is inconclusive.

        References:
            van den Burg, G.J.J., Nazábal, A. & Sutton, C. Wrangling messy CSV
            files by detecting row and type patterns. Data Min Knowl Disc 33,
            1799–1820 (2019). https://doi.org/10.1007/s10618-019-00646-y
        """

        # result is None if clevercsv's sniff is indeterminant
        result = clevercsv.Sniffer().sniff(self.sample, delimiters=delimiters)
        if result is None:
            msg1 = "Dialect could not be determined from Sniffer's sample.  "
            msg2 = "Please set this Sniffer's dialect attribute."
            warnings.warn(msg1 + msg2)
            self._dialect = None
        else:
            self.dialect = result

    # no mutation of exclude list here
    # pylint: disable-next=dangerous-default-value
    def types(
        self,
        poll: int,
        exclude: List[str] = ['', ' ', '-', 'nan', 'NaN', 'NAN'],
    ) -> Tuple[CellTypes, bool]:
        """Infer the column types from the last poll count rows.

        Args:
            poll:
                The number of last sample rows to poll for type.
            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored for type determination.

        Returns:
            A list of types and a boolean indicating if types are
            consistent across polled rows. Ints, floats and complex within the
            same column are defined as consistent.
        """

        rows = self.rows[-poll:]
        rows = [row for row in rows if not bool(set(exclude).intersection(row))]
        if not rows:
            msg = (
                f'Types could not be determined as last {poll} polling '
                f'rows all contained at least one exclusion {exclude}. Try '
                'increasing the number of polling rows.'
            )
            raise RuntimeError(msg)

        cols = list(zip(*rows))
        type_cnts = [
            Counter([type(parsing.convert(el)) for el in col]) for col in cols
        ]

        consistent = True
        for s in [set(cnts) for cnts in type_cnts]:
            # inconsistent if > 1 type per column & any non-numerics
            if len(s) > 1 and not s.issubset({float, int, complex}):
                consistent = False
                break

        common_types = [cnt.most_common(1)[0][0] for cnt in type_cnts]

        return common_types, consistent

    # no mutation of exclude list here
    # pylint: disable-next=dangerous-default-value
    def datetime_formats(
        self,
        poll: int,
        exclude: List[str] = ['', ' ', '-', 'nan', 'NaN', 'NAN'],
    ) -> Tuple[List[str | None], bool]:
        """Infer time, date or datetime formats from last poll count rows.

        Args:
            poll:
                The number of last sample rows to poll for type and format
                consistency.

        Returns:
            A tuple containing a list of formats the same length as last polled
            row and a boolean indicating if the formats are consistent across
            the polled rows. Columns that are not time, date or datetime type
            have a format of None.
        """

        fmts = {
            time: parsing.time_formats(),
            date: parsing.date_formats(),
            datetime: parsing.datetime_formats(),
        }
        polled = []
        for row in self.rows[-poll:]:
            row_fmts = []
            for astring, tp in zip(row, self.types(poll, exclude)[0]):
                fmt = (
                    parsing.find_format(astring, fmts[tp])
                    if tp in fmts
                    else None
                )
                row_fmts.append(fmt)
            polled.append(row_fmts)

        # consistency within each column of polled
        consistent = all(len(set(col)) == 1 for col in list(zip(*polled)))

        return polled[-1], consistent

    def _length_diff(
        self,
        poll: int,
        exclude: List[str],
    ) -> Tuple[int | None, List[str] | None]:
        """Locates metadata by identifying the first row from the end of the
        sample whose length does not match the length of the last poll rows.

        This method assumes that the metadata row lengths do not match the data
        row lengths. This can obviously be untrue but detecting the difference
        between a header row whose length must match the number of data columns
        from a metadata row with the same number of columns is challenging.

        Args:
            poll:
                The number of last sample rows to poll for common types.
            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored.

        Returns:
            A 2-tuple of integer line number and the metadata row if found and
            a 2-tuple of Nones otherwise.
        """

        types, _ = self.types(poll, exclude)
        for idx, row in reversed(list(zip(self.lines, self.rows))):

            if len(row) != len(types):
                return idx, row

        return None, None

    def _type_diff(
        self,
        poll: int,
        exclude: List[str],
    ) -> Tuple[int | None, List[str] | None]:
        """Locates a header row by looking for the first row from the last of
        this Sniffer's rows whose types do not match the last polled row types.

        This heuristic assumes a consistent type within a column of data. If
        this is found to be untrue it returns a two-tuple of Nones. Ints, floats
        and complex are treated as consistent by type_diff.

        Args:
            poll:
                The number of last sample rows to poll for common types.
            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored.

        Returns:
            A 2-tuple integer line number and header row or a 2-tuple of Nones.
        """

        types, consistent = self.types(poll, exclude)

        if not consistent:
            msg = 'Detection failure due to inconsistent column data types'
            warnings.warn(msg)
            return None, None

        # int, float and complex mismatches are not type mismatches
        numerics = {int, float, complex}
        for idx, row in reversed(list(zip(self.lines, self.rows))):

            # ignore rows that have missing values
            if bool(set(exclude).intersection(row)):
                continue

            if len(row) != len(types):
                # we've encountered a metadata row without hitting a header
                return None, None

            row_types = [type(parsing.convert(el)) for el in row]
            # check types
            for typ, expect in zip(row_types, types):
                if typ != expect and not {typ, expect}.issubset(numerics):
                    return idx, row

        return None, None

    def _string_diff(
        self,
        poll: int,
        exclude: List[str],
        len_requirement: bool = True,
    ) -> Tuple[int | None, List[str] | None]:
        """Locates first row from last whose strings have no overlap with
        strings in the last poll rows.

        Args:
            poll:
                The number of last sample rows to poll for string values.

            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored.
            len_requirement:
                A boolean indicating if the first row from last with a type
                mismatch must have the same length as the last row of the
                sample. This will be True for headers and False for metadata.

        Returns:
            An integer line number and header row or a 2-tuple of Nones
        """

        observed = set(chain.from_iterable(self.rows[-poll:]))
        for idx, row in reversed(list(zip(self.lines, self.rows))):

            items = set(row)
            # ignore rows with missing values
            if bool(set(exclude).intersection(items)):
                continue

            # check disjoint with observed and completeness
            disjoint = items.isdisjoint(observed)
            complete = len(row) == len(self.rows[-1])

            if not len_requirement:
                # complete is always True if no length requirement
                complete = True

            if disjoint and complete:
                return idx, row

            # add unseen items to observed
            observed.update(items)

        return None, None

    # no mutation of exclude list here
    # pylint: disable-next=dangerous-default-value
    def header(
        self,
        poll: int,
        exclude: List[str] = ['', ' ', '-', 'nan', 'NaN', 'NAN'],
    ) -> Header:
        """Detects the header row (if any) from this Sniffers sample rows.

        Headers are located using one of two possible methods.
            1. If the last row contains mixed types and the last poll rows have
               consistent types, then the first row from the last whose types
               differ from the last row types and whose length matches the last
               row is taken as the header.
            2. If the last poll rows are all string type. The first row from the
               last with string values that have never been seen in the previous
               rows and whose length matches the last row is taken to be the
               header. Caution, the poll amount should be sufficiently large
               enough to sample the possible string values expected in the data
               section. If the header is not correct, consider increasing the
               poll rows parameter.

        Args:
            poll:
                The number of last sample rows to poll for locating the header
                using string or type differences. Poll should be large enough to
                capture many of the string values that appear in the data
                section.
            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored.

        Notes:
            If no header is detected this method constructs a header. The names
            in this header are of the form; 'Column_1', ... 'Column_n' where
            n is the expected number of columns from the last row of the sample
            rows.  Just like all other file sniffers, this heuristic will make
            mistakes.  A judicious sample choice that ignores problematic rows
            via the skip parameter may aide detection.

        Returns:
            A Header dataclass instance.
        """

        types, _ = self.types(poll, exclude)
        if all(typ == str for typ in types):
            line, row = self._string_diff(poll, exclude)

        else:
            line, row = self._type_diff(poll, exclude)

        if line is None:
            row = [f'Column_{i}' for i in range(len(self.rows[-1]))]

        # type-narrow for mypy check-- row can no longer be None
        assert isinstance(row, list)
        # get original string if line
        if line is not None:
            # string should include the rows we skipped so use sample not rows
            s = self.sample.splitlines()[self.lines.index(line)]
        else:
            s = None

        return Header(line=line, names=row, string=s)

    # no mutation of exclude list here
    # pylint: disable-next=dangerous-default-value
    def metadata(
        self,
        header: Header | None,
        poll: Optional[int] = None,
        exclude: List[str] = ['', ' ', '-', 'nan', 'NaN', 'NAN'],
    ) -> MetaData:
        """Detects the metadata section (if any) in this Sniffer's sample.

        Args:
            header:
                A Header dataclass instance.
            poll:
                The number of last sample rows to poll for locating metadata by
                length differences if the header arg is None.
            exclude:
                A sequence of characters that indicate missing values. Rows
                containing these strings will be ignored during metadata
                detection. This is ignored if a header is given.

        Returns:
            A MetaData dataclass instance.
        """

        # if header provided get lines upto header line
        if header and header.line:
            idx = self.lines.index(header.line)
            s = '\n'.join(self.sample.splitlines()[0:idx])
            return MetaData((0, header.line), s)

        if not header and poll is None:
            msg = 'Arguments header and poll cannot both be None type'
            raise ValueError(msg)

        # type narrow poll to int type for mypy
        assert isinstance(poll, int)
        line, _ = self._length_diff(poll, exclude)
        if line is not None:
            metarows = self.sample.splitlines()[: line + 1]
            string = '\n'.join(metarows)
            return MetaData((0, line + 1), string)

        return MetaData((0, None), None)


if __name__ == '__main__':

    import doctest

    doctest.testmod()
