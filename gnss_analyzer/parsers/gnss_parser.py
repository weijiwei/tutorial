"""Parser for GNSS log files supporting multiple formats."""

import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class GNSSPoint:
    """Represents a single GNSS position reading."""
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float
    satellites: int
    hdop: float
    quality: int
    raw_line: str

    def distance_to(self, other: 'GNSSPoint') -> float:
        """Calculate distance to another point in meters using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371000  # Earth radius in meters

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        distance = R * c

        # Include altitude difference
        altitude_diff = abs(self.altitude - other.altitude)
        return sqrt(distance**2 + altitude_diff**2)


class GNSSLogParser:
    """Parse GNSS logs from various formats (NMEA, custom logs, etc.)."""

    def __init__(self):
        self.points: List[GNSSPoint] = []

    def parse_nmea_gga(self, line: str) -> Optional[GNSSPoint]:
        """Parse NMEA GGA sentence."""
        if not line.startswith('$GPGGA') and not line.startswith('$GNGGA'):
            return None

        try:
            parts = line.strip().split(',')

            # Extract time
            time_str = parts[1]
            if not time_str:
                return None

            hours = int(time_str[0:2])
            minutes = int(time_str[2:4])
            seconds = float(time_str[4:])
            timestamp = datetime.now().replace(hour=hours, minute=minutes,
                                              second=int(seconds),
                                              microsecond=int((seconds % 1) * 1000000))

            # Extract latitude
            lat_str = parts[2]
            lat_dir = parts[3]
            if not lat_str:
                return None
            lat_deg = float(lat_str[:2])
            lat_min = float(lat_str[2:])
            latitude = lat_deg + lat_min/60
            if lat_dir == 'S':
                latitude = -latitude

            # Extract longitude
            lon_str = parts[4]
            lon_dir = parts[5]
            if not lon_str:
                return None
            lon_deg = float(lon_str[:3])
            lon_min = float(lon_str[3:])
            longitude = lon_deg + lon_min/60
            if lon_dir == 'W':
                longitude = -longitude

            # Quality, satellites, HDOP
            quality = int(parts[6]) if parts[6] else 0
            satellites = int(parts[7]) if parts[7] else 0
            hdop = float(parts[8]) if parts[8] else 99.9

            # Altitude
            altitude = float(parts[9]) if parts[9] else 0.0

            return GNSSPoint(
                timestamp=timestamp,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                satellites=satellites,
                hdop=hdop,
                quality=quality,
                raw_line=line
            )
        except (IndexError, ValueError) as e:
            return None

    def parse_custom_format(self, line: str) -> Optional[GNSSPoint]:
        """Parse custom log format: timestamp,lat,lon,alt,sats,hdop,quality."""
        try:
            parts = line.strip().split(',')
            if len(parts) < 7:
                return None

            timestamp = datetime.fromisoformat(parts[0])

            return GNSSPoint(
                timestamp=timestamp,
                latitude=float(parts[1]),
                longitude=float(parts[2]),
                altitude=float(parts[3]),
                satellites=int(parts[4]),
                hdop=float(parts[5]),
                quality=int(parts[6]),
                raw_line=line
            )
        except (ValueError, IndexError):
            return None

    def parse_file(self, filepath: str) -> List[GNSSPoint]:
        """Parse a GNSS log file and return list of points."""
        self.points = []

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Try NMEA format first
                point = self.parse_nmea_gga(line)
                if point:
                    self.points.append(point)
                    continue

                # Try custom format
                point = self.parse_custom_format(line)
                if point:
                    self.points.append(point)

        return self.points

    def get_statistics(self) -> Dict:
        """Get basic statistics about parsed data."""
        if not self.points:
            return {}

        return {
            'total_points': len(self.points),
            'avg_satellites': sum(p.satellites for p in self.points) / len(self.points),
            'avg_hdop': sum(p.hdop for p in self.points) / len(self.points),
            'time_span': (self.points[-1].timestamp - self.points[0].timestamp).total_seconds(),
            'quality_distribution': {
                'no_fix': sum(1 for p in self.points if p.quality == 0),
                'gps_fix': sum(1 for p in self.points if p.quality == 1),
                'dgps_fix': sum(1 for p in self.points if p.quality == 2),
            }
        }
