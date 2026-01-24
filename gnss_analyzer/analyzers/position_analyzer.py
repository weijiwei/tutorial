"""Analyzer for detecting position jumps and anomalies in GNSS data."""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from ..parsers import GNSSPoint


@dataclass
class PositionAnomaly:
    """Represents a detected position anomaly."""
    index: int
    point: GNSSPoint
    anomaly_type: str
    severity: str
    distance_jump: float
    expected_max_distance: float
    description: str
    context: Dict


class PositionAnalyzer:
    """Detect and analyze position jumps and anomalies."""

    def __init__(self, max_speed_mps: float = 50.0, max_acceleration: float = 10.0):
        """
        Initialize analyzer.

        Args:
            max_speed_mps: Maximum expected speed in meters per second
            max_acceleration: Maximum expected acceleration in m/s²
        """
        self.max_speed_mps = max_speed_mps
        self.max_acceleration = max_acceleration
        self.anomalies: List[PositionAnomaly] = []

    def detect_position_jumps(self, points: List[GNSSPoint]) -> List[PositionAnomaly]:
        """Detect sudden position jumps that exceed physical limits."""
        self.anomalies = []

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            # Calculate time difference
            time_diff = (curr_point.timestamp - prev_point.timestamp).total_seconds()
            if time_diff <= 0:
                continue

            # Calculate distance
            distance = prev_point.distance_to(curr_point)

            # Calculate implied speed
            speed = distance / time_diff

            # Expected maximum distance based on time and max speed
            expected_max = self.max_speed_mps * time_diff

            # Detect jump
            if speed > self.max_speed_mps:
                severity = "CRITICAL" if speed > self.max_speed_mps * 2 else "HIGH"

                # Analyze context
                context = {
                    'time_diff_seconds': time_diff,
                    'distance_meters': distance,
                    'implied_speed_mps': speed,
                    'implied_speed_kmh': speed * 3.6,
                    'prev_satellites': prev_point.satellites,
                    'curr_satellites': curr_point.satellites,
                    'prev_hdop': prev_point.hdop,
                    'curr_hdop': curr_point.hdop,
                    'prev_quality': prev_point.quality,
                    'curr_quality': curr_point.quality,
                    'satellite_drop': prev_point.satellites - curr_point.satellites,
                    'hdop_increase': curr_point.hdop - prev_point.hdop,
                }

                description = (
                    f"Position jump detected: {distance:.1f}m in {time_diff:.1f}s "
                    f"(implied speed: {speed*3.6:.1f} km/h, max expected: {self.max_speed_mps*3.6:.1f} km/h)"
                )

                anomaly = PositionAnomaly(
                    index=i,
                    point=curr_point,
                    anomaly_type="POSITION_JUMP",
                    severity=severity,
                    distance_jump=distance,
                    expected_max_distance=expected_max,
                    description=description,
                    context=context
                )

                self.anomalies.append(anomaly)

        return self.anomalies

    def detect_hdop_spikes(self, points: List[GNSSPoint], threshold: float = 5.0) -> List[PositionAnomaly]:
        """Detect sudden HDOP (accuracy) degradation."""
        hdop_anomalies = []

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            hdop_increase = curr_point.hdop - prev_point.hdop

            if hdop_increase > threshold:
                severity = "HIGH" if hdop_increase > threshold * 2 else "MEDIUM"

                context = {
                    'prev_hdop': prev_point.hdop,
                    'curr_hdop': curr_point.hdop,
                    'hdop_increase': hdop_increase,
                    'satellites': curr_point.satellites,
                }

                description = (
                    f"HDOP spike detected: {prev_point.hdop:.1f} → {curr_point.hdop:.1f} "
                    f"(increase: {hdop_increase:.1f})"
                )

                anomaly = PositionAnomaly(
                    index=i,
                    point=curr_point,
                    anomaly_type="HDOP_SPIKE",
                    severity=severity,
                    distance_jump=0,
                    expected_max_distance=0,
                    description=description,
                    context=context
                )

                hdop_anomalies.append(anomaly)

        return hdop_anomalies

    def detect_satellite_loss(self, points: List[GNSSPoint], threshold: int = 4) -> List[PositionAnomaly]:
        """Detect sudden satellite signal loss."""
        sat_anomalies = []

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            sat_drop = prev_point.satellites - curr_point.satellites

            if sat_drop >= threshold:
                severity = "HIGH" if sat_drop >= threshold * 2 else "MEDIUM"

                context = {
                    'prev_satellites': prev_point.satellites,
                    'curr_satellites': curr_point.satellites,
                    'satellites_lost': sat_drop,
                    'hdop': curr_point.hdop,
                }

                description = (
                    f"Satellite loss detected: {prev_point.satellites} → {curr_point.satellites} "
                    f"(lost {sat_drop} satellites)"
                )

                anomaly = PositionAnomaly(
                    index=i,
                    point=curr_point,
                    anomaly_type="SATELLITE_LOSS",
                    severity=severity,
                    distance_jump=0,
                    expected_max_distance=0,
                    description=description,
                    context=context
                )

                sat_anomalies.append(anomaly)

        return sat_anomalies

    def analyze_all(self, points: List[GNSSPoint]) -> List[PositionAnomaly]:
        """Run all anomaly detection algorithms."""
        all_anomalies = []

        all_anomalies.extend(self.detect_position_jumps(points))
        all_anomalies.extend(self.detect_hdop_spikes(points))
        all_anomalies.extend(self.detect_satellite_loss(points))

        # Sort by index
        all_anomalies.sort(key=lambda x: x.index)

        return all_anomalies
