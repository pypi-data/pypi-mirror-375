# tests/test_phrappy/test_segmentation_rules_tag.py
import pytest
from urllib.parse import quote as urlquote
from random import randint

from phrappy.models import CreateSegmentationRuleMeta, EditSegmentationRuleDto

SAMPLE_SEGRULE = r"""<?xml version="1.0" encoding="UTF-8"?>
<srx xmlns="http://www.lisa.org/srx20" xmlns:okpsrx="http://okapi.sf.net/srx-extensions" version="2.0">
<header cascade="yes" segmentsubflows="yes"><formathandle include="no" type="start"/><formathandle include="yes" type="end"/>
<formathandle include="no" type="isolated"/><okpsrx:options oneSegmentIncludesAll="no" trimLeadingWhitespaces="yes" trimTrailingWhitespaces="yes"/>
<okpsrx:rangeRule/></header><body><languagerules><languagerule languagerulename="supplement"><rule break="no">
<beforebreak>(\b|\p{Z})[\p{Cc}\p{Cf}\p{Co}\p{Cn}]*(\Qapprox.\E|\QApprox.\E)</beforebreak>
<afterbreak>[\p{Cc}\p{Cf}\p{Co}\p{Cn}]*[\p{Z}]+[\p{Cc}\p{Cf}\p{Co}\p{Cn}]*\p{Lu}</afterbreak></rule></languagerule></languagerules>
<maprules><languagemap languagerulename="supplement" languagepattern=".*" /></maprules></body></srx>"""

@pytest.mark.live
@pytest.mark.destructive
@pytest.mark.asyncio
async def test_segmentation_rule_full_cycle(aclient):
    dto = await aclient.segmentation_rules.create_segmentation_rule(
        file_bytes=SAMPLE_SEGRULE.encode("utf-8"),
        seg_rule=CreateSegmentationRuleMeta(
            name="Test Segmentation Rule",
            locale="sv",
            primary=True,
            filename=urlquote("saåpa.srx"),
        )
    )
    try:
        new_name = f"New nåme {randint(1000, 9999)}"
        dto = await aclient.segmentation_rules.updates_segmentation_rule(
            dto.id, EditSegmentationRuleDto(name=new_name, primary=False)
        )

        lst = (await aclient.segmentation_rules.get_list_of_segmentation_rules()).content
        names = [x.name for x in lst]
        assert new_name in names

        this = next(x for x in lst if x.name == new_name)
        segrule = await aclient.segmentation_rules.get_segmentation_rule(this.id)
        downloaded = await aclient.segmentation_rules.export_segmentation_rule(segrule.id)
        assert len(downloaded) == len(SAMPLE_SEGRULE.encode("utf-8"))

        owners = await aclient.segmentation_rules.get_segmentation_rules_owners()
        assert owners and owners.owners
    finally:
        try:
            await aclient.segmentation_rules.deletes_segmentation_rule(dto.uid)
        except Exception:
            pass
