from pymarc import (Field, Indicators, Subfield, Record)

from rara_tools.constants import EMPTY_INDICATORS
from rara_tools.normalizers.viaf import VIAFRecord
from rara_tools.normalizers import RecordNormalizer

from typing import List


class BibRecordNormalizer(RecordNormalizer):
    """ Normalize bib records. """

    def __init__(self, linking_results: List[dict] = [], sierra_data: List[dict] = [],
                 ALLOW_EDIT_FIELDS: List[str] = ["008", "925"],
                 REPEATABLE_FIELDS: List[str] = ["667"]):
        super().__init__(linking_results, sierra_data)
        self.DEFAULT_LEADER = "00399nz  a2200145n  4500" # must be 24 digits
        self.ALLOW_EDIT_FIELDS = ALLOW_EDIT_FIELDS
        self.REPEATABLE_FIELDS = REPEATABLE_FIELDS
        
        self.records_extra_data = []
        self.sierra_data = sierra_data
        self.records = self._setup_records(linking_results, sierra_data)

    def _normalize_sierra(self, record: Record) -> Record:
        
        suffix_008 = "|||aznnnaabn          || |||      "
        
        fields = [
            Field(
                tag="008",
                data=f"{self.current_timestamp()}{suffix_008}"
            ),
        ]

        self._add_fields_to_record(record, fields)

    def _normalize_viaf(self, record: Record, viaf_record: VIAFRecord) -> None:

        if not viaf_record:
            return record

        viaf_id = viaf_record.viaf_id
        fields = [
            Field(
                tag="035",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("a", viaf_id)
                ]
            )
        ]

        self._add_fields_to_record(record, fields)
        self._add_author(record, viaf_record)

    def _normalize_record(self, record: Record, sierraID: str,
                          viaf_record: VIAFRecord, is_editing_existing_record: bool) -> Record:

        self._normalize_sierra(record)
        self._normalize_viaf(record, viaf_record)

        return record
