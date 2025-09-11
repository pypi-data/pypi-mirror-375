import logging

import click

from edos.services.invoice_service import InvoiceService

LOG = logging.getLogger(__name__)


@click.group()
def invoice():
    """Managing invoices"""


@invoice.command()
def generate():
    """Generate invoices"""
    click.secho("Generating invoice...", fg="blue")
    service = InvoiceService()
    invoice_url = service.create_invoice()
    click.secho("Invoice generated", fg="green")
    click.secho(f"URL: {invoice_url}", fg="blue")
