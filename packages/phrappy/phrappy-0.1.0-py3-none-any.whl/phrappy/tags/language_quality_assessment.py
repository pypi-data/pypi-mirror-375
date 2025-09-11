from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..client import Phrappy

from ..models import (
    AssessmentBasicDto,
    AssessmentDetailDto,
    AssessmentDetailsDto,
    AssessmentRequestDto,
    AssessmentResultDto,
    AssessmentResultsDto,
    FinishAssessmentDto,
    FinishAssessmentsDto,
    LqaReportEmailRequestDto,
    LqaReportLinkDto,
    PageDtoLqaReportRecipientDto,
    RunAutoLqaDto,
    ScoringResultDto,
)


class LanguageQualityAssessmentOperations:
    def __init__(self, client: Phrappy):
        self.client = client

    def discard_assessment_results(
        self,
        assessment_request_dto: Optional[AssessmentRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: discardAssessmentResults
        Discard multiple finished LQA Assessment results

        :param assessment_request_dto: Optional[AssessmentRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/lqa/assessments/scorings"
        if type(assessment_request_dto) is dict:
            assessment_request_dto = AssessmentRequestDto.model_validate(
                assessment_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assessment_request_dto

        self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    def discard_ongoing_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: discardOngoingAssessment
        Discard ongoing LQA Assessment

        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    def discard_ongoing_assessments(
        self,
        assessment_request_dto: Optional[AssessmentRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> None:
        """
        Operation id: discardOngoingAssessments
        Discard multiple ongoing LQA Assessments

        :param assessment_request_dto: Optional[AssessmentRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """

        endpoint = "/api2/v1/lqa/assessments"
        if type(assessment_request_dto) is dict:
            assessment_request_dto = AssessmentRequestDto.model_validate(
                assessment_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assessment_request_dto

        self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return

    def download_lqa_reports(
        self,
        job_parts: str,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: downloadLqaReports
        Download LQA Assessment XLSX reports
        Returns a single xlsx report or ZIP archive with multiple reports.
        If any given jobPart is not from LQA workflow step, reports from successive workflow steps may be returned
        If none were found returns 404 error, otherwise returns those that were found.
        :param job_parts: str (required), query. Comma separated list of JobPart UIDs, between 1 and 100 UIDs .

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/lqa/assessments/reports"

        params = {"jobParts": job_parts}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return r.content

    def finish_assessment(
        self,
        job_uid: str,
        finish_assessment_dto: Optional[FinishAssessmentDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> ScoringResultDto:
        """
        Operation id: finishAssessment
        Finish LQA Assessment
        Finishing LQA Assessment will calculate score
        :param job_uid: str (required), path.
        :param finish_assessment_dto: Optional[FinishAssessmentDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScoringResultDto
        """

        endpoint = f"/api2/v1/lqa/assessments/{job_uid}/scorings"
        if type(finish_assessment_dto) is dict:
            finish_assessment_dto = FinishAssessmentDto.model_validate(
                finish_assessment_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = finish_assessment_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return ScoringResultDto.model_validate(r.json())

    def finish_assessments(
        self,
        finish_assessments_dto: Optional[FinishAssessmentsDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AssessmentResultsDto:
        """
        Operation id: finishAssessments
        Finish multiple LQA Assessments
        Finishing LQA Assessments will calculate scores
        :param finish_assessments_dto: Optional[FinishAssessmentsDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentResultsDto
        """

        endpoint = "/api2/v1/lqa/assessments/scorings"
        if type(finish_assessments_dto) is dict:
            finish_assessments_dto = FinishAssessmentsDto.model_validate(
                finish_assessments_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = finish_assessments_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentResultsDto.model_validate(r.json())

    def get_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> AssessmentDetailDto:
        """
        Operation id: getAssessment
        Get LQA Assessment
        Returns Assessment status and the results.
        If given job is not from LQA workflow step, result from successive workflow steps may be returned
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailDto
        """

        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentDetailDto.model_validate(r.json())

    def get_assessment_results(
        self,
        assessment_request_dto: Optional[AssessmentRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AssessmentResultDto:
        """
        Operation id: getAssessmentResults
        Get LQA Assessment results

        :param assessment_request_dto: Optional[AssessmentRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentResultDto
        """

        endpoint = "/api2/v1/lqa/assessments/results"
        if type(assessment_request_dto) is dict:
            assessment_request_dto = AssessmentRequestDto.model_validate(
                assessment_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assessment_request_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentResultDto.model_validate(r.json())

    def get_assessments(
        self,
        assessment_request_dto: Optional[AssessmentRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AssessmentDetailsDto:
        """
        Operation id: getAssessments
        Get multiple LQA Assessments
        Returns Assessment results for given jobs.
        If any given job is not from LQA workflow step, result from successive workflow steps may be returned
        :param assessment_request_dto: Optional[AssessmentRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailsDto
        """

        endpoint = "/api2/v1/lqa/assessments"
        if type(assessment_request_dto) is dict:
            assessment_request_dto = AssessmentRequestDto.model_validate(
                assessment_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assessment_request_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentDetailsDto.model_validate(r.json())

    def get_lqa_report_link(
        self,
        job_parts: str,
        phrase_token: Optional[str] = None,
    ) -> LqaReportLinkDto:
        """
        Operation id: getLqaReportLink
        Get sharable link of LQA reports

        :param job_parts: str (required), query. Comma separated list of JobPart UIDs.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaReportLinkDto
        """

        endpoint = "/api2/v1/lqa/assessments/reports/link"

        params = {"jobParts": job_parts}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return LqaReportLinkDto.model_validate(r.json())

    def get_lqa_report_recipients(
        self,
        job_parts: str,
        name_or_email: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
    ) -> PageDtoLqaReportRecipientDto:
        """
        Operation id: getLqaReportRecipients
        Get recipients of email with LQA reports

        :param job_parts: str (required), query. Comma separated list of JobPart UIDs.
        :param name_or_email: Optional[str] = None (optional), query.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoLqaReportRecipientDto
        """

        endpoint = "/api2/v1/lqa/assessments/reports/recipients"

        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "jobParts": job_parts,
            "nameOrEmail": name_or_email,
        }

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return PageDtoLqaReportRecipientDto.model_validate(r.json())

    def run_auto_lqa(
        self,
        project_uid: str,
        run_auto_lqa_dto: Optional[RunAutoLqaDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: runAutoLqa
        Run Auto LQA
        Runs Auto LQA either for job parts listed in `jobParts`
                            or for all job parts in the given `projectWorkflowStep`.
                            Both fields are mutually exclusive. If the project has no steps,
                            then all job parts in the project accessible to the user are used.
        :param project_uid: str (required), path.
        :param run_auto_lqa_dto: Optional[RunAutoLqaDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = f"/api2/v1/projects/{project_uid}/runAutoLqa"
        if type(run_auto_lqa_dto) is dict:
            run_auto_lqa_dto = RunAutoLqaDto.model_validate(run_auto_lqa_dto)

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = run_auto_lqa_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return r.content

    def send_lqa_report_email(
        self,
        lqa_report_email_request_dto: Optional[LqaReportEmailRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> bytes:
        """
        Operation id: sendLqaReportEmail
        Send email(s) with LQA reports

        :param lqa_report_email_request_dto: Optional[LqaReportEmailRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """

        endpoint = "/api2/v1/lqa/assessments/reports/emails"
        if type(lqa_report_email_request_dto) is dict:
            lqa_report_email_request_dto = LqaReportEmailRequestDto.model_validate(
                lqa_report_email_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = lqa_report_email_request_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return r.content

    def start_assessments(
        self,
        assessment_request_dto: Optional[AssessmentRequestDto | dict] = None,
        phrase_token: Optional[str] = None,
    ) -> AssessmentDetailsDto:
        """
        Operation id: startAssessments
        Start multiple LQA Assessments
        Starts LQA assessments for the given job parts.
                            If any of them have the assessment already started or finished, they are left unchanged.
        :param assessment_request_dto: Optional[AssessmentRequestDto | dict] = None (optional), body.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailsDto
        """

        endpoint = "/api2/v1/lqa/assessments"
        if type(assessment_request_dto) is dict:
            assessment_request_dto = AssessmentRequestDto.model_validate(
                assessment_request_dto
            )

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = assessment_request_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentDetailsDto.model_validate(r.json())

    def start_new_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
    ) -> AssessmentBasicDto:
        """
        Operation id: startNewAssessment
        Start LQA Assessment
        Starts LQA assessment for the given job part.
                            If the assessment has already been started or finished, it's discarded and started fresh.
        :param job_uid: str (required), path.

        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentBasicDto
        """

        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"

        params = {}

        headers = {}
        headers = {k: v for k, v in headers.items() if v is not None}
        files = None
        content = None
        payload = None

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content,
        )

        return AssessmentBasicDto.model_validate(r.json())
