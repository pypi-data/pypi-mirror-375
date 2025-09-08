"""Simple dialog orchestrator for CLI demo with AI-generated questionnaires."""
from __future__ import annotations

import uuid
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json

from . import models
from .evaluators.jsonlogic_eval import evaluate_rule
from .auto_rules import build_annex3_index, build_article5_index
from sqlalchemy import text as sql_text


# Dynamic risk classification based on database features
def classify_from_answers(answers: dict) -> dict:
    """Classify risk dynamically based on database features and answers."""
    if not answers:
        return {"category": "minimal_risk", "score": 0.0, "legal_refs": [], "exception_applied": False}
    
    # If no database URL provided, use default
    db_url = os.getenv('ANNEX4AC_DB_URL') or os.getenv('DB_URL') or "sqlite:///risk.db"
    
    # Create database connection
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
    
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as db:
            # ——— Legally correct, data-driven classifier (AI Act) ———
            features = {f.key: f for f in db.execute(select(models.RiskFeature)).scalars()}
            questions = {q.feature_key: q for q in db.execute(select(models.RiskQuestion)).scalars()}
            constraints = list(db.execute(select(models.PolicyConstraint)).scalars())
            annex3 = build_annex3_index(db, table_name=os.environ.get("ANNEX_TABLE","rules"))
            all_items = {code for items in annex3["items"].values() for code,_ in items}
            art5   = build_article5_index(db, table_name=os.environ.get("ANNEX_TABLE","rules"))
            art5_codes = set(art5.get("items", {}).keys())
            # Без хардкода: тянем ссылки Annex I прямо из таблицы правил
            annex1_refs = [r[0] for r in db.execute(sql_text(
                f"SELECT section_code FROM {os.environ.get('ANNEX_TABLE','rules')} "
                "WHERE section_code ~* '^Annex\\s*I(\\D|$)' ORDER BY section_code"
            )).fetchall()]

            legal_refs: list[str] = []
            exception_applied = False
            risk_factors: list[str] = []
            obligations: set[str] = set()
            client = OpenAI()

            def _truthy(v):
                if isinstance(v, bool): return v
                if v is None: return False
                if isinstance(v, (list, dict, tuple, set)): return len(v) > 0
                if isinstance(v, str): return v.strip() != ""
                return True

            # (1) Больше не полагаемся на "сумму legal_bases вопросов".
            # Обязанности выводим отдельно LLM-ом по актуальному тексту (ст.49 + Прил. VIII),
            # учитывая answers + финальную категорию.
            def _llm_obligations(category: str, exception_applied: bool) -> list[str]:
                if category in {"minimal_risk", "out_of_scope"}:
                    return []
                art49 = "\n".join(r[0] for r in db.execute(sql_text(
                    f"SELECT COALESCE(title,'')||E'\\n'||COALESCE(content,'') FROM {os.environ.get('ANNEX_TABLE','rules')} "
                    "WHERE section_code ~* '^(Article|Art\\.)\\s*49(\\D|$)' ORDER BY section_code"
                )).fetchall() if r and r[0])[:5000]
                annex8 = "\n".join(r[0] for r in db.execute(sql_text(
                    f"SELECT COALESCE(title,'')||E'\\n'||COALESCE(content,'') FROM {os.environ.get('ANNEX_TABLE','rules')} "
                    "WHERE section_code ~* '^Annex\\s*VIII(\\D|$)' ORDER BY section_code"
                )).fetchall() if r and r[0])[:5000]
                prompt = f"""Given the user's answers {json.dumps(answers, ensure_ascii=False)},
final category='{category}', exception_applied={exception_applied}.
From the legal texts below (Article 49 + Annex VIII), list the obligations that apply NOW to this user
as concise strings with article/annex anchors. Return a JSON object: {{"items": ["Art.49 ...", "Annex VIII ..."]}}.
ARTICLE 49:\n{art49}\n\nANNEX VIII:\n{annex8}"""
                try:
                    resp = client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
                        temperature=0, max_tokens=512,
                        response_format={"type":"json_object"},
                        messages=[{"role":"user","content":prompt}],
                    )
                    js = json.loads(resp.choices[0].message.content)
                    return (js or {}).get("items", [])
                except Exception:
                    return []

            # Не делаем ранний возврат по prohibited_item.
            # Решение по ст.5 принимается через policy_constraints (см. динамический триггер ниже).

            # (−1) Сфера применения: если пользователь отметил исключение по ст.2 — выходим как out_of_scope
            if _truthy(answers.get("scope_excluded_reason")):
                return {
                    "category": "out_of_scope",
                    "score": 0.0,
                    "legal_refs": ["Article 2 (scope/exclusions)"],
                    "exception_applied": False,
                    "risk_factors": ["scope_exclusion"],
                    "obligations": _llm_obligations("out_of_scope", False),
                }

            # (0) Annex I / ст.6(1): high-risk ТОЛЬКО если (a) safety component/или продукт И (b) обязателен third-party CA
            annex1_a = _truthy(answers.get("annex1_safety_component"))
            # NB: не опираемся на Annex I ref для (b), т.к. требование third-party зависит от конкретного акта/режима
            annex1_b = _truthy(answers.get("third_party_assessment"))
            if annex1_a and annex1_b:
                refs = ["Article 6(1)", "Annex I"]
                if _truthy(answers.get("annex1_act_ref")):
                    refs.append(str(answers.get("annex1_act_ref")))
                return {
                    "category": "high_risk",
                    "score": 1.0,
                    "legal_refs": sorted(set(refs)),
                    "exception_applied": False,
                    "risk_factors": ["annex1_path"],
                    "obligations": _llm_obligations("high_risk", False),
                }

            # 0) Разделяем constraints по правовым основаниям:
            def _is_a63(c):
                lbs = (c.legal_bases or [])
                return any(isinstance(lb, str) and "Article 6(3)" in lb for lb in lbs)
            pre_constraints  = [c for c in constraints if not _is_a63(c)]
            a63_constraints  = [c for c in constraints if _is_a63(c)]

            # 0a) Применяем "ранние" ограничения (ст.5, ст.6(1)/Annex I и др., но не ст.6(3))
            pre_fired = []
            for c in pre_constraints:
                try:
                    if evaluate_rule(c.trigger, answers):
                        pre_fired.append(c)
                except Exception:
                    pass
            if any(c.effect == "force_prohibited" for c in pre_fired):
                res = {
                    "category": "prohibited",
                    "score": 1.0,
                    "legal_refs": sorted(set(["Article 5"] + sum([c.legal_bases or [] for c in pre_fired], []))),
                    "exception_applied": False,
                    "risk_factors": ["constraint:force_prohibited"],
                    "obligations": _llm_obligations("prohibited", False),
                }
                return res
            if any(c.effect == "force_high_risk" for c in pre_fired):
                res = {
                    "category": "high_risk",
                    "score": 1.0,
                    "legal_refs": sorted(set(sum([c.legal_bases or [] for c in pre_fired], []))),
                    "exception_applied": False,
                    "risk_factors": ["constraint:force_high_risk"],
                    "obligations": _llm_obligations("high_risk", False),
                }
                return res

            # Annex III item selected → high-risk (Art. 6(2)), если нет снижения по 6(3)
            annex3_item = answers.get("annex3_item")
            if isinstance(annex3_item, str) and annex3_item in all_items:
                category = "high_risk"
                legal_refs.append(annex3_item)
                risk_factors.append(f"annex3:{annex3_item}")

                # 1) Применяем ТОЛЬКО здесь ограничения по ст.6(3) (включая "always_high_risk_profiling")
                a63_fired = []
                for c in a63_constraints:
                    try:
                        if evaluate_rule(c.trigger, answers):
                            a63_fired.append(c)
                    except Exception:
                        pass
                # Сначала жёсткие эффекты:
                if any(c.effect == "force_prohibited" for c in a63_fired):
                    return {
                        "category": "prohibited",
                        "score": 1.0,
                        "legal_refs": sorted(set(["Article 6(3)"] + sum([c.legal_bases or [] for c in a63_fired], []))),
                        "exception_applied": False,
                        "risk_factors": ["constraint:force_prohibited","annex3"],
                        "obligations": _llm_obligations("prohibited", False),
                    }
                if any(c.effect == "force_high_risk" for c in a63_fired):
                    return {
                        "category": "high_risk",
                        "score": 1.0,
                        "legal_refs": sorted(set(sum([c.legal_bases or [] for c in a63_fired], []))),
                        "exception_applied": False,
                        "risk_factors": ["constraint:force_high_risk","annex3"],
                        "obligations": _llm_obligations("high_risk", False),
                    }

                a63 = answers.get("a6_conditions") or []
                if isinstance(a63, list) and len(a63) > 0:
                    # при попытке «снизить» учитываем ТОЛЬКО а63-ограничения
                    blocks_downgrade = any(
                        c.effect in ("force_high_risk","force_prohibited","disallow_a6_relief")
                        for c in a63_fired
                    )
                    if not blocks_downgrade:
                        category = "limited_risk"
                        exception_applied = True
                        legal_refs.append("Article 6(3)")
                res = {
                    "category": category,
                    "score": 1.0 if category == "high_risk" else 0.5,
                    "legal_refs": sorted(set(legal_refs)),
                    "exception_applied": exception_applied,
                    "risk_factors": risk_factors,
                    "obligations": _llm_obligations(category, exception_applied),
                }
                return res

            # No Annex III / Article 5 / Annex I triggers → minimal
            return {
                "category": "minimal_risk",
                "score": 0.0,
                "legal_refs": [],
                "exception_applied": False,
                "risk_factors": [],
                "obligations": _llm_obligations("minimal_risk", False),
            }
            
    except Exception as e:
        # Fallback to minimal risk if database access fails
        return {
            "category": "minimal_risk", 
            "score": 0.0, 
            "legal_refs": [], 
            "exception_applied": False,
            "error": f"Database error: {str(e)}"
        }


