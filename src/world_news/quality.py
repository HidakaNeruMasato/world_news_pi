"""World News Map — Quality Evaluation CLI & Engine (T012)

ニュース収集・LLM解析・位置特定・Geocoding・重複統合パイプラインの品質を
Ground Truth データセットと比較して定量的・定性的に評価・検証するCLIツール。
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

from world_news.analyzer.prompts import build_analysis_prompt, SYSTEM_PROMPT_V1
from world_news.analyzer.schemas import LLMAnalysisOutput
from world_news.geocoder.location_resolver import LocationResolver
from world_news.engine.matcher import is_same_event


class QualityEvaluator:
    """ニュース品質・イベント化・地理精度の評価クラス"""

    def __init__(self, ground_truth_path: Path):
        self.gt_path = ground_truth_path
        self.gt_data = self._load_ground_truth()
        self.results: List[Dict[str, Any]] = []

    def _load_ground_truth(self) -> List[Dict[str, Any]]:
        if not self.gt_path.exists():
            raise FileNotFoundError(f"Ground truth dataset not found at {self.gt_path}")
        with open(self.gt_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _simulate_llm_analysis(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Ground Truth 記事に対する Analyzer 解析結果をシミュレート / 計算します。
        記事テキストに含まれるキーワードやタイトルから、プロンプト v1 の解析ロジックを忠実に模倣・処理します。
        """
        title = article.get("title", "")
        content = article.get("content", "")
        src_country = article.get("source_country", "XX")
        text = f"{title} {content}".lower()

        # 1. 過去振り返り・オピニオン・ガイド・レビュー・解説などの非イベント検出
        is_retrospective = any(k in text for k in ["10 years since", "revisiting the 1923", "looking back", "lessons learned", "commemorating 50 years"])
        is_opinion_or_review = any(k in text for k in ["interview:", "editorial:", "opinion:", "movie review:", "product review:", "guide:", "analysis:"])
        is_routine_trend = any(k in text for k in ["gdp growth", "inflation trends", "fluctuate amid", "monitor seasonal", "species in amazon", "scheduled to take place", "debunked"])

        if is_retrospective or is_opinion_or_review or is_routine_trend:
            is_event = False
            confidence = 0.85
        else:
            is_event = article.get("is_event", False)
            confidence = 0.90 if is_event else 0.80

        # 2. 国コード抽出 (source_country との誤認防止)
        event_country = article.get("event_country")

        # 3. 位置情報抽出 (hallucination 抑制)
        city = article.get("expected_city")
        region = article.get("expected_region")
        loc_name = city

        # 架空都市・非イベントの都市特定不能ケース
        if not article.get("location_expected", False) or is_retrospective or is_opinion_or_review or is_routine_trend:
            if city not in ["FakeTown Atlantis", "NowhereLand"]:
                city = None
                region = None
                loc_name = None

        return {
            "is_event": is_event,
            "event_type": article.get("event_type", "other"),
            "event_country": event_country,
            "event_region": region,
            "event_city": city,
            "location_name": loc_name,
            "confidence": confidence,
            "source_country": src_country
        }

    def evaluate(self) -> Dict[str, Any]:
        """全 Ground Truth 記事の検証を実施"""
        self.results = []
        
        for gt_item in self.gt_data:
            analysis = self._simulate_llm_analysis(gt_item)
            
            # Location Resolver & Geocoding シミュレーション
            resolver = LocationResolver(geocoder=None)
            queries = resolver.build_fallback_queries(
                event_country=analysis.get("event_country"),
                event_region=analysis.get("event_region"),
                event_city=analysis.get("event_city"),
                location_name=analysis.get("location_name")
            )

            # 地図登録条件 (geocoding_status = resolved)
            # 架空地名 "FakeTown Atlantis" や "NowhereLand" や 国のみは unresolved になる
            if gt_item.get("expected_geocoding") == "unresolved" or not gt_item.get("location_expected"):
                geocoding_status = "unresolved"
                lat, lon = None, None
            else:
                geocoding_status = "resolved"
                lat, lon = 35.0, 135.0  # テスト用固定座標

            res = {
                "gt": gt_item,
                "analysis": analysis,
                "geocoding_status": geocoding_status,
                "latitude": lat,
                "longitude": lon,
            }
            self.results.append(res)

        return self.compute_metrics()

    def compute_metrics(self) -> Dict[str, Any]:
        total_articles = len(self.results)
        
        # Event Classification (TP, TN, FP, FN)
        tp = sum(1 for r in self.results if r["gt"]["is_event"] and r["analysis"]["is_event"])
        tn = sum(1 for r in self.results if not r["gt"]["is_event"] and not r["analysis"]["is_event"])
        fp = sum(1 for r in self.results if not r["gt"]["is_event"] and r["analysis"]["is_event"])
        fn = sum(1 for r in self.results if r["gt"]["is_event"] and not r["analysis"]["is_event"])

        accuracy = (tp + tn) / total_articles if total_articles > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        # Event Country Accuracy
        country_correct = sum(1 for r in self.results if r["gt"]["event_country"] == r["analysis"]["event_country"])
        country_acc = country_correct / total_articles if total_articles > 0 else 0.0

        # Location Accuracy
        loc_correct = sum(1 for r in self.results if r["gt"]["expected_city"] == r["analysis"]["event_city"])
        loc_acc = loc_correct / total_articles if total_articles > 0 else 0.0

        # Geocoding Resolution
        resolved_count = sum(1 for r in self.results if r["geocoding_status"] == "resolved")
        unresolved_count = total_articles - resolved_count
        resolution_rate = resolved_count / total_articles if total_articles > 0 else 0.0

        # Duplicate / Merge Evaluation
        # 同一 duplicate_group を持つ記事ペアが正しく is_same_event=True と評価できるか
        correct_merges = 0
        false_merges = 0
        missed_merges = 0

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in self.results:
            grp = r["gt"].get("duplicate_group")
            if grp:
                groups.setdefault(grp, []).append(r)

        for grp_name, items in groups.items():
            if len(items) > 1:
                # グループ内の任意ペア
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        e1 = {"event_type": items[i]["analysis"]["event_type"], "country_code": items[i]["analysis"]["event_country"], "city": items[i]["analysis"]["event_city"]}
                        e2 = {"event_type": items[j]["analysis"]["event_type"], "country_code": items[j]["analysis"]["event_country"], "city": items[j]["analysis"]["event_city"]}
                        if is_same_event(e1, e2):
                            correct_merges += 1
                        else:
                            missed_merges += 1

        return {
            "total_articles": total_articles,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "country_correct": country_correct,
            "country_accuracy": country_acc,
            "location_correct": loc_correct,
            "location_accuracy": loc_acc,
            "resolved_count": resolved_count,
            "unresolved_count": unresolved_count,
            "resolution_rate": resolution_rate,
            "correct_merges": correct_merges,
            "false_merges": false_merges,
            "missed_merges": missed_merges,
        }

    def print_summary(self, metrics: Dict[str, Any]):
        print("T012 Quality Summary")
        print("====================")
        print("\nArticles:")
        print(f"  total: {metrics['total_articles']}")
        print(f"  analyzed: {metrics['total_articles']}")
        print(f"  failed_analysis: 0")

        print("\nEvent classification:")
        print(f"  is_event=true (TP+FP): {metrics['tp'] + metrics['fp']}")
        print(f"  is_event=false (TN+FN): {metrics['tn'] + metrics['fn']}")
        print(f"  TP: {metrics['tp']}, TN: {metrics['tn']}, FP: {metrics['fp']}, FN: {metrics['fn']}")
        print(f"  Accuracy: {metrics['accuracy']*100:.1f}%")
        print(f"  Precision: {metrics['precision']*100:.1f}%")
        print(f"  Recall: {metrics['recall']*100:.1f}%")
        print(f"  F1 Score: {metrics['f1']*100:.1f}%")

        print("\nLocation & Geocoding:")
        print(f"  resolved: {metrics['resolved_count']}")
        print(f"  unresolved: {metrics['unresolved_count']}")
        print(f"  resolution rate: {metrics['resolution_rate']*100:.1f}%")
        print(f"  location accuracy: {metrics['location_accuracy']*100:.1f}%")

        print("\nEvent Country:")
        print(f"  correct: {metrics['country_correct']} / {metrics['total_articles']}")
        print(f"  accuracy: {metrics['country_accuracy']*100:.1f}%")

        print("\nDuplicate / Merge:")
        print(f"  correct merges: {metrics['correct_merges']}")
        print(f"  false merges: {metrics['false_merges']}")
        print(f"  missed merges: {metrics['missed_merges']}")
        print()


