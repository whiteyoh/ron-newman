from pathlib import Path


def test_candidate_output_preserves_whitespace():
    css = Path("web/styles.css").read_text(encoding="utf-8")
    assert ".final-output-body" in css
    assert "white-space: pre-wrap;" in css


def test_download_label_updated():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "Download full run trace (.txt)" in html
    assert "Download latest artifact (.txt)" not in html


def test_candidate_status_mapping_and_copy_scope_static():
    js = Path("web/js/main.js").read_text(encoding="utf-8")
    for snippet in [
        "getCandidateStatusLabel",
        "'Ready for review'",
        "'Needs human review'",
        "'Blocked by check'",
        "'Could not complete safely'",
        "'Review needed'",
        "renderFinalOutput(refs.finalOutputBody, normalizedFinalAnswer)",
        "refs.copyOutputBtn.textContent = 'Copy output';",
        "state.latestCandidateOutput = normalizedFinalAnswer;",
        "state.latestCandidateOutput || refs.finalOutputBody?.textContent?.trim() || ''",
        ".replace(/^#+\\s*/, '')",
        ".replace(/^\\*\\*/, '')",
        ".replace(/\\*\\*$/, '')",
    ]:
        assert snippet in js


def test_render_final_output_groups_heading_with_following_content_and_avoids_innerhtml():
    js = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "function renderFinalOutput" in js
    assert "innerHTML" not in js
    assert "current.appendChild(createEl('h4', 'final-output-heading', cleanedHeading));" in js
    assert "bodyNode.appendChild(block);" not in js


def test_copy_reset_in_clear_helpers():
    run_ui = Path("web/js/run-ui.js").read_text(encoding="utf-8")
    assert "state.latestCandidateOutput = null;" in run_ui


def test_approval_success_text_and_states_static():
    js = Path("web/js/render-taskboard.js").read_text(encoding="utf-8")
    for snippet in [
        "approval.approved === true",
        "approvedValue === 'true'",
        "['approved', 'merged'].includes(decision)",
        "['approved', 'merged', 'completed'].includes(finalStatus)",
        "would still wait for human review before use",
        "Needs human review — simulated merge would not proceed.",
    ]:
        assert snippet in js


def test_taskboard_plain_english_labels_and_approval_humanization():
    js = Path("web/js/render-taskboard.js").read_text(encoding="utf-8")
    for snippet in [
        "appendKV(wc, 'Step'",
        "appendKV(wc, 'What it worked on'",
        "appendKV(wc, 'Result'",
        "appendKV(wc, 'Try'",
        "appendKV(wc, 'Summary'",
        "humanizeApprovalValue",
        "return 'Yes'",
        "return 'No'",
        "return 'Needs human review'",
    ]:
        assert snippet in js


def test_workflow_detail_and_raw_transcript_remain_present():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "Show workflow detail" in html
    assert "Raw output transcript" in html
