"""AI-powered root cause analysis for GNSS anomalies using on-premise models."""

import os
import json
import requests
from typing import List, Dict, Optional
from .position_analyzer import PositionAnomaly


class AIAnalyzer:
    """Use on-premise AI models to analyze GNSS anomalies and determine root causes.

    Supports:
    - Ollama (local model deployment) - RECOMMENDED
    - HuggingFace Transformers (direct model loading)
    - Any OpenAI-compatible API endpoint
    """

    def __init__(
        self,
        model: str = "mistral:7b",
        backend: str = "ollama",
        api_url: Optional[str] = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize AI analyzer with on-premise model.

        Args:
            model: Model name (e.g., "mistral:7b", "llama2:13b", "codellama:7b")
            backend: Backend to use ("ollama", "huggingface", or "api")
            api_url: Custom API endpoint URL (for "api" backend)
            hf_token: HuggingFace token (optional, for gated models)
        """
        self.model = model
        self.backend = backend
        self.api_url = api_url or os.getenv('LLM_API_URL', 'http://localhost:11434')
        self.hf_token = hf_token or os.getenv('HF_TOKEN')
        self.client = None

        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the selected backend."""
        if self.backend == "ollama":
            # Check if Ollama is running
            try:
                response = requests.get(f"{self.api_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    self.client = "ollama"
                    print(f"✓ Connected to Ollama at {self.api_url}")
                else:
                    print(f"⚠ Ollama not responding at {self.api_url}")
            except Exception as e:
                print(f"⚠ Cannot connect to Ollama: {e}")
                print("  Install: https://ollama.ai/download")
                print(f"  Then run: ollama pull {self.model}")

        elif self.backend == "huggingface":
            try:
                from transformers import pipeline
                print(f"Loading HuggingFace model: {self.model}...")
                self.client = pipeline(
                    "text-generation",
                    model=self.model,
                    token=self.hf_token,
                    device_map="auto"
                )
                print("✓ HuggingFace model loaded")
            except ImportError:
                print("⚠ transformers package not installed")
                print("  Install with: pip install transformers torch")
            except Exception as e:
                print(f"⚠ Error loading model: {e}")

        elif self.backend == "api":
            # Custom API endpoint
            self.client = "api"
            print(f"Using custom API endpoint: {self.api_url}")

    def analyze_anomaly(self, anomaly: PositionAnomaly, surrounding_context: Dict = None) -> Dict:
        """
        Analyze a single anomaly and determine likely root cause.

        Args:
            anomaly: The detected anomaly
            surrounding_context: Additional context about surrounding points

        Returns:
            Dictionary with analysis results including root cause and recommendations
        """
        if not self.client:
            return self._fallback_analysis(anomaly)

        # Prepare context for AI
        context_str = self._format_anomaly_context(anomaly, surrounding_context)

        # Create prompt
        prompt = f"""You are a GNSS/GPS expert analyzing positioning errors.

Analyze this GNSS anomaly and provide:
1. Most likely root cause(s)
2. Confidence level (0-100%)
3. Recommended fixes or mitigations
4. Additional diagnostic steps

Anomaly Details:
{context_str}

Provide your analysis in JSON format:
{{
    "root_causes": [
        {{
            "cause": "description of cause",
            "confidence": 85,
            "evidence": ["evidence point 1", "evidence point 2"]
        }}
    ],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "diagnostic_steps": ["step 1", "step 2"],
    "summary": "brief summary of the issue"
}}
"""

        try:
            # Route to appropriate backend
            if self.backend == "ollama":
                content = self._call_ollama(prompt)
            elif self.backend == "huggingface":
                content = self._call_huggingface(prompt)
            elif self.backend == "api":
                content = self._call_custom_api(prompt)
            else:
                return self._fallback_analysis(anomaly)

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)
            analysis['ai_model'] = f"{self.backend}:{self.model}"
            analysis['backend'] = self.backend

            return analysis

        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_analysis(anomaly)

    def analyze_multiple_anomalies(self, anomalies: List[PositionAnomaly]) -> Dict:
        """
        Analyze multiple related anomalies to find patterns.

        Args:
            anomalies: List of detected anomalies

        Returns:
            Dictionary with pattern analysis and overall assessment
        """
        if not self.client:
            return self._fallback_pattern_analysis(anomalies)

        # Prepare summary
        summary = self._format_anomaly_summary(anomalies)

        prompt = f"""You are a GNSS/GPS expert analyzing multiple positioning errors.

Analyze these {len(anomalies)} GNSS anomalies and identify:
1. Common patterns or trends
2. Systemic issues vs isolated incidents
3. Primary root cause affecting multiple anomalies
4. Priority order for addressing issues

Anomaly Summary:
{summary}

Provide analysis in JSON format:
{{
    "patterns": ["pattern 1", "pattern 2"],
    "systemic_issues": [
        {{
            "issue": "description",
            "affected_anomalies": [0, 1, 2],
            "severity": "HIGH/MEDIUM/LOW"
        }}
    ],
    "primary_root_cause": "main issue description",
    "priority_actions": ["action 1", "action 2"],
    "overall_assessment": "summary of findings"
}}
"""

        try:
            # Route to appropriate backend
            if self.backend == "ollama":
                content = self._call_ollama(prompt)
            elif self.backend == "huggingface":
                content = self._call_huggingface(prompt)
            elif self.backend == "api":
                content = self._call_custom_api(prompt)
            else:
                return self._fallback_pattern_analysis(anomalies)

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)
            analysis['ai_model'] = f"{self.backend}:{self.model}"
            analysis['backend'] = self.backend
            analysis['total_anomalies_analyzed'] = len(anomalies)

            return analysis

        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._fallback_pattern_analysis(anomalies)

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        url = f"{self.api_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1000
            }
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()['response']

    def _call_huggingface(self, prompt: str) -> str:
        """Call HuggingFace pipeline."""
        result = self.client(
            prompt,
            max_new_tokens=1000,
            temperature=0.3,
            do_sample=True,
            top_p=0.95
        )
        return result[0]['generated_text'][len(prompt):]

    def _call_custom_api(self, prompt: str) -> str:
        """Call custom API endpoint (OpenAI-compatible format)."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert in GNSS/GPS systems and error analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        response = requests.post(f"{self.api_url}/v1/chat/completions", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def _format_anomaly_context(self, anomaly: PositionAnomaly, surrounding_context: Dict = None) -> str:
        """Format anomaly data for AI analysis."""
        lines = [
            f"Type: {anomaly.anomaly_type}",
            f"Severity: {anomaly.severity}",
            f"Description: {anomaly.description}",
            f"",
            "Context:",
        ]

        for key, value in anomaly.context.items():
            lines.append(f"  {key}: {value}")

        if surrounding_context:
            lines.append("\nSurrounding Context:")
            for key, value in surrounding_context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

    def _format_anomaly_summary(self, anomalies: List[PositionAnomaly]) -> str:
        """Format multiple anomalies for pattern analysis."""
        lines = []

        for i, anomaly in enumerate(anomalies):
            lines.append(f"\nAnomaly #{i}:")
            lines.append(f"  Type: {anomaly.anomaly_type}")
            lines.append(f"  Severity: {anomaly.severity}")
            lines.append(f"  {anomaly.description}")

            # Key context
            if 'satellite_drop' in anomaly.context:
                lines.append(f"  Satellite drop: {anomaly.context['satellite_drop']}")
            if 'hdop_increase' in anomaly.context:
                lines.append(f"  HDOP increase: {anomaly.context['hdop_increase']:.1f}")
            if 'implied_speed_kmh' in anomaly.context:
                lines.append(f"  Implied speed: {anomaly.context['implied_speed_kmh']:.1f} km/h")

        return "\n".join(lines)

    def _fallback_analysis(self, anomaly: PositionAnomaly) -> Dict:
        """Fallback rule-based analysis when AI is unavailable."""
        root_causes = []

        if anomaly.anomaly_type == "POSITION_JUMP":
            # Analyze based on context
            if anomaly.context.get('satellite_drop', 0) >= 3:
                root_causes.append({
                    "cause": "Satellite signal loss",
                    "confidence": 85,
                    "evidence": [f"Lost {anomaly.context['satellite_drop']} satellites"]
                })

            if anomaly.context.get('hdop_increase', 0) > 3:
                root_causes.append({
                    "cause": "HDOP degradation indicating poor geometry",
                    "confidence": 80,
                    "evidence": [f"HDOP increased by {anomaly.context['hdop_increase']:.1f}"]
                })

            if anomaly.context.get('curr_quality', 1) == 0:
                root_causes.append({
                    "cause": "Fix quality lost",
                    "confidence": 90,
                    "evidence": ["Quality indicator shows no fix"]
                })

            if not root_causes:
                root_causes.append({
                    "cause": "Multipath interference or signal obstruction",
                    "confidence": 60,
                    "evidence": ["Position jump without clear satellite/HDOP correlation"]
                })

        elif anomaly.anomaly_type == "HDOP_SPIKE":
            root_causes.append({
                "cause": "Poor satellite geometry",
                "confidence": 85,
                "evidence": [f"HDOP increased to {anomaly.context['curr_hdop']:.1f}"]
            })

        elif anomaly.anomaly_type == "SATELLITE_LOSS":
            root_causes.append({
                "cause": "Signal obstruction or interference",
                "confidence": 80,
                "evidence": [f"Lost {anomaly.context['satellites_lost']} satellites"]
            })

        return {
            "root_causes": root_causes,
            "recommendations": [
                "Check for physical obstructions (buildings, terrain)",
                "Verify antenna placement and condition",
                "Review for interference sources",
                "Consider using DGPS/RTK corrections"
            ],
            "diagnostic_steps": [
                "Review satellite visibility at time of anomaly",
                "Check signal strength indicators",
                "Analyze environment for obstructions",
                "Verify receiver configuration"
            ],
            "summary": f"{anomaly.anomaly_type} detected with {anomaly.severity} severity",
            "ai_model": "rule-based (fallback)"
        }

    def _fallback_pattern_analysis(self, anomalies: List[PositionAnomaly]) -> Dict:
        """Fallback pattern analysis when AI is unavailable."""
        types = {}
        for a in anomalies:
            types[a.anomaly_type] = types.get(a.anomaly_type, 0) + 1

        return {
            "patterns": [f"{count} {atype} anomalies detected" for atype, count in types.items()],
            "systemic_issues": [],
            "primary_root_cause": f"Multiple {max(types, key=types.get)} events detected",
            "priority_actions": ["Review GNSS receiver configuration", "Check for environmental factors"],
            "overall_assessment": f"Detected {len(anomalies)} total anomalies requiring investigation",
            "ai_model": "rule-based (fallback)"
        }
