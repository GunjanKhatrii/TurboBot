from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime, timedelta
from rag.rag_manager import RAGManager

app = Flask(__name__)
CORS(app)

print("\n🤖 Using MOCK AI (for testing)")
print("💰 Cost: FREE\n")

# Initialize RAG
rag_manager = RAGManager('data/knowledge_base')
rag_initialized = rag_manager.initialize()


def mock_ai_response(question, latest, rag_context):
    """Generate intelligent mock responses"""
    
    q = question.lower()
    
    # Extract info from RAG context if available
    has_rag = bool(rag_context)
    
    # Status check
    if 'status' in q or 'current' in q:
        temp_status = "⚠️ ELEVATED" if latest.get('temperature', 0) > 70 else "✅ NORMAL"
        vib_status = "⚠️ HIGH" if latest.get('vibration', 0) > 4.0 else "✅ NORMAL"
        
        response = f"""**Current Turbine Status**

**Metrics:**
- Power Output: {latest.get('power_output', 0):.0f} kW
- Wind Speed: {latest.get('wind_speed', 0):.1f} m/s
- Temperature: {latest.get('temperature', 0):.1f}°C {temp_status}
- Vibration: {latest.get('vibration', 0):.2f} {vib_status}
- Overall Status: {latest.get('status', 'N/A').upper()}

"""
        if has_rag:
            response += "\n**Based on maintenance guidelines:** Temperature should be kept below 70°C and vibration below 4.0 for optimal operation."
        
        return response
    
    # Issue detection
    elif 'issue' in q or 'problem' in q or 'wrong' in q:
        issues = []
        
        if latest.get('temperature', 0) > 70:
            issues.append(f"🌡️ High temperature ({latest.get('temperature'):.1f}°C > 70°C threshold)")
        
        if latest.get('vibration', 0) > 4.0:
            issues.append(f"📳 Elevated vibration ({latest.get('vibration'):.2f} > 4.0 threshold)")
        
        if latest.get('power_output', 0) < 1000 and latest.get('wind_speed', 0) > 8:
            issues.append(f"⚡ Underperformance (low power at {latest.get('wind_speed'):.1f} m/s wind)")
        
        if not issues:
            return "✅ **No issues detected.** System is operating within normal parameters."
        
        response = "⚠️ **Issues Detected:**\n\n"
        for issue in issues:
            response += f"- {issue}\n"
        
        if has_rag:
            response += "\n**Recommendation:** Monitor closely and schedule inspection within 24-48 hours if conditions persist. Review maintenance manual for detailed troubleshooting procedures."
        
        return response
    
    # Vibration questions
    elif 'vibration' in q:
        vib = latest.get('vibration', 0)
        
        if vib < 3.5:
            status = "within normal range"
            action = "Continue normal monitoring"
        elif vib < 4.0:
            status = "slightly elevated"
            action = "Increase monitoring frequency"
        else:
            status = "above warning threshold"
            action = "Schedule inspection within 48 hours"
        
        response = f"""**Vibration Analysis**

Current Level: {vib:.2f}
Status: {status}

**Normal Ranges:**
- Normal: 1.0 - 3.5
- Warning: 3.5 - 4.5
- Critical: > 4.5

**Action:** {action}
"""
        if has_rag:
            response += "\n**From maintenance manual:** High vibration can indicate bearing wear, blade imbalance, or misalignment. See vibration analysis guide for frequency-based diagnostics."
        
        return response
    
    # Temperature questions
    elif 'temperature' in q or 'temp' in q:
        temp = latest.get('temperature', 0)
        
        if temp < 60:
            status = "normal"
        elif temp < 70:
            status = "acceptable"
        else:
            status = "elevated - requires attention"
        
        response = f"""**Temperature Monitoring**

Current: {temp:.1f}°C
Status: {status}

**Normal Ranges:**
- Normal: 40-60°C
- Acceptable: 60-70°C
- Warning: 70-75°C
- Critical: >75°C
"""
        if has_rag:
            response += "\n**From maintenance manual:** Elevated temperatures may indicate inadequate lubrication, bearing wear, or cooling system issues. Check oil level and quality."
        
        return response
    
    # Power/performance questions
    elif 'power' in q or 'performance' in q or 'output' in q:
        power = latest.get('power_output', 0)
        wind = latest.get('wind_speed', 0)
        expected = min(((wind / 12) ** 3) * 2000, 2000) if wind > 0 else 0
        efficiency = (power / expected * 100) if expected > 0 else 0
        
        response = f"""**Performance Analysis**

Current Power: {power:.0f} kW
Wind Speed: {wind:.1f} m/s
Expected Power: {expected:.0f} kW
Efficiency: {efficiency:.0f}%

"""
        if efficiency < 85:
            response += "⚠️ Turbine is underperforming. Possible causes: blade erosion, pitch misalignment, or gearbox issues.\n"
        else:
            response += "✅ Performance is within expected range.\n"
        
        return response
    
    # Maintenance questions
    elif 'maintenance' in q or 'service' in q or 'repair' in q:
        response = """**Maintenance Recommendations**

**Immediate Actions:**
"""
        if latest.get('temperature', 0) > 70:
            response += "- Investigate high temperature (check oil level, inspect bearings)\n"
        if latest.get('vibration', 0) > 4.0:
            response += "- Perform vibration analysis to identify source\n"
        
        response += """
**Regular Maintenance Schedule:**
- Oil analysis: Every 6 months
- Visual inspection: Every 3 months
- Oil change: Every 12-24 months
- Major overhaul: Every 5-7 years
"""
        if has_rag:
            response += "\n**Note:** Detailed procedures available in maintenance manual. Costs range from $800 (oil change) to $250,000 (major failure)."
        
        return response
    
    # Default response
    else:
        return f"""I can help you analyze the turbine performance. Current data shows:

- Power: {latest.get('power_output', 0):.0f} kW
- Temperature: {latest.get('temperature', 0):.1f}°C
- Vibration: {latest.get('vibration', 0):.2f}
- Status: {latest.get('status', 'N/A')}

You can ask me about:
- Current status or issues
- Vibration or temperature analysis
- Performance and power output
- Maintenance recommendations
"""


