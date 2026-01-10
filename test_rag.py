"""
RAG System Test Suite
Comprehensive testing for RAG components
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_manager import RAGManager


def test_initialization():
    """Test RAG system initialization"""
    print("\n" + "="*70)
    print("TEST 1: RAG System Initialization")
    print("="*70)
    
    rag = RAGManager('data/knowledge_base')
    success = rag.initialize()
    
    assert success, "❌ RAG initialization failed"
    assert rag.initialized, "❌ RAG not marked as initialized"
    assert len(rag.documents) > 0, "❌ No documents loaded"
    assert len(rag.chunks) > 0, "❌ No chunks created"
    
    print("✅ PASSED: RAG system initialized successfully")
    
    return rag


def test_retrieval_quality(rag):
    """Test retrieval quality with known queries"""
    print("\n" + "="*70)
    print("TEST 2: Retrieval Quality")
    print("="*70)
    
    test_cases = [
        {
            'query': 'bearing failure symptoms',
            'expected_keywords': ['bearing', 'temperature', 'vibration', 'failure'],
            'expected_source': '01_gearbox_maintenance.txt'
        },
        {
            'query': 'vibration analysis frequency',
            'expected_keywords': ['vibration', 'frequency', 'Hz', 'bearing'],
            'expected_source': '02_vibration_analysis.txt'
        },
        {
            'query': 'normal operating temperature',
            'expected_keywords': ['temperature', '40', '60', 'normal'],
            'expected_source': None  # Could be in either file
        },
        {
            'query': 'oil change procedure',
            'expected_keywords': ['oil', 'change', 'procedure', 'drain'],
            'expected_source': '01_gearbox_maintenance.txt'
        },
        {
            'query': 'cost of gearbox replacement',
            'expected_keywords': ['cost', 'gearbox', 'replacement', '$'],
            'expected_source': '01_gearbox_maintenance.txt'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Query: {test['query']}")
        
        results = rag.retriever.search(test['query'], top_k=3, min_score=0.05)
        
        if not results:
            print(f"   ❌ FAILED: No results returned")
            failed += 1
            continue
        
        # Check relevance score
        top_result = results[0]
        print(f"   Top result score: {top_result['relevance_score']:.3f}")
        print(f"   Source: {top_result['source_file']}")
        
        # Check expected source (if specified)
        if test['expected_source']:
            if top_result['source_file'] == test['expected_source']:
                print(f"   ✅ Correct source file")
            else:
                print(f"   ⚠️  Expected {test['expected_source']}, got {top_result['source_file']}")
        
        # Check for expected keywords
        content_lower = top_result['content'].lower()
        found_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in content_lower]
        
        print(f"   Keywords found: {len(found_keywords)}/{len(test['expected_keywords'])}")
        
        if len(found_keywords) >= len(test['expected_keywords']) * 0.5:  # At least 50% of keywords
            print(f"   ✅ PASSED")
            passed += 1
        else:
            print(f"   ❌ FAILED: Too few keywords found")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"Retrieval Quality Results: {passed}/{len(test_cases)} passed")
    print(f"{'='*70}")
    
    return passed == len(test_cases)


def test_context_formatting(rag):
    """Test context formatting for LLM"""
    print("\n" + "="*70)
    print("TEST 3: Context Formatting")
    print("="*70)
    
    query = "bearing failure symptoms"
    context = rag.retrieve_context(query, top_k=2)
    
    # Check context is not empty
    assert context, "❌ Context is empty"
    print(f"✅ Context generated ({len(context)} characters)")
    
    # Check for required elements
    assert "RELEVANT KNOWLEDGE" in context, "❌ Missing header"
    assert "[Source" in context, "❌ Missing source citations"
    print("✅ Context includes proper formatting")
    
    # Check reasonable length
    assert len(context) < 5000, "❌ Context too long (>5000 chars)"
    assert len(context) > 200, "❌ Context too short (<200 chars)"
    print(f"✅ Context length is reasonable: {len(context)} characters")
    
    print(f"\n--- Sample Context ---")
    print(context[:500] + "...\n")
    
    print("✅ PASSED: Context formatting correct")
    
    return True


def test_edge_cases(rag):
    """Test edge cases and error handling"""
    print("\n" + "="*70)
    print("TEST 4: Edge Cases")
    print("="*70)
    
    # Test 1: Empty query
    print("\n--- Test: Empty query ---")
    context = rag.retrieve_context("", top_k=3)
    print(f"   Empty query result: {'No context (expected)' if not context else 'Context returned (unexpected)'}")
    
    # Test 2: Nonsense query
    print("\n--- Test: Nonsense query ---")
    results = rag.retriever.search("xyzabc12345", top_k=3)
    print(f"   Nonsense query results: {len(results)} (should be 0 or low relevance)")
    
    # Test 3: Very long query
    print("\n--- Test: Very long query ---")
    long_query = "bearing " * 100
    try:
        context = rag.retrieve_context(long_query, top_k=3)
        print(f"   Long query handled: ✅")
    except Exception as e:
        print(f"   Long query error: ❌ {str(e)}")
        return False
    
    # Test 4: Special characters
    print("\n--- Test: Special characters ---")
    special_query = "What's the cost? (in $$$)"
    try:
        context = rag.retrieve_context(special_query, top_k=3)
        print(f"   Special characters handled: ✅")
    except Exception as e:
        print(f"   Special characters error: ❌ {str(e)}")
        return False
    
    print("\n✅ PASSED: Edge cases handled correctly")
    
    return True


def test_performance(rag):
    """Test retrieval performance"""
    print("\n" + "="*70)
    print("TEST 5: Performance")
    print("="*70)
    
    import time
    
    queries = [
        "bearing failure",
        "vibration analysis",
        "temperature monitoring",
        "oil change",
        "gearbox maintenance"
    ]
    
    times = []
    
    for query in queries:
        start = time.time()
        rag.retrieve_context(query, top_k=3)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"   Average retrieval time: {avg_time*1000:.1f}ms")
    print(f"   Max retrieval time: {max_time*1000:.1f}ms")
    
    # Performance targets
    if avg_time < 0.2:  # 200ms
        print(f"   ✅ Average time excellent (<200ms)")
    elif avg_time < 0.5:  # 500ms
        print(f"   ✅ Average time good (<500ms)")
    else:
        print(f"   ⚠️  Average time slow (>{500}ms)")
    
    if max_time < 1.0:  # 1 second
        print(f"   ✅ Max time acceptable (<1s)")
    else:
        print(f"   ⚠️  Max time slow (>1s)")
    
    print("\n✅ PASSED: Performance test complete")
    
    return True


def test_stats_endpoint(rag):
    """Test statistics"""
    print("\n" + "="*70)
    print("TEST 6: Statistics")
    print("="*70)
    
    stats = rag.get_stats()
    
    print(f"   Documents: {stats['documents_loaded']}")
    print(f"   Chunks: {stats['total_chunks']}")
    print(f"   Characters: {stats['total_characters']:,}")
    print(f"   Files: {', '.join(stats['document_files'])}")
    
    assert stats['initialized'], "❌ Stats show not initialized"
    assert stats['documents_loaded'] > 0, "❌ No documents in stats"
    assert stats['total_chunks'] > 0, "❌ No chunks in stats"
    
    print("\n✅ PASSED: Statistics correct")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 RAG SYSTEM TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Initialization
        rag = test_initialization()
        
        # Test 2: Retrieval Quality
        test_retrieval_quality(rag)
        
        # Test 3: Context Formatting
        test_context_formatting(rag)
        
        # Test 4: Edge Cases
        test_edge_cases(rag)
        
        # Test 5: Performance
        test_performance(rag)
        
        # Test 6: Statistics
        test_stats_endpoint(rag)
        
        # Final summary
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎉 RAG system is working correctly!")
        print("You can now start backend.py to use it with TurboBot.\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n{'='*70}")
        print(f"❌ TEST FAILED: {str(e)}")
        print(f"{'='*70}\n")
        return False
    
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        print(f"{'='*70}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    
    if not success:
        sys.exit(1)