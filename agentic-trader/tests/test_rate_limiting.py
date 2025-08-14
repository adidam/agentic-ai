#!/usr/bin/env python3
"""
Test script to verify rate limiting functionality
"""

import time
import logging
from config import API_DELAY, MAX_RETRIES, RETRY_DELAY
from test_strategies import safe_api_call, fetch_top_volume

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_rate_limiting():
    """Test the rate limiting functionality"""
    logger.info("Testing rate limiting functionality...")

    # Test 1: Single API call
    logger.info("Test 1: Single API call")
    result = safe_api_call(fetch_top_volume, index_nifty='', size=5)
    if result:
        logger.info(f"✓ Successfully fetched {len(result)} stocks")
    else:
        logger.error("✗ Failed to fetch data")

    # Test 2: Multiple API calls with delays
    logger.info("Test 2: Multiple API calls with delays")
    indices = ['', 'next', 'midcap', 'smallcap']

    for i, index in enumerate(indices):
        logger.info(f"Fetching data for index: {index or 'NIFTY'}")
        result = safe_api_call(fetch_top_volume, index_nifty=index, size=3)
        if result:
            logger.info(
                f"✓ Successfully fetched {len(result)} stocks for {index or 'NIFTY'}")
        else:
            logger.error(f"✗ Failed to fetch data for {index or 'NIFTY'}")

        # Add extra delay between different indices
        if i < len(indices) - 1:
            logger.info(f"Waiting 2 seconds before next index...")
            time.sleep(2)

    logger.info("Rate limiting test completed!")


if __name__ == "__main__":
    test_rate_limiting()

