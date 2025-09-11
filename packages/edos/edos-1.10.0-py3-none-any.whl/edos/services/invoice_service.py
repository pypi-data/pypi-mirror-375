import datetime
import uuid

from clockify_api_client.client import ClockifyAPIClient
from clockify_api_client.models.report import Report
from clockify_api_client.models.user import User
from dateutil.relativedelta import relativedelta
from fakturoid import Fakturoid, Invoice, InvoiceLine

from edos.exceptions import UserReadableException
from edos.settings import conf


class InvoiceService:
    def __init__(self):
        self.fakturoid = Fakturoid(
            conf.INVOICE_CONFIG.get("fakturoid_account_slug"),
            conf.INVOICE_CONFIG.get("fakturoid_account_email"),
            conf.INVOICE_CONFIG.get("fakturoid_api_key"),
            conf.FAKTUROID_USER_AGENT,
        )
        self.clockify = ClockifyAPIClient().build(conf.INVOICE_CONFIG.get("clockify_api_key"), conf.CLOCKIFY_API_URL)

    def create_invoice(self) -> str:
        """generate invoice and return its URL"""
        last_month_hour_report = self.get_last_month_hour_report()
        custom_id = uuid.uuid4()
        invoice = Invoice(
            subject_id=self.get_subject_id(),
            issued_on=(datetime.datetime.now().replace(day=1) - relativedelta(days=1)).date(),
            lines=[
                InvoiceLine(
                    name="software development",
                    unit_name="hod",
                    quantity=last_month_hour_report,
                    unit_price=1,
                )
            ],
            custom_id=str(custom_id),
        )
        self.fakturoid.save(invoice)
        invoices = self.fakturoid.invoices(custom_id=custom_id)
        if len(invoices) == 0:
            raise UserReadableException("Invoice not found")
        return invoices[0].html_url

    def get_subject_id(self) -> int:
        for subject in self.fakturoid.subjects():
            if subject.registration_no == conf.ENDEVEL_ICO:
                return subject.id
        raise UserReadableException("Subject not found")

    def get_last_month_hour_report(self) -> int:
        report_api: Report = self.clockify.reports
        last_month_start = (datetime.datetime.now() - relativedelta(months=1)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_end = (datetime.datetime.now().replace(day=1) - relativedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        return (
            report_api.get_summary_report(
                conf.CLOCKIFY_ENDEVEL_WORKSPACE_ID,
                {
                    "dateRangeStart": last_month_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "dateRangeEnd": last_month_end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "summaryFilter": {"groups": ["USER_GROUP"]},
                    "users": {
                        "ids": [self.get_clockify_user_id()],
                        "status": "ACTIVE_WITH_PENDING",
                        "contains": "CONTAINS",
                    },
                    "amountShown": "HIDE_AMOUNT",
                },
            )
            .get("totals", [])[0]
            .get("totalTime")
            / 3600
        )

    def get_clockify_user_id(self) -> str:
        user_api: User = self.clockify.users
        return user_api.get_current_user().get("id")
