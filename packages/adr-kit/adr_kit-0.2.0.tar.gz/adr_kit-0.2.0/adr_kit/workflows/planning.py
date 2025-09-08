"""Planning Workflow - Provide architectural context for agent tasks."""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from .base import BaseWorkflow, WorkflowResult, WorkflowStatus, WorkflowError
from ..core.model import ADR
from ..core.parse import find_adr_files, parse_adr_file
from ..contract.builder import ConstraintsContractBuilder


@dataclass
class PlanningInput:
    """Input for planning workflow."""
    task_description: str  # What the agent is trying to do
    context_type: str = "implementation"  # implementation, refactoring, debugging, feature
    domain_hints: Optional[List[str]] = None  # frontend, backend, database, etc.
    priority_level: str = "normal"  # low, normal, high - affects detail level


@dataclass
class ArchitecturalContext:
    """Curated architectural context for a specific task."""
    relevant_adrs: List[Dict[str, Any]]  # ADRs ranked by relevance
    applicable_constraints: List[Dict[str, Any]]  # Policy constraints to follow
    guidance_prompts: List[str]  # Specific guidance for the task
    technology_recommendations: Dict[str, List[str]]  # Recommended vs avoided technologies
    architecture_patterns: List[str]  # Relevant architectural patterns
    compliance_checklist: List[str]  # Things to verify for compliance
    related_decisions: List[str]  # Decision context that might be relevant


