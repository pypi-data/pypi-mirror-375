import sys


def import_bulkload_api():
    try:
        from clickzetta.bulkload import bulkload_api

        return bulkload_api
    except ImportError:
        print(
            "*** NOTE: bulkload is a standalone package now; please install it: \n"
            "***    pip install clickzetta-ingestion-python",
            file=sys.stderr,
        )
        raise

def import_bulkload_v2_api():
    try:
        from clickzetta_ingestion.bulkload import bulkload_api

        return bulkload_api
    except ImportError:
        print(
            "*** NOTE: bulkload is a standalone package now; please install it: \n"
            "***    pip install clickzetta-ingestion-python-v2",
            file=sys.stderr,
        )
        raise
