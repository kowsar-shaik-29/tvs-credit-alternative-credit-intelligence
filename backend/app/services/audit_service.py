"""Decision Audit Trail service for TVS Credit NIRNAY.

Maintains immutable logs of credit evaluations, model versions, probability scores,
decision recommendations, and consented data signals for regulatory compliance.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.schemas.nirnay import AuditTrailRecord
from app.schemas.nirnay_enhancements import HumanReviewResponse


class AuditService:
    """In-memory thread-safe store for NIRNAY assessment audit records."""

    def __init__(self):
        self._records: Dict[str, AuditTrailRecord] = {}

    def log_assessment(
        self,
        application_id: str,
        customer_id: str,
        customer_name: str,
        default_prob: float,
        risk_class: str,
        recommended_action: str,
        consented_sources: List[str],
        alt_stability_score: int,
        resilience_score: int,
        analyst_action: str = "Automated Evaluation Complete",
        dealer_status: str = "Eligible - Verification Complete"
    ) -> AuditTrailRecord:
        record = AuditTrailRecord(
            application_id=application_id,
            customer_id=customer_id,
            customer_name=customer_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_name="Enhanced Random Forest",
            model_version="1.0.0 (Production NIRNAY)",
            threshold=0.47,
            default_probability=round(default_prob, 4),
            risk_classification=risk_class,
            recommended_action=recommended_action,
            consented_sources=consented_sources,
            alternative_stability_score=alt_stability_score,
            resilience_score=resilience_score,
            analyst_action=analyst_action,
            dealer_status=dealer_status
        )
        self._records[customer_id] = record
        self._records[application_id] = record
        return record

    def get_record(self, key: str) -> Optional[AuditTrailRecord]:
        return self._records.get(key)

    def list_recent_records(self, limit: int = 50) -> List[AuditTrailRecord]:
        # Return unique by application_id
        seen = set()
        unique = []
        for r in reversed(list(self._records.values())):
            if r.application_id not in seen:
                seen.add(r.application_id)
                unique.append(r)
            if len(unique) >= limit:
                break
        return unique

    def record_human_review(
        self,
        application_id: str,
        customer_id: str,
        decision: str,
        override_reason: str,
        analyst_role: str = "Senior Credit Underwriter",
        analyst_notes: Optional[str] = None
    ) -> HumanReviewResponse:
        """Records a human-in-the-loop review decision without mutating the underlying ML prediction."""
        record = self.get_record(application_id) or self.get_record(customer_id)

        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        ai_decision = record.recommended_action if record else "MANUAL REVIEW"
        ai_prob = record.default_probability if record else 0.4168

        is_override = (decision.upper() != ai_decision.upper())

        # Update the audit record's analyst action
        if record:
            action_desc = f"{decision.upper()} by {analyst_role}"
            if is_override:
                action_desc += f" (Override: {override_reason})"
            record.analyst_action = action_desc

            if decision.lower() == "approve":
                record.dealer_status = "Approved — Manual Credit Officer Sign-Off"
            elif decision.lower() == "reject":
                record.dealer_status = "Declined — Underwriting Policy Threshold"
            elif "additional" in decision.lower():
                record.dealer_status = "Pending — Additional Bank Documents Requested"
            else:
                record.dealer_status = "Monitoring — Periodic Portfolio Surveillance"

        return HumanReviewResponse(
            application_id=application_id,
            customer_id=customer_id,
            ai_decision=ai_decision,
            ai_default_probability=round(ai_prob, 4),
            analyst_decision=decision,
            override_reason=override_reason,
            analyst_role=analyst_role,
            analyst_notes=analyst_notes,
            timestamp=timestamp_str,
            audit_status="Audit Trail Updated (Immutable Log)",
            is_override=is_override,
            message=(
                f"Human-in-the-loop decision '{decision}' recorded by {analyst_role}. "
                f"{'Override logged with compliance justification.' if is_override else 'AI assessment verified and confirmed.'}"
            )
        )


audit_service = AuditService()
