from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import traceback

# Import RAG and Guardrails
from rag.rag_manager import RAGManager
from guardrails import content_filter

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

AI_MODEL = None

# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================

print(f"\n🤖 AI Provider: OLLAMA")
print("="*70)

import ollama

print("🔍 Searching for working Ollama model...")
try:
    available = ollama.list()
    models = available.get('models', [])
    
    if not models:
        print("❌ No models installed!")
        print("💡 Install: ollama pull llama3.2:1b")
        exit(1)
    
    print(f"\n📋 Available models:")
    for model in models:
        name = model.get('name', 'unknown')
        size_bytes = model.get('size', 0)
        size_gb = size_bytes / (1024**3)
        print(f"   • {name} ({size_gb:.1f} GB)")
    
    # Test models
    print(f"\n🧪 Testing models...")
    for model in models:
        model_name = model.get('name', '')
        if not model_name:
            continue
        
        print(f"   Testing: {model_name}...", end=" ")
        
        try:
            response = ollama.generate(
                model=model_name,
                prompt="Say OK",
                options={"num_predict": 5}
            )
            print("✅ WORKS!")
            AI_MODEL = model_name
            break
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            continue
    
    if not AI_MODEL:
        print("\n❌ No working models!")
        print("💡 Try: ollama pull llama3.2:1b")
        exit(1)
    
    print(f"\n✅ Selected: {AI_MODEL}")
        
except Exception as e:
    print(f"❌ Cannot connect to Ollama: {e}")
    print("💡 Start Ollama: ollama serve")
    exit(1)

print(f"📦 Model: {AI_MODEL}")
print(f"🔧 API: generate")
print("💰 Cost: FREE")
print("="*70)

# ============================================================================
# RAG INITIALIZATION
# ============================================================================

print("\n🚀 Initializing RAG System...")
print("="*70)

rag_manager = RAGManager('data/knowledge_base')
rag_initialized = rag_manager.initialize()

if not rag_initialized:
    print("\n⚠️  RAG not initialized")
else:
    print("\n✅ RAG System ready!")

# ============================================================================
# GUARDRAILS INITIALIZATION
# ============================================================================

print("\n🛡️  Initializing Guardrails...")
print("="*70)

guardrail_stats = content_filter.get_stats()
print(f"✅ Input validator: {guardrail_stats['input_validator']['blocked_patterns']} security patterns")
print(f"✅ Output validator: {guardrail_stats['output_validator']['harmful_patterns']} safety checks")
print(f"✅ Topic validator: {guardrail_stats['input_validator']['on_topic_keywords']} turbine keywords")

print("\n✅ Backend ready with guardrails!\n")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_fallback_response(latest):
    """Fallback if AI fails"""
    temp = latest.get('temperature', 0)
    vib = latest.get('vibration', 0)
    power = latest.get('power_output', 0)
    
    issues = []
    if temp > 70:
        issues.append("⚠️ Temperature elevated (>70°C)")
    if vib > 4.0:
        issues.append("⚠️ Vibration high (>4.0)")
    
    status = "\n".join(issues) if issues else "✅ Parameters normal"
    
    return f"""**TurboBot Automated Analysis**

**Current Status:**
- Power: {power} kW
- Temperature: {temp}°C
- Vibration: {vib} mm/s

**Assessment:**
{status}

**Normal Ranges:**
- Temperature: 40-60°C (Warning >70°C)
- Vibration: 1.0-3.5 (Warning >4.0)

*AI assistant temporarily unavailable - automated analysis provided*"""


def call_ollama(system_prompt, question):
    """Call Ollama - Generate detailed response"""
    try:
        # Build prompt
        prompt = f"{system_prompt}\n\nUser: {question}\n\nAssistant:"
        
        print(f"   🔄 Generating response...")
        
        response = ollama.generate(
            model=AI_MODEL,
            prompt=prompt,
            options={
                "temperature": 0.7,
                "num_predict": 800,
            }
        )
        
        return response['response'].strip()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        return None

# ============================================================================
# CHAT ENDPOINT WITH GUARDRAILS
# ============================================================================

