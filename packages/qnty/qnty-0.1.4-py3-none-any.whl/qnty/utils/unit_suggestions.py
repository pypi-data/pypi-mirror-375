"""
Unit Suggestions System
======================

Provides fuzzy string matching for unit validation errors with intelligent recommendations.
"""

from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..units.registry import Registry


class UnitSuggester:
    """Provides intelligent suggestions for invalid unit strings."""
    
    __slots__ = ("_unit_names", "_unit_aliases", "_all_suggestions", "_loaded")
    
    def __init__(self):
        self._unit_names: list[str] = []
        self._unit_aliases: dict[str, str] = {}  # alias -> canonical_name
        self._all_suggestions: list[str] = []  # All searchable strings
        self._loaded = False
    
    def _load_units(self) -> None:
        """Load unit names and aliases from the unit_data.json file."""
        if self._loaded:
            return
            
        try:
            # Load from the unit data file used by code generation
            unit_data_path = Path(__file__).parent.parent.parent.parent / "codegen" / "generators" / "data" / "unit_data.json"
            
            if not unit_data_path.exists():
                # Fallback: try to load from registry if available
                self._load_from_registry()
                return
                
            with open(unit_data_path, 'r', encoding='utf-8') as f:
                unit_data = json.load(f)
            
            # Extract all unit names and aliases
            for field_data in unit_data.values():
                if not isinstance(field_data, dict) or 'units' not in field_data:
                    continue
                    
                for unit in field_data['units']:
                    # Add normalized name
                    unit_name = unit.get('normalized_name', '')
                    if unit_name:
                        self._unit_names.append(unit_name)
                        self._all_suggestions.append(unit_name)
                    
                    # Add notation as an alias
                    notation = unit.get('notation', '')
                    if notation and notation != unit_name:
                        # Clean up notation (remove LaTeX formatting)
                        clean_notation = self._clean_notation(notation)
                        if clean_notation and clean_notation not in self._unit_aliases:
                            self._unit_aliases[clean_notation] = unit_name
                            self._all_suggestions.append(clean_notation)
                    
                    # Add aliases
                    aliases = unit.get('aliases', [])
                    for alias in aliases:
                        if alias and alias not in self._unit_aliases:
                            self._unit_aliases[alias] = unit_name
                            self._all_suggestions.append(alias)
            
            self._loaded = True
            
        except Exception:
            # Fallback to registry-based loading
            self._load_from_registry()
    
    def _load_from_registry(self) -> None:
        """Fallback: load units from registry if available."""
        try:
            from ..units.registry import registry
            
            if hasattr(registry, 'units'):
                for unit_name in registry.units.keys():
                    self._unit_names.append(unit_name)
                    self._all_suggestions.append(unit_name)
            
            self._loaded = True
        except Exception:
            # If all else fails, just mark as loaded with empty data
            self._loaded = True
    
    def _clean_notation(self, notation: str) -> str:
        """Clean LaTeX and special formatting from notation strings."""
        # Remove common LaTeX patterns
        notation = notation.replace('\\mathrm{', '').replace('}', '')
        notation = notation.replace('\\text{', '').replace('$', '')
        notation = notation.replace('\\', '')
        notation = notation.replace('{', '').replace('}', '')
        
        # Remove extra spaces and common patterns
        notation = notation.strip()
        notation = notation.replace(' ', '')
        
        # Skip if too long or contains special characters that make it unusable
        if len(notation) > 20 or any(char in notation for char in ['(', ')', '^', '_', '/']):
            return ''
            
        return notation if notation and len(notation) <= 10 else ''
    
    def get_suggestions(self, invalid_unit: str, max_suggestions: int = 3) -> list[str]:
        """
        Get fuzzy string matching suggestions for an invalid unit.
        
        Args:
            invalid_unit: The invalid unit string that was entered
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of suggested unit strings, ordered by similarity
        """
        self._load_units()
        
        if not self._all_suggestions:
            return []
        
        # Calculate similarity scores for all units
        similarities = []
        invalid_lower = invalid_unit.lower().strip()
        
        for suggestion in self._all_suggestions:
            suggestion_lower = suggestion.lower()
            
            # Exact match (shouldn't happen, but just in case)
            if invalid_lower == suggestion_lower:
                continue
                
            # Calculate similarity using SequenceMatcher
            similarity = SequenceMatcher(None, invalid_lower, suggestion_lower).ratio()
            
            # Bonus for starts-with matches
            if suggestion_lower.startswith(invalid_lower) or invalid_lower.startswith(suggestion_lower):
                similarity += 0.2
            
            # Bonus for contains matches
            if invalid_lower in suggestion_lower or suggestion_lower in invalid_lower:
                similarity += 0.1
            
            similarities.append((similarity, suggestion))
        
        # Sort by similarity score (descending) and return top matches
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Filter for meaningful suggestions (similarity > 0.4)
        meaningful_suggestions = [
            suggestion for similarity, suggestion in similarities 
            if similarity > 0.4
        ]
        
        return meaningful_suggestions[:max_suggestions]


class UnitValidationError(ValueError):
    """Error raised when an invalid unit is provided, with suggestions."""
    
    def __init__(self, invalid_unit: str, variable_type: str = "", suggestions: list[str] | None = None):
        self.invalid_unit = invalid_unit
        self.variable_type = variable_type
        self.suggestions = suggestions or []
        
        # Construct error message
        if variable_type:
            msg = f"Unknown unit '{invalid_unit}' for {variable_type}"
        else:
            msg = f"Unknown unit '{invalid_unit}'"
        
        if self.suggestions:
            msg += f". Did you mean: {', '.join(repr(s) for s in self.suggestions)}?"
        
        super().__init__(msg)


# Global suggester instance
_suggester = UnitSuggester()


def get_unit_suggestions(invalid_unit: str, max_suggestions: int = 3) -> list[str]:
    """Get unit suggestions for an invalid unit string."""
    return _suggester.get_suggestions(invalid_unit, max_suggestions)


def create_unit_validation_error(invalid_unit: str, variable_type: str = "") -> UnitValidationError:
    """Create a UnitValidationError with intelligent suggestions."""
    suggestions = get_unit_suggestions(invalid_unit)
    return UnitValidationError(invalid_unit, variable_type, suggestions)