class DialogOrchestrator:
    def __init__(self, db_url: str):
        if db_url.startswith("sqlite"):
            self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
        self.Session = sessionmaker(bind=self.engine)

    def start_session(self, customer_id: str = None) -> str:
        with self.Session() as db:
            # Get current questionnaire version from meta_kv
            a_hash = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='annex3_hash'")).scalar() or "unknown"
            l_hash = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='legal_hash'")).scalar() or "unknown"
            version = f"{a_hash[:12]}+{l_hash[:12]}"
            
            session_id = str(uuid.uuid4())
            chat = models.ChatSession(
                id=session_id, customer_id=customer_id, rule_snapshot_version=version
            )
            db.add(chat)
            db.commit()
            return session_id

    def _get_missing_required_features(self, features, questions, answers):
        """
        Return required features that are currently *visible* under gating and still unanswered.
        This prevents blocking on required fields that are not yet gated-in.
        """
        missing: list[str] = []
        for q in sorted(questions, key=lambda q: getattr(q, "priority", 0)):
            f = features.get(q.feature_key)
            if not f:
                continue
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            if getattr(f, "required", False):
                missing.append(q.feature_key)
        return missing

    def _visible_unanswered(self, questions, answers):
        """List feature_keys for questions that are currently visible (gating passes) and unanswered."""
        out = []
        for q in questions:
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            out.append(q.feature_key)
        return out

    def _get_next_question(self, questions, features, answers):
        """Get the next question to ask based on priority and gating."""
        for q in sorted(questions, key=lambda q: getattr(q, "priority", 0)):
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            
            f = features.get(q.feature_key)
            if not f:
                continue
                
            result = {
                "feature_key": q.feature_key,
                "prompt": q.prompt_en or f.prompt_en,
                "type": f.type,
                "options": (f.options or []),
            }
            
            # Dynamic filtering for annex3_item based on selected area
            if q.feature_key == "annex3_item":
                area = answers.get("annex3_area")
                if area:
                    # Filter options to only show items under the selected area
                    filtered_options = [opt for opt in f.options if opt.startswith(area + ".")]
                    if filtered_options:
                        result["options"] = filtered_options
                    else:
                        result["options"] = [area]  # Fallback to area itself
            
            return result
        return None

    def next_question(self, session_id: str):
        with self.Session() as db:
            chat = db.get(models.ChatSession, session_id)
            if not chat:
                raise RuntimeError(f"Chat session not found: {session_id}")
            
            # Load AI-generated features and questions
            features = {f.key: f for f in db.execute(select(models.RiskFeature)).scalars()}
            questions = list(db.execute(select(models.RiskQuestion).order_by(models.RiskQuestion.priority)).scalars())
            answers = {a.feature_key: a.value for a in chat.answers}
            
            # Get current questionnaire version (consistent with start_session)
            a_hash = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='annex3_hash'")).scalar() or "unknown"
            l_hash = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='legal_hash'")).scalar() or "unknown"
            version = f"{a_hash[:12]}+{l_hash[:12]}"

            def finalize():
                """Finalize the session with risk classification."""
                outcome = classify_from_answers(answers)
                reasoning = {"outcome": outcome, "answers": answers}
                res = models.RiskOutcome(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    rule_snapshot_version=version,
                    category=outcome["category"],
                    score=outcome["score"],
                    reasoning=reasoning,
                    legal_refs=outcome["legal_refs"],
                    exception_applied=outcome["exception_applied"],
                )
                db.add(res)
                db.commit()
                return {"outcome": outcome, "answers": answers}

            # Fast-path: if Article 5 was selected, finish immediately.
            # (Classifier will return "prohibited" based on legal_bases from that question.)
            if answers.get("prohibited_item"):
                return finalize()

            # Generic early-finish rule:
            # if no gated question remains visible (i.e., nothing to ask now), finalize.
            visible_still_unanswered = self._visible_unanswered(questions, answers)
            if not visible_still_unanswered:
                return finalize()

            # Find next question to ask
            next_q = self._get_next_question(questions, features, answers)
            if next_q:
                return next_q

            # If no next question, check if any required (and *visible*) features remain; otherwise finalize
            missing = self._get_missing_required_features(features, questions, answers)
            if missing:
                raise RuntimeError(f"Missing required answers for: {', '.join(missing)}")

            return finalize()

    def submit_answer(self, session_id: str, feature_key: str, value):
        with self.Session() as db:
            if not db.get(models.ChatSession, session_id):
                raise RuntimeError(f"Chat session not found: {session_id}")
            ans = models.ChatAnswer(
                id=str(uuid.uuid4()),
                session_id=session_id,
                feature_key=feature_key,
                value=value,
            )
            db.add(ans)
            db.commit()