@app.route('/api/turbine-chat', methods=['POST'])
def turbine_chat():
    try:
        data = request.json
        question = data.get('question')
        turbine_data = data.get('turbineData', [])
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        latest = turbine_data[-1] if turbine_data else {}
        
        # Get RAG context
        rag_context = ""
        if rag_initialized:
            rag_context = rag_manager.retrieve_context(question, top_k=2)
        
        # Generate response
        response_text = mock_ai_response(question, latest, rag_context)
        
        return jsonify({"response": response_text})
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/turbine-data', methods=['GET'])
def get_turbine_data():
    try:
        data = []
        now = datetime.now()
        
        for i in range(48):
            timestamp = (now - timedelta(hours=47-i)).isoformat()
            wind_speed = random.uniform(5, 14) + random.gauss(0, 1)
            wind_speed = max(3, min(15, wind_speed))
            
            max_power = 2000
            power_output = min(((wind_speed / 12) ** 3) * max_power, max_power)
            power_output += random.gauss(0, 50)
            power_output = max(0, power_output)
            
            temperature = 40 + (power_output / max_power) * 20 + random.gauss(0, 3)
            if i >= 36:
                temperature += (i - 36) * 1.2
                power_output *= 0.85
            
            vibration = 1.5 + (temperature - 40) / 20 + random.gauss(0, 0.3)
            if i >= 36:
                vibration += (i - 36) * 0.15
            
            status = 'warning' if (temperature > 70 or vibration > 4.0) else 'operating'
            
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


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "TurboBot Backend (Mock AI)",
        "ai_provider": "mock",
        "rag_initialized": rag_initialized
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 TurboBot Backend Server (Mock AI for Testing)")
    print("="*70)
    print("📡 Server: http://localhost:5000")
    print("💡 This is a temporary mock - install Ollama for real AI")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)