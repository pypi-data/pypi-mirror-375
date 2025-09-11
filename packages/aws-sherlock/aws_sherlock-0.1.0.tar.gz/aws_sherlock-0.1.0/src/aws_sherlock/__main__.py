import boto3
import click
import sys
from datetime import datetime


def filter_log_events(log_group: str, from_iso8601: str, to_iso8601: str, region:str, filter_pattern:str, output:str):
    click.echo(f"Filtering logs from {log_group}...")

    client = boto3.client("logs", region_name=region)

    # Convert ISO 8601 to milliseconds since epoch
    start_time = int(datetime.fromisoformat(from_iso8601).timestamp() * 1000)
    end_time = int(datetime.fromisoformat(to_iso8601).timestamp() * 1000)

    try:
        paginator = client.get_paginator("filter_log_events")
        page_iterator = paginator.paginate(
            logGroupName=log_group, startTime=start_time, endTime=end_time, filterPattern=filter_pattern
        )

        with open(output, "w") as f:
            for page in page_iterator:
                for event in page["events"]:
                    # Convert timestamp from milliseconds to readable date
                    timestamp_ms = event['timestamp']
                    readable_date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    f.write(
                        f"{event['timestamp']}\t{readable_date}\t\t{event['logStreamName']}\t{event['message']}\n"
                    )

        print(f"Logs saved to {output}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


@click.command()
@click.option('--log-group', required=True, help='CloudWatch Log Group name')
@click.option('--start', required=True, help='From time for log filtering')
@click.option('--end', required=True, help='To time for log filtering')
@click.option('--region', required=True, help='AWS region name')
@click.option('--filter-pattern', default='', help='Filter pattern for logs')
@click.option('--output', default='logs.txt', help='Output file name')
def main(log_group, start, end, region, filter_pattern, output):
    filter_log_events(log_group, start, end, region, filter_pattern, output)

if __name__ == '__main__':
    main()