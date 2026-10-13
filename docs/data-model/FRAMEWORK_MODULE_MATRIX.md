# Framework Module Matrix

This matrix is a planning tool. It intentionally avoids fixing numerical weights or formulas because requirements depend on the applicable framework edition, institution/programme category and reporting year.

| Module | Main data domains | Special modelling needs | Reporting output |
|---|---|---|---|
| NAAC | Curriculum, teaching/learning, research, extension, infrastructure, student support, governance, institutional values | Criteria and metric versions; quantitative vs qualitative fields; evidence and DVV trail | Criterion/metric workbooks, narratives, evidence indexes, readiness checklists |
| NBA | Programme, curriculum, CO/PO/PSO, assessment, attainment, continuous improvement, faculty, facilities | Programme-level boundary; outcome mappings; attainment methods; indirect/direct assessment; action taken | Programme SAR sections, CO/PO attainment tables, supporting evidence |
| NIRF | Teaching/learning resources, research/professional practice, graduation outcomes, outreach/inclusivity, perception | Category-specific eligibility, time windows, staff/student denominators, ranking edition | Parameter-level validated tables and prescribed return/export |
| AICTE | Institution/programme approvals, intake, faculty, facilities, mandatory disclosures | Approval type and validity, programme applicability, handbook year, document expiry | Approval/disclosure checklists and authorised disclosure package |
| IIC | Innovation calendar, events, student/faculty participation, mentoring, IP, incubation, startups | Activity cycle, event evidence, participant deduplication, activity and outcome linkage | IIC activity/outcome reports and evidence collection |
| AISHE | Institutional identity, programmes, enrolment, staff, examination, finance, infrastructure | Annual survey edition, controlled categories, totals and cross-field validations | AISHE annual return preparation and validation |
| Affiliation / university | Programme/branch affiliation, approved intake, inspection, staff, infrastructure, academic processes | University/state-specific rules, renewal date, programme and campus scope | Renewal checklist, affiliation return, inspection evidence |
| UGC / other | Recognition, disclosures, regulations and specific surveys/returns | Explicit applicability and versioning; do not enable automatically for all institutions | Configured return and compliance tracking |

## Example: one fact, multiple metric mappings

Canonical fact: `faculty.full_time_count` = 84, scope = institution, academic year = 2025–26, source = approved HR snapshot, status = approved.

It may be consumed by multiple framework metrics only if each framework's definition accepts that population and scope. NBA may require eligible faculty for a specific programme; in that case the institution-wide count is not sufficient, and programme-specific faculty records or a validated allocation rule is needed.

The application should show each mapping as one of:
- **Compatible** — the canonical scope/definition matches the metric.
- **Needs transformation** — a reviewed calculation or mapping is required.
- **Insufficient** — the data has the wrong scope, time window, population or evidence.
- **Not applicable** — authorised reviewer records a reason under the relevant edition.

Never assume the same-looking number is equivalent across frameworks.
