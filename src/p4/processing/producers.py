from __future__ import annotations

import hashlib
import re
from html import unescape
from typing import Any

from p4.collection.detail import parse_next_data, select_activity_text

SECTION_PATTERN = re.compile(
    r"^\s*\[(업무내용|담당업무|자격요건|지원자격|우대사항)\]\s*$", re.MULTILINE
)
SECTION_TYPES = {
    "업무내용": "duty",
    "담당업무": "duty",
    "자격요건": "required",
    "지원자격": "required",
    "우대사항": "preferred",
}
CHUNK_ROLES = {"duty": "DUTY", "required": "REQUIREMENT", "preferred": "REQUIREMENT"}


def stable_id(prefix: str, *parts: object) -> str:
    material = "\x1f".join(str(part) for part in parts)
    return f"{prefix}-{hashlib.sha256(material.encode()).hexdigest()[:20]}"


def _plain_text(value: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"</(?:p|div|li|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text).replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _track_type(value: str) -> str:
    normalized = str(value).lower()
    if "intern" in normalized or "인턴" in normalized:
        return "intern"
    if "experience" in normalized or "경력" in normalized:
        return "experienced"
    if "entry" in normalized or "신입" in normalized:
        return "entry"
    return "unknown"


def _requirement_type(text: str) -> str:
    rules = (
        ("degree", ("학사", "석사", "박사", "졸업")),
        ("career", ("경력", "년 이상", "개월 이상")),
        ("certificate", ("자격증", "기사")),
        ("portfolio", ("포트폴리오",)),
        ("project", ("프로젝트",)),
        ("skill", ("python", "sql", "데이터", "개발")),
    )
    lowered = text.lower()
    for requirement_type, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            return requirement_type
    return "other"


def produce_raw_to_semantic(html: str, raw_manifest: dict[str, Any]) -> dict[str, list[dict]]:
    next_data = parse_next_data(html)
    props = next_data.get("props", {})
    page_props = props.get("pageProps", {})
    apollo = props.get("apolloState") or page_props.get("__APOLLO_STATE__", {})
    source_posting_id = str(raw_manifest["sourcePostingId"])
    activity = select_activity_text(apollo, source_posting_id)
    detail = page_props.get("data", {}).get("activityData", {}).get("activity", {})
    content = _plain_text(str(activity.get("content") or activity.get("text", "")))
    posting_id = stable_id("POST", source_posting_id)
    track_id = stable_id("TRACK", posting_id, 0)
    source_block_id = stable_id("BLOCK", raw_manifest["rawPostingId"], "ACTIVITY_TEXT", content)
    raw_row = {
        **raw_manifest,
        "sourceMode": "ACTIVITY_TEXT",
    }
    posting = {
        "postingId": posting_id,
        "sourcePostingId": source_posting_id,
        "rawPostingId": raw_manifest["rawPostingId"],
        "titleText": str(activity.get("title") or detail.get("title", "")),
        "companyName": str(
            activity.get("companyName")
            or detail.get("organizationName")
            or detail.get("company", {}).get("name", "")
        ),
        "canonicalPostedAt": activity.get("postedAt") or detail.get("createdAt"),
        "postingEligibleFlag": bool(
            (activity.get("postedAt") or detail.get("createdAt"))
            and (
                activity.get("companyName")
                or detail.get("organizationName")
                or detail.get("company", {}).get("name")
            )
        ),
    }
    block = {
        "sourceBlockId": source_block_id,
        "postingId": posting_id,
        "rawPostingId": raw_manifest["rawPostingId"],
        "rawSha256": raw_manifest["contentSha256"],
        "sourceMode": "ACTIVITY_TEXT",
        "sourceText": content,
        "startOffset": 0,
        "endOffset": len(content),
    }
    track_type = _track_type(
        str(activity.get("recruitType") or detail.get("jobTypes") or detail.get("recruitType", ""))
    )
    track = {
        "trackId": track_id,
        "postingId": posting_id,
        "trackOrdinal": 0,
        "trackType": track_type,
        "mixedResolvedFlag": track_type != "unknown",
    }
    matches = list(SECTION_PATTERN.finditer(content))
    sections: list[dict] = []
    section_blocks: list[dict] = []
    chunks: list[dict] = []
    chunk_blocks: list[dict] = []
    mentions: list[dict] = []
    facts: list[dict] = []
    fact_mentions: list[dict] = []
    ordinal_offset = 0
    if matches and (preamble := content[: matches[0].start()].strip()):
        section_id = stable_id("SECTION", track_id, 0, "other", preamble)
        sections.append(
            {
                "sectionId": section_id,
                "trackId": track_id,
                "sectionOrder": 0,
                "sectionType": "other",
                "sectionText": preamble,
                "boundaryResolvedFlag": True,
            }
        )
        section_blocks.append(
            {
                "sectionId": section_id,
                "sourceBlockId": source_block_id,
                "relationType": "PRIMARY_SPAN",
            }
        )
        for chunk_ordinal, line in enumerate(
            line.lstrip("-• ").strip() for line in preamble.splitlines() if line.strip()
        ):
            chunk_id = stable_id("CHUNK", section_id, chunk_ordinal, line)
            chunks.append(
                {
                    "chunkId": chunk_id,
                    "trackId": track_id,
                    "sectionId": section_id,
                    "chunkOrdinal": chunk_ordinal,
                    "chunkText": line,
                    "chunkRole": "OTHER",
                }
            )
            chunk_blocks.append(
                {"chunkId": chunk_id, "sourceBlockId": source_block_id, "evidenceRole": "PRIMARY"}
            )
        ordinal_offset = 1
    for match_ordinal, match in enumerate(matches):
        body_start = match.end()
        body_end = (
            matches[match_ordinal + 1].start() if match_ordinal + 1 < len(matches) else len(content)
        )
        body = content[body_start:body_end].strip()
        section_type = SECTION_TYPES[match.group(1)]
        ordinal = match_ordinal + ordinal_offset
        section_id = stable_id("SECTION", track_id, ordinal, section_type, body)
        sections.append(
            {
                "sectionId": section_id,
                "trackId": track_id,
                "sectionOrder": ordinal,
                "sectionType": section_type,
                "sectionText": body,
                "boundaryResolvedFlag": True,
            }
        )
        section_blocks.append(
            {
                "sectionId": section_id,
                "sourceBlockId": source_block_id,
                "relationType": "PRIMARY_SPAN",
            }
        )
        lines = [line.lstrip("-• ").strip() for line in body.splitlines() if line.strip()]
        for chunk_ordinal, line in enumerate(lines):
            chunk_id = stable_id("CHUNK", section_id, chunk_ordinal, line)
            chunks.append(
                {
                    "chunkId": chunk_id,
                    "trackId": track_id,
                    "sectionId": section_id,
                    "chunkOrdinal": chunk_ordinal,
                    "chunkText": line,
                    "chunkRole": CHUNK_ROLES[section_type],
                }
            )
            chunk_blocks.append(
                {
                    "chunkId": chunk_id,
                    "sourceBlockId": source_block_id,
                    "evidenceRole": "PRIMARY",
                }
            )
            if section_type not in {"required", "preferred"}:
                continue
            mention_id = stable_id("MENTION", chunk_id, line)
            requirement_type = _requirement_type(line)
            fact_id = stable_id("FACT", track_id, requirement_type, section_type, line.lower())
            mentions.append(
                {
                    "mentionId": mention_id,
                    "trackId": track_id,
                    "sectionId": section_id,
                    "chunkId": chunk_id,
                    "sourceText": line,
                    "requirementType": requirement_type,
                    "obligation": section_type,
                }
            )
            facts.append(
                {
                    "requirementFactId": fact_id,
                    "trackId": track_id,
                    "requirementType": requirement_type,
                    "normalizedSubject": line.lower(),
                    "obligation": section_type,
                }
            )
            fact_mentions.append({"requirementFactId": fact_id, "mentionId": mention_id})
    return {
        "raw_posting_version": [raw_row],
        "posting_normalized": [posting],
        "posting_source_block": [block],
        "posting_track": [track],
        "posting_section": sections,
        "section_source_block": section_blocks,
        "semantic_chunk": chunks,
        "chunk_source_block": chunk_blocks,
        "requirement_mention": mentions,
        "requirement_fact": facts,
        "requirement_fact_mention": fact_mentions,
    }