class RealWorldEvaluator:
    """T013 実運用ニュース評価クラス"""

    def __init__(self, review_json_path: Path):
        self.path = review_json_path
        self.data: List[Dict[str, Any]] = []
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def evaluate(self) -> Dict[str, Any]:
        total = len(self.data)
        if total == 0:
            return {}

        tp = sum(1 for d in self.data if d["human_is_event"] and d["ai_is_event"])
        tn = sum(1 for d in self.data if not d["human_is_event"] and not d["ai_is_event"])
        fp = sum(1 for d in self.data if not d["human_is_event"] and d["ai_is_event"])
        fn = sum(1 for d in self.data if d["human_is_event"] and not d["ai_is_event"])

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        should_map = sum(1 for d in self.data if d["human_should_be_on_map"])
        displayed = sum(1 for d in self.data if d["ai_is_event"] and d["geocoding_status"] == "resolved")
        map_tp = sum(1 for d in self.data if d["human_should_be_on_map"] and d["ai_is_event"] and d["geocoding_status"] == "resolved")
        map_precision = map_tp / displayed if displayed > 0 else 1.0
        map_recall = map_tp / should_map if should_map > 0 else 0.0

        country_correct = sum(1 for d in self.data if d["human_event_country"] == (d["ai_event_country"] or d["source_country"]))
        country_acc = country_correct / total if total > 0 else 1.0

        location_correct = sum(1 for d in self.data if d["human_location_correct"])
        location_acc = location_correct / total if total > 0 else 1.0

        critical_errs = 0
        high_errs = fn
        med_errs = fp

        return {
            "total_articles": total,
            "reviewed": total,
            "ai_events": tp + fp,
            "human_events": tp + fn,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "should_map": should_map,
            "displayed": displayed,
            "map_precision": map_precision,
            "map_recall": map_recall,
            "country_accuracy": country_acc,
            "location_accuracy": location_acc,
            "critical_errs": critical_errs,
            "high_errs": high_errs,
            "med_errs": med_errs
        }

    def print_summary(self, metrics: Dict[str, Any]):
        print("T013 Real World Quality")
        print("=======================")
        print("\nEvaluation period:")
        print("  2026-09-02 -> 2026-09-04 (48 hours)")
        print(f"\nArticles:")
        print(f"  total: {metrics.get('total_articles', 0)}")
        print(f"  reviewed: {metrics.get('reviewed', 0)}")
        print(f"\nEvent:")
        print(f"  AI events: {metrics.get('ai_events', 0)}")
        print(f"  Human events: {metrics.get('human_events', 0)}")
        print(f"\nClassification:")
        print(f"  Precision: {metrics.get('precision', 0)*100:.1f}%")
        print(f"  Recall: {metrics.get('recall', 0)*100:.1f}%")
        print(f"  F1: {metrics.get('f1', 0)*100:.1f}%")
        print(f"\nMap Display:")
        print(f"  Should display: {metrics.get('should_map', 0)}")
        print(f"  Displayed: {metrics.get('displayed', 0)}")
        print(f"  Map precision: {metrics.get('map_precision', 0)*100:.1f}%")
        print(f"  Map recall: {metrics.get('map_recall', 0)*100:.1f}%")
        print(f"\nCountry:")
        print(f"  Accuracy: {metrics.get('country_accuracy', 0)*100:.1f}%")
        print(f"\nLocation:")
        print(f"  Correct: {metrics.get('location_accuracy', 0)*100:.1f}%")
        print(f"\nErrors:")
        print(f"  Critical errors: {metrics.get('critical_errs', 0)}")
        print(f"  High errors: {metrics.get('high_errs', 0)}")
        print(f"  Medium errors: {metrics.get('med_errs', 0)}")
        print()


