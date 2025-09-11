# tests/test_phrappy/test_project_e2e.py
import asyncio, pytest
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
@pytest.mark.asyncio
async def test_project_e2e(aclient, aproject, test_file):
    _ = await aclient.project.get_project(aproject.uid)
    _ = await aclient.project.get_project_access_settings_v2(aproject.uid)
    _ = await aclient.project.get_file_naming_settings(aproject.uid)
    _ = await aclient.project.get_financial_settings(aproject.uid)
    _ = await aclient.project.get_project_pre_translate_settings_v4(aproject.uid)
    _ = await aclient.project.get_import_settings_for_project(aproject.uid)
    _ = await aclient.project.get_analyse_settings_for_project(aproject.uid)
    _ = await aclient.project.get_project_settings(aproject.uid)
    _ = await aclient.project.get_project_workflow_steps_v2(aproject.uid)

    p1 = await aclient.project.patch_project(aproject.uid, PatchProjectDto.model_validate({"name": aproject.name + " x"}))
    assert p1.name.endswith(" x")
    p2 = await aclient.project.edit_project_v2(aproject.uid, {"name": aproject.name + " y"})
    assert p2.name.endswith(" y")
    p3 = await aclient.project.edit_project_v3(aproject.uid, {"name": aproject.name + " z"})
    assert p3.name.endswith(" z")

    curp = await aclient.project.get_mt_settings_for_project(aproject.uid)
    await aclient.project.set_mt_settings_for_project(aproject.uid, {"machineTranslateSettings": getattr(curp, "machineTranslateSettings", None)})
    await aclient.project.set_mt_settings_per_language_for_project(aproject.uid, {"mtSettingsPerLanguage": getattr(curp, "mtSettingsPerLanguage", None)})

    _ = await aclient.project.enabled_quality_checks(aproject.uid)

    tb_rel = await aclient.project.relevant_term_bases(aproject.uid, target_langs=["sv"])
    if tb_rel and getattr(tb_rel, "content", None):
        dto = SetTermBaseDto(writeTermBase=IdReference(id=tb_rel.content[0].id))
        _ = await aclient.project.set_project_term_bases(aproject.uid, dto)
        _ = await aclient.project.get_project_term_bases(aproject.uid)
    tm_rel = await aclient.project.relevant_trans_memories_for_project(aproject.uid, target_langs=["sv"])
    if tm_rel and getattr(tm_rel, "content", None):
        tm_uid = tm_rel.content[0].uid
        dto = SetProjectTransMemoriesV3Dto(dataPerContext=[
            SetContextTransMemoriesDtoV3Dto(
                transMemories=[SetProjectTransMemoryV3Dto(transMemory=UidReference(uid=tm_uid), readMode=True, writeMode=True)]
            )
        ])
        _ = await aclient.project.set_project_trans_memories_v3(aproject.uid, dto)
        _ = await aclient.project.get_project_trans_memories_v3(aproject.uid)

    _ = await aclient.project.get_quotes_for_project(aproject.uid)
    _ = await aclient.project.list_by_project_v3(aproject.uid)

    await aclient.project.add_target_language_to_project(aproject.uid, AddTargetLangDto(targetLangs=["nb"]))

    me = await aclient.authentication.who_am_i()
    _ = await aclient.project.get_project_assignments(aproject.uid)
    _ = await aclient.project.list_assigned_projects(me.user.uid, target_lang=["sv","da"])

    jobs = await aclient.job.create_job(
        project_uid=aproject.uid,
        content_disposition=cdh_generator("en_test_ÄöÖÅas£223.docx"),
        file_bytes=b"two words",
        memsource=JobCreateRequestDto(targetLangs=aproject.targetLangs),
    )
    await asyncio.sleep(5)
    parts = await aclient.job.list_parts_v2(project_uid=aproject.uid)
    if parts.content:
        for j in parts.content:
            _ = await aclient.job.get_part(j.uid, aproject.uid)

        refs = [UidReference(uid=j.uid) for j in jobs.jobs or []]
        await aclient.job.delete_parts(job_part_delete_references=JobPartReferences(jobs=refs), project_uid=aproject.uid, purge=True)

    clone = await aclient.project.clone_project(aproject.uid, {"name": aproject.name + " clone"})
    try:
        assert getattr(clone, "uid", None)
    finally:
        try:
            await aclient.project.delete_project(clone.uid, purge=True)
        except Exception:
            pass
