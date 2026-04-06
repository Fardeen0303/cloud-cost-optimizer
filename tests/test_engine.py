import pytest
import sys
import os
import json
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'recommendation-engine'))

from engine import RecommendationEngine

engine = RecommendationEngine.__new__(RecommendationEngine)

Resource = namedtuple('Resource', ['id', 'resource_id', 'recommendation_type', 'data', 'scanned_at'])


def make_resource(avg_cpu):
    return Resource(1, 'i-1234567890', 'downsize', json.dumps({'avg_cpu': avg_cpu}), None)


def test_underutilized_below_threshold():
    assert engine.is_underutilized(make_resource(10.0)) is True


def test_not_underutilized_above_threshold():
    assert engine.is_underutilized(make_resource(50.0)) is False


def test_not_underutilized_at_threshold():
    assert engine.is_underutilized(make_resource(20.0)) is False


def test_no_cpu_data_returns_false():
    resource = Resource(1, 'i-abc', 'downsize', json.dumps({'avg_cpu': None}), None)
    assert engine.is_underutilized(resource) is False


def test_missing_cpu_key_returns_false():
    resource = Resource(1, 'i-abc', 'downsize', json.dumps({}), None)
    assert engine.is_underutilized(resource) is False
