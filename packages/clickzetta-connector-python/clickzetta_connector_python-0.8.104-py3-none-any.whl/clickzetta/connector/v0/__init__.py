import sys

PY39 = sys.version_info >= (3, 9)


def import_ingestion_api():
    try:
        from clickzetta_ingestion.realtime import realtime_stream_api

        return realtime_stream_api
    except ImportError:
        print(
            "*** NOTE: bulkload is a standalone package now; please install it: \n"
            "***    pip install clickzetta-ingestion-python-v2",
            file=sys.stderr,
        )
        raise


def import_igs_client_builder():
    try:
        from clickzetta_ingestion.realtime.cz_client import CZClientBuilder
        return CZClientBuilder()
    except ImportError:
        print(
            "*** NOTE: bulkload is a standalone package now; please install it: \n"
            "***    pip install clickzetta-ingestion-python-v2",
            file=sys.stderr,
        )
        raise

def import_bulkload_v2_api():
    try:
        from clickzetta_ingestion.bulkload.v2 import BulkLoadStreamV2

        return BulkLoadStreamV2
    except ImportError:
        print(
            "*** NOTE: bulkload is a standalone package now; please install it: \n"
            "***    pip install clickzetta-ingestion-python-v2",
            file=sys.stderr,
        )
        raise