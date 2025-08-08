# Autonomous Multi-Agent System - Dynamic Memory Management Specification

## Overview
This document outlines an autonomous, multi-agent system built on **Celery distributed task processing** with intelligent memory management that dynamically spawns and consolidates agents based on available resources. The system adapts its architecture in real-time to optimize performance within memory constraints using Python's mature distributed computing ecosystem.

## Current System Context
The existing system (POC #1) requires users to:
1. Upload Excel and PDF files
2. Click "Create Embeddings" to extract and vectorize PDF content
3. Click "Validate" to compare Excel parameters against PDF data

The new system (POC #2) will automate this entire workflow through intelligent agent coordination with adaptive resource management.

## Core Innovation: Dynamic Agent Management

### Memory-Aware Agent Spawning
- **Resource Monitoring:** Continuous memory usage tracking
- **Dynamic Spawning:** Create sub-agents only when memory permits
- **Role Consolidation:** Single agents can assume multiple roles when resources are limited
- **Graceful Degradation:** System maintains functionality even with minimal agent count

## System Objectives
1. **Autonomous Operation:** Single file upload triggers complete validation workflow via a web application interface
2. **Comprehensive Frontend Integration:** User-friendly web interface for uploading files, monitoring progress, and viewing results, ensuring seamless user experience across devices
3. **Adaptive Resource Management:** Dynamic agent spawning based on memory availability
3. **Intelligent Role Consolidation:** Agents can combine multiple capabilities when needed
4. **Local Efficiency:** Optimized for 8GB RAM with 16GB scalability
5. **Precision Validation:** Exact matching for numerical values, semantic for text

## Dynamic Agent Architecture

### Resource Manager (Core Component)
**Responsibilities:**
- Real-time memory monitoring and prediction
- Agent lifecycle management (spawn/consolidate/terminate)
- Resource allocation optimization
- Performance vs. memory trade-off decisions

**Capabilities:**
- Track memory usage per agent and model
- Predict memory requirements for potential sub-agent spawning
- Make intelligent decisions about role consolidation
- Implement memory cleanup and garbage collection

### 1. Orchestrator Agent (Always Active)
**Base Responsibilities:**
- File intake and initial analysis
- Resource-aware workflow planning
- Agent lifecycle management decisions
- Progress monitoring and error recovery
- Final result compilation and reporting

**Adaptive Capabilities:**
- **High Memory Mode:** Delegates to specialized agents and sub-agents
- **Low Memory Mode:** Performs basic processing internally
- **Hybrid Mode:** Selective delegation based on task complexity

**Dynamic Sub-agents (Memory Permitting):**
- File Analysis Sub-agent: Quick metadata analysis
- Workflow Planning Sub-agent: Advanced pipeline optimization

### 2. PDF Intelligence Agent (Conditionally Spawned)
**Base Responsibilities:**
- PDF structure analysis and content extraction
- Multimodal processing coordination
- Quality assessment of extracted data

**Adaptive Capabilities:**
- **Standalone Mode:** Handles all PDF processing internally
- **Delegated Mode:** Spawns specialized sub-agents for complex tasks
- **Consolidated Mode:** Can absorb Excel processing if memory is limited

**Dynamic Sub-agents (Memory Permitting):**
- OCR Sub-agent: Tesseract-based text extraction
- Multimodal Sub-agent: BLIP-based visual-text understanding
- Structure Analysis Sub-agent: Table and layout detection

**Fallback Strategy:**
- If sub-agents cannot be spawned, performs all operations sequentially
- Unloads models between processing steps to free memory

### 3. Excel Intelligence Agent (Conditionally Spawned)
**Base Responsibilities:**
- Excel structure analysis and parameter extraction
- Data validation and cleansing
- Cross-reference preparation

**Adaptive Capabilities:**
- **Independent Mode:** Full Excel processing capability
- **Merged Mode:** Can be consolidated with PDF agent if memory is tight
- **Minimal Mode:** Basic extraction only, delegates validation to main agent

**Dynamic Sub-agents (Memory Permitting):**
- Schema Detection Sub-agent: Automatic structure identification
- Data Quality Sub-agent: Validation and cleansing

**Consolidation Strategy:**
- Can be absorbed by PDF Intelligence Agent to create "Document Processing Agent"
- Falls back to Orchestrator Agent in extreme memory constraints

### 4. Validation Intelligence Agent (Conditionally Spawned)
**Base Responsibilities:**
- **Dual-mode matching:** Exact matching for precision values, semantic matching for descriptive text
- Discrepancy analysis and classification
- Comprehensive reporting

**Adaptive Capabilities:**
- **Specialized Mode:** Dedicated matching algorithms and sub-agents
- **Integrated Mode:** Core matching logic within Orchestrator
- **Hybrid Mode:** Exact matching locally, semantic matching via sub-agent

**Reasoning Capabilities:**
- **Intelligently classify data types** (numerical, categorical, textual, precision measurements)
- **Choose appropriate matching strategy** based on data type and context:
  - **Exact matching** for numerical values, dates, IDs, measurements, and precision data
  - **Semantic matching** for descriptions, names, and unstructured text
- **Tolerance-based matching** for floating-point precision values with configurable thresholds

**Dynamic Sub-agents (Memory Permitting):**
- **Exact Matching Sub-agent:** Precise numerical and categorical comparisons
- **Semantic Matching Sub-agent:** Advanced similarity algorithms for text
- **Data Type Classifier Sub-agent:** Automatic data type identification
- **Precision Validator Sub-agent:** Floating-point tolerance handling
- **Reporting Sub-agent:** Advanced report generation

## Memory Management Strategy

### Memory Monitoring
```python
class MemoryManager:
    def __init__(self, max_memory_gb=8):
        self.max_memory = max_memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.safety_margin = 0.15  # 15% safety buffer
        self.agent_memory_map = {}
        
    def can_spawn_agent(self, agent_type, estimated_memory):
        current_usage = self.get_current_memory_usage()
        available = self.max_memory * (1 - self.safety_margin) - current_usage
        return available >= estimated_memory
        
    def suggest_consolidation(self):
        # Logic to identify which agents can be consolidated
        pass
```

### Dynamic Agent Spawning Logic
1. **Memory Assessment:** Check available memory before spawning
2. **Priority-Based Spawning:** Critical agents first, optimization agents last
3. **Capability Inheritance:** Parent agents can absorb child capabilities
4. **Graceful Fallback:** System functions with minimum viable agent set

### Agent Consolidation Patterns

#### Pattern 1: Document Processing Consolidation
- **High Memory:** PDF Agent + Excel Agent + Validation Agent
- **Medium Memory:** Document Processing Agent (PDF + Excel) + Validation Agent
- **Low Memory:** Orchestrator Agent handles all processing

#### Pattern 2: Processing-Validation Consolidation
- **High Memory:** Specialized processing agents + Validation Agent with sub-agents
- **Medium Memory:** Processing agents + Integrated validation
- **Low Memory:** Single agent with sequential processing

#### Pattern 3: Sub-agent Absorption
- **High Memory:** Main agents with specialized sub-agents
- **Medium Memory:** Main agents with internal sub-capabilities
- **Low Memory:** Single multi-capability agent

## Resource-Aware Decision Making

### Memory Threshold Levels
- **High (>6GB available):** Full agent ecosystem with sub-agents
- **Medium (3-6GB available):** Core agents with selective sub-agent spawning
- **Low (1-3GB available):** Consolidated agents with minimal sub-agents
- **Critical (<1GB available):** Single orchestrator with sequential processing

### Dynamic Capability Assignment
```python
class AdaptiveAgent:
    def __init__(self, base_capabilities):
        self.base_capabilities = base_capabilities
        self.absorbed_capabilities = []
        
    def absorb_capability(self, capability, memory_constraint):
        if self.can_handle_additional_load(capability, memory_constraint):
            self.absorbed_capabilities.append(capability)
            return True
        return False
        
    def delegate_or_execute(self, task):
        if self.should_delegate(task) and self.can_spawn_sub_agent():
            return self.delegate_to_sub_agent(task)
        else:
            return self.execute_internally(task)
```

## Matching Strategy Details

### Exact Matching (for Precision Values)
**Data Types:**
- Numerical values (integers, floats)
- Dates and timestamps
- IDs and reference numbers
- Measurements and quantities
- Currency values
- Percentages

**Matching Logic:**
- String-based exact comparison for integers and IDs
- Tolerance-based comparison for floating-point numbers (configurable precision)
- Normalized format comparison for dates
- Unit-aware comparison for measurements

### Semantic Matching (for Descriptive Content)
**Data Types:**
- Product descriptions
- Company names
- Address information
- Comments and notes
- Categorical labels (with variations)

**Matching Logic:**
- Embedding-based similarity using sentence-transformers
- Fuzzy string matching for slight variations
- Synonym and abbreviation handling
- Context-aware matching

## Agent Communication Framework

### A2A Protocol Implementation
- **Message Format:** JSON-based structured communication
- **Transport:** In-memory message queues with persistence option
- **Routing:** Capability-based message routing
- **Error Handling:** Automatic retry and escalation mechanisms

### Memory-Aware Messaging
- **Lightweight Messages:** Minimal payload to reduce memory overhead
- **Streaming Results:** Process and pass data in chunks to avoid large buffers
- **Cleanup Signals:** Automatic cleanup of completed tasks

### Agent Lifecycle Events
- **spawn_request:** Request to create new agent with memory requirements
- **consolidation_needed:** Signal that memory pressure requires role merging
- **capability_transfer:** Transfer responsibilities between agents
- **graceful_shutdown:** Orderly agent termination with state preservation

## Learning and Memory System

### Agent Memory Architecture
- **Short-term Memory:** Current session context and intermediate results
- **Long-term Memory:** Historical patterns, successful strategies, and learned optimizations
- **Shared Knowledge Base:** Common insights accessible to all agents

### Learning Mechanisms
1. **Performance Tracking:** Monitor success rates and processing times
2. **Strategy Optimization:** Learn which approaches work best for different file types
3. **Error Pattern Recognition:** Identify and prevent recurring issues
4. **User Feedback Integration:** Incorporate validation corrections into learning
5. **Resource Pattern Learning:** Learn optimal agent configurations for different scenarios

## Technical Implementation

### Celery-Based Agent Architecture

#### Core Components
1. **ResourceManager:** Central memory monitoring and agent lifecycle management
2. **AdaptiveAgent:** Base Celery task class with dynamic capability management  
3. **CapabilityRegistry:** Catalog of available functionalities and memory requirements
4. **ConsolidationEngine:** Logic for intelligent agent merging

#### Celery Agent Implementation
```python
from celery import Celery, Task
import psutil
import logging

app = Celery('autonomous_validation_agents')

class AdaptiveAgentTask(Task):
    """Base class for all autonomous agents"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.capabilities = []
        self.absorbed_capabilities = []
    
    def before_start(self, task_id, args, kwargs):
        """Check memory before agent spawning"""
        if not self.memory_manager.can_spawn_agent(self.__class__.__name__):
            # Trigger consolidation or reject task
            raise MemoryConstraintError("Insufficient memory for agent")

@app.task(bind=True, base=AdaptiveAgentTask)
def orchestrator_agent(self, excel_file, pdf_file):
    """Main orchestrator agent - always active"""
    try:
        memory_stats = self.memory_manager.get_current_stats()
        
        if memory_stats['available_gb'] > 6:
            # High memory mode - spawn specialized agents
            pdf_result = pdf_intelligence_agent.delay(pdf_file)
            excel_result = excel_intelligence_agent.delay(excel_file)
            validation_result = validation_agent.delay(pdf_result.get(), excel_result.get())
            return validation_result.get()
            
        elif memory_stats['available_gb'] > 3:
            # Medium memory mode - consolidated processing
            doc_result = document_processing_agent.delay(pdf_file, excel_file)
            return validation_agent.delay(doc_result.get()).get()
            
        else:
            # Low memory mode - single agent processing
            return self.process_internally(pdf_file, excel_file)
            
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        # Graceful fallback to basic processing
        return self.fallback_processing(pdf_file, excel_file)

@app.task(bind=True, base=AdaptiveAgentTask)
def pdf_intelligence_agent(self, pdf_file):
    """Specialized PDF processing agent"""
    memory_stats = self.memory_manager.get_current_stats()
    
    if memory_stats['available_gb'] > 4:
        # Spawn sub-agents for complex processing
        ocr_result = ocr_sub_agent.delay(pdf_file)
        multimodal_result = multimodal_sub_agent.delay(pdf_file)
        structure_result = structure_analysis_sub_agent.delay(pdf_file)
        
        return self.consolidate_results([
            ocr_result.get(),
            multimodal_result.get(), 
            structure_result.get()
        ])
    else:
        # Process internally without sub-agents
        return self.process_pdf_internally(pdf_file)

@app.task(bind=True, base=AdaptiveAgentTask)
def validation_agent(self, pdf_data, excel_data):
    """Validation agent with hybrid matching"""
    results = []
    
    for excel_item in excel_data:
        # Determine matching strategy based on data type
        if self.is_numerical(excel_item['value']):
            match_result = self.exact_match(excel_item, pdf_data)
        else:
            match_result = self.semantic_match(excel_item, pdf_data)
        
        results.append(match_result)
    
    return self.generate_validation_report(results)

# Sub-agents for specialized processing
@app.task(bind=True, base=AdaptiveAgentTask)
def ocr_sub_agent(self, pdf_file):
    """OCR-based text extraction sub-agent"""
    return self.extract_text_with_tesseract(pdf_file)

@app.task(bind=True, base=AdaptiveAgentTask) 
def multimodal_sub_agent(self, pdf_file):
    """BLIP-based multimodal processing sub-agent"""
    return self.extract_with_blip_model(pdf_file)

@app.task(bind=True, base=AdaptiveAgentTask)
def evaluation_agent(self, telemetry_data):
    """Agent performance evaluation and behavioral analysis"""
    return {
        'performance_metrics': self.calculate_performance_metrics(telemetry_data),
        'behavioral_analysis': self.analyze_agent_decisions(telemetry_data),
        'optimization_recommendations': self.generate_recommendations(telemetry_data)
    }
```

#### Memory Management with Celery
```python
class MemoryManager:
    def __init__(self, max_memory_gb=8):
        self.max_memory = max_memory_gb * 1024 * 1024 * 1024
        self.safety_margin = 0.15
        
    def get_current_stats(self):
        """Get real-time memory statistics"""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_percent': memory.percent,
            'can_spawn_agents': memory.available > (self.max_memory * self.safety_margin)
        }
    
    def can_spawn_agent(self, agent_type, estimated_memory_mb=512):
        """Check if we can spawn a new agent"""
        current_stats = self.get_current_stats()
        required_gb = estimated_memory_mb / 1024
        return current_stats['available_gb'] > required_gb
```

#### Celery Configuration for Agent Management
```python
# Celery configuration for dynamic scaling
app.conf.update(
    # Task routing for different agent types
    task_routes={
        'orchestrator_agent': {'queue': 'orchestrator'},
        'pdf_intelligence_agent': {'queue': 'processing'},
        'validation_agent': {'queue': 'validation'},
        'evaluation_agent': {'queue': 'evaluation'}
    },
    
    # Memory-based worker configuration
    worker_prefetch_multiplier=1,  # Prevent memory overload
    task_acks_late=True,          # Ensure task completion
    worker_max_tasks_per_child=100, # Restart workers to prevent memory leaks
    
    # Monitoring and evaluation
    task_send_sent_event=True,
    task_track_started=True,
    
    # Beat schedule for periodic evaluation
    beat_schedule={
        'evaluate-system-performance': {
            'task': 'evaluation_agent',
            'schedule': 300.0,  # Every 5 minutes
        },
        'memory-cleanup': {
            'task': 'memory_cleanup_agent', 
            'schedule': 60.0,   # Every minute
        }
    }
)
```

### Memory Optimization Techniques
1. **Lazy Loading:** Load models only when needed
2. **Model Sharing:** Multiple agents share the same model instances
3. **Batch Processing:** Group similar operations to maximize efficiency
4. **Aggressive Cleanup:** Immediate cleanup of completed tasks
5. **Memory Pools:** Pre-allocated memory chunks for agent operations

## Feasibility Analysis

### Technical Feasibility: HIGH ✅
**Strengths:**
- Dynamic agent management is well-established pattern
- Memory monitoring straightforward with psutil
- Capability consolidation reduces architectural complexity
- Graceful degradation ensures system reliability
- Exact matching algorithms straightforward to implement

**Implementation Considerations:**
- Agent state management during consolidation
- Message routing during topology changes
- Performance testing across memory configurations

### Resource Feasibility: HIGH ✅
**Memory Utilization Scenarios:**
- **8GB High Utilization:** 4 main agents + 6 sub-agents
- **8GB Medium Utilization:** 3 consolidated agents + 2 sub-agents  
- **8GB Low Utilization:** 1 orchestrator agent with internal capabilities
- **Minimum Viable:** 512MB for basic validation functionality

### Development Feasibility: MEDIUM-HIGH ✅
**Advantages:**
- Clear fallback strategies reduce risk
- Incremental complexity (start simple, add intelligence)
- Memory management patterns well-documented
- Strong foundation from existing POC #1

**Considerations:**
- Testing across multiple memory configurations
- Agent handoff and state preservation logic
- Performance profiling and optimization

## Success Metrics
1. **Adaptability:** System functions across 512MB to 8GB+ memory ranges
2. **Efficiency:** Optimal agent topology for given memory constraints
3. **Reliability:** No failures due to memory exhaustion
4. **Performance:** Graceful performance degradation, not functionality loss
5. **Intelligence:** Learn optimal consolidation patterns over time
6. **Precision:** 100% accuracy for exact numerical matches

## Implementation Roadmap

### Phase 1: Foundation (2-3 weeks)
- Resource monitoring and basic agent lifecycle management
- Simple consolidation patterns (2-3 configurations)
- Basic exact matching for numerical data
- Convert existing processors to agent tools

### Phase 2: Intelligence (3-4 weeks)
- Dynamic spawning decisions based on file complexity
- Advanced consolidation patterns
- Data type classification and matching strategy selection
- Learning and adaptation mechanisms

### Phase 3: Optimization (2-3 weeks)
- Performance tuning across memory configurations
- Advanced memory optimization techniques
- Precision threshold optimization
- Comprehensive testing and validation

## Risk Mitigation
1. **Complexity Management:** Start with simple agent behaviors, add intelligence incrementally
2. **Resource Constraints:** Implement aggressive memory management and model sharing
3. **Performance Issues:** Maintain fallback to current system architecture
4. **Development Timeline:** Modular development with working milestones
5. **Memory Management:** Comprehensive testing across resource configurations

## Conclusion
This adaptive multi-agent system solves the critical memory management challenge through intelligent resource allocation and dynamic role consolidation. The system maintains full functionality even under severe memory constraints while optimizing performance when resources are abundant.

The key innovation is the ability of agents to seamlessly absorb each other's capabilities, ensuring that the user experience remains consistent regardless of the underlying resource topology. The dual matching approach ensures both precision for numerical data and flexibility for textual content.
