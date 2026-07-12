"""Tests for document list entity filters."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AppError
from app.modules.documents.service import list_documents


def _mock_query() -> MagicMock:
    query = MagicMock()
    query.filter.return_value = query
    query.join.return_value = query
    query.distinct.return_value = query
    query.order_by.return_value = query
    query.count.return_value = 0
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = []
    return query


class TestListDocumentsEntityFilter:
    def test_requires_entity_type_and_id_together(self):
        db = MagicMock()
        with pytest.raises(AppError, match="entity_type and entity_id must be provided together"):
            list_documents(db, uuid4(), 1, 20, entity_type="procurement", entity_id=None)
        with pytest.raises(AppError, match="entity_type and entity_id must be provided together"):
            list_documents(db, uuid4(), 1, 20, entity_type=None, entity_id=uuid4())

    def test_joins_links_when_entity_filter_present(self):
        db = MagicMock()
        query = _mock_query()
        db.query.return_value = query
        entity_id = uuid4()

        items, total = list_documents(
            db,
            uuid4(),
            1,
            20,
            entity_type="procurement",
            entity_id=entity_id,
        )

        assert items == []
        assert total == 0
        query.join.assert_called_once()
        query.distinct.assert_called_once()

    def test_skips_join_without_entity_filter(self):
        db = MagicMock()
        query = _mock_query()
        db.query.return_value = query

        list_documents(db, uuid4(), 1, 20)

        query.join.assert_not_called()