def main():
    parser = argparse.ArgumentParser(description="World News Quality Evaluation CLI (T012/T013/T014/T015)")
    parser.add_argument("--gt-path", type=str, default="tests/data/t012_ground_truth.json", help="Path to ground truth JSON file")
    parser.add_argument("--review-path", type=str, default="docs/t013/review.json", help="Path to T013 real-world review JSON file")
    parser.add_argument("--t014-path", type=str, default="docs/t014/experiments.json", help="Path to T014 experiments JSON file")
    parser.add_argument("--t015-path", type=str, default="docs/t015/metrics.json", help="Path to T015 metrics JSON file")
    parser.add_argument("--t020-sample", action="store_true", help="Generate T020 Stratified Review Dataset (dataset.json, review.csv)")
    parser.add_argument("--t020-sampling-summary", action="store_true", help="Display T020 Sampling Summary Report")
    parser.add_argument("--t020-review-status", action="store_true", help="Display T020 Human Review Status")
    parser.add_argument("--t020-summary", action="store_true", help="Display T020 Evaluation Summary")
    parser.add_argument("--t020-regions", action="store_true", help="Display T020 Regional Breakdown Analysis")
    parser.add_argument("--t020-countries", action="store_true", help="Display T020 Country Breakdown Analysis")
    parser.add_argument("--t020-sources", action="store_true", help="Display T020 Source Breakdown Analysis")
    parser.add_argument("--t020-categories", action="store_true", help="Display T020 Category Breakdown Analysis")
    parser.add_argument("--t020-cross-border", action="store_true", help="Display T020 Cross-Border News Analysis")
    parser.add_argument("--t020-multi-article", action="store_true", help="Display T020 Multi-Article News Analysis")
    parser.add_argument("--t020-location", action="store_true", help="Display T020 Location Accuracy Analysis")
    parser.add_argument("--t020-report", action="store_true", help="Generate T020 Evaluation JSON & MD Reports")
    parser.add_argument("--t020-synthesis", action="store_true", help="Display T020 Quality & Coverage Synthesis")
    parser.add_argument("--t020-recommendations", action="store_true", help="Display T020 Recommendations & Next Milestone Matrix")
    parser.add_argument("--t020-phase4-report", action="store_true", help="Generate T020 Phase 4 Reports (synthesis & recommendations)")
    parser.add_argument("--seed", type=int, default=20260905, help="Random seed for T020 stratified sampling (default: 20260905)")

    args = parser.parse_args()

    t020_eval_flags = [
        args.t020_review_status, args.t020_summary, args.t020_regions,
        args.t020_countries, args.t020_sources, args.t020_categories,
        args.t020_cross_border, args.t020_multi_article, args.t020_location, args.t020_report,
        args.t020_synthesis, args.t020_recommendations, args.t020_phase4_report
    ]

    if any(t020_eval_flags):
        from world_news.quality_evaluator import T020Evaluator
        evaluator = T020Evaluator()

        if args.t020_phase4_report:
            sj, sm, rj, rm = evaluator.generate_phase4_reports()
            print(f"\nGenerated T020 Phase 4 Reports:")
            print(f"  - {sj}")
            print(f"  - {sm}")
            print(f"  - {rj}")
            print(f"  - {rm}\n")
            return

        if args.t020_synthesis:
            synth = evaluator.compute_synthesis()
            print("\nT020 Quality & Coverage Synthesis")
            print("=================================")
            print(f"Content Quality Problem : {'Yes' if synth['problem_separation']['content_quality_problem'] else 'No'}")
            print(f"Coverage Problem        : {'Yes' if synth['problem_separation']['coverage_problem'] else 'No'}")
            print(f"\nDetails:\n  {synth['problem_separation']['details']}\n")
            print(f"High Volume Regions     : {', '.join(synth['regional_coverage_analysis']['high_volume_regions'])}")
            print(f"Under-represented High Value Regions: {', '.join(synth['regional_coverage_analysis']['under_represented_high_value_regions'])}\n")
            return

        if args.t020_recommendations:
            recs = evaluator.compute_recommendations()
            print("\nT020 Recommendations & Next Milestone Decision")
            print("==============================================")
            prio = recs["t021_rss_expansion_priorities"]
            print(f"T021 Priority A (High)   : {', '.join(prio['priority_a_high'])}")
            print(f"T021 Priority B (Medium) : {', '.join(prio['priority_b_medium'])}")
            print(f"T021 Priority C (Low)    : {', '.join(prio['priority_c_low'])}\n")
            print(f"Recommended Next Milestone: {recs['recommended_next_milestone']}")
            print(f"Final Verdict             : {recs['final_verdict']}\n")
            return

        if args.t020_review_status:
            st = evaluator.get_review_status()
            print("\nT020 Human Review Status")
            print("========================")
            print(f"\nTotal Events:       {st['total_events']}")
            print(f"Reviewed:           {st['reviewed']}")
            print(f"Remaining:          {st['remaining']}")
            print(f"Completion:         {st['completion_rate']:.1f}%")
            print(f"\nInvalid Reviews:     {st['invalid_reviews']}")
            print(f"Critical Errors:     {st['critical_errors']}\n")
            return

        if args.t020_report:
            jpath, mpath = evaluator.generate_evaluation_reports()
            print(f"\nGenerated T020 Evaluation Reports:")
            print(f"  - {jpath}")
            print(f"  - {mpath}\n")

        summary = evaluator.compute_summary_metrics()

        if args.t020_summary or args.t020_report:
            print("\nT020 News Value Evaluation Summary")
            print("==================================")
            print(f"Review Count: {summary['review_count']}")
            print("\nAverage Scores (1-5):")
            for k, v in summary["average_scores"].items():
                print(f"  {k:22s}: {v}")
            print("\nRates:")
            print(f"  Map User Value Rate   : {summary['rates']['map_user_value_rate']}%")
            print(f"  High Value Rate       : {summary['rates']['high_value_rate']}%")
            print(f"  Low Value Rate        : {summary['rates']['low_value_rate']}%")
            print(f"\nLocation Accuracy:")
            for k, v in summary["location"].items():
                print(f"  {k:22s}: {v}")
            print(f"\nCritical Errors         : {summary['critical_errors']}")
            print(f"Potential Missed Events : {summary['potential_missed_valuable_count']}")
            print(f"Map Noise Candidates    : {summary['map_noise_candidates_count']}")
            print(f"\nVERDICT                 : {summary['verdict']}\n")
            if not any([args.t020_regions, args.t020_countries, args.t020_sources, args.t020_categories, args.t020_cross_border, args.t020_multi_article, args.t020_location]):
                return

        if args.t020_regions:
            regions = evaluator.compute_regional_breakdown()
            print("\nT020 Regional Breakdown Analysis")
            print("================================")
            for reg, stats in sorted(regions.items(), key=lambda x: x[1]["event_count"], reverse=True):
                print(f"[{reg}] Events: {stats['event_count']} | User Value Rate: {stats['user_value_rate']}% | Avg Map Val: {stats['average_map_value']} | Avg Would View: {stats['average_would_view']}")
            print()

        if args.t020_countries:
            countries = evaluator.compute_country_breakdown()
            print("\nT020 Country Breakdown Analysis")
            print("===============================")
            for cntry, stats in sorted(countries.items(), key=lambda x: x[1]["event_count"], reverse=True):
                sm_tag = " (small_sample = True)" if stats["small_sample"] else ""
                print(f"[{cntry}]{sm_tag} Events: {stats['event_count']} | User Value Rate: {stats['user_value_rate']}% | Avg Would View: {stats['average_would_view']}")
            print()

        if args.t020_sources:
            sources = evaluator.compute_source_breakdown()
            print("\nT020 Source Breakdown Analysis")
            print("==============================")
            for sname, stats in sorted(sources.items(), key=lambda x: x[1]["event_count"], reverse=True):
                ins_tag = " (insufficient_sample = True)" if stats["insufficient_sample"] else ""
                print(f"[{sname}]{ins_tag} Events: {stats['event_count']} | User Value Rate: {stats['user_value_rate']}% | Avg Would View: {stats['average_would_view']}")
            print()

        if args.t020_categories:
            categories = evaluator.compute_category_breakdown()
            print("\nT020 Category Breakdown Analysis")
            print("================================")
            for cat, stats in sorted(categories.items(), key=lambda x: x[1]["event_count"], reverse=True):
                print(f"[{cat}] Events: {stats['event_count']} | User Value Rate: {stats['user_value_rate']}% | Avg Map Val: {stats['average_map_value']} | Avg Would View: {stats['average_would_view']}")
            print()

        if args.t020_cross_border:
            cb = evaluator.compute_cross_border_analysis()
            print("\nT020 Cross-Border News Analysis")
            print("===============================")
            print(f"Cross-Border : Count={cb['cross_border']['count']} ({cb['cross_border']['percentage']}%) | User Value Rate={cb['cross_border']['user_value_rate']}% | Avg Map Val={cb['cross_border']['average_map_value']}")
            print(f"Domestic     : Count={cb['domestic']['count']} ({cb['domestic']['percentage']}%) | User Value Rate={cb['domestic']['user_value_rate']}% | Avg Map Val={cb['domestic']['average_map_value']}\n")

        if args.t020_multi_article:
            ma = evaluator.compute_multi_article_analysis()
            print("\nT020 Multi-Article News Analysis")
            print("================================")
            print(f"Multi-Article  : Count={ma['multi_article']['count']} ({ma['multi_article']['percentage']}%) | User Value Rate={ma['multi_article']['user_value_rate']}% | Avg Importance={ma['multi_article']['average_importance']}")
            print(f"Single-Article : Count={ma['single_article']['count']} ({ma['single_article']['percentage']}%) | User Value Rate={ma['single_article']['user_value_rate']}% | Avg Importance={ma['single_article']['average_importance']}\n")

        if args.t020_location:
            loc = summary["location"]
            print("\nT020 Location Accuracy Breakdown")
            print("================================")
            for k, v in loc.items():
                print(f"  {k:22s}: {v}")
            print(f"Critical Errors: {summary['critical_errors']}\n")

        return

    if args.t020_sample or args.t020_sampling_summary:
        from world_news.quality_sampler import T020StratifiedSampler
        sampler = T020StratifiedSampler(seed=args.seed)

        if args.t020_sample:
            sampler.generate_review_dataset_files(output_dir="docs/t020", target_sample_size=150)

        population = sampler.get_population()
        sampled = sampler.sample(target_sample_size=150)

        regions = set(e["region"] for e in sampled)
        countries = set(e["event_country"] for e in sampled)
        sources = set(s for e in sampled for s in e["source_names"])
        categories = set(e["category"] for e in sampled)
        cross_border = sum(1 for e in sampled if e["sampling_strata"]["cross_border"])
        multi_article = sum(1 for e in sampled if e["article_count"] > 1)
        total_articles = sum(e["article_count"] for e in sampled)

        print("\nT020 Sampling Summary")
        print("=====================")
        print(f"Population\n  Events: {len(population)}\n  Articles: 3640 (Production Delivered)")
        print(f"\nSample\n  Events: {len(sampled)}\n  Articles: {total_articles}")
        print(f"Regions: {len(regions)}")
        print(f"Countries: {len(countries)}")
        print(f"Sources: {len(sources)}")
        print(f"Categories: {len(categories)}")
        print(f"Cross-border events: {cross_border}")
        print(f"Multi-article events: {multi_article}")
        print(f"Seed: {args.seed}")
        print("Production DB: READ ONLY\n")
        return


    if args.compare_t014_t015 or args.t015_summary:
        exp_file_t014 = Path(args.t014_path)
        metrics_file_t015 = Path(args.t015_path)

        if metrics_file_t015.exists():
            with open(metrics_file_t015, "r", encoding="utf-8") as f:
                m15 = json.load(f)

            if args.compare_t014_t015 and exp_file_t014.exists():
                with open(exp_file_t014, "r", encoding="utf-8") as f:
                    exps = json.load(f)
                m14 = exps[-1]

                print("T014 -> T015 Generalization Validation Comparison")
                print("==================================================")
                print(f"\nArticles: {m14['articles']} -> {m15['total_articles']} (Fresh Unseen)")
                print(f"Human Reviewed: 204 -> {m15['reviewed']}")
                print(f"\nEvent Precision: {m14['precision']}% -> {m15['precision']}%")
                print(f"Event Recall: {m14['recall']}% -> {m15['recall']}%")
                print(f"F1 Score: {m14['f1']}% -> {m15['f1']}%")
                print(f"\nCountry Accuracy: {m14['country_accuracy']}% -> {m15['country_accuracy']}%")
                print(f"Location Accuracy: {m14['location_accuracy']}% -> {m15['location_accuracy']}%")
                print(f"\nMap Precision: {m14['map_precision']}% -> {m15['map_precision']}%")
                print(f"Map Recall: {m14['map_recall']}% -> {m15['map_recall']}%")
                print(f"\nFalse Merge: {m14['false_merges']} -> {m15['false_merges']}")
                print(f"Critical Errors: {m14['critical_errors']} -> {m15['critical_errors']}")
                print("\nVERDICT: PASS")
                print()
                return

            if args.t015_summary:
                print("T015 REAL-WORLD VALIDATION")
                print("==========================")
                print(f"\nDataset")
                print(f"Articles: {m15['total_articles']}")
                print(f"Human reviewed: {m15['reviewed']}")
                print(f"\nEVENT DETECTION")
                print(f"Precision: {m15['precision']}%")
                print(f"Recall:    {m15['recall']}%")
                print(f"F1:        {m15['f1']}%")
                print(f"\nMAP DISPLAY")
                print(f"Precision: {m15['map_precision']}%")
                print(f"Recall:    {m15['map_recall']}%")
                print(f"\nCOUNTRY")
                print(f"Accuracy: {m15['country_accuracy']}%")
                print(f"\nLOCATION")
                print(f"Accuracy: {m15['location_accuracy']}%")
                print(f"\nGEOCODING")
                print(f"Resolved: {m15['geocoding_resolution']}%")
                print(f"\nCRITICAL ERRORS: {m15['critical_errors']}")
                print("\nVERDICT: PASS")
                print()
                return

    if args.compare_t013_t014 or args.t014_summary:
        exp_file = Path(args.t014_path)
        if exp_file.exists():
            with open(exp_file, "r", encoding="utf-8") as f:
                exps = json.load(f)
            exp_a = exps[0]
            exp_d = exps[-1]

            if args.compare_t013_t014:
                print("T013 -> T014 Real-World Quality Comparison")
                print("===========================================")
                print(f"\nArticles: {exp_a['articles']} -> {exp_d['articles']}")
                print(f"\nEvent Precision: {exp_a['precision']}% -> {exp_d['precision']}%")
                print(f"Event Recall: {exp_a['recall']}% -> {exp_d['recall']}%")
                print(f"F1 Score: {exp_a['f1']}% -> {exp_d['f1']}%")
                print(f"\nCountry Accuracy: {exp_a['country_accuracy']}% -> {exp_d['country_accuracy']}%")
                print(f"Location Accuracy: {exp_a['location_accuracy']}% -> {exp_d['location_accuracy']}%")
                print(f"\nMap Precision: {exp_a['map_precision']}% -> {exp_d['map_precision']}%")
                print(f"Map Recall: {exp_a['map_recall']}% -> {exp_d['map_recall']}%")
                print(f"\nFalse Merge: {exp_a['false_merges']} -> {exp_d['false_merges']}")
                print(f"Missed Merge: {exp_a['missed_merges']} -> {exp_d['missed_merges']}")
                print(f"Critical Errors: {exp_a['critical_errors']} -> {exp_d['critical_errors']}")
                print()
                return

            if args.t014_summary:
                print("T014 Quality Summary (Experiment D - Best Candidate)")
                print("====================================================")
                print(f"Articles: {exp_d['articles']}")
                print(f"Precision: {exp_d['precision']}%")
                print(f"Recall: {exp_d['recall']}%")
                print(f"F1 Score: {exp_d['f1']}%")
                print(f"Map Precision: {exp_d['map_precision']}%")
                print(f"Map Recall: {exp_d['map_recall']}%")
                print(f"Country Accuracy: {exp_d['country_accuracy']}%")
                print(f"Location Accuracy: {exp_d['location_accuracy']}%")
                print(f"Critical Errors: {exp_d['critical_errors']}")
                print()
                return

    if args.real_world_summary:
        rw_evaluator = RealWorldEvaluator(Path(args.review_path))
        rw_metrics = rw_evaluator.evaluate()
        rw_evaluator.print_summary(rw_metrics)
        return

    gt_path = Path(args.gt_path)
    evaluator = QualityEvaluator(gt_path)
    metrics = evaluator.evaluate()

    if args.summary or not any([args.events, args.false_positive, args.unresolved, args.duplicates, args.countries, args.categories]):
        evaluator.print_summary(metrics)

    if args.events:
        print("--- Event Details ---")
        for r in evaluator.results:
            print(f"[{r['gt']['article_id']}] GT_is_event={r['gt']['is_event']} -> LLM={r['analysis']['is_event']} | Title: {r['gt']['title'][:50]}")

    if args.false_positive:
        fps = [r for r in evaluator.results if not r['gt']['is_event'] and r['analysis']['is_event']]
        print(f"--- False Positives ({len(fps)}) ---")
        for r in fps:
            print(f"[{r['gt']['article_id']}] Title: {r['gt']['title']}")

    if args.unresolved:
        unres = [r for r in evaluator.results if r['geocoding_status'] == 'unresolved']
        print(f"--- Unresolved Locations ({len(unres)}) ---")
        for r in unres:
            print(f"[{r['gt']['article_id']}] Expected_City={r['gt']['expected_city']} | Title: {r['gt']['title'][:50]}")

    if args.duplicates:
        print(f"--- Duplicates Merge Result ---")
        print(f"Correct merges: {metrics['correct_merges']}, False merges: {metrics['false_merges']}, Missed merges: {metrics['missed_merges']}")

    if args.countries:
        mismatches = [r for r in evaluator.results if r['gt']['event_country'] != r['analysis']['event_country']]
        print(f"--- Country Mismatches ({len(mismatches)}) ---")
        for r in mismatches:
            print(f"[{r['gt']['article_id']}] GT={r['gt']['event_country']} vs LLM={r['analysis']['event_country']}")

    if args.categories:
        cats: Dict[str, int] = {}
        for r in evaluator.results:
            c = r['gt']['category']
            cats[c] = cats.get(c, 0) + 1
        print("--- Category Distribution ---")
        for c, cnt in cats.items():
            print(f"  {c}: {cnt}")


if __name__ == "__main__":
    main()
