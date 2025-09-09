"""
Integration utilities for SwarmSort when used within the swarmtracker pipeline.

This module provides compatibility layers and integration helpers that allow
SwarmSort to seamlessly work with the full swarmtracker ecosystem while
maintaining standalone functionality.
"""
import sys
import importlib
import numpy as np
from typing import Optional, Any, Type, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import SwarmSortTracker
from pathlib import Path

from .data_classes import Detection as StandaloneDetection, TrackedObject as StandaloneTrackedObject
from .config import SwarmSortConfig


def is_within_swarmtracker() -> bool:
    """
    Detect if SwarmSort is being used within the swarmtracker pipeline.

    Returns:
        bool: True if running within swarmtracker, False if standalone
    """
    try:
        # Check if swarmtracker modules are available
        import swarmtracker
        import swarmtracker.tracking.data_class

        return True
    except ImportError:
        return False


def get_swarmtracker_detection_class() -> Optional[Type]:
    """
    Get the swarmtracker Detection class if available.

    Returns:
        Detection class from swarmtracker or None if not available
    """
    try:
        from swarmtracker.tracking.data_class import Detection

        return Detection
    except ImportError:
        return None


def get_swarmtracker_tracked_object_class() -> Optional[Type]:
    """
    Get the swarmtracker TrackedObject class if available.

    Returns:
        TrackedObject class from swarmtracker or None if not available
    """
    try:
        from swarmtracker.tracking.data_class import create_tracked_object_fast

        return create_tracked_object_fast
    except ImportError:
        return None


def convert_swarmtracker_detection(swarmtracker_det) -> StandaloneDetection:
    """
    Convert a swarmtracker Detection to standalone Detection.

    Args:
        swarmtracker_det: Detection object from swarmtracker

    Returns:
        StandaloneDetection: Converted detection
    """
    # Extract common attributes
    position = getattr(swarmtracker_det, "position", getattr(swarmtracker_det, "pos", None))
    confidence = getattr(swarmtracker_det, "confidence", getattr(swarmtracker_det, "conf", 1.0))
    bbox = getattr(swarmtracker_det, "bbox", getattr(swarmtracker_det, "xyxy", None))
    embedding = getattr(swarmtracker_det, "embedding", getattr(swarmtracker_det, "feature", None))
    class_id = getattr(swarmtracker_det, "class_id", getattr(swarmtracker_det, "cls", None))
    detection_id = getattr(swarmtracker_det, "id", None)

    return StandaloneDetection(
        position=position,
        confidence=confidence,
        bbox=bbox,
        embedding=embedding,
        class_id=class_id,
        id=detection_id,
    )


def convert_to_swarmtracker_tracked_object(standalone_obj: StandaloneTrackedObject):
    """
    Convert a standalone TrackedObject to swarmtracker format.

    Args:
        standalone_obj: StandaloneTrackedObject instance

    Returns:
        Swarmtracker compatible tracked object
    """
    try:
        from swarmtracker.tracking.data_class import create_tracked_object_fast

        # Try with different parameter combinations based on swarmtracker's API
        try:
            return create_tracked_object_fast(
                track_id=standalone_obj.id,
                position=standalone_obj.position,
                bbox=standalone_obj.bbox,
                confidence=standalone_obj.confidence,
            )
        except TypeError:
            # Try alternative parameter names
            try:
                return create_tracked_object_fast(
                    id=standalone_obj.id,
                    pos=standalone_obj.position,
                    bbox=standalone_obj.bbox,
                    conf=standalone_obj.confidence,
                )
            except TypeError:
                # Try minimal parameters
                return create_tracked_object_fast(
                    track_id=standalone_obj.id, pos=standalone_obj.position
                )
    except (ImportError, TypeError):
        # Fallback to standalone object
        return standalone_obj


def create_adaptive_detection_converter():
    """
    Create a detection converter that automatically handles both formats.

    Returns:
        Callable that converts any detection to standalone format
    """
    swarmtracker_detection_class = get_swarmtracker_detection_class()

    def convert_detection(detection) -> StandaloneDetection:
        # If it's already a standalone detection, return as-is
        if isinstance(detection, StandaloneDetection):
            return detection

        # If we have swarmtracker available and it's a swarmtracker detection
        if swarmtracker_detection_class and isinstance(detection, swarmtracker_detection_class):
            return convert_swarmtracker_detection(detection)

        # Try to convert from dict-like object
        if hasattr(detection, "__dict__") or isinstance(detection, dict):
            if isinstance(detection, dict):
                attrs = detection
            else:
                attrs = detection.__dict__

            position = attrs.get("position", attrs.get("pos"))
            if position is not None:
                position = np.asarray(position)

            bbox = attrs.get("bbox", attrs.get("xyxy"))
            if bbox is not None:
                bbox = np.asarray(bbox)

            embedding = attrs.get("embedding", attrs.get("feature"))
            if embedding is not None:
                embedding = np.asarray(embedding)

            return StandaloneDetection(
                position=position,
                confidence=attrs.get("confidence", attrs.get("conf", 1.0)),
                bbox=bbox,
                embedding=embedding,
                class_id=attrs.get("class_id", attrs.get("cls")),
                id=attrs.get("id"),
            )

        raise ValueError(
            f"Cannot convert detection of type {type(detection)} to StandaloneDetection"
        )

    return convert_detection


