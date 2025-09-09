#!/usr/bin/env python3
"""
Test script to verify that the refactored OmniBenchmarker correctly delegates
all tracking to the logger while acting as a pure orchestrator.
"""

import uuid
from typing import Dict, Any

from omnibench.core.benchmarker import OmniBenchmarker, Benchmark
from omnibench.objectives.combined import CombinedBenchmarkObjective
from omnibench.objectives.output import StringEqualityObjective
from omnibench.objectives.output import RegexMatchObjective
from omnibench.core.types import BoolEvalResult


class TestAgent:
    """Simple test agent that returns predictable results."""
    
    def invoke(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query", "default")
        if "success" in query:
            return {"status": "success", "message": "success test completed"}
        elif "fail" in query:
            return {"status": "failed", "message": "fail test completed"}
        else:
            return {"status": "unknown", "message": "default test completed"}


def create_test_agent():
    return TestAgent()


def test_orchestrator_architecture():
    """Test that the benchmarker acts as pure orchestrator with no internal tracking."""
    
    print("🧪 Testing Refactored OmniBenchmarker Architecture")
    print("=" * 50)
    
    # Create combined objective
    status_obj = StringEqualityObjective(
        name="StatusCheck",
        goal="success",
        output_key="status",
        valid_eval_result_type=BoolEvalResult
    )
    
    message_obj = RegexMatchObjective(
        name="MessageCheck",
        goal="success.*completed",
        output_key="message",
        valid_eval_result_type=BoolEvalResult
    )
    
    combined_obj = CombinedBenchmarkObjective(
        name="CombinedTest",
        objectives=[status_obj, message_obj]
    )
    
    # Create benchmarks with different success patterns
    benchmarks = [
        Benchmark(
            name="SuccessTest",
            input_kwargs={"query": "success_case"},
            objective=combined_obj,
            iterations=2,
            verbose=False
        ),
        Benchmark(
            name="FailTest", 
            input_kwargs={"query": "fail_case"},
            objective=combined_obj,
            iterations=2,
            verbose=False
        )
    ]
    
    # Create benchmarker
    benchmarker = OmniBenchmarker(
        executor_fn=create_test_agent,
        executor_kwargs={},
        initial_input=benchmarks,
        enable_logging=True,
        notebook=False
    )
    
    print("📊 Initial State (should be all zeros):")
    print(f"   Total iterations: {benchmarker.total_iter}")
    print(f"   Success iterations: {benchmarker.success_iter}")
    print(f"   Failed iterations: {benchmarker.fail_iter}")
    print(f"   Success rate: {benchmarker.success_rate:.1f}%")
    print(f"   Logger logs count: {len(benchmarker.logger)}")
    
    # Verify initial state
    assert benchmarker.total_iter == 0, "Initial total_iter should be 0"
    assert benchmarker.success_iter == 0, "Initial success_iter should be 0"
    assert benchmarker.fail_iter == 0, "Initial fail_iter should be 0"
    assert benchmarker.success_rate == 0.0, "Initial success_rate should be 0.0"
    assert len(benchmarker.logger) == 0, "Initial logger should be empty"
    
    print("✅ Initial state verified")
    
    # Run benchmarks
    print(f"\n🚀 Running benchmarks...")
    results = benchmarker.benchmark()
    
    print(f"\n📊 Final State (computed from logger):")
    print(f"   Total iterations: {benchmarker.total_iter}")
    print(f"   Success iterations: {benchmarker.success_iter}")
    print(f"   Failed iterations: {benchmarker.fail_iter}")
    print(f"   Success rate: {benchmarker.success_rate:.1f}%")
    print(f"   Logger logs count: {len(benchmarker.logger)}")
    
    # Verify that metrics are computed from logger
    expected_logs = len(benchmarks) * len(combined_obj.objectives)  # 2 benchmarks × 2 objectives = 4 logs
    expected_total_iter = sum(b.iterations for b in benchmarks) * len(combined_obj.objectives)  # 4 iterations × 2 objectives = 8 entries
    
    assert len(benchmarker.logger) == expected_logs, f"Expected {expected_logs} logs, got {len(benchmarker.logger)}"
    assert benchmarker.total_iter == expected_total_iter, f"Expected {expected_total_iter} total iterations, got {benchmarker.total_iter}"
    
    print("✅ Logger delegation verified")
    
    # Test individual objective tracking
    print(f"\n🎯 Individual Objective Analysis:")
    
    status_logs = benchmarker.get_logs_for_objective(status_obj.uuid)
    message_logs = benchmarker.get_logs_for_objective(message_obj.uuid)
    
    print(f"   StatusCheck logs: {len(status_logs)} benchmarks")
    print(f"   MessageCheck logs: {len(message_logs)} benchmarks")
    
    # Verify separate logging for each sub-objective
    assert len(status_logs) == len(benchmarks), "Status objective should have logs for all benchmarks"
    assert len(message_logs) == len(benchmarks), "Message objective should have logs for all benchmarks"
    
    # Check that each log has the correct number of entries
    total_status_entries = sum(len(log.entries) for log in status_logs.values())
    total_message_entries = sum(len(log.entries) for log in message_logs.values())
    expected_entries_per_obj = sum(b.iterations for b in benchmarks)
    
    assert total_status_entries == expected_entries_per_obj, f"Status objective should have {expected_entries_per_obj} entries"
    assert total_message_entries == expected_entries_per_obj, f"Message objective should have {expected_entries_per_obj} entries"
    
    print("✅ Combined objective separation verified")
    
    # Test that benchmarker has no internal tracking state
    print(f"\n🔍 Architecture Verification:")
    
    # Verify that benchmarker doesn't have tracking attributes
    assert not hasattr(benchmarker, '_success_iter'), "Benchmarker should not have _success_iter attribute"
    assert not hasattr(benchmarker, '_fail_iter'), "Benchmarker should not have _fail_iter attribute"
    assert not hasattr(benchmarker, '_total_iter'), "Benchmarker should not have _total_iter attribute"
    assert not hasattr(benchmarker, '_objective_results'), "Benchmarker should not have _objective_results attribute"
    
    print("   ✅ No internal tracking attributes")
    print("   ✅ All metrics computed from logger")
    print("   ✅ Clean orchestrator architecture verified")
    
    return benchmarker


def test_logger_only_tracking():
    """Test that disabling logging results in zero metrics."""
    
    print(f"\n🧪 Testing Logger-Only Tracking")
    print("-" * 30)
    
    # Create simple benchmark
    simple_obj = StringEqualityObjective(
        name="SimpleTest",
        goal="success",
        output_key="status",
        valid_eval_result_type=BoolEvalResult
    )
    
    benchmark = Benchmark(
        name="SimpleTest",
        input_kwargs={"query": "success_case"},
        objective=simple_obj,
        iterations=3,
        verbose=False
    )
    
    # Create benchmarker with logging DISABLED
    benchmarker = OmniBenchmarker(
        executor_fn=create_test_agent,
        executor_kwargs={},
        initial_input=[benchmark],
        enable_logging=False,  # 🔑 Logging disabled
        notebook=False
    )
    
    # Run benchmark
    results = benchmarker.benchmark()
    
    # Verify that all metrics are 0 when logging is disabled
    print(f"   Logging enabled: {benchmarker.enable_logging}")
    print(f"   Total iterations: {benchmarker.total_iter}")
    print(f"   Success rate: {benchmarker.success_rate:.1f}%")
    
    assert benchmarker.total_iter == 0, "Should be 0 when logging disabled"
    assert benchmarker.success_rate == 0.0, "Should be 0.0 when logging disabled"
    assert len(benchmarker.logger) == 0, "Logger should be empty when logging disabled"
    
    print("✅ Logger-only tracking verified")


def main():
    """Run all tests."""
    
    print("🚀 Refactored OmniBenchmarker Test Suite")
    print("=" * 60)
    
    try:
        # Test main architecture
        benchmarker = test_orchestrator_architecture()
        
        # Test logger-only behavior
        test_logger_only_tracking()
        
        print(f"\n🎉 All Tests Passed!")
        print(f"✅ Benchmarker successfully refactored as pure orchestrator")
        print(f"✅ All tracking delegated to logger")
        print(f"✅ Combined objectives handled correctly")
        print(f"✅ Clean architecture verified")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
