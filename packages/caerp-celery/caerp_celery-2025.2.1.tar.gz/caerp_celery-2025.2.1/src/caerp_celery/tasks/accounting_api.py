import datetime
import requests
import time
import transaction

from inspect import stack
from pyramid_celery import celery_app
from sqlalchemy import select, insert, delete

from caerp_base.mail import send_mail
from caerp_celery.conf import (
    get_setting,
    get_recipients_addresses,
    get_request,
)
from caerp_celery.tasks import utils
from caerp.models.accounting.operations import (
    AccountingOperationUpload,
    AccountingOperation,
)
from caerp.models.company import Company
from caerp import version as caerp_version


logger = utils.get_logger(__name__)


MAIL_ERROR_SUBJECT = "[ERREUR] Échec de la remontée comptable quotidienne"

MAIL_ERROR_BODY = """Une erreur est survenue lors de la remontée comptable
quotidienne. Vos états comptables pourraient ne pas être à jour.

Si le problème persiste, veuillez contacter votre administrateur en lui
transmettant le détail suivant :

    {error_message}
"""


class QuadraOnDemandApiHandler:

    base_url = "https://www.quadraondemand.com/QuadraODOpenApi"
    auth_url = f"{base_url}/token"
    check_url = f"{base_url}/api/v1/security/getHealthCheck"
    accounting_url = f"{base_url}/api/v1/comptabilite/ecritures_analytique"
    auth_token = None
    analytical_accounts_cache = {}
    accounting_upload_cache = {}
    used_upload_ids = []
    items_per_page = 5000
    max_attempt = 10
    retry_delay = 60  # in seconds
    attempt = 1

    def __init__(self, request):
        self.request = request
        self.mail_addresses = get_recipients_addresses(self.request)
        self._get_ini_config()

    def _get_ini_config(self):
        try:
            self.client_id = get_setting("caerp.quadraod_client_id", mandatory=True)
            self.client_secret = get_setting(
                "caerp.quadraod_client_secret", mandatory=True
            )
            self.vendor_name = get_setting("caerp.quadraod_vendor_name", mandatory=True)
            self.file_id = get_setting("caerp.quadraod_file_id", mandatory=True)
        except Exception as err:
            raise Exception(
                "QuadraOnDemand configuration missing, expecting : \
quadraod_client_id, quadraod_client_secret, quadraod_vendor_name, quadraod_file_id"
            )

    def _cache_companies_analytical_accounts(self):
        for company in Company.query().order_by(Company.id):
            if not company.code_compta in self.analytical_accounts_cache:
                self.analytical_accounts_cache[company.code_compta] = company.id

    def _cache_accounting_uploads(self):
        for upload in AccountingOperationUpload.query().filter_by(
            filetype=AccountingOperationUpload.SYNCHRONIZED_ACCOUNTING
        ):
            self.accounting_upload_cache[upload.date.year] = upload.id

    def _get_or_create_upload_id(self, date_object):
        upload_id = self.accounting_upload_cache.get(date_object.year)
        if not upload_id:
            upload = AccountingOperationUpload(
                date=datetime.date(date_object.year, 1, 1),
                filetype=AccountingOperationUpload.SYNCHRONIZED_ACCOUNTING,
                filename="Écritures {}".format(date_object.year),
            )
            self.request.dbsession.add(upload)
            self.request.dbsession.flush()
            self.accounting_upload_cache[date_object.year] = upload.id
            upload_id = upload.id
        if not upload_id in self.used_upload_ids:
            self.used_upload_ids.append(upload_id)
        return upload_id

    def _update_used_accounting_uploads(self):
        logger.debug("Updating used accounting uploads...")
        for upload_id in self.used_upload_ids:
            upload = self.request.dbsession.execute(
                select(AccountingOperationUpload).where(
                    AccountingOperationUpload.id == upload_id
                )
            ).scalar()
            if upload:
                upload.updated_at = datetime.datetime.now()
                self.request.dbsession.merge(upload)
        self.used_upload_ids = []
        transaction.commit()
        transaction.begin()

    def _delete_existing_operations(self, limit_date=datetime.date(1970, 1, 1)):
        logger.info(
            "Deleting existing accounting operations from {}...".format(
                limit_date.strftime("%Y-%m-%d")
            )
        )
        self.request.dbsession.execute(
            delete(AccountingOperation).where(AccountingOperation.date >= limit_date)
        )
        transaction.commit()
        transaction.begin()

    def _handle_api_response(self, api_response: requests.Response, **kw):
        if str(api_response.status_code)[:1] == "2":
            # SUCCESS
            self.attempt = 1
            return api_response.json()
        elif str(api_response.status_code)[:1] == "5":
            # SERVER ERROR (retrying)
            logger.error(
                "QuadraOnDemand API server error (HTTP {}) - Attempt {} / {}".format(
                    api_response.status_code,
                    self.attempt,
                    self.max_attempt,
                )
            )
            self.attempt += 1
            if self.attempt > self.max_attempt:
                raise Exception("[FAILED] QuadraOnDemand API server is not available")
            else:
                # Retry lauching parent function after delay
                time.sleep(self.retry_delay)
                return getattr(self, stack()[1].function)(**kw)
        else:
            # CLIENT ERROR
            raise Exception(
                "[FAILED] QuadraOnDemand API client error : HTTP {} / {}".format(
                    api_response.status_code, api_response.content
                )
            )

    def _handle_api_exception(self, api_exception, **kw):
        logger.error(
            "QuadraOnDemand API server exception - Attempt {} / {}".format(
                self.attempt,
                self.max_attempt,
            )
        )
        logger.error(api_exception)
        self.attempt += 1
        if self.attempt > self.max_attempt:
            raise Exception(
                "[FAILED] QuadraOnDemand API server is not available : {}".format(
                    api_exception
                )
            )
        else:
            # Retry lauching parent function after delay
            time.sleep(self.retry_delay)
            return getattr(self, stack()[1].function)(**kw)

    def _api_authorize(self):
        try:
            logger.debug(f"Requesting bearer token from {self.auth_url}")
            response = requests.post(
                self.auth_url,
                data=dict(
                    grant_type="client_credentials",
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    vendor_name=self.vendor_name,
                    application_name="CAERP",
                    application_version=caerp_version(),
                ),
            )
        except Exception as e:
            raise Exception("QuadraOnDemand API authorization failed : {}".format(e))
        else:
            json_response = self._handle_api_response(response)
            logger.debug("Bearer token received !")
            self.auth_token = json_response["access_token"]
            return True

    def _api_fetch_operations(self, page=1):
        url = "{}?numeroDossier={}&maxPage={}&numeroPage={}".format(
            self.accounting_url,
            self.file_id,
            self.items_per_page,
            page,
        )
        logger.debug(f"Fetching accounting operations from {url}")
        try:
            headers = dict(Authorization=f"Bearer {self.auth_token}")
            response = requests.post(url, headers=headers)
        except Exception as e:
            self._handle_api_exception(e, page=page)
        else:
            json_response = self._handle_api_response(response, page=page)
            logger.debug(
                "Successfully fetch {} operations from API (page {}/{})".format(
                    min(self.items_per_page, json_response["NbElement"]),
                    page,
                    json_response["NbPage"],
                )
            )
            return json_response

    def _get_operations_metadata_from_api_response(self, api_response):
        try:
            return (
                api_response["NbElement"],
                api_response["NbPage"],
                datetime.datetime.strptime(
                    api_response["Data"][0]["EcritureDate"], "%d/%m/%Y"
                ),
            )
        except Exception as e:
            raise Exception(
                "Missing metadata from QuadraOnDemand API response : {}".format(e)
            )

    def _format_operation_from_json(self, operation_json):
        ec_ana = operation_json["Centre"]
        ec_date = datetime.datetime.strptime(operation_json["EcritureDate"], "%d/%m/%Y")
        ec_compte = (
            operation_json["CompAuxNum"]
            if operation_json["CompAuxNum"] != ""
            else operation_json["CompteNum"]
        )
        ec_label = operation_json["EcritureLib"]
        if float(operation_json["Debit"]) == 0:
            ec_debit = 0
            ec_credit = operation_json["MontantAna"]
        else:
            ec_debit = operation_json["MontantAna"]
            ec_credit = 0
        company_id = (
            self.analytical_accounts_cache[ec_ana]
            if ec_ana in self.analytical_accounts_cache
            else None
        )
        upload_id = self._get_or_create_upload_id(ec_date)
        return {
            "id": None,
            "date": ec_date.strftime("%Y-%m-%d"),
            "analytical_account": ec_ana,
            "general_account": ec_compte,
            "label": ec_label,
            "debit": ec_debit,
            "credit": ec_credit,
            "balance": ec_debit - ec_credit,
            "company_id": company_id,
            "upload_id": upload_id,
        }

    def _store_operations(self, operations_data):
        logger.info(f"Storing {len(operations_data)} operations ...")
        operations_to_insert = []
        for json_op in operations_data:
            operations_to_insert.append(self._format_operation_from_json(json_op))
        self.request.dbsession.execute(
            insert(AccountingOperation), operations_to_insert
        )
        transaction.commit()
        transaction.begin()

    def _send_error_by_mail(self, error):
        if self.mail_addresses:
            try:
                message = MAIL_ERROR_BODY.format(error_message=str(error))
                subject = MAIL_ERROR_SUBJECT
                send_mail(
                    self.request,
                    self.mail_addresses,
                    message,
                    subject,
                )
            except Exception as err:
                logger.exception(
                    "Failed to send error to {} : {}".format(self.mail_addresses, err)
                )

    def synchronize_accounting(self):

        try:

            # Prepare cache
            self._cache_companies_analytical_accounts()
            self._cache_accounting_uploads()

            # Authenticate
            self._api_authorize()

            # Fetch operations
            page_num = 1
            logger.info(f"Fetching accounting operations page {page_num} ...")
            api_response = self._api_fetch_operations(page_num)
            (
                nb_operations,
                nb_pages,
                first_op_date,
            ) = self._get_operations_metadata_from_api_response(api_response)
            logger.debug(f"{nb_operations} operations will be sync on {nb_pages} pages")
            self._delete_existing_operations(first_op_date)
            self._store_operations(api_response["Data"])
            while page_num < nb_pages:
                page_num += 1
                logger.info(
                    f"Fetching accounting operations page {page_num} / {nb_pages}..."
                )
                api_response = self._api_fetch_operations(page_num)
                self._store_operations(api_response["Data"])

            # Update accounting uploads
            self._update_used_accounting_uploads()

        except Exception as err:

            logger.error(err)
            logger.error("Synchronization failed !")
            self._send_error_by_mail(err)

        else:

            logger.info(f"Synchronization succeed with {nb_operations} operations !")


@celery_app.task(bind=True)
def synchronize_accounting_from_quadraod(self, request=None):

    if not request:
        request = get_request()
    handler = QuadraOnDemandApiHandler(request)
    handler.synchronize_accounting()
