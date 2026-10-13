# Multi-Framework Institutional Accreditation & Compliance Hub

## Goal

Extend the existing NAAC evidence application into one institutional source of truth for NAAC, NBA, NIRF, AICTE, IIC, AISHE, UGC and university/affiliation requirements. The framework modules must be configurable and must reuse verified facts and evidence rather than copy the same institutional data into separate silos.

This branch is an architecture and data-contract starter. It does not claim that regulator-specific report generation or portal submission is already implemented.

## Design principles

1. **Capture once, map many times.** A fact such as annual student intake is stored as an institutional fact with its period, scope, source and approval state. Framework mappings decide which criteria/metrics may consume it.
2. **Version every rule.** Reporting rules are versioned by framework, framework edition, effective date and applicability. Prior submissions must remain reproducible.
3. **Do not silently calculate official metrics.** A metric definition includes a formula/version, unit, denominator, eligible population, exclusions and rounding policy. All calculation results retain lineage to source facts.
4. **Evidence is distinct from data.** A data value may be supported by one or more evidence documents; a document may support multiple applicable metrics. Evidence links do not prove that the linked content meets a regulator's rules; human review remains required.
5. **Academic-year and scope aware.** Every value has an effective period and a scope such as institution, department, programme, cohort or activity. Avoid mixing years, programmes, campuses or sanctioned/actual counts.
6. **Configurable modules.** Framework modules can be enabled/disabled per institution and can load versioned definitions from reviewed configuration packages.
7. **Traceable approvals.** Track who submitted, checked, approved, rejected or superseded data and when. Drafts never become approved because a report was generated.
8. **Export first, portal integration separately.** Generate validated export packages where possible. Direct submission/API integration must be verified for each authority and must never be assumed.

## Proposed application layers

- **Institutional core**: institution profile, campuses, departments, programmes, academic years, people/roles, cohorts, facilities and organisational hierarchy.
- **Data catalogue**: data element definitions, units, type/validation rules, scope rules, retention rules and responsible owner.
- **Institutional facts**: period-based measurements or records with scope, source system, submitted/verified/approved status and provenance.
- **Evidence vault**: files, URLs, document metadata, hashes, versions, OCR/search metadata, confidentiality level and review status. Existing document upload functionality can be retained and evolved.
- **Framework registry**: framework, edition/version, criterion/parameter, metric, applicability, required data elements, calculation definition and report/export mapping.
- **Mapping & lineage**: mapping between canonical data elements and framework metrics; source fact → calculation run → report cell lineage.
- **Workflow & compliance calendar**: assignments, deadlines, approvals, reminders, exception tracking and risk/readiness dashboards.
- **Reporting**: draft preview, completeness checks, calculation results, evidence index, exports and immutable submission snapshots.
- **Integration adapters**: ERP/SIS/examination/HR/research/placement/finance/import connectors. Use read-only ingestion by default until reconciled and approved.

## Initial framework coverage

| Module code | Scope to configure | Common data reused |
|---|---|---|
| NAAC | Applicable criteria, metrics, qualitative/quantitative inputs, evidence and DVV preparation | Faculty, students, curriculum, results, research, extension, facilities, governance, student support |
| NBA | Programme-specific SAR, PEO/PO/PSO, CO mapping, attainment and continuous improvement | Programme structure, course outcomes, assessments, results, faculty, placements, facilities |
| NIRF | Applicable category/edition, parameters, metric definitions, reporting windows and evidence | Intake, strength, faculty, financial/research data, graduation outcomes, placements, inclusivity, perception records |
| AICTE | Approval and mandatory disclosure requirements applicable to institution/programmes | Approved intake, programmes, faculty, infrastructure, fees and disclosures |
| IIC | Applicable innovation council activities, programmes, participation, outcomes and evidence | Events, teams, students, faculty mentors, innovation/startups/IP/industry engagement |
| AISHE | Annual return questions and validation rules for the applicable cycle | Institution identity, programmes, enrolment, faculty, examination, finance and infrastructure |
| Affiliation / University | University, state, programme, intake, inspection and renewal requirements | Programme approvals, intake, staff, infrastructure, academic calendar, results and compliance evidence |
| UGC / other | Only applicable regulations, recognition/disclosure requirements and editions | Shared institutional profile and related source records |

Framework-specific definitions must be loaded from the relevant authority's official, current guidance and reviewed by the institution before use.

## Data model overview

`Institution` → `AcademicYear`, `Campus`, `Department`, `Programme`, `Person`.

