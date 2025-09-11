import boto3
from botocore.exceptions import ClientError


class LogsClient:
    def __init__(self, region_name="eu-central-1", profile_name=None):
        """Initialize the CloudWatch Logs client wrapper."""
        session = boto3.Session(profile_name=profile_name)
        self.client = session.client("logs", region_name=region_name)

    def filter_log_events(
        self,
        log_group_name,
        log_stream_names=None,
        start_time=None,
        end_time=None,
        filter_pattern=None,
        next_token=None,
        limit=None,
    ):
        """Filter log events from CloudWatch Logs.

        Args:
            log_group_name (str): The name of the log group.
            log_stream_names (list, optional): List of log stream names to filter.
            start_time (int, optional): Start time in milliseconds since epoch.
            end_time (int, optional): End time in milliseconds since epoch.
            filter_pattern (str, optional): Filter pattern to match log events.
            next_token (str, optional): Token for pagination.
            limit (int, optional): Maximum number of events to return.

        Returns:
            dict: Response from filter_log_events API call.
        """
        params = {"logGroupName": log_group_name}

        if log_stream_names:
            params["logStreamNames"] = log_stream_names
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if filter_pattern:
            params["filterPattern"] = filter_pattern
        if next_token:
            params["nextToken"] = next_token
        if limit:
            params["limit"] = limit

        try:
            response = self.client.filter_log_events(**params)
            return response
        except ClientError as e:
            raise e