@app.route('/api/turbine-chat', methods=['POST'])
def turbine_chat():
    """Chat endpoint with RAG and Guardrails"""
    print(f"\n{'='*70}")
    print("📥 CHAT REQUEST WITH GUARDRAILS")
    print(f"{'='*70}")
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        turbine_data = data.get('turbineData', [])
        
        # =================================================================
        # GUARDRAIL 1: INPUT VALIDATION
        # =================================================================
        
        print("🛡️  Step 1: Input validation...")
        input_check = content_filter.filter_input(question)
        
        if not input_check['valid']:
            print(f"   ❌ Invalid input: {input_check['error']}")
            return jsonify({
                "error": input_check['error'],
                "type": "input_validation_error",
                "warnings": input_check['warnings']
            }), 400
        
        print(f"   ✅ Input valid")
        
        # =================================================================
        # GUARDRAIL 2: TOPIC VALIDATION
        # =================================================================
        
        print(f"🛡️  Step 2: Topic validation...")
        
        if not input_check['on_topic']:
            print(f"   ⚠️  Off-topic (confidence: {input_check['topic_confidence']:.2f})")
            print(f"   Reason: {input_check['topic_reason']}")
            
            off_topic_response = content_filter.generate_off_topic_response(
                question, 
                input_check['topic_confidence'],
                input_check['suggestions']
            )
            
            return jsonify({
                "response": off_topic_response,
                "rag_used": False,
                "guardrails": {
                    "off_topic": True,
                    "topic_confidence": input_check['topic_confidence'],
                    "reason": input_check['topic_reason'],
                    "suggestions": input_check['suggestions']
                }
            })
        
        print(f"   ✅ On-topic (confidence: {input_check['topic_confidence']:.2f})")
        
        # Use sanitized question
        question = input_check['sanitized_question']
        print(f"❓ {question}")
        
        # =================================================================
        # TURBINE DATA PROCESSING
        # =================================================================
        
        latest = turbine_data[-1] if turbine_data else {}
        
        # Calculate stats
        if len(turbine_data) > 0:
            avg_power = sum(d.get('power_output', 0) for d in turbine_data) / len(turbine_data)
            max_temp = max(d.get('temperature', 0) for d in turbine_data)
            max_vib = max(d.get('vibration', 0) for d in turbine_data)
            avg_wind = sum(d.get('wind_speed', 0) for d in turbine_data) / len(turbine_data)
        else:
            avg_power = max_temp = max_vib = avg_wind = 0
        
        # =================================================================
        # RAG RETRIEVAL
        # =================================================================
        
        print("🔍 Step 3: RAG retrieval...")
        rag_context = ""
        rag_used = False
        
        if rag_initialized:
            try:
                rag_context = rag_manager.retrieve_context(question, top_k=3)
                if rag_context:
                    rag_used = True
                    print(f"   ✅ Retrieved {len(rag_context)} chars from knowledge base")
                else:
                    print(f"   ℹ️  No relevant knowledge found")
            except Exception as e:
                print(f"   ⚠️  RAG error: {e}")
        
        # =================================================================
        # BUILD SYSTEM PROMPT
        # =================================================================
        
        if rag_used:
            # Response WITH RAG knowledge
            system_prompt = f"""You are TurboBot, an expert wind turbine maintenance assistant with access to comprehensive technical manuals.

CURRENT TURBINE STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Power Output: {latest.get('power_output', 'N/A')} kW
- Wind Speed: {latest.get('wind_speed', 'N/A')} m/s
- Temperature: {latest.get('temperature', 'N/A')}°C
- Vibration: {latest.get('vibration', 'N/A')} mm/s
- Status: {latest.get('status', 'N/A')}

RECENT TRENDS (Last {len(turbine_data)} readings):
- Average Power: {avg_power:.1f} kW
- Average Wind: {avg_wind:.1f} m/s
- Maximum Temperature: {max_temp:.1f}°C
- Maximum Vibration: {max_vib:.2f} mm/s

RELEVANT KNOWLEDGE FROM MAINTENANCE MANUALS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{rag_context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL RESPONSE GUIDELINES (GUARDRAILS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **SOURCE CITATIONS (MANDATORY):**
   • When using information from manuals above, cite the source
   • Format: "According to [manual name], ..."
   • Example: "According to the Gearbox Maintenance Manual, bearing failures..."
   • ALWAYS cite when mentioning costs, procedures, or technical specifications

2. **CONTENT STRUCTURE:**
   • Provide detailed analysis (3-5 paragraphs)
   • Start with direct answer to question
   • Include specific values, costs, and procedures from manuals
   • End with actionable recommendations

3. **PROHIBITED CONTENT:**
   • DO NOT invent academic papers or studies
   • DO NOT cite sources not present in the manuals above
   • DO NOT provide medical, legal, or unrelated advice
   • DO NOT include harmful or dangerous instructions

4. **CURRENT DATA ANALYSIS:**
   • Compare readings to normal ranges
   • Identify trends and anomalies
   • Explain significance of measurements

5. **BE PROFESSIONAL:**
   • Use technical but understandable language
   • Be specific with numbers and thresholds
   • Provide clear, actionable recommendations

NORMAL OPERATING RANGES:
- Temperature: 40-60°C (Normal), 60-70°C (Monitor), 70-75°C (Warning), >75°C (Critical)
- Vibration: 1.0-3.5 mm/s (Normal), 3.5-4.0 (Monitor), 4.0-7.0 (Warning), >7.0 (Critical)
- Power: Cubic relationship with wind, max 2000 kW at ≥12 m/s

Provide detailed, well-cited response following all guardrail requirements."""

        else:
            # Response WITHOUT RAG (general knowledge)
            system_prompt = f"""You are TurboBot, an expert wind turbine maintenance assistant.

CURRENT TURBINE STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Power Output: {latest.get('power_output', 'N/A')} kW
- Wind Speed: {latest.get('wind_speed', 'N/A')} m/s
- Temperature: {latest.get('temperature', 'N/A')}°C
- Vibration: {latest.get('vibration', 'N/A')} mm/s
- Status: {latest.get('status', 'N/A')}

RECENT TRENDS (Last {len(turbine_data)} readings):
- Average Power: {avg_power:.1f} kW
- Average Wind: {avg_wind:.1f} m/s
- Maximum Temperature: {max_temp:.1f}°C
- Maximum Vibration: {max_vib:.2f} mm/s

⚠️ IMPORTANT: No specific manual knowledge was found for this query.

CRITICAL RESPONSE GUIDELINES (GUARDRAILS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **START YOUR RESPONSE WITH:**
   "⚠️ Note: This response is based on general wind turbine expertise rather than specific maintenance manual procedures."

2. **PROHIBITED CONTENT:**
   • DO NOT invent specific costs or cite made-up sources
   • DO NOT reference academic papers or studies
   • DO NOT claim information is from manuals when it isn't
   • DO NOT provide medical, legal, or unrelated advice

3. **PROVIDE:**
   • Analysis of current turbine data
   • General recommendations based on industry standards
   • Suggestion to consult manuals for specific procedures/costs

4. **BE HONEST:**
   • Acknowledge limitations without manual access
   • Provide ranges rather than specific values
   • Recommend verification with documentation

NORMAL OPERATING RANGES:
- Temperature: 40-60°C (Normal), 60-70°C (Monitor), 70-75°C (Warning), >75°C (Critical)
- Vibration: 1.0-3.5 mm/s (Normal), 3.5-4.0 (Monitor), 4.0-7.0 (Warning), >7.0 (Critical)
- Power: Cubic relationship with wind, max 2000 kW at ≥12 m/s

Provide detailed response based on general turbine expertise."""
        
        # =================================================================
        # CALL AI MODEL
        # =================================================================
        
        print(f"🤖 Step 4: Calling {AI_MODEL}...")
        print(f"   RAG context: {'Yes' if rag_used else 'No'}")
        
        response = call_ollama(system_prompt, question)
        
        if not response:
            print("⚠️ AI failed, using fallback")
            return jsonify({
                "response": generate_fallback_response(latest),
                "rag_used": False,
                "guardrails": {"ai_failed": True}
            })
        
        # =================================================================
        # GUARDRAIL 3: OUTPUT VALIDATION
        # =================================================================
        
        print("🛡️  Step 5: Output validation...")
        output_check = content_filter.filter_output(response, rag_used, rag_context)
        
        if not output_check['valid']:
            print(f"   ❌ Invalid output: {output_check['error']}")
            
            # Use fallback instead of showing error to user
            return jsonify({
                "response": generate_fallback_response(latest),
                "rag_used": False,
                "guardrails": {
                    "output_validation_failed": True,
                    "reason": output_check['error'],
                    "warnings": output_check['warnings']
                }
            })
        
        print(f"   ✅ Output valid (quality: {output_check['quality_score']:.2f})")
        
        if output_check['hallucination_detected']:
            print(f"   ⚠️  Hallucination detected (confidence: {output_check['hallucination_confidence']:.2f})")
        
        if output_check['warnings']:
            print(f"   ⚠️  Warnings: {', '.join(output_check['warnings'])}")
        
        # =================================================================
        # SUCCESS RESPONSE
        # =================================================================
        
        print(f"✅ Response: {len(output_check['sanitized_response'])} chars")
        print(f"{'='*70}\n")
        
        return jsonify({
            "response": output_check['sanitized_response'],
            "rag_used": rag_used,
            "sources_count": 3 if rag_used else 0,
            "guardrails": {
                "input_validated": True,
                "output_validated": True,
                "on_topic": True,
                "topic_confidence": input_check['topic_confidence'],
                "quality_score": output_check['quality_score'],
                "hallucination_detected": output_check['hallucination_detected'],
                "hallucination_confidence": output_check['hallucination_confidence'],
                "warnings": output_check['warnings'],
                "input_warnings": input_check['warnings']
            }
        })
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OTHER ENDPOINTS
# ============================================================================