class PlanningWorkflow(BaseWorkflow):
    """
    Planning Workflow provides curated architectural context for agent tasks.
    
    This workflow analyzes the agent's task and provides relevant architectural
    context, constraints, and guidance to help the agent make informed decisions
    that align with existing ADRs.
    
    Workflow Steps:
    1. Analyze task description to extract key concepts
    2. Load current constraints contract
    3. Find ADRs relevant to the task domain
    4. Extract applicable policy constraints
    5. Generate technology recommendations
    6. Create task-specific guidance prompts
    7. Build compliance checklist
    8. Package everything into actionable context
    """
    
    def execute(self, input_data: PlanningInput) -> WorkflowResult:
        """Execute planning context workflow."""
        try:
            # Step 1: Analyze task to extract key concepts
            task_analysis = self._analyze_task_description(input_data)
            
            # Step 2: Load constraints contract
            contract = self._load_constraints_contract()
            
            # Step 3: Find relevant ADRs
            relevant_adrs = self._find_relevant_adrs(task_analysis, contract)
            
            # Step 4: Extract applicable constraints
            applicable_constraints = self._extract_applicable_constraints(task_analysis, contract)
            
            # Step 5: Generate technology recommendations
            tech_recommendations = self._generate_technology_recommendations(
                task_analysis, 
                relevant_adrs, 
                contract
            )
            
            # Step 6: Create guidance prompts
            guidance_prompts = self._generate_guidance_prompts(
                task_analysis, 
                relevant_adrs, 
                input_data.context_type
            )
            
            # Step 7: Build compliance checklist
            compliance_checklist = self._build_compliance_checklist(
                task_analysis, 
                applicable_constraints
            )
            
            # Step 8: Extract architecture patterns
            architecture_patterns = self._extract_architecture_patterns(relevant_adrs)
            
            # Step 9: Identify related decisions
            related_decisions = self._identify_related_decisions(task_analysis, relevant_adrs)
            
            context = ArchitecturalContext(
                relevant_adrs=relevant_adrs,
                applicable_constraints=applicable_constraints,
                guidance_prompts=guidance_prompts,
                technology_recommendations=tech_recommendations,
                architecture_patterns=architecture_patterns,
                compliance_checklist=compliance_checklist,
                related_decisions=related_decisions
            )
            
            return WorkflowResult(
                status=WorkflowStatus.SUCCESS,
                message=f"Planning context generated for {input_data.context_type} task",
                data={"architectural_context": context, "task_analysis": task_analysis}
            )
            
        except Exception as e:
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                message=f"Planning workflow failed: {str(e)}",
                error=WorkflowError(
                    error_type="PlanningError",
                    error_message=str(e),
                    context={"input": input_data}
                )
            )
    
    def _analyze_task_description(self, input_data: PlanningInput) -> Dict[str, Any]:
        """Analyze task description to extract key concepts and domains."""
        task_text = input_data.task_description.lower()
        
        # Extract technology mentions
        technologies = self._extract_technologies(task_text)
        
        # Extract domains
        domains = self._extract_domains(task_text, input_data.domain_hints)
        
        # Extract intent/actions
        intents = self._extract_intents(task_text)
        
        # Extract architectural concepts
        arch_concepts = self._extract_architectural_concepts(task_text)
        
        # Determine complexity level
        complexity = self._assess_task_complexity(task_text, technologies, domains)
        
        return {
            "original_task": input_data.task_description,
            "technologies": technologies,
            "domains": domains,
            "intents": intents,
            "architectural_concepts": arch_concepts,
            "complexity": complexity,
            "context_type": input_data.context_type,
            "priority_level": input_data.priority_level
        }
    
    def _extract_technologies(self, task_text: str) -> List[str]:
        """Extract mentioned technologies from task description."""
        # Common technology patterns
        tech_patterns = {
            # Databases
            r'\b(postgres|postgresql|mysql|mongodb|redis|sqlite|dynamodb|cassandra|elasticsearch)\b': 'database',
            # Frontend
            r'\b(react|vue|angular|svelte|next\.?js|nuxt|gatsby|typescript|javascript)\b': 'frontend',
            # Backend
            r'\b(express|fastapi|django|flask|spring|rails|node\.?js|python|java|go|rust)\b': 'backend',
            # Infrastructure
            r'\b(docker|kubernetes|aws|azure|gcp|terraform|ansible)\b': 'infrastructure',
            # Architecture
            r'\b(microservice|monolith|serverless|graphql|rest|grpc|api)\b': 'architecture'
        }
        
        technologies = []
        for pattern, category in tech_patterns.items():
            matches = re.findall(pattern, task_text, re.IGNORECASE)
            for match in matches:
                technologies.append({
                    "name": match.lower(),
                    "category": category,
                    "confidence": "high"
                })
        
        return technologies
    
    def _extract_domains(self, task_text: str, domain_hints: Optional[List[str]]) -> List[str]:
        """Extract domain areas from task description."""
        domains = set()
        
        # Add explicit hints
        if domain_hints:
            domains.update(domain_hints)
        
        # Domain keywords
        domain_keywords = {
            "frontend": ["ui", "interface", "component", "page", "view", "client", "browser"],
            "backend": ["server", "api", "endpoint", "service", "controller", "middleware"],
            "database": ["data", "schema", "query", "model", "table", "collection"],
            "security": ["auth", "login", "permission", "token", "encrypt", "secure"],
            "performance": ["optimize", "fast", "cache", "load", "speed", "latency"],
            "testing": ["test", "spec", "mock", "coverage", "unit", "integration"],
            "deployment": ["deploy", "build", "ci/cd", "pipeline", "production"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in task_text for keyword in keywords):
                domains.add(domain)
        
        return list(domains)
    
    def _extract_intents(self, task_text: str) -> List[str]:
        """Extract what the agent intends to do."""
        intent_patterns = [
            r'\b(implement|create|build|develop|add|make)\b',  # Creation
            r'\b(fix|debug|resolve|solve|correct)\b',  # Debugging  
            r'\b(refactor|improve|optimize|enhance|update)\b',  # Improvement
            r'\b(test|verify|validate|check)\b',  # Validation
            r'\b(integrate|connect|combine|merge)\b',  # Integration
            r'\b(deploy|release|launch|publish)\b'  # Deployment
        ]
        
        intents = []
        for pattern in intent_patterns:
            matches = re.findall(pattern, task_text, re.IGNORECASE)
            intents.extend([match.lower() for match in matches])
        
        return list(set(intents))  # Remove duplicates
    
    def _extract_architectural_concepts(self, task_text: str) -> List[str]:
        """Extract architectural concepts from task description."""
        arch_keywords = [
            "pattern", "architecture", "design", "structure", "component",
            "module", "service", "layer", "boundary", "interface",
            "scalability", "reliability", "maintainability", "security"
        ]
        
        concepts = []
        for keyword in arch_keywords:
            if keyword in task_text:
                concepts.append(keyword)
        
        return concepts
    
    def _assess_task_complexity(
        self, 
        task_text: str, 
        technologies: List[Dict[str, Any]], 
        domains: List[str]
    ) -> str:
        """Assess the complexity level of the task."""
        complexity_score = 0
        
        # Multiple technologies = more complex
        complexity_score += len(technologies)
        
        # Multiple domains = more complex
        complexity_score += len(domains) * 2
        
        # Architectural keywords increase complexity
        arch_keywords = ["architecture", "design", "pattern", "scalability", "security"]
        complexity_score += sum(2 for keyword in arch_keywords if keyword in task_text)
        
        # Integration/system-wide changes are complex
        if any(word in task_text for word in ["integrate", "system", "entire", "across"]):
            complexity_score += 3
        
        if complexity_score >= 8:
            return "high"
        elif complexity_score >= 4:
            return "medium"
        else:
            return "low"
    
    def _load_constraints_contract(self):
        """Load current constraints contract."""
        try:
            builder = ConstraintsContractBuilder(adr_dir=self.adr_dir)
            return builder.build()
        except Exception:
            # Return empty contract if none exists
            from ..contract.models import ConstraintsContract
            return ConstraintsContract(
                approved_adrs=[],
                policy_gates=[],
                constraints=[],
                metadata={"generated_at": "planning", "adr_count": 0}
            )
    
    def _find_relevant_adrs(self, task_analysis: Dict[str, Any], contract) -> List[Dict[str, Any]]:
        """Find ADRs relevant to the task."""
        relevant_adrs = []
        
        # Get task keywords
        task_keywords = set()
        for tech in task_analysis["technologies"]:
            task_keywords.add(tech["name"])
        task_keywords.update(task_analysis["domains"])
        task_keywords.update(task_analysis["intents"])
        task_keywords.update(task_analysis["architectural_concepts"])
        
        # Note: contract.approved_adrs should be a list of ADR objects
        for adr in contract.approved_adrs:
            relevance_score = self._calculate_adr_relevance(adr, task_keywords)
            
            if relevance_score > 0.1:  # Relevance threshold
                relevant_adrs.append({
                    "adr_id": adr.id,
                    "title": adr.title,
                    "relevance_score": relevance_score,
                    "matching_areas": self._get_matching_areas(adr, task_keywords),
                    "key_policies": self._extract_key_policies(adr),
                    "decision_summary": adr.decision[:200] + "..." if len(adr.decision) > 200 else adr.decision
                })
        
        # Sort by relevance
        relevant_adrs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Return top relevant ADRs (limit based on priority)
        limit = {"high": 10, "normal": 6, "low": 3}[task_analysis["priority_level"]]
        return relevant_adrs[:limit]
    
    def _calculate_adr_relevance(self, adr: ADR, task_keywords: Set[str]) -> float:
        """Calculate relevance score between ADR and task."""
        adr_text = (
            f"{adr.title} {adr.decision} {' '.join(adr.tags)} {adr.context}"
        ).lower()
        
        matches = 0
        total_keywords = len(task_keywords)
        
        if total_keywords == 0:
            return 0.0
        
        for keyword in task_keywords:
            if keyword in adr_text:
                matches += 1
        
        # Base relevance
        relevance = matches / total_keywords
        
        # Boost for tag matches (tags are more specific)
        tag_matches = len(set(adr.tags) & task_keywords)
        relevance += (tag_matches * 0.3)
        
        # Boost for title matches (titles are very specific)
        title_matches = sum(1 for keyword in task_keywords if keyword in adr.title.lower())
        relevance += (title_matches * 0.5)
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    def _get_matching_areas(self, adr: ADR, task_keywords: Set[str]) -> List[str]:
        """Get areas where ADR and task overlap."""
        adr_text = f"{adr.title} {adr.decision} {' '.join(adr.tags)}".lower()
        
        matching_areas = []
        for keyword in task_keywords:
            if keyword in adr_text:
                matching_areas.append(keyword)
        
        return matching_areas
    
    def _extract_key_policies(self, adr: ADR) -> List[str]:
        """Extract key policies from ADR."""
        policies = []
        
        if adr.policy:
            for policy_type, policy_content in adr.policy.items():
                if isinstance(policy_content, dict):
                    if "disallow" in policy_content:
                        policies.append(f"Disallows: {', '.join(policy_content['disallow'])}")
                    if "prefer" in policy_content:
                        policies.append(f"Prefers: {', '.join(policy_content['prefer'])}")
                    if "require" in policy_content:
                        policies.append(f"Requires: {', '.join(policy_content['require'])}")
        
        return policies
    
    def _extract_applicable_constraints(self, task_analysis: Dict[str, Any], contract) -> List[Dict[str, Any]]:
        """Extract constraints applicable to the task."""
        applicable = []
        
        task_domains = set(task_analysis["domains"])
        task_tech = {tech["name"] for tech in task_analysis["technologies"]}
        
        for constraint in contract.constraints:
            constraint_relevance = self._assess_constraint_relevance(
                constraint, 
                task_domains, 
                task_tech
            )
            
            if constraint_relevance > 0.3:  # Relevance threshold
                applicable.append({
                    "adr_id": constraint.adr_id,
                    "constraint_type": constraint.constraint_type,
                    "policy_summary": self._summarize_policy(constraint.policy),
                    "relevance": constraint_relevance,
                    "enforcement_level": "required" if constraint_relevance > 0.7 else "recommended"
                })
        
        return applicable
    
    def _assess_constraint_relevance(self, constraint, task_domains: Set[str], task_tech: Set[str]) -> float:
        """Assess how relevant a constraint is to the task."""
        relevance = 0.0
        
        # Check if constraint applies to task technologies
        constraint_text = str(constraint.policy).lower()
        for tech in task_tech:
            if tech in constraint_text:
                relevance += 0.4
        
        # Check if constraint applies to task domains
        for domain in task_domains:
            if domain in constraint_text:
                relevance += 0.3
        
        return min(relevance, 1.0)
    
    def _summarize_policy(self, policy: Dict[str, Any]) -> str:
        """Create human-readable summary of policy."""
        summary_parts = []
        
        for policy_type, content in policy.items():
            if isinstance(content, dict):
                if "disallow" in content:
                    summary_parts.append(f"Avoid {', '.join(content['disallow'])}")
                if "prefer" in content:
                    summary_parts.append(f"Use {', '.join(content['prefer'])}")
                if "require" in content:
                    summary_parts.append(f"Must use {', '.join(content['require'])}")
        
        return "; ".join(summary_parts) if summary_parts else "No specific constraints"
    
    def _generate_technology_recommendations(
        self, 
        task_analysis: Dict[str, Any], 
        relevant_adrs: List[Dict[str, Any]], 
        contract
    ) -> Dict[str, List[str]]:
        """Generate technology recommendations based on ADRs."""
        recommendations = {
            "recommended": [],
            "avoid": [],
            "required": []
        }
        
        # Extract recommendations from relevant ADRs
        for adr_info in relevant_adrs:
            for policy in adr_info["key_policies"]:
                if policy.startswith("Prefers:"):
                    tech_list = policy.replace("Prefers:", "").strip().split(", ")
                    recommendations["recommended"].extend(tech_list)
                elif policy.startswith("Disallows:"):
                    tech_list = policy.replace("Disallows:", "").strip().split(", ")
                    recommendations["avoid"].extend(tech_list)
                elif policy.startswith("Requires:"):
                    tech_list = policy.replace("Requires:", "").strip().split(", ")
                    recommendations["required"].extend(tech_list)
        
        # Remove duplicates
        for key in recommendations:
            recommendations[key] = list(set(recommendations[key]))
        
        return recommendations
    
    def _generate_guidance_prompts(
        self, 
        task_analysis: Dict[str, Any], 
        relevant_adrs: List[Dict[str, Any]], 
        context_type: str
    ) -> List[str]:
        """Generate specific guidance prompts for the task."""
        prompts = []
        
        # Context-specific base prompts
        if context_type == "implementation":
            prompts.append("Before implementing, ensure your approach aligns with existing architectural decisions.")
        elif context_type == "refactoring":
            prompts.append("When refactoring, preserve architectural patterns established in ADRs.")
        elif context_type == "debugging":
            prompts.append("Consider whether the bug relates to violations of architectural constraints.")
        elif context_type == "feature":
            prompts.append("New features should follow established architectural patterns and constraints.")
        
        # Add specific guidance based on relevant ADRs
        if relevant_adrs:
            top_adr = relevant_adrs[0]
            prompts.append(f"Pay special attention to {top_adr['adr_id']}: {top_adr['title']}")
            
            if len(relevant_adrs) > 1:
                other_adrs = [adr['adr_id'] for adr in relevant_adrs[1:3]]
                prompts.append(f"Also consider guidance from {', '.join(other_adrs)}")
        
        # Add complexity-specific guidance
        if task_analysis["complexity"] == "high":
            prompts.append("This is a complex task - consider breaking it down and validating each step against ADRs.")
        
        return prompts
    
    def _build_compliance_checklist(
        self, 
        task_analysis: Dict[str, Any], 
        applicable_constraints: List[Dict[str, Any]]
    ) -> List[str]:
        """Build a compliance checklist for the task."""
        checklist = []
        
        # Add constraint-based checks
        for constraint in applicable_constraints:
            if constraint["enforcement_level"] == "required":
                checklist.append(f"✓ Verify compliance with {constraint['adr_id']}: {constraint['policy_summary']}")
        
        # Add general architectural checks
        if task_analysis["complexity"] in ["medium", "high"]:
            checklist.extend([
                "✓ Check that new components follow established patterns",
                "✓ Verify that dependencies align with architectural decisions",
                "✓ Ensure security considerations are addressed per ADRs"
            ])
        
        # Add technology-specific checks
        for tech in task_analysis["technologies"]:
            if tech["category"] == "database":
                checklist.append("✓ Verify database choice aligns with data architecture ADRs")
            elif tech["category"] == "frontend":
                checklist.append("✓ Check frontend framework choice against UI architecture ADRs")
        
        return checklist
    
    def _extract_architecture_patterns(self, relevant_adrs: List[Dict[str, Any]]) -> List[str]:
        """Extract architectural patterns from relevant ADRs."""
        patterns = set()
        
        # Common patterns to look for
        pattern_keywords = [
            "microservices", "monolith", "layered", "hexagonal", "clean architecture",
            "mvc", "mvp", "mvvm", "event-driven", "cqrs", "saga", "repository",
            "factory", "singleton", "observer", "strategy", "adapter"
        ]
        
        for adr_info in relevant_adrs:
            decision_text = adr_info["decision_summary"].lower()
            for pattern in pattern_keywords:
                if pattern in decision_text:
                    patterns.add(pattern)
        
        return list(patterns)
    
    def _identify_related_decisions(
        self, 
        task_analysis: Dict[str, Any], 
        relevant_adrs: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify decision context that might be relevant."""
        decisions = []
        
        # Extract key decisions from most relevant ADRs
        for adr_info in relevant_adrs[:3]:  # Top 3 most relevant
            decision = adr_info["decision_summary"]
            # Extract the core decision (first sentence usually)
            first_sentence = decision.split('.')[0] + '.'
            decisions.append(f"{adr_info['adr_id']}: {first_sentence}")
        
        return decisions