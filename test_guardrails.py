"""
Test guardrails system
"""

from guardrails import content_filter

print("\n" + "="*70)
print("🧪 TESTING GUARDRAILS SYSTEM")
print("="*70)

# Test cases
test_cases = [
    # (question, should_be_valid, should_be_on_topic, description)
    
    # Valid on-topic
    ("What causes bearing failure?", True, True, "Valid technical question"),
    ("Is vibration of 4.2 mm/s too high?", True, True, "Valid measurement query"),
    ("How much does gearbox maintenance cost?", True, True, "Valid cost question"),
    ("Analyze current turbine performance", True, True, "Valid analysis request"),
    
    # Valid but off-topic
    ("What's the weather today?", True, False, "Off-topic: weather"),
    ("Tell me a joke", True, False, "Off-topic: entertainment"),
    ("How do I cook pasta?", True, False, "Off-topic: cooking"),
    
    # Invalid: too short
    ("", False, False, "Empty input"),
    ("a", False, False, "Too short"),
    
    # Invalid: security risks
    ("<script>alert('xss')</script>", False, False, "XSS attempt"),
    ("'; DROP TABLE users; --", False, False, "SQL injection attempt"),
    ("$(rm -rf /)", False, False, "Command injection"),
    
    # Invalid: inappropriate
    ("Show me porn", False, False, "Inappropriate content"),
    ("How to make a bomb", False, False, "Dangerous content"),
    
    # Invalid: spam
    ("x" * 600, False, False, "Too long"),
    ("!!!!!!!!!!!!!!!!!!!!!!!!!!", False, False, "Excessive special chars"),
]

print("\n📋 INPUT VALIDATION TESTS:\n")

passed = 0
failed = 0

for i, (question, should_be_valid, should_be_on_topic, description) in enumerate(test_cases, 1):
    result = content_filter.filter_input(question)
    
    # Check if result matches expectation
    valid_match = result['valid'] == should_be_valid
    topic_match = (not should_be_valid or result['on_topic'] == should_be_on_topic)
    
    test_passed = valid_match and topic_match
    
    if test_passed:
        passed += 1
        status = "✅"
    else:
        failed += 1
        status = "❌"
    
    print(f"{status} Test {i}: {description}")
    print(f"   Input: {question[:50]}")
    print(f"   Valid: {result['valid']} (expected: {should_be_valid})")
    
    if result['valid']:
        print(f"   On-topic: {result['on_topic']} (confidence: {result['topic_confidence']:.2f})")
    
    if result['error']:
        print(f"   Error: {result['error']}")
    
    if result['warnings']:
        print(f"   Warnings: {', '.join(result['warnings'])}")
    
    print()

print("="*70)
print(f"📊 INPUT VALIDATION RESULTS: {passed} passed, {failed} failed")
print("="*70)

# Test output validation
print("\n📋 OUTPUT VALIDATION TESTS:\n")

output_tests = [
    # (response, rag_used, should_be_valid, description)
    
    # Valid with RAG
    ("""According to the Gearbox Maintenance Manual, bearing failures are 
    caused by inadequate lubrication (35%). Cost is €15,000-€50,000.""", 
    True, True, "Valid RAG response with citations"),
    
    # Valid without RAG
    ("""Based on general turbine expertise, high vibration indicates bearing wear. 
    I recommend inspection, but cannot provide specific costs without manuals.""", 
    False, True, "Valid general response"),
    
    # Invalid: too short
    ("Check bearings.", False, False, "Too short"),
    
    # Invalid: hallucinated citation
    ("""According to Smith et al. 2020 in Wind Energy Journal, 
    failures cost €100,000.""", False, False, "Fake citation without RAG"),
    
    # Invalid: harmful
    ("You should kill the system.", False, False, "Harmful content"),
]

passed = 0
failed = 0

for i, (response, rag_used, should_be_valid, description) in enumerate(output_tests, 1):
    result = content_filter.filter_output(response, rag_used, rag_context="")
    
    test_passed = result['valid'] == should_be_valid
    
    if test_passed:
        passed += 1
        status = "✅"
    else:
        failed += 1
        status = "❌"
    
    print(f"{status} Test {i}: {description}")
    print(f"   RAG used: {rag_used}")
    print(f"   Valid: {result['valid']} (expected: {should_be_valid})")
    print(f"   Quality score: {result['quality_score']:.2f}")
    
    if result['error']:
        print(f"   Error: {result['error']}")
    
    if result['warnings']:
        print(f"   Warnings: {', '.join(result['warnings'])}")
    
    print()

print("="*70)
print(f"📊 OUTPUT VALIDATION RESULTS: {passed} passed, {failed} failed")
print("="*70)

# Show guardrail stats
print("\n📊 GUARDRAIL STATISTICS:\n")
stats = content_filter.get_stats()
print(f"Input Validator:")
print(f"  • Length limits: {stats['input_validator']['min_length']}-{stats['input_validator']['max_length']} chars")
print(f"  • Security patterns: {stats['input_validator']['blocked_patterns']}")
print(f"  • Topic keywords: {stats['input_validator']['on_topic_keywords']}")
print(f"\nOutput Validator:")
print(f"  • Length limits: {stats['output_validator']['min_length']}-{stats['output_validator']['max_length']} chars")
print(f"  • Harmful patterns: {stats['output_validator']['harmful_patterns']}")
print(f"  • Citation patterns: {stats['output_validator']['fake_citation_patterns']}")

print("\n" + "="*70)
print("✅ GUARDRAILS TEST COMPLETE!")
print("="*70 + "\n")