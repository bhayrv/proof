"""
PROOF Protocol — Graph Tests

Tests graph relationships defined in spec/PROOF.md §7.
"""

from proof.graph import ProofGraph, ProofRelation, Relation


def _id(n: int) -> str:
    """Generate a fake PROOF identity for testing."""
    return f"sha256:{n:064x}"


class TestRelationEnum:
    """Tests for the Relation enum."""

    def test_all_relations_defined(self):
        expected = {"supports", "contradicts", "supersedes", "derived_from", "corroborates"}
        actual = {r.value for r in Relation}
        assert actual == expected

    def test_relation_is_string(self):
        assert Relation.SUPPORTS == "supports"
        assert Relation.CONTRADICTS == "contradicts"


class TestProofRelation:
    """Tests for the ProofRelation dataclass."""

    def test_to_dict_minimal(self):
        rel = ProofRelation(
            source_id=_id(1),
            target_id=_id(2),
            relation=Relation.SUPPORTS,
        )
        d = rel.to_dict()
        assert d["source_id"] == _id(1)
        assert d["target_id"] == _id(2)
        assert d["relation"] == "supports"
        assert "metadata" not in d

    def test_to_dict_with_metadata(self):
        rel = ProofRelation(
            source_id=_id(1),
            target_id=_id(2),
            relation=Relation.CONTRADICTS,
            metadata={"reason": "Conflicting data"},
        )
        d = rel.to_dict()
        assert d["metadata"]["reason"] == "Conflicting data"


class TestProofGraph:
    """Tests for the in-memory ProofGraph."""

    def test_add_and_list(self):
        graph = ProofGraph()
        rel = ProofRelation(_id(1), _id(2), Relation.SUPPORTS)
        graph.add(rel)
        assert len(graph.relations) == 1

    def test_find_by_source(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(2), Relation.SUPPORTS))
        graph.add(ProofRelation(_id(1), _id(3), Relation.CONTRADICTS))
        graph.add(ProofRelation(_id(2), _id(3), Relation.SUPERSEDES))

        results = graph.find_by_source(_id(1))
        assert len(results) == 2

    def test_find_by_target(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(3), Relation.SUPPORTS))
        graph.add(ProofRelation(_id(2), _id(3), Relation.CORROBORATES))

        results = graph.find_by_target(_id(3))
        assert len(results) == 2

    def test_find_by_relation(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(2), Relation.SUPPORTS))
        graph.add(ProofRelation(_id(3), _id(4), Relation.SUPPORTS))
        graph.add(ProofRelation(_id(5), _id(6), Relation.CONTRADICTS))

        results = graph.find_by_relation(Relation.SUPPORTS)
        assert len(results) == 2

    def test_contradictions(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(2), Relation.CONTRADICTS))
        graph.add(ProofRelation(_id(3), _id(2), Relation.SUPPORTS))

        # Check as target
        results = graph.contradictions(_id(2))
        assert len(results) == 1

        # Check as source
        results = graph.contradictions(_id(1))
        assert len(results) == 1

    def test_supporters(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(3), Relation.SUPPORTS))
        graph.add(ProofRelation(_id(2), _id(3), Relation.CORROBORATES))
        graph.add(ProofRelation(_id(4), _id(3), Relation.CONTRADICTS))

        results = graph.supporters(_id(3))
        assert len(results) == 2  # supports + corroborates

    def test_to_dict(self):
        graph = ProofGraph()
        graph.add(ProofRelation(_id(1), _id(2), Relation.SUPERSEDES))
        result = graph.to_dict()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["relation"] == "supersedes"

    def test_empty_graph(self):
        graph = ProofGraph()
        assert graph.relations == []
        assert graph.find_by_source(_id(1)) == []
        assert graph.contradictions(_id(1)) == []
