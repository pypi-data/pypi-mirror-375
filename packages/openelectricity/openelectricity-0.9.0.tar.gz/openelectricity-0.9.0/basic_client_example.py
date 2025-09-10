#!/usr/bin/env python

from datetime import datetime

from openelectricity import OEClient
from openelectricity.types import DataMetric, UnitFueltechType

# Create client
with OEClient() as client:
    # Get network data
    response = client.get_network_data(
        network_code="NEM",
        metrics=[DataMetric.POWER],
        interval="5m",
        fueltech=[UnitFueltechType.WIND],
        date_start=datetime(2025, 9, 7, 0, 0, 0),
        date_end=datetime(2025, 9, 8, 14, 15, 0),
        primary_grouping="network_region",
        secondary_grouping="fueltech_group",
    )

    # Print first 100 data points
    count = 0
    for series in response.data:
        for result in series.results:
            for point in result.data:
                if count < 1000:
                    print(
                        f"{count + 1}. {result.name} - {result.columns.fueltech_group}: {point.timestamp} = {point.value:.2f} {series.unit}"
                    )
                    count += 1
                else:
                    break
            if count >= 100:
                break
        if count >= 100:
            break

    print(f"\nTotal series: {len(response.data)}")
    if response.data:
        total_points = sum(len(result.data) for series in response.data for result in series.results)
        print(f"Total data points: {total_points}")
