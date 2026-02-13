# Unified Data Processing Layer - Implementation TODO

## Phase 1: Database Layer - Master Tables & Normalization ✅ COMPLETED

### 1.1 Create Master Reference Tables
- [x] Update Bacteria model with canonical_name and aliases (handled via normalization)
- [x] Update Antibiotic model with canonical_name and aliases (handled via normalization)
- [x] Create database migrations
- [x] Add indexes for performance

### 1.2 Create Data Normalization Utilities
- [x] Create core/data_normalization.py
- [x] Create core/master_data.py
- [x] Create data cleanup management command
- [x] Register core app in Django settings

---

## Phase 2: Unified Query Engine ✅ COMPLETED

### 2.1 Create Unified Filter Service
- [x] Create core/filters.py - Global filter engine
- [x] Implement date range filtering
- [x] Implement bacteria filtering (case-insensitive)
- [x] Implement department filtering
- [x] Implement antibiotic filtering

### 2.2 Create Unified Data Service
- [x] Create core/data_service.py
- [x] Implement get_filtered_results()
- [x] Implement get_statistics()
- [x] Implement get_resistance_data()
- [x] Implement get_effectiveness_data()

---

## Phase 3: Backend API Updates

### 3.1 Update All Views to Use Unified Services
- [ ] Update StatsView
- [ ] Update SensitivityDistributionView
- [ ] Update AntibioticEffectivenessView
- [ ] Update ResistanceOverTimeView
- [ ] Update ResistanceHeatmapView
- [ ] Update ReportView
- [ ] Update AIPredictView

### 3.2 Add Filter Parameters to All Endpoints
- [ ] Add filter parameter parsing
- [ ] Add filter validation
- [ ] Update API documentation

---

## Phase 4: AI Enhancement with Gemma Integration

### 4.1 Enhanced AI Recommendations
- [ ] Create ai_engine/gemma_service.py
- [ ] Integrate with Ollama/Gemma 3:4b
- [ ] Implement comprehensive data reading
- [ ] Add medical explanation generation
- [ ] Add MDR/XDR pattern detection

### 4.2 Create AI Analysis Service
- [ ] Create ai_engine/enhanced_predictions.py
- [ ] Implement resistance trend analysis
- [ ] Implement antibiotic recommendation logic
- [ ] Add category/mechanism inference
- [ ] Create medical knowledge base

---

## Phase 5: Frontend Updates

### 5.1 Enhanced Data Filters Component
- [ ] Add Search button with loading state
- [ ] Display active filters
- [ ] Show filtered results count
- [ ] Add filter reset functionality

### 5.2 Unified Reports Component
- [ ] Create single unified report component
- [ ] Add bacteria filter
- [ ] Add antibiotic filter
- [ ] Add department filter
- [ ] Ensure consistent styling

### 5.3 Update All Components to Use Filters
- [ ] Update Dashboard to pass filters to all charts
- [ ] Update Heatmap to use filters
- [ ] Update AIRecommendation to use filters
- [ ] Update DatabaseRecommendation to use filters

---

## Phase 6: Database Migration & Cleanup

### 6.1 Data Cleanup Script
- [ ] Create management command for data cleanup
- [ ] Identify duplicate bacteria (case variations)
- [ ] Merge duplicate records
- [ ] Update foreign key references
- [ ] Normalize all existing text fields
- [ ] Generate cleanup report

---

## Testing & Validation

- [ ] Test filter functionality across all endpoints
- [ ] Test case-insensitive queries
- [ ] Test AI recommendations with full dataset
- [ ] Test report generation with filters
- [ ] Test heatmap with normalized data
- [ ] Verify no data loss during cleanup
- [ ] Performance testing with large datasets

---

## Documentation

- [ ] Update API documentation
- [ ] Create user guide for filters
- [ ] Document data normalization process
- [ ] Create admin guide for data cleanup
- [ ] Update deployment guide

---

## Current Status: Phase 3 - Updating Backend API Views
**Next Step**: Update all API views to use unified data service