@app.route('/api/turbine-data', methods=['GET'])
def get_turbine_data():
    """Generate synthetic turbine data"""
    try:
        data = []
        now = datetime.now()
        
        for i in range(48):
            timestamp = (now - timedelta(hours=47-i)).isoformat()
            wind_speed = random.uniform(5, 14) + random.gauss(0, 1)
            wind_speed = max(3, min(15, wind_speed))
            
            if wind_speed < 3:
                power_output = 0
            elif wind_speed >= 12:
                power_output = 2000
            else:
                power_output = (wind_speed / 12) ** 3 * 2000
            
            power_output += random.gauss(0, 50)
            power_output = max(0, min(2000, power_output))
            
            temperature = 40 + (power_output / 2000) * 20 + random.gauss(0, 3)
            if i >= 36:
                temperature += (i - 36) * 1.2
                power_output *= 0.85
            
            vibration = 1.5 + (temperature - 40) / 20 + random.gauss(0, 0.3)
            if i >= 36:
                vibration += (i - 36) * 0.15
            vibration = max(0.5, vibration)
            
            status = 'operating'
            if temperature > 70 or vibration > 4.0:
                status = 'warning'
            
            data.append({
                'timestamp': timestamp,
                'power_output': round(power_output, 1),
                'wind_speed': round(wind_speed, 2),
                'temperature': round(temperature, 1),
                'vibration': round(vibration, 2),
                'status': status
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/knowledge-base/stats', methods=['GET'])
def kb_stats():
    """Knowledge base statistics"""
    if not rag_initialized:
        return jsonify({"initialized": False})
    return jsonify(rag_manager.get_stats())


@app.route('/api/guardrails/stats', methods=['GET'])
def guardrails_stats():
    """Guardrail statistics"""
    return jsonify(content_filter.get_stats())


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "model": AI_MODEL,
        "rag": rag_initialized,
        "guardrails": True,
        "features": ["RAG", "Guardrails", "Ollama"]
    })


@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "message": "TurboBot with Guardrails running!",
        "model": AI_MODEL,
        "features": ["RAG", "Guardrails", "Topic Validation", "Output Filtering"]
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 TURBOBOT BACKEND WITH GUARDRAILS")
    print("="*70)
    print(f"🤖 Model: {AI_MODEL}")
    print(f"📚 RAG: {'✅ Enabled' if rag_initialized else '⚠️  Disabled'}")
    print(f"🛡️  Guardrails: ✅ Enabled")
    print(f"📡 Server: http://localhost:5000")
    print("="*70)
    print("\n🛡️  Guardrail Features:")
    print("   • Input validation (security, length, spam)")
    print("   • Topic relevance checking")
    print("   • Output quality validation")
    print("   • Hallucination detection")
    print("   • Citation verification")
    print("="*70)
    print("\n⚠️  Requirements:")
    print("   1. Ollama server running: ollama serve")
    print("   2. Model loaded: ollama pull llama3.2:1b")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)