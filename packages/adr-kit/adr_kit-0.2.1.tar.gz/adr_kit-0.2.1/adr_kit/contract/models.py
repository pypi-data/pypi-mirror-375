"""Data models for the constraints contract system.

These models define the structure of the unified contract that agents use
as their definitive source of truth for architectural decisions.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from pydantic import BaseModel, Field
import hashlib
import json

from ..core.model import PolicyModel, ImportPolicy, BoundaryPolicy, PythonPolicy


class PolicyProvenance(BaseModel):
    """Tracks which ADR contributed each policy rule."""
    
    adr_id: str = Field(..., description="ADR that defined this rule")
    adr_title: str = Field(..., description="Human-readable title of the ADR")
    rule_path: str = Field(..., description="Path to the specific rule (e.g., 'imports.disallow.axios')")
    effective_date: datetime = Field(..., description="When this rule became active")


class ContractMetadata(BaseModel):
    """Metadata about the constraints contract."""
    
    version: str = Field("1.0", description="Contract format version")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When contract was generated")
    hash: str = Field(..., description="SHA-256 hash of the contract content")
    source_adrs: List[str] = Field(..., description="List of ADR IDs that contributed to this contract")
    adr_directory: str = Field(..., description="Path to ADR directory used")


class MergedConstraints(BaseModel):
    """The unified policy constraints from all accepted ADRs."""
    
    imports: Optional[ImportPolicy] = Field(None, description="Merged import policies")
    boundaries: Optional[BoundaryPolicy] = Field(None, description="Merged boundary policies") 
    python: Optional[PythonPolicy] = Field(None, description="Merged Python-specific policies")
    
    def is_empty(self) -> bool:
        """Check if there are any constraints defined."""
        return (
            (not self.imports or (not self.imports.disallow and not self.imports.prefer)) and
            (not self.boundaries or (not self.boundaries.layers and not self.boundaries.rules)) and
            (not self.python or not self.python.disallow_imports)
        )


class ConstraintsContract(BaseModel):
    """The complete constraints contract - the definitive source of truth for agents.
    
    This is the single file (constraints_accepted.json) that agents read to understand
    all architectural constraints they must follow.
    """
    
    metadata: ContractMetadata = Field(..., description="Contract metadata and provenance")
    constraints: MergedConstraints = Field(..., description="The actual policy constraints")
    provenance: Dict[str, PolicyProvenance] = Field(..., description="Maps each rule to its source ADR")
    
    @classmethod
    def create_empty(cls, adr_directory: Path) -> "ConstraintsContract":
        """Create an empty contract with no constraints."""
        metadata = ContractMetadata(
            hash=cls._calculate_hash({}),
            source_adrs=[],
            adr_directory=str(adr_directory)
        )
        
        return cls(
            metadata=metadata,
            constraints=MergedConstraints(),
            provenance={}
        )
    
    @staticmethod
    def _calculate_hash(data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of contract data for change detection."""
        # Sort keys for deterministic hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def calculate_content_hash(self) -> str:
        """Calculate hash of the contract content (excluding metadata)."""
        content = {
            "constraints": self.constraints.model_dump(exclude_none=True),
            "provenance": {k: v.model_dump() for k, v in self.provenance.items()}
        }
        return self._calculate_hash(content)
    
    def update_hash(self) -> None:
        """Update the metadata hash to match current content."""
        self.metadata.hash = self.calculate_content_hash()
        self.metadata.generated_at = datetime.utcnow()
    
    def to_json_file(self, file_path: Path) -> None:
        """Write contract to JSON file with proper formatting."""
        # Update hash before saving
        self.update_hash()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                self.model_dump(exclude_none=True), 
                f, 
                indent=2, 
                default=str,
                sort_keys=True
            )
    
    @classmethod
    def from_json_file(cls, file_path: Path) -> "ConstraintsContract":
        """Load contract from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.model_validate(data)
    
    def has_conflicts_with_policy(self, policy: PolicyModel, adr_id: str) -> List[str]:
        """Check if a new policy would conflict with existing constraints.
        
        Returns list of conflict descriptions, empty if no conflicts.
        """
        conflicts = []
        
        if policy.imports and self.constraints.imports:
            # Check for disallow conflicts (new disallow vs existing prefer)
            if policy.imports.disallow and self.constraints.imports.prefer:
                for disallow_item in policy.imports.disallow:
                    if disallow_item in self.constraints.imports.prefer:
                        source_adr = self._find_provenance_for_rule(f"imports.prefer.{disallow_item}")
                        conflicts.append(
                            f"ADR {adr_id} wants to disallow '{disallow_item}' but {source_adr} prefers it"
                        )
            
            # Check for prefer conflicts (new prefer vs existing disallow)
            if policy.imports.prefer and self.constraints.imports.disallow:
                for prefer_item in policy.imports.prefer:
                    if prefer_item in self.constraints.imports.disallow:
                        source_adr = self._find_provenance_for_rule(f"imports.disallow.{prefer_item}")
                        conflicts.append(
                            f"ADR {adr_id} wants to prefer '{prefer_item}' but {source_adr} disallows it"
                        )
        
        return conflicts
    
    def _find_provenance_for_rule(self, rule_path: str) -> str:
        """Find which ADR contributed a specific rule."""
        for path, prov in self.provenance.items():
            if path == rule_path:
                return prov.adr_id
        return "unknown ADR"