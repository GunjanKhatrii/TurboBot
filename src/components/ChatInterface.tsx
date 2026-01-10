import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Loader2 } from "lucide-react";
import { TurbineDataPoint } from "@/lib/turbineData";
import { toast } from "sonner";

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  turbineData: TurbineDataPoint[];
}

// Clean markdown formatting from AI responses
function cleanMarkdown(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold **text**
    .replace(/\*([^*]+)\*/g, '$1')     // Remove italic *text*
    .replace(/^\*\s+/gm, '• ')         // Convert bullet points to •
    .replace(/^-\s+/gm, '• ')          // Convert - bullets to •
    .replace(/^#+\s*/gm, '')           // Remove markdown headers
    .replace(/`([^`]+)`/g, '$1')       // Remove inline code
    .trim();
}

const QUICK_QUESTIONS = [
  "What's the current turbine status?",
  "Are there any issues?",
  "Show performance summary",
  "Explain the power curve"
];

export const ChatInterface = ({ turbineData }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I\'m TurboBot. Ask me anything about the wind turbine performance and health.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (question: string) => {
    if (!question.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: question };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call Python Flask backend
      const response = await fetch('http://localhost:5000/api/turbine-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          turbineData: turbineData.slice(-24), // Last 24 hours
          messages: messages.slice(-6) // Keep conversation context
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const cleanedResponse = cleanMarkdown(data.response);
      const assistantMessage: Message = { role: 'assistant', content: cleanedResponse };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response from TurboBot. Using fallback analysis.');
      // Fallback to basic analysis
      const fallbackResponse = generateFallbackResponse(question, turbineData);
      setMessages(prev => [...prev, { role: 'assistant', content: fallbackResponse }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    sendMessage(question);
  };

  return (
    <Card className="flex flex-col border-4 border-[hsl(207,44%,49%)] flex-1 min-h-0">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <span>TurboBot</span>
          <span>💬</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4 p-4 min-h-0">
        <ScrollArea className="flex-1 min-h-0" ref={scrollRef}>
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`rounded-lg px-4 py-2 max-w-[85%] ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            {QUICK_QUESTIONS.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => handleQuickQuestion(question)}
                disabled={isLoading}
                className="text-xs"
              >
                {question}
              </Button>
            ))}
          </div>

          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
              placeholder="Ask about turbine performance..."
              disabled={isLoading}
            />
            <Button onClick={() => sendMessage(input)} disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Fallback response when AI is not available
function generateFallbackResponse(question: string, data: TurbineDataPoint[]): string {
  const latest = data[data.length - 1];
  const recent = data.slice(-12);
  const avgPower = recent.reduce((sum, d) => sum + d.power_output, 0) / recent.length;
  
  const lowerQuestion = question.toLowerCase();
  
  if (lowerQuestion.includes('status') || lowerQuestion.includes('current')) {
    return `Current turbine status: ${latest.status.toUpperCase()}\n\nPower: ${latest.power_output}kW\nWind Speed: ${latest.wind_speed}m/s\nTemperature: ${latest.temperature}°C\nVibration: ${latest.vibration}`;
  }
  
  if (lowerQuestion.includes('issue') || lowerQuestion.includes('problem') || lowerQuestion.includes('wrong')) {
    const issues = [];
    if (latest.temperature > 70) issues.push(`High temperature (${latest.temperature}°C)`);
    if (latest.vibration > 4.0) issues.push(`Elevated vibration (${latest.vibration})`);
    if (issues.length === 0) return 'No issues detected. System operating normally.';
    return `Issues detected:\n${issues.join('\n')}\n\nRecommend inspection within 48 hours.`;
  }
  
  if (lowerQuestion.includes('summary') || lowerQuestion.includes('performance')) {
    return `Performance Summary (Last 12 hours):\n\nAverage Power: ${Math.round(avgPower)}kW\nCurrent Status: ${latest.status}\nTemperature: ${latest.temperature}°C\nVibration: ${latest.vibration}`;
  }
  
  if (lowerQuestion.includes('power curve') || lowerQuestion.includes('explain')) {
    return 'The power curve shows the relationship between wind speed and power output. Power increases cubically with wind speed until rated capacity (2000kW). The turbine operates most efficiently at wind speeds between 8-12 m/s.';
  }
  
  return 'I can help you analyze turbine performance, identify issues, and explain operational patterns. Try asking about the current status, any issues, or performance summary.';
}