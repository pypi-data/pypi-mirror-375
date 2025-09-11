import time, pytest
from logging import getLogger

from phrappy import cdh_generator
from phrappy.models import (
    PatchProjectDto, IdReference, AddTargetLangDto, SetProjectStatusDto, BuyerStatusEnum,
    SearchTMRequestDto, UidReference, JobPartReferences, SetTermBaseDto,
    SetProjectTransMemoriesV3Dto, SetContextTransMemoriesDtoV3Dto, SetProjectTransMemoryV3Dto, JobCreateRequestDto,
)

logger = getLogger(__name__)

@pytest.mark.live
@pytest.mark.slow
@pytest.mark.destructive
def test_project_e2e(client, project, test_file):
    # ---- basic reads / settings roundtrips ----
    _ = client.project.get_project(project.uid)
    _ = client.project.get_project_access_settings_v2(project.uid)
    _ = client.project.get_file_naming_settings(project.uid)
    _ = client.project.get_financial_settings(project.uid)
    _ = client.project.get_project_pre_translate_settings_v4(project.uid)
    _ = client.project.get_import_settings_for_project(project.uid)
    _ = client.project.get_analyse_settings_for_project(project.uid)
    _ = client.project.get_project_settings(project.uid)          # LQA
    _ = client.project.get_project_workflow_steps_v2(project.uid)

    # edits / patches
    p1 = client.project.patch_project(project.uid, PatchProjectDto.model_validate({"name": project.name + " x"}))
    assert p1.name.endswith(" x")
    p2 = client.project.edit_project_v2(project.uid, {"name": project.name + " y"})
    assert p2.name.endswith(" y")
    p3 = client.project.edit_project_v3(project.uid, {"name": project.name + " z"})
    assert p3.name.endswith(" z")

    # roundtrip mt settings (two endpoints)
    curp = client.project.get_mt_settings_for_project(project.uid)
    client.project.set_mt_settings_for_project(project.uid, {"machineTranslateSettings": getattr(curp, "machineTranslateSettings", None)})
    client.project.set_mt_settings_per_language_for_project(project.uid, {"mtSettingsPerLanguage": getattr(curp, "mtSettingsPerLanguage", None)})

    # enabled quality checks should parse even if docs drifted (your normalizer adds some enums)
    _ = client.project.enabled_quality_checks(project.uid)

    # term bases / TMs (best-effort: skip if none relevant)
    tb_rel = client.project.relevant_term_bases(project.uid, target_langs=["sv"])
    if tb_rel and getattr(tb_rel, "content", None):
        dto = SetTermBaseDto(writeTermBase=IdReference(id=tb_rel.content[0].id))
        _ = client.project.set_project_term_bases(project.uid, dto)
        _ = client.project.get_project_term_bases(project.uid)
    tm_rel = client.project.relevant_trans_memories_for_project(project.uid, target_langs=["sv"])
    if tm_rel and getattr(tm_rel, "content", None):
        tm_uid = tm_rel.content[0].uid
        dto = SetProjectTransMemoriesV3Dto(dataPerContext=[
            SetContextTransMemoriesDtoV3Dto(
                transMemories=[SetProjectTransMemoryV3Dto(transMemory=UidReference(uid=tm_uid), readMode=True, writeMode=True)]
            )
        ])
        _ = client.project.set_project_trans_memories_v3(project.uid, dto)
        _ = client.project.get_project_trans_memories_v3(project.uid)

    # quotes / analyses pages (existence)
    _ = client.project.get_quotes_for_project(project.uid)
    _ = client.project.list_by_project_v3(project.uid)

    # add a target language
    client.project.add_target_language_to_project(project.uid, AddTargetLangDto(targetLangs=["nb"]))

    # assignments / me
    me = client.authentication.who_am_i()
    _ = client.project.get_project_assignments(project.uid)
    _ = client.project.list_assigned_projects(me.user.uid, target_lang=["sv","da"])

    # upload job preview package (multipart)
    # _ = client.project.upload_job_preview_package(b"PK\x03\x04preview", project.uid, filename="preview.zip")

    # templates assign if available (best-effort)
    tpl = client.project.assignable_templates(project.uid)
    if tpl and getattr(tpl, "assignableTemplates", None):
        first = tpl.assignableTemplates[0]
        parts = client.job.list_parts_v2(project_uid=project.uid)
        client.project.assign_linguists_from_template(project.uid, first.id)
        if parts.content:
            refs = {"jobs": [{"uid": j.uid} for j in parts.content[:1]]}
            client.project.assign_linguists_from_template_to_job_parts(project.uid, first.id, refs)

    # vendor assign (may require specific account perms; ignore failures)
    try:
        client.project.assign_vendor_to_project(project.uid, {})
    except Exception:
        pass

    # custom fields (best-effort)
    page = client.project.get_custom_fields_page_of_project(project.uid)
    if page and getattr(page, "content", None):
        first = page.content[0]
        got = client.project.get_custom_field_of_project(first.uid, project.uid)
        try:
            _ = client.project.edit_custom_field_on_project(first.uid, project.uid, got.model_dump())
            _ = client.project.edit_custom_fields_on_project(project.uid, {"fields": [got.model_dump()]})
        except Exception:
            # some accounts restrict editing; don't fail the whole e2e
            pass

    # status set and revert
    client.project.set_project_status(project.uid, SetProjectStatusDto(status=BuyerStatusEnum.COMPLETED))
    client.project.set_project_status(project.uid, SetProjectStatusDto(status=BuyerStatusEnum.NEW))

    # search TM (may be empty; just ensure the call works)
    _ = client.project.search_tm_segment(project.uid, SearchTMRequestDto(segment="Hello", targetLangs=["sv"]))

    # jobs lifecycle inside the same project
    jobs = client.job.create_job(
        project_uid=project.uid,
        content_disposition=cdh_generator("en_test_ÄöÖÅas£223.docx"),
        file_bytes=b"two words",
        memsource=JobCreateRequestDto(targetLangs=project.targetLangs),
    )
    time.sleep(5)
    parts = client.job.list_parts_v2(project_uid=project.uid)
    if parts.content:
        for j in parts.content:
            _ = client.job.get_part(j.uid, project.uid)

        # cleanup jobs explicitly before project teardown
        refs = [UidReference(uid=j.uid) for j in jobs.jobs or []]
        client.job.delete_parts(job_part_delete_references=JobPartReferences(jobs=refs), project_uid=project.uid, purge=True)

    # clone & delete clone
    clone = client.project.clone_project(project.uid, {"name": project.name + " clone"})
    try:
        assert getattr(clone, "uid", None)
    finally:
        try:
            client.project.delete_project(clone.uid, purge=True)
        except Exception:
            pass