`DataElement` defines the reusable concept (for example `faculty.full_time_count`) and expected type/unit/scope.

`InstitutionalFact` stores one value for a specific period and scope, with provenance, status, submitter, verifier, approver and timestamps.

`EvidenceAsset` describes a document or external supporting reference. `FactEvidenceLink` links source facts to evidence; `MetricEvidenceLink` links evidence to a framework metric.

`Framework` → `FrameworkEdition` → `FrameworkCriterion` → `FrameworkMetric`.

`MetricDataMapping` links one canonical `DataElement` (or a reviewed calculation) to a metric. `CalculationRun` stores formula version, inputs, outputs, validation messages and run status. `ReportSnapshot` freezes values and evidence references for a particular draft/final export so later edits do not rewrite history.

## Suggested initial canonical data domains

- Institutional identity and approvals
- Academic years, terms and reporting periods
- Campuses, schools/departments, programmes, sanctioned intake
- Faculty/staff profiles, appointment type, qualification and workload
- Student enrolment, cohort, category where lawfully required, progression and completion
- Course/curriculum, CO/PO/PSO mapping, assessment and attainment
- Examination results, pass percentage, backlog, graduation and progression
- Research publications, patents/IP, grants, projects and consultancy
- Placement, higher education, entrepreneurship and employer evidence
- Extension, outreach, IIC events, innovation, incubation and startup activities
- Infrastructure, laboratories, library, accessibility and learning resources
- Finance, scholarships, student support and governance
- MOUs, collaborations, faculty development, awards, disclosures and minutes

## Data lifecycle

1. Owner submits a fact or imports it from an identified source.
2. Validation checks type, required scope, reporting period, duplicate candidates and source lineage.
3. Department data coordinator reviews it and requests corrections if needed.
4. Authorised institutional reviewer approves, rejects or supersedes it.
5. Only approved facts are eligible for official report calculations by default.
6. A metric mapping evaluates completeness and freshness and explains missing/invalid inputs.
7. IQAC/framework coordinator checks evidence and results; authorised sign-off freezes a report snapshot.
8. Exports retain framework edition, calculation version, approval state, generation time and lineage.

## Security and data governance

- Enforce institution boundary and role/action permissions in the backend, not merely in the UI.
- Support scoped roles: institution admin, principal, IQAC coordinator, framework coordinator, HOD, data owner, reviewer, auditor and read-only viewer.
- Separate personal data from aggregate reporting values; restrict sensitive attributes and log access.
- Use environment-provided secrets, production HTTPS, upload size/type controls, malware scanning where available, secure object storage and backups.
- Never store real student/faculty data in fixtures, sample screenshots, public issues or test logs.
- Define retention and authorised deletion policies while preserving required audit/submission records.
- Apply row-level security or institution-scoped querysets before considering a multi-institution SaaS deployment.

## Delivery phases

### Phase 1 — Foundation
Canonical catalogue, academic years/scopes, framework registry, facts and evidence links, roles, workflow statuses, audit trail and API tests.

### Phase 2 — Reuse and readiness
Metric mappings, completeness/freshness rules, calculation lineage, data import templates, dashboards and review queues.

### Phase 3 — Framework packages
Implement one versioned framework package at a time, validating every criterion/metric against official current documentation. Start with NAAC and NIRF institutional metrics; add NBA as a programme-level module because its OBE model has distinct structures.

### Phase 4 — Operational hardening
Production configuration, migrations, tests, security review, backup/restore drill, accessibility, performance, retention and incident procedures.

## Acceptance criteria for the first implementation

- An administrator can register frameworks and versioned editions without changing core fact tables.
- One approved canonical fact can be mapped to multiple framework metrics.
- Each fact requires an academic period and explicit scope when the data element definition says so.
- Evidence can be linked to more than one fact/metric without duplicating the underlying file.
- Unapproved or superseded facts are excluded from official calculations unless a reviewed rule explicitly says otherwise.
- Every mapping/calculation shows missing inputs, source lineage, formula version and validation messages.
- A report snapshot remains reproducible after source data changes.
- APIs and tests enforce tenant/institution and role boundaries.
- The existing NAAC document workflow keeps working while the new framework-neutral foundation is introduced.

## Known boundary

The implementation must not claim official endorsement, automatic accreditation, guaranteed scores or direct submission to portals. Regulatory editions and report formats change; configuration packages require ongoing review by designated institutional owners.
