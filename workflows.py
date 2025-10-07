from datamodels import TextRequest, ResponseItem, PolicyRow
from extractor.extract import extract_compliance_questions, extract_questions
from extractor.cite import check_requirement
from indexer.search import search_similar_purpose, get_policyprocedure
from logs import logger


def audit_one(req: ResponseItem, top_k: int = 3) -> ResponseItem:
    # logger.info(f"Checking {i}/{len(responses)} requirements...")
    policies: list[PolicyRow] = search_similar_purpose(req.requirement, top_k=top_k)
    policy_content: list[PolicyRow] = []

    for p in policies:
        proceduresRows = get_policyprocedure(p.file_name)
        policy_item = PolicyRow(
            file_name=p.file_name,
            section='policy+procedure',
            paragraph_id=p.paragraph_id,
            content='',
        )
        for section in proceduresRows:
            policy_item.content += section.content
        policy_content.append(policy_item)

    logger.info(
        f"Retrieved {len(policy_content)} policy+procedure sections from {len(policies)} documents."
    )

    is_met_flag = False
    for policy in policy_content:
        
        check_result = check_requirement(policy.content, req.requirement)
        if check_result["is_met"]:
            is_met_flag = True
            req.is_met = True
            req.file_name = policy.file_name
            req.citation = check_result["citation"]
            break

    if not is_met_flag:
        req.is_met = False
        req.citation = None
        req.explanation = "Documents reviewed: " + "; ".join(
            [p.file_name for p in policies]
        )

    logger.info(f"Requirement: {req.requirement[:50]}... Met: {req.is_met}")
    return req


def audit_main(request: TextRequest) -> list[ResponseItem]:
    responses: list[ResponseItem] = extract_questions(request.text)
    logger.info(f"Extracted {len(responses)} compliance questions.")

    for i, r in enumerate(responses, 1):
        logger.info(f"Checking {i}/{len(responses)} requirements...")
        policies: list[PolicyRow] = search_similar_purpose(r.requirement, top_k=3)
        policy_content: list[PolicyRow] = []

        for p in policies:
            proceduresRows = get_policyprocedure(p.file_name)
            policy_content.extend(proceduresRows)

        logger.info(
            f"Retrieved {len(policy_content)} policy/procedure sections from {len(policies)} documents."
        )

        is_met_flag = False
        for policy in policy_content:
            check_result = check_requirement(policy.content, r.requirement)
            if check_result["is_met"]:
                is_met_flag = True
                r.is_met = True
                r.file_name = policy.file_name
                r.citation = check_result["citation"]
                break

        if not is_met_flag:
            r.is_met = False
            r.citation = None
            r.explanation = "Documents reviewed: " + "; ".join(
                [p.file_name for p in policies]
            )

        logger.info(f"Requirement: {r.requirement[:50]}... Met: {r.is_met}")

    return {"responses": responses}


def audit_test(request: TextRequest) -> list[ResponseItem]:
    responses = extract_questions(request.text)
    logger.info(f"Extracted {len(responses)} compliance questions.")
    return responses
