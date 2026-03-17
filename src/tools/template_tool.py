"""
Template Tool — provides reference checklists and templates to agents.

Agents use this to ensure they don't miss important items. Instead of
relying purely on LLM memory, agents load proven checklists:
  - NFR categories checklist (for Requirements Agent)
  - API design checklist (for Architecture Agent)
  - Risk categories checklist (for Planning Agent)

These templates are curated from industry standards and best practices.
"""

from autogen_core.tools import FunctionTool


NFR_CHECKLIST = """## Non-Functional Requirements Checklist

Review each category and include relevant NFRs:

### Performance
- Response time targets (e.g., API < 200ms, page load < 2s)
- Throughput requirements (requests/second)
- Database query performance targets

### Scalability
- Expected concurrent users
- Data growth projections
- Horizontal vs vertical scaling needs

### Security
- Authentication method (OAuth2, JWT, SSO)
- Authorization model (RBAC, ABAC)
- Data encryption (at rest, in transit)
- Input validation and sanitization
- Rate limiting and DDoS protection

### Reliability
- Uptime target (99.9% = 8.76h downtime/year)
- Backup and recovery strategy
- Failover requirements

### Usability
- Accessibility standards (WCAG 2.1 AA)
- Mobile responsiveness
- Supported browsers/platforms
- Internationalization (i18n) needs

### Compliance
- Data privacy (GDPR, CCPA)
- Industry-specific (HIPAA, PCI-DSS, SOC2)
- Data residency requirements

### Maintainability
- Code coverage targets
- Documentation requirements
- Logging and monitoring standards
"""

API_DESIGN_CHECKLIST = """## API Design Checklist

Ensure your API design covers:

### Core Patterns
- RESTful resource naming (plural nouns: /users, /orders)
- Proper HTTP methods (GET=read, POST=create, PUT=update, DELETE=remove)
- Consistent response format (envelope pattern with data/error/meta)
- Pagination for list endpoints (cursor-based or offset)
- Filtering and sorting support on list endpoints

### Authentication & Authorization
- Auth endpoint (login/register/refresh token)
- Token-based authentication (JWT or OAuth2)
- Role-based access on protected endpoints
- API key support for service-to-service calls

### Error Handling
- Standard error response format (code, message, details)
- Proper HTTP status codes (400, 401, 403, 404, 422, 500)
- Validation error details for 422 responses

### Essential Endpoints Often Missed
- Health check endpoint (GET /health or GET /api/v1/health)
- User profile/settings endpoints
- Search/filter endpoints
- Bulk operations (if needed)
- File upload endpoints (if needed)
- Webhook endpoints (if integrating with external services)

### Versioning
- API versioning strategy (URL path /v1/ recommended)
"""

RISK_CATEGORIES_CHECKLIST = """## Project Risk Categories Checklist

Evaluate each category for potential risks:

### Technical Risks
- New/unfamiliar technology choices
- Complex integrations with third-party services
- Performance bottlenecks at scale
- Data migration complexity
- Security vulnerabilities in dependencies

### Resource Risks
- Team skill gaps for chosen tech stack
- Key person dependency
- Insufficient testing resources
- Infrastructure cost overruns

### Schedule Risks
- Underestimated complexity
- Dependencies on external teams or services
- Scope creep from unclear requirements
- Holiday/vacation impact on timeline

### Business Risks
- Changing requirements mid-development
- Competitor launches similar feature
- Regulatory/compliance changes
- User adoption uncertainty

### Operational Risks
- Deployment failures
- Monitoring gaps
- Incident response readiness
- Documentation gaps for handoff
"""


async def load_nfr_checklist() -> str:
    """
    Load the non-functional requirements checklist.

    Use this BEFORE generating NFRs to ensure you cover all important
    categories: performance, security, scalability, reliability, usability,
    compliance, and maintainability.

    Returns:
        A comprehensive NFR checklist organized by category
    """
    return NFR_CHECKLIST


async def load_api_design_checklist() -> str:
    """
    Load the API design best practices checklist.

    Use this BEFORE designing API endpoints to ensure you follow RESTful
    conventions and don't miss commonly forgotten endpoints like health
    checks, pagination, and error handling patterns.

    Returns:
        An API design checklist with patterns and common endpoints
    """
    return API_DESIGN_CHECKLIST


async def load_risk_checklist() -> str:
    """
    Load the project risk categories checklist.

    Use this BEFORE identifying risks to ensure you evaluate all
    categories: technical, resource, schedule, business, and operational.

    Returns:
        A risk assessment checklist organized by category
    """
    return RISK_CATEGORIES_CHECKLIST


# Create AutoGen-compatible tools
nfr_checklist_tool = FunctionTool(
    load_nfr_checklist,
    name="load_nfr_checklist",
    description="Load a comprehensive non-functional requirements checklist covering performance, security, scalability, reliability, usability, compliance, and maintainability.",
)

api_checklist_tool = FunctionTool(
    load_api_design_checklist,
    name="load_api_design_checklist",
    description="Load an API design best practices checklist covering RESTful patterns, auth, error handling, pagination, and commonly missed endpoints.",
)

risk_checklist_tool = FunctionTool(
    load_risk_checklist,
    name="load_risk_checklist",
    description="Load a project risk categories checklist covering technical, resource, schedule, business, and operational risks.",
)
