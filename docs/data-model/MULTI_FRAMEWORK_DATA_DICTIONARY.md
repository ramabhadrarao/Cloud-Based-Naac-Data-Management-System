# Shared Institutional Data Dictionary — Initial Draft

This dictionary is the canonical naming proposal for reusable data. It is not an official schema of NAAC, NBA, NIRF, AICTE, IIC, AISHE or any university. Each release must be reviewed against the official guidance applicable to the reporting year.

## Naming convention

Use stable namespaced keys: `domain.concept`. Do not encode a framework name in a canonical key. Framework-specific differences belong in mappings and versioned rules.

| Canonical key | Meaning | Default unit/type | Typical scope | Possible source |
|---|---|---|---|---|
| institution.legal_name | Registered institutional name | text | institution | institutional master |
| institution.recognition_status | Current recognition/approval state | enum + date range | institution/programme | approval records |
| academic_year.label | Academic-year label | text/date range | institution | academic calendar |
| programme.sanctioned_intake | Approved intake for a programme and year | integer, students | programme + year | approval/affiliation order |
| student.enrolled_count | Count of enrolled students under specified population rules | integer, students | programme/cohort/year | SIS |
| student.admitted_count | Count admitted in reporting period | integer, students | programme/cohort/year | admissions |
| student.completed_count | Count meeting completion definition | integer, students | programme/cohort/year | examination/SIS |
| student.progressed_count | Count progressing to next year/stage under specified rule | integer, students | programme/cohort/year | SIS |
| faculty.full_time_count | Count of eligible full-time faculty under the applicable definition | integer, persons | department/programme/year | HR |
| faculty.part_time_count | Count of eligible part-time faculty under the applicable definition | integer, persons | department/programme/year | HR |
| faculty.qualification_profile | Staff qualifications using effective-dated staff records | structured records | staff/department/year | HR |
| course.outcome_definition | Approved course outcome statement/version | text/version | course/term | curriculum system |
| programme.po_definition | Approved programme outcome statement/version | text/version | programme/version | academic council/OBE records |
| programme.pso_definition | Approved programme-specific outcome/version | text/version | programme/version | academic council/OBE records |
| obe.co_po_mapping | Approved CO-to-PO/PSO mapping and scale | structured mapping | course/programme/version | OBE system |
| obe.co_attainment | Calculated CO attainment with method and input references | decimal/scale | course/term/version | exam/assessment |
| obe.po_attainment | Calculated PO/PSO attainment with method and input references | decimal/scale | programme/cohort/version | OBE system |
| examination.appeared_count | Eligible candidates appeared under a stated exam/reporting rule | integer, students | cohort/exam/year | examination system |
| examination.passed_count | Eligible candidates passed under a stated rule | integer, students | cohort/exam/year | examination system |
| placement.placed_count | Students placed under a stated placement eligibility/deduplication rule | integer, students | cohort/year | placement cell |
| placement.higher_studies_count | Graduates in verified higher studies under a stated rule | integer, students | cohort/year | placement/alumni |
| research.publication_record | Publication with DOI/identifier, authors, year and verification state | structured record | person/department/year | research repository |
| research.grant_amount | Eligible research grant receipts as defined for a reporting framework | currency + period | institution/department/year | finance/research |
| research.patent_record | IP/patent record and status | structured record | institution/person/year | IP cell |
| innovation.event_record | IIC/innovation programme or event details | structured record | institution/department/date | IIC coordinator |
| innovation.startup_record | Verified startup/incubation record | structured record | institution/team/period | incubation cell |
| extension.activity_record | Extension/outreach activity, partner, date, participants and outcome | structured record | institution/department/date | NSS/extension cell |
| infrastructure.facility_record | Facility, capacity, inventory and effective date | structured record | campus/department | estate/lab/library |
| finance.expenditure_category | Expense totals according to controlled account categories | currency + period | institution/year | finance/ERP |
| support.scholarship_record | Scholarship/financial support records with privacy restrictions | structured record | student/cohort/year | student welfare/finance |
| collaboration.mou_record | MOU with parties, validity, activity and outcomes | structured record | institution/department/period | department/industry cell |
| faculty.development_activity | FDP/training participation or delivery record | structured record | staff/department/year | HR/IQAC |
| governance.meeting_record | Meeting, agenda/minutes/decision and follow-up | structured record | committee/date | office/IQAC |
| student.satisfaction_result | Survey response aggregate, method, sample and period | structured result | cohort/programme/year | survey system |

## Fields required on each fact or record

Every number or record submitted into accreditation workflows should carry:

- Canonical data key or domain-specific record type.
- Institution identifier.
- Reporting period, usually academic year and optionally term/date window.
- Scope kind and scope identifier: institution, campus, department, programme, cohort, person, facility or activity.
- Value and unit, including currency and currency year where relevant.
- Population/eligibility rule and definition version when counting people or outcomes.
- Source system / source record identifier / import batch where applicable.
- Supporting evidence references.
- Data owner, submission timestamp, reviewer, approval status and approval timestamp.
- Validation results, revision history and superseded-by relationship.
- Classification/access level and retention rule where personal or confidential data is involved.

## Common validation rules

1. Do not compare counts unless their scope, period and eligibility rules match.
2. Guard against double counting across departments, programmes, co-authors, placements, events and financial transactions.
3. Preserve raw source values and calculation results separately.
4. Formulae need a version and an auditable input set; do not update old results in place.
5. Treat missing, zero, not applicable, not yet verified and not reported as distinct states.
6. Dates must include effective periods where approvals, employment, facilities and MOUs expire or start.
7. Reconcile aggregate counts with underlying records before approval.
8. Make framework-specific denominator, rounding and exclusion rules explicit.
