import os
import subprocess
from datetime import datetime


def git_tag():
    get_git_tag_cmd = ["git", "rev-parse", "--short", "HEAD"]
    tag_result = subprocess.run(get_git_tag_cmd, capture_output=True)
    if tag_result.returncode == 0:
        tag = tag_result.stdout.decode("utf-8").strip()
        check_modifications_cmd = ["git", "diff", "--quiet", "--exit-code"]
        mod_result = subprocess.run(check_modifications_cmd)
        if mod_result.returncode != 0:
            tag += "-edited"
    else:
        tag = "undefined"
    return tag


def time_now():
    return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


def project_root():
    return os.path.abspath(os.path.join(__file__, "..", "..", ".."))


def report_performance(tag, logger, packet_count, passed_time_ns):
    logger.info(f"[{ tag }] Completed processing:")
    logger.info(f" > { packet_count } packets")
    logger.info(f" > { passed_time_ns } ns")
    if packet_count:
        logger.info(f" > { passed_time_ns / packet_count } ns/packet")
    if passed_time_ns:
        logger.info(f" > { packet_count / (passed_time_ns / 1000000000) } packets/s")
