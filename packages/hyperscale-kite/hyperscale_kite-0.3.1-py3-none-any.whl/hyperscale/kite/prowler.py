import glob
import os
import re
from dataclasses import dataclass

from hyperscale.kite.config import Config
from hyperscale.kite.helpers import get_account_ids_in_scope


@dataclass
class ProwlerResult:
    account_id: str
    status: str
    extended_status: str
    resource_uid: str
    resource_name: str
    resource_details: str
    region: str


class NoProwlerDataException(Exception):
    pass


def _filter_old_files(files: list[str]) -> list[str]:
    latest_files = {}
    pattern = re.compile(r"prowler-output-(\d+)-(\d+)\.csv")
    for f in files:
        filename = os.path.basename(f)
        m = pattern.match(filename)
        if m:
            account_id, timestamp = m.groups()
            if (
                account_id not in latest_files
                or timestamp > latest_files[account_id][0]
            ):
                latest_files[account_id] = (timestamp, f)
    return [e[1] for e in latest_files.values()]


def get_prowler_output() -> dict[str, list[ProwlerResult]]:
    config = Config.get()
    prowler_files = glob.glob(f"{config.prowler_output_dir}/prowler-output-*.csv")
    prowler_files = _filter_old_files(prowler_files)

    if not prowler_files:
        raise NoProwlerDataException(
            f"No prowler output files found in {config.prowler_output_dir}"
        )

    results = {}
    for file_path in prowler_files:
        with open(file_path) as f:
            # Skip header line
            next(f)
            for line in f:
                records = line.strip().split(";")
                if len(records) >= 26:  # Ensure we have enough fields
                    check_id = records[10]
                    result = ProwlerResult(
                        account_id=records[2],
                        status=records[13],
                        extended_status=records[14],
                        resource_uid=records[20],
                        resource_name=records[21],
                        resource_details=records[22],
                        region=records[25],
                    )

                    if check_id not in results:
                        results[check_id] = []
                    results[check_id].append(result)
    return results


def find_failed_accounts_and_regions(check_id: str) -> list[tuple[str, str]]:
    config = Config.get()
    failing = []
    for account_id in get_account_ids_in_scope():
        for region in config.active_regions:
            if not did_check_pass(check_id, account_id, region):
                failing.append((account_id, region))
    return failing


def did_check_pass(check_id: str, account_id: str, region: str) -> bool:
    prowler_output = get_prowler_output()
    results = prowler_output.get(check_id, [])
    check_found = False
    for result in results:
        if result.account_id == account_id and result.region == region:
            if result.status == "PASS":
                check_found = True
            else:
                return False
    return check_found