def create_adaptive_tracker_output_converter():
    """
    Create an output converter that returns the appropriate format.

    Returns:
        Callable that converts tracked objects to the expected format
    """
    within_swarmtracker = is_within_swarmtracker()

    def convert_output(tracked_objects):
        if not within_swarmtracker:
            # Return standalone format
            return tracked_objects

        # Convert to swarmtracker format
        converted = []
        for obj in tracked_objects:
            try:
                converted_obj = convert_to_swarmtracker_tracked_object(obj)
                converted.append(converted_obj)
            except Exception:
                # If conversion fails, use original object
                converted.append(obj)

        return converted

    return convert_output


class AdaptiveSwarmSortTracker:
    """
    Adaptive wrapper for SwarmSortTracker that automatically handles
    both standalone and swarmtracker integration modes.
    """

    def __init__(self, config: Optional[Union[SwarmSortConfig, dict]] = None):
        from .core import SwarmSortTracker

        self.tracker = SwarmSortTracker(config)
        self.detection_converter = create_adaptive_detection_converter()
        self.output_converter = create_adaptive_tracker_output_converter()
        self.within_swarmtracker = is_within_swarmtracker()

    def update(self, detections):
        """
        Update tracker with detections in any supported format.

        Args:
            detections: List of detection objects (any supported format)

        Returns:
            List of tracked objects in the appropriate format
        """
        # Convert detections to standalone format
        standalone_detections = [self.detection_converter(det) for det in detections]

        # Run tracking
        tracked_objects = self.tracker.update(standalone_detections)

        # Convert output to appropriate format
        return self.output_converter(tracked_objects)

    def reset(self):
        """Reset tracker state."""
        self.tracker.reset()

    def get_statistics(self):
        """Get tracker statistics."""
        return self.tracker.get_statistics()

    @property
    def config(self):
        """Access tracker configuration."""
        return self.tracker.config


def load_swarmtracker_config(config_path: str) -> SwarmSortConfig:
    """
    Load configuration from swarmtracker YAML format if available.

    Args:
        config_path: Path to swarmtracker configuration file

    Returns:
        SwarmSortConfig: Converted configuration
    """
    try:
        # Try to use swarmtracker's config loading if available
        from swarmtracker.tracking.config_base import merge_config_with_priority
        import yaml

        with open(config_path, "r") as f:
            swarmtracker_config = yaml.safe_load(f)

        # Extract SwarmSort-specific configuration
        swarmsort_config = swarmtracker_config.get("swarmsort", {})

        return SwarmSortConfig.from_dict(swarmsort_config)

    except ImportError:
        # Fall back to standard YAML loading
        return SwarmSortConfig.from_yaml(config_path)


# Convenient aliases for different use cases
SwarmSort = AdaptiveSwarmSortTracker  # Main entry point


# Define StandaloneSwarmSort lazily to avoid import issues
class _StandaloneSwarmSortWrapper:
    def __new__(cls, *args, **kwargs):
        from .core import SwarmSortTracker

        return SwarmSortTracker(*args, **kwargs)


StandaloneSwarmSort = _StandaloneSwarmSortWrapper


def create_tracker(config=None, force_standalone=False):
    """
    Factory function to create the appropriate tracker instance.

    Args:
        config: Configuration (SwarmSortConfig, dict, or path to YAML file)
        force_standalone: If True, always create standalone tracker

    Returns:
        Tracker instance (adaptive or standalone)
    """
    # Handle config loading
    if isinstance(config, (str, Path)):
        if force_standalone:
            config = SwarmSortConfig.from_yaml(str(config))
        else:
            config = load_swarmtracker_config(str(config))

    if force_standalone:
        from .core import SwarmSortTracker

        return SwarmSortTracker(config)
    else:
        return AdaptiveSwarmSortTracker(config)
