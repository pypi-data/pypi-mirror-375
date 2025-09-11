from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..async_client import AsyncPhrappy

from ..models import (
    JobPartReadyReferences,
    SegmentListDto,
    SegmentsCountsResponseListDto,
)


class SegmentOperations:
    def __init__(self, client: AsyncPhrappy):
        self.client = client

    async def get_segments_count(
        self,
        project_uid: str,
        job_part_ready_references: Optional[JobPartReadyReferences | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> SegmentsCountsResponseListDto:
        """
        Operation id: getSegmentsCount
        Get segments count

        This API provides the current count of segments (progress data).

        Every time this API is called, it returns the most up-to-date information. Consequently, these numbers will change
        dynamically over time. The data retrieved from this API call is utilized to calculate the progress percentage in the UI.

        The call returns the following information:

        Counts of characters, words, and segments for each of the locked, confirmed, and completed categories. In this context,
        _completed_ is defined as `confirmed` + `locked` - `confirmed and locked`.

        The number of added words if the [Update source](https://support.phrase.com/hc/en-us/articles/10825557848220-Job-Tools)
        operation has been performed on the job. In this context, added words are defined as the original word count plus the
        sum of words added during all subsequent update source operations.

        The count of segments where relevant machine translation (MT) was available (machineTranslationRelevantSegmentsCount)
        and the number of segments where the MT output was post-edited (machineTranslationPostEditedSegmentsCount).

        A breakdown of [Quality assurance](https://support.phrase.com/hc/en-us/articles/5709703799324-Quality-Assurance-QA-TMS-)
        results, including the number of segments on which it was performed, the count of warnings found, and the number of
        warnings that were ignored.

        Additionally, a breakdown of the aforementioned information from the previous
        [Workflow step](https://support.phrase.com/hc/en-us/articles/5709717879324-Workflow-TMS-) is also provided.

        :param project_uid: str (required), path.
        :param job_part_ready_references: Optional[JobPartReadyReferences | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentsCountsResponseListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/segmentsCount"
        if type(job_part_ready_references) is dict:
            job_part_ready_references = JobPartReadyReferences.model_validate(
                job_part_ready_references
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = job_part_ready_references

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return SegmentsCountsResponseListDto.model_validate(r.json())

    async def list_segments(
        self,
        job_uid: str,
        project_uid: str,
        begin_index: Optional[int] = 0,
        end_index: Optional[int] = 0,
        phrase_token: Optional[str] = None,
    ) -> SegmentListDto:
        """
        Operation id: listSegments
        Get segments

        :param job_uid: str (required), path.
        :param project_uid: str (required), path.
        :param begin_index: Optional[int] = 0 (optional), query.
        :param end_index: Optional[int] = 0 (optional), query.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SegmentListDto
        """

        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/segments"

        params = {"beginIndex": begin_index, "endIndex": end_index}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return SegmentListDto.model_validate(r.json())
