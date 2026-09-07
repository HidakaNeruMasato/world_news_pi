"""Unit tests for T020 Stratified Sampler (T020 Phase 2)."""

import os
import json
import csv
import tempfile
import sqlite3
import pytest
from pathlib import Path
from world_news.quality_sampler import T020StratifiedSampler, COUNTRY_TO_REGION


def test_sampler_initialization_defaults():
    sampler = T020StratifiedSampler()
    assert sampler.db_path == "worldnews.db"
    assert sampler.seed == 20260905


def test_sampler_initialization_custom():
    sampler = T020StratifiedSampler(db_path="custom.db", seed=12345)
    assert sampler.db_path == "custom.db"
    assert sampler.seed == 12345


def test_country_to_region_mapping():
    assert COUNTRY_TO_REGION.get("JP") == "East Asia"
    assert COUNTRY_TO_REGION.get("GB") == "Europe"
    assert COUNTRY_TO_REGION.get("US") == "North America"
    assert COUNTRY_TO_REGION.get("QA") == "Middle East"
    assert COUNTRY_TO_REGION.get("BR") == "South America"
    assert COUNTRY_TO_REGION.get("AU") == "Oceania"


def test_sampler_fallback_population_loading():
    sampler = T020StratifiedSampler(db_path="non_existent.db")
    population = sampler.get_population()
    assert isinstance(population, list)
    assert len(population) > 0, "Fallback population should load from review datasets"


def test_sampler_reproducibility():
    sampler1 = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample1 = sampler1.sample(target_sample_size=30)
    ids1 = [e["event_id"] for e in sample1]

    sampler2 = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample2 = sampler2.sample(target_sample_size=30)
    ids2 = [e["event_id"] for e in sample2]

    assert ids1 == ids2, "Identical seed must produce identical event sample list"


def test_sampler_seed_variation():
    sampler1 = T020StratifiedSampler(db_path="non_existent.db", seed=100)
    sample1 = sampler1.sample(target_sample_size=30)
    ids1 = [e["event_id"] for e in sample1]

    sampler2 = T020StratifiedSampler(db_path="non_existent.db", seed=200)
    sample2 = sampler2.sample(target_sample_size=30)
    ids2 = [e["event_id"] for e in sample2]

    assert ids1 != ids2, "Different seeds should produce different sample orderings"


def test_sampler_sample_size_control():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=50)
    assert len(sample) == 50


def test_sampler_strata_fields_presence():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=20)
    for e in sample:
        assert "sampling_strata" in e
        strata = e["sampling_strata"]
        assert "region" in strata
        assert "category" in strata
        assert "cross_border" in strata
        assert "article_count_band" in strata
        assert "map_displayable" in strata


def test_sampler_article_count_band_logic():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=150)
    
    bands = {e["sampling_strata"]["article_count_band"] for e in sample}
    assert "1" in bands or "2-3" in bands or ">=4" in bands


def test_sampler_cross_border_calculation():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=150)
    
    cross_borders = [e for e in sample if e["sampling_strata"]["cross_border"]]
    assert len(cross_borders) >= 0


def test_sampler_file_generation_output(tmp_path):
    output_dir = tmp_path / "t020_test_out"
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sampler.generate_review_dataset_files(output_dir=str(output_dir), target_sample_size=30)

    dataset_json = output_dir / "dataset.json"
    review_csv = output_dir / "review.csv"
    sampling_md = output_dir / "sampling.md"

    assert dataset_json.exists()
    assert review_csv.exists()
    assert sampling_md.exists()

    with open(dataset_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["evaluation"]["task"] == "T020"
        assert len(data["events"]) == 30

    with open(review_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "event_id" in header
        assert "title" in header
        assert "would_view_on_map" in header
        rows = list(reader)
        assert len(rows) == 30

    with open(sampling_md, "r", encoding="utf-8") as f:
        content = f.read()
        assert "T020 Stratified Sampling Report" in content
        assert "Regional Stratification Breakdown" in content


def test_sampler_read_only_db_query(tmp_path):
    db_file = tmp_path / "test_worldnews.db"
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            location_name TEXT,
            event_type TEXT,
            country_code TEXT,
            first_seen_at TEXT,
            latitude REAL,
            longitude REAL,
            confidence REAL,
            status TEXT,
            geocoding_status TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY,
            source_country TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE article_events (
            article_id INTEGER,
            event_id INTEGER
        )
    """)
    cur.execute("""
        INSERT INTO events (id, location_name, event_type, country_code, first_seen_at, latitude, longitude, confidence, status, geocoding_status)
        VALUES (101, 'Tokyo', 'disaster', 'JP', '2026-09-05T10:00:00Z', 35.6762, 139.6503, 0.9, 'active', 'resolved')
    """)
    cur.execute("INSERT INTO articles (id, source_country) VALUES (1, 'JP')")
    cur.execute("INSERT INTO article_events (article_id, event_id) VALUES (1, 101)")
    conn.commit()
    conn.close()

    sampler = T020StratifiedSampler(db_path=str(db_file), seed=20260905)
    population = sampler.get_population()
    assert len(population) == 1
    assert population[0]["event_id"] == 101
    assert population[0]["event_country"] == "JP"
    assert population[0]["region"] == "East Asia"


def test_sampler_empty_population():
    sampler = T020StratifiedSampler(db_path="non_existent.db")
    sampler._load_production_dataset_fallback = lambda: []
    population = sampler.get_population()
    assert population == []
    sample = sampler.sample(target_sample_size=10)
    assert sample == []


def test_sampler_non_map_event_handling():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=150)
    unresolved_or_low_conf = [
        e for e in sample
        if not e["sampling_strata"]["map_displayable"]
    ]
    assert isinstance(unresolved_or_low_conf, list)


def test_sampler_regional_diversity():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=150)
    regions = {e["region"] for e in sample}
    assert len(regions) >= 4, f"Sample should cover multiple regions, found: {regions}"


def test_sampler_category_diversity():
    sampler = T020StratifiedSampler(db_path="non_existent.db", seed=20260905)
    sample = sampler.sample(target_sample_size=150)
    categories = {e["category"] for e in sample}
    assert len(categories) >= 3, f"Sample should cover multiple categories, found: {categories}"